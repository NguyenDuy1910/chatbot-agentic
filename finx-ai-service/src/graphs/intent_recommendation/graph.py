"""
Intent & Recommendation Graph.

Main graph orchestrating the intent classification and recommendation workflow.
Handles intent classification and routes to appropriate recommendation nodes.
"""

import logging
from typing import Any, Dict, Type, TypedDict

from langgraph.graph import END

from src.core.base_graph import BaseGraph
from src.graphs.intent_recommendation.nodes import (
    intent_classification_node,
    question_recommendation_node,
    relationship_recommendation_node,
    semantics_description_node,
)
from src.graphs.intent_recommendation.state import IntentRecommendationState

logger = logging.getLogger(__name__)


class IntentRecommendationGraph(BaseGraph):
    """
    LangGraph for Intent Classification and Recommendations.
    
    Workflow:
    1. Intent Classification - Classify user intent (TEXT_TO_SQL, GENERAL, USER_GUIDE, MISLEADING_QUERY)
    2. Route by Intent:
       - TEXT_TO_SQL -> Question Recommendation
       - GENERAL -> Semantics Description -> Relationship Recommendation
       - USER_GUIDE -> Question Recommendation
       - MISLEADING_QUERY -> End (no recommendations)
    
    The graph supports:
    - Intent-based conditional routing
    - Multiple recommendation types based on intent
    - Graceful handling of all intent types
    """
    
    def __init__(self):
        """Initialize the Intent & Recommendation Graph."""
        super().__init__("intent_recommendation")
    
    def get_state_schema(self) -> Type[TypedDict]:
        """Get the state schema for this graph."""
        return IntentRecommendationState
    
    def _add_nodes(self) -> None:
        """Add all processing nodes to the graph."""
        # Main workflow nodes
        self.graph.add_node("intent_classification", intent_classification_node)
        self.graph.add_node("question_recommendation", question_recommendation_node)
        self.graph.add_node("relationship_recommendation", relationship_recommendation_node)
        self.graph.add_node("generate_semantics_description", semantics_description_node)
        
        # Helper nodes for response formatting
        self.graph.add_node("format_response", self._format_response_node)
    
    def _add_edges(self) -> None:
        """Define workflow with conditional routing."""
        
        # ========== Entry Point ==========
        self.graph.set_entry_point("intent_classification")
        
        # ========== Intent Routing ==========
        # After intent classification, route based on intent type
        self.graph.add_conditional_edges(
            "intent_classification",
            self._route_by_intent,
            {
                "text2sql_recommendation": "question_recommendation",
                "general_recommendation": "generate_semantics_description",
                "user_guide_recommendation": "question_recommendation",
                "misleading_end": "format_response",
            }
        )
        
        # ========== TEXT_TO_SQL & USER_GUIDE Path ==========
        # Question recommendation -> Format response -> End
        self.graph.add_edge("question_recommendation", "format_response")
        
        # ========== GENERAL Path ==========
        # Semantics description -> Relationship recommendation -> Format response -> End
        self.graph.add_edge("generate_semantics_description", "relationship_recommendation")
        self.graph.add_edge("relationship_recommendation", "format_response")
        
        # ========== Final Step ==========
        self.graph.add_edge("format_response", END)
    
    # ==================== Routing Functions ====================
    
    def _route_by_intent(self, state: Dict[str, Any]) -> str:
        """
        Route based on classified intent.
        
        Args:
            state: Current graph state
            
        Returns:
            Routing decision based on intent
        """
        intent = state.get("intent", "TEXT_TO_SQL")
        
        if intent == "TEXT_TO_SQL":
            logger.info("Routing to question recommendation for TEXT_TO_SQL")
            return "text2sql_recommendation"
        elif intent == "GENERAL":
            logger.info("Routing to semantics description for GENERAL")
            return "general_recommendation"
        elif intent == "USER_GUIDE":
            logger.info("Routing to question recommendation for USER_GUIDE")
            return "user_guide_recommendation"
        elif intent == "MISLEADING_QUERY":
            logger.info("Routing to end for MISLEADING_QUERY (no recommendations)")
            return "misleading_end"
        else:
            # Default to question recommendation for unknown intents
            logger.warning(f"Unknown intent: {intent}, defaulting to question recommendation")
            return "text2sql_recommendation"
    
    # ==================== Helper Nodes ====================
    
    async def _format_response_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format final response based on intent and recommendations.
        
        Args:
            state: Current graph state
            
        Returns:
            Updated state with formatted response
        """
        logger.info("Formatting intent & recommendation response...")
        state["current_step"] = "format_response"
        
        try:
            intent = state.get("intent", "TEXT_TO_SQL")
            
            response = {
                "intent": intent,
                "rephrased_question": state.get("rephrased_question", ""),
                "intent_reasoning": state.get("intent_reasoning", ""),
                "confidence_score": state.get("confidence_score", 0.0),
            }
            
            # Add recommendations based on what was generated
            if state.get("recommended_questions"):
                response["recommended_questions"] = state["recommended_questions"]
            
            if state.get("recommended_relationships"):
                response["recommended_relationships"] = state["recommended_relationships"]
            
            if state.get("semantics_description"):
                response["semantics_description"] = state["semantics_description"]
            
            # Add metadata
            response["metadata"] = {
                "db_schemas_count": len(state.get("db_schemas", [])),
                "retrieved_tables": state.get("retrieved_tables", []),
            }
            
            state["response"] = response
            state["response_type"] = f"intent_{intent.lower()}"
            state["status"] = "completed"
            
            logger.info(f"Response formatted successfully for intent: {intent}")
            
        except Exception as e:
            logger.error(f"Error formatting response: {e}")
            state["errors"].append(f"Response formatting failed: {str(e)}")
            state["response"] = {
                "intent": state.get("intent", "TEXT_TO_SQL"),
                "error": "Failed to format response",
            }
            state["status"] = "failed"
        
        return state


# Factory function for easy graph creation
def create_intent_recommendation_graph() -> IntentRecommendationGraph:
    """
    Create and build an Intent & Recommendation graph.
    
    Returns:
        Built IntentRecommendationGraph ready for execution
    """
    graph = IntentRecommendationGraph()
    graph.build()
    return graph

