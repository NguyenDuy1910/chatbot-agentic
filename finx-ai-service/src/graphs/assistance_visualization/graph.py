"""
Assistance & Visualization Graph.

Main graph orchestrating user assistance and chart visualization workflow.
Handles different types of assistance (data, user guide, misleading) and
chart generation/adjustment.
"""

import logging
from typing import Any, Dict, Type, TypedDict

from langgraph.graph import END

from src.core.base_graph import BaseGraph
from src.graphs.assistance_visualization.state import AssistanceVisualizationState

logger = logging.getLogger(__name__)


class AssistanceVisualizationGraph(BaseGraph):
    """
    LangGraph for Assistance & Visualization.
    
    Workflow:
    1. Route by Intent:
       - GENERAL -> Data Assistance (streaming)
       - USER_GUIDE -> User Guide Assistance (streaming)
       - MISLEADING_QUERY -> Misleading Assistance
       - TEXT_TO_SQL (with visualization flag) -> Chart Generation
    2. Chart Adjustment (if needed):
       - Check if adjustment instructions provided
       - Yes: Chart Adjustment
       - No: End
    
    The graph supports:
    - Intent-based routing to different assistance types
    - Streaming responses for assistance nodes
    - Chart generation and adjustment
    - Graceful handling of all intent types
    """
    
    def __init__(self):
        """Initialize the Assistance & Visualization Graph."""
        super().__init__("assistance_visualization")
    
    def get_state_schema(self) -> Type[TypedDict]:
        """Get the state schema for this graph."""
        return AssistanceVisualizationState
    
    def _add_nodes(self) -> None:
        """Add all processing nodes to the graph."""
        # Import nodes here to avoid circular imports
        from src.graphs.assistance_visualization.nodes import (
            data_assistance_node,
            user_guide_assistance_node,
            misleading_assistance_node,
            chart_generation_node,
            chart_adjustment_node,
        )
        
        # User assistance nodes
        self.graph.add_node("data_assistance", data_assistance_node)
        self.graph.add_node("user_guide_assistance", user_guide_assistance_node)
        self.graph.add_node("misleading_assistance", misleading_assistance_node)
        
        # Chart visualization nodes
        self.graph.add_node("chart_generation", chart_generation_node)
        self.graph.add_node("chart_adjustment", chart_adjustment_node)
        
        # Helper nodes
        self.graph.add_node("format_response", self._format_response_node)
    
    def _add_edges(self) -> None:
        """Define workflow with conditional routing."""
        
        # ========== Entry Point ==========
        self.graph.set_entry_point("route_by_intent")
        self.graph.add_node("route_by_intent", self._route_by_intent_node)
        
        # ========== Intent Routing ==========
        self.graph.add_conditional_edges(
            "route_by_intent",
            self._route_by_intent,
            {
                "data_assistance": "data_assistance",
                "user_guide_assistance": "user_guide_assistance",
                "misleading_assistance": "misleading_assistance",
                "chart_generation": "chart_generation",
            }
        )
        
        # ========== Assistance Paths ==========
        # All assistance nodes go directly to format response
        self.graph.add_edge("data_assistance", "format_response")
        self.graph.add_edge("user_guide_assistance", "format_response")
        self.graph.add_edge("misleading_assistance", "format_response")
        
        # ========== Chart Generation Path ==========
        # After chart generation, check if adjustment is needed
        self.graph.add_conditional_edges(
            "chart_generation",
            self._check_chart_adjustment,
            {
                "adjust": "chart_adjustment",
                "no_adjust": "format_response",
            }
        )
        
        # Chart adjustment -> Format response
        self.graph.add_edge("chart_adjustment", "format_response")
        
        # ========== Final Step ==========
        self.graph.add_edge("format_response", END)
    
    # ==================== Routing Functions ====================
    
    def _route_by_intent(self, state: Dict[str, Any]) -> str:
        """Route based on intent and visualization flag."""
        intent = state.get("intent", "GENERAL")
        needs_visualization = state.get("metadata", {}).get("needs_visualization", False)
        
        # If TEXT_TO_SQL and needs visualization, route to chart generation
        if intent == "TEXT_TO_SQL" and needs_visualization:
            logger.info("Routing to chart generation")
            return "chart_generation"
        elif intent == "GENERAL":
            logger.info("Routing to data assistance")
            return "data_assistance"
        elif intent == "USER_GUIDE":
            logger.info("Routing to user guide assistance")
            return "user_guide_assistance"
        elif intent == "MISLEADING_QUERY":
            logger.info("Routing to misleading assistance")
            return "misleading_assistance"
        else:
            # Default to data assistance
            logger.warning(f"Unknown intent: {intent}, defaulting to data assistance")
            return "data_assistance"
    
    def _check_chart_adjustment(self, state: Dict[str, Any]) -> str:
        """Check if chart adjustment is needed."""
        adjustment_instructions = state.get("adjustment_instructions")
        
        if adjustment_instructions:
            logger.info("Chart adjustment instructions provided, routing to adjustment")
            return "adjust"
        else:
            logger.info("No chart adjustment needed")
            return "no_adjust"
    
    # ==================== Helper Nodes ====================
    
    async def _route_by_intent_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare state for intent-based routing."""
        state["current_step"] = "route_by_intent"
        intent = state.get("intent", "GENERAL")
        logger.info(f"Routing by intent: {intent}")
        
        # Set assistance type based on intent
        if intent == "GENERAL":
            state["assistance_type"] = "data"
        elif intent == "USER_GUIDE":
            state["assistance_type"] = "user_guide"
        elif intent == "MISLEADING_QUERY":
            state["assistance_type"] = "misleading"
        
        return state
    
    async def _format_response_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Format final response."""
        logger.info("Formatting assistance & visualization response...")
        state["current_step"] = "format_response"
        
        try:
            response = {}
            
            # Add assistance response if present
            if state.get("assistance_response"):
                response["assistance"] = {
                    "type": state.get("assistance_type"),
                    "response": state["assistance_response"],
                    "reasoning": state.get("assistance_reasoning"),
                }
            
            # Add chart if present
            if state.get("chart_schema"):
                response["chart"] = {
                    "type": state.get("chart_type"),
                    "schema": state.get("adjusted_chart") or state["chart_schema"],
                    "reasoning": state.get("chart_reasoning"),
                }
            
            state["response"] = response
            state["response_type"] = f"assistance_{state.get('assistance_type', 'unknown')}"
            state["status"] = "completed"
            
            logger.info("Assistance & visualization response formatted successfully")
            
        except Exception as e:
            logger.error(f"Error formatting response: {e}")
            state["errors"].append(f"Response formatting failed: {str(e)}")
            state["status"] = "failed"
        
        return state


# Factory function for easy graph creation
def create_assistance_visualization_graph() -> AssistanceVisualizationGraph:
    """
    Create and build an Assistance & Visualization graph.
    
    Returns:
        Built AssistanceVisualizationGraph ready for execution
    """
    graph = AssistanceVisualizationGraph()
    graph.build()
    return graph

