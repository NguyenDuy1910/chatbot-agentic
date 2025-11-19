"""
State definition for Assistance & Visualization Graph.

This module defines the state schema for user assistance and chart visualization workflow.
"""

from typing import Any, Dict, List, Literal, Optional, TypedDict

from src.core.base_state import BaseState


class AssistanceVisualizationState(BaseState):
    """
    State for Assistance & Visualization workflow.
    
    This state tracks user assistance (data, user guide, misleading) and
    chart generation/adjustment workflows.
    """
    
    # ============= Input =============
    query: str  # User's question
    project_id: Optional[str]
    intent: Optional[str]  # Intent from Intent & Recommendation Graph
    histories: List[Dict[str, Any]]  # Conversation history
    configuration: Optional[Dict[str, Any]]  # User configuration (language, etc.)
    
    # ============= Database Context =============
    db_schemas: List[str]  # Database schemas in DDL format
    
    # ============= SQL Context (from SQL Processing Graph) =============
    sql: Optional[str]  # SQL query for visualization
    sql_results: Optional[Any]  # SQL execution results for visualization
    
    # ============= User Assistance =============
    assistance_type: Optional[Literal["data", "user_guide", "misleading"]]
    assistance_response: Optional[str]  # Assistance response text
    assistance_reasoning: Optional[str]  # Reasoning for assistance
    is_streaming: bool  # Whether response is streaming
    
    # ============= Chart Generation =============
    chart_type: Optional[str]  # Chart type: line, bar, pie, etc.
    chart_schema: Optional[Dict[str, Any]]  # Vega-Lite chart schema
    chart_reasoning: Optional[str]  # Reasoning for chart generation
    sample_data: Optional[Dict[str, Any]]  # Sample data for chart
    sample_column_values: Optional[Dict[str, Any]]  # Sample column values
    vega_schema: Optional[Dict[str, Any]]  # Vega-Lite schema template
    remove_data_from_chart_schema: bool  # Whether to remove data from schema
    
    # ============= Chart Adjustment =============
    adjustment_instructions: Optional[str]  # Instructions for chart adjustment
    adjusted_chart: Optional[Dict[str, Any]]  # Adjusted chart schema
    adjustment_reasoning: Optional[str]  # Reasoning for adjustment
    
    # ============= Final Response =============
    response: Optional[Dict[str, Any]]  # Final formatted response
    response_type: Optional[str]  # Response type


def create_initial_assistance_visualization_state(
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
    """
    Create initial state for Assistance & Visualization workflow.
    
    Args:
        query: User's question
        project_id: Optional project identifier
        intent: Intent from Intent & Recommendation Graph
        histories: Conversation history
        configuration: User configuration
        db_schemas: Database schemas
        sql: SQL query for visualization
        sql_results: SQL execution results
        is_streaming: Whether response is streaming
        remove_data_from_chart_schema: Whether to remove data from chart schema
        
    Returns:
        Initial AssistanceVisualizationState
    """
    return AssistanceVisualizationState(
        # Input
        query=query,
        project_id=project_id,
        intent=intent,
        histories=histories or [],
        configuration=configuration or {},
        
        # Database context
        db_schemas=db_schemas or [],
        
        # SQL context
        sql=sql,
        sql_results=sql_results,
        
        # User assistance
        assistance_type=None,
        assistance_response=None,
        assistance_reasoning=None,
        is_streaming=is_streaming,
        
        # Chart generation
        chart_type=None,
        chart_schema=None,
        chart_reasoning=None,
        sample_data=None,
        sample_column_values=None,
        vega_schema=None,
        remove_data_from_chart_schema=remove_data_from_chart_schema,
        
        # Chart adjustment
        adjustment_instructions=None,
        adjusted_chart=None,
        adjustment_reasoning=None,
        
        # Response
        response=None,
        response_type=None,
        
        # Base state fields
        errors=[],
        warnings=[],
        status="pending",
        current_step="",
        metadata={},
        context={},
    )

