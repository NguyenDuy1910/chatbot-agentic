"""Assistance & Visualization Workflow - handles user assistance and chart generation."""

import logging
from typing import Any, Dict, List, Literal, Optional

from langgraph.graph import END
from langfuse.decorators import observe

from src.core.base_graph import BaseGraph
from src.core.base_state import BaseState
from src.workflows.config import (
    get_workflow_config,
    WORKFLOW_LOGGER_NAME,
)

logger = logging.getLogger(WORKFLOW_LOGGER_NAME)


class AssistanceVisualizationState(BaseState):
    """State for Assistance & Visualization workflow."""
    
    # Input
    query: str
    project_id: Optional[str]
    intent: Optional[str]
    histories: List[Dict[str, Any]]
    configuration: Optional[Dict[str, Any]]
    
    # Database Context
    db_schemas: List[str]
    
    # SQL Context (from SQL Processing Graph)
    sql: Optional[str]
    sql_results: Optional[Any]
    
    # User Assistance
    assistance_type: Optional[Literal["data", "user_guide", "misleading"]]
    assistance_response: Optional[str]
    assistance_reasoning: Optional[str]
    is_streaming: bool
    
    # Chart Generation
    chart_type: Optional[str]
    chart_schema: Optional[Dict[str, Any]]
    chart_reasoning: Optional[str]
    sample_data: Optional[Dict[str, Any]]
    sample_column_values: Optional[Dict[str, Any]]
    vega_schema: Optional[Dict[str, Any]]
    remove_data_from_chart_schema: bool
    
    # Chart Adjustment
    adjustment_instructions: Optional[str]
    adjusted_chart: Optional[Dict[str, Any]]
    adjustment_reasoning: Optional[str]
    
    # Final Response
    response: Optional[Dict[str, Any]]
    response_type: Optional[str]


def create_initial_state(
    query: str,
    project_id: Optional[str] = None,
    intent: Optional[str] = None,
    histories: Optional[List[Dict[str, Any]]] = None,
    configuration: Optional[Dict[str, Any]] = None,
    db_schemas: Optional[List[str]] = None,
    sql: Optional[str] = None,
    sql_results: Optional[Any] = None,
    is_streaming: bool = False,
    remove_data_from_chart_schema: bool = False,
) -> AssistanceVisualizationState:
    return AssistanceVisualizationState(
        query=query,
        project_id=project_id,
        intent=intent,
        histories=histories or [],
        configuration=configuration or {},
        db_schemas=db_schemas or [],
        sql=sql,
        sql_results=sql_results,
        assistance_type=None,
        assistance_response=None,
        assistance_reasoning=None,
        is_streaming=is_streaming,
        chart_type=None,
        chart_schema=None,
        chart_reasoning=None,
        sample_data=None,
        sample_column_values=None,
        vega_schema=None,
        remove_data_from_chart_schema=remove_data_from_chart_schema,
        adjustment_instructions=None,
        adjusted_chart=None,
        adjustment_reasoning=None,
        response=None,
        response_type=None,
        errors=[],
        warnings=[],
        status="pending",
        current_step="",
        metadata={},
        context={},
    )


@observe(name="Data Assistance Node")
async def data_assistance_node(state: Dict[str, Any]) -> Dict[str, Any]:
    state["current_step"] = "data_assistance"
    try:
        # TODO: Implement data assistance logic
        pass
    except Exception as e:
        logger.error(f"Error in data_assistance: {e}")
        state["errors"].append(f"Data Assistance failed: {str(e)}")
    return state


@observe(name="User Guide Assistance Node")
async def user_guide_assistance_node(state: Dict[str, Any]) -> Dict[str, Any]:
    state["current_step"] = "user_guide_assistance"
    try:
        # TODO: Implement user guide assistance logic
        pass
    except Exception as e:
        logger.error(f"Error in user_guide_assistance: {e}")
        state["errors"].append(f"User Guide Assistance failed: {str(e)}")
    return state


@observe(name="Misleading Assistance Node")
async def misleading_assistance_node(state: Dict[str, Any]) -> Dict[str, Any]:
    state["current_step"] = "misleading_assistance"
    try:
        # TODO: Implement misleading query handling
        pass
    except Exception as e:
        logger.error(f"Error in misleading_assistance: {e}")
        state["errors"].append(f"Misleading Assistance failed: {str(e)}")
    return state


@observe(name="Chart Generation Node")
async def chart_generation_node(state: Dict[str, Any]) -> Dict[str, Any]:
    state["current_step"] = "chart_generation"
    try:
        # TODO: Implement chart generation logic
        pass
    except Exception as e:
        logger.error(f"Error in chart_generation: {e}")
        state["errors"].append(f"Chart Generation failed: {str(e)}")
    return state


@observe(name="Chart Adjustment Node")
async def chart_adjustment_node(state: Dict[str, Any]) -> Dict[str, Any]:
    state["current_step"] = "chart_adjustment"
    try:
        # TODO: Implement chart adjustment logic
        pass
    except Exception as e:
        logger.error(f"Error in chart_adjustment: {e}")
        state["errors"].append(f"Chart Adjustment failed: {str(e)}")
    return state

class AssistanceVisualizationGraph(BaseGraph):
    """Assistance & Visualization graph with intent-based routing."""

    def __init__(self):
        super().__init__("assistance_visualization")

    def get_state_schema(self) -> type:
        return AssistanceVisualizationState

    def _add_nodes(self) -> None:
        self.graph.add_node("data_assistance", data_assistance_node)
        self.graph.add_node("user_guide_assistance", user_guide_assistance_node)
        self.graph.add_node("misleading_assistance", misleading_assistance_node)
        self.graph.add_node("chart_generation", chart_generation_node)
        self.graph.add_node("chart_adjustment", chart_adjustment_node)
        self.graph.add_node("format_response", self._format_response_node)

    def _add_edges(self) -> None:
        self.graph.set_entry_point("route_by_intent")
        self.graph.add_node("route_by_intent", self._route_by_intent_node)
        
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
        
        self.graph.add_edge("data_assistance", "format_response")
        self.graph.add_edge("user_guide_assistance", "format_response")
        self.graph.add_edge("misleading_assistance", "format_response")
        
        self.graph.add_conditional_edges(
            "chart_generation",
            self._check_chart_adjustment,
            {
                "adjust": "chart_adjustment",
                "no_adjust": "format_response",
            }
        )
        
        self.graph.add_edge("chart_adjustment", "format_response")
        self.graph.add_edge("format_response", END)

    def _route_by_intent(self, state: Dict[str, Any]) -> str:
        intent = state.get("intent", "GENERAL")
        needs_visualization = state.get("metadata", {}).get("needs_visualization", False)

        if intent == "TEXT_TO_SQL" and needs_visualization:
            return "chart_generation"
        elif intent == "GENERAL":
            return "data_assistance"
        elif intent == "USER_GUIDE":
            return "user_guide_assistance"
        elif intent == "MISLEADING_QUERY":
            return "misleading_assistance"
        else:
            logger.warning(f"Unknown intent: {intent}, defaulting to data assistance")
            return "data_assistance"

    def _check_chart_adjustment(self, state: Dict[str, Any]) -> str:
        return "adjust" if state.get("adjustment_instructions") else "no_adjust"

    async def _route_by_intent_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        state["current_step"] = "route_by_intent"
        intent = state.get("intent", "GENERAL")

        if intent == "GENERAL":
            state["assistance_type"] = "data"
        elif intent == "USER_GUIDE":
            state["assistance_type"] = "user_guide"
        elif intent == "MISLEADING_QUERY":
            state["assistance_type"] = "misleading"

        return state

    async def _format_response_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        state["current_step"] = "format_response"
        try:
            response = {}

            if state.get("assistance_response"):
                response["assistance"] = {
                    "type": state.get("assistance_type"),
                    "response": state["assistance_response"],
                    "reasoning": state.get("assistance_reasoning"),
                }

            if state.get("chart_schema"):
                response["chart"] = {
                    "type": state.get("chart_type"),
                    "schema": state.get("adjusted_chart") or state["chart_schema"],
                    "reasoning": state.get("chart_reasoning"),
                }

            state["response"] = response
            state["response_type"] = f"assistance_{state.get('assistance_type', 'unknown')}"
            state["status"] = "completed"
        except Exception as e:
            logger.error(f"Error formatting response: {e}")
            state["errors"].append(f"Response formatting failed: {str(e)}")
            state["status"] = "failed"

        return state


def create_graph() -> AssistanceVisualizationGraph:
    graph = AssistanceVisualizationGraph()
    graph.build()
    return graph

