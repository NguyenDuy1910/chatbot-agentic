"""
Orchestrator State Schema.

Defines the state structure for the Master Orchestrator graph.
Combines state from all sub-graphs for complete workflow management.
"""

from typing import Any, Dict, List, Optional, TypedDict


class OrchestratorState(TypedDict, total=False):
    """
    State schema for the Master Orchestrator graph.
    
    Session Management:
        session_id: Unique session identifier
        session_start: Session start timestamp
        conversation_history: List of previous queries and responses
        user_preferences: User configuration and preferences
        
    Query Processing:
        query: Original user query
        rephrased_question: Rephrased/clarified version of query
        
    Intent Classification:
        intent: Classified intent (TEXT_TO_SQL, GENERAL, USER_GUIDE, MISLEADING_QUERY)
        intent_reasoning: Explanation for intent classification
        confidence_score: Confidence score for intent (0.0-1.0)
        
    Database Context:
        project_id: Project identifier
        db_schemas: Database schemas in DDL format
        retrieved_tables: List of relevant table names
        instructions: User-provided instructions
        
    SQL Processing:
        generated_sql: Generated SQL query
        sql_reasoning: Reasoning for SQL generation
        sql_answer: Formatted answer from SQL results
        extracted_tables: Tables extracted from SQL
        sql_valid: Whether SQL is valid
        correction_attempts: Number of SQL correction attempts
        previous_sql: Previous SQL for follow-up detection
        is_followup: Whether query is a follow-up
        
    Assistance & Visualization:
        assistance_response: Generated assistance text
        assistance_reasoning: Reasoning for assistance
        chart_schema: Chart configuration schema
        chart_type: Type of chart (bar, line, pie, etc.)
        chart_reasoning: Reasoning for chart choice
        needs_visualization: Whether visualization is needed
        preferred_chart_type: User's preferred chart type
        chart_adjustment_instructions: Instructions for chart adjustment
        
    Recommendations:
        recommended_questions: List of recommended follow-up questions
        recommended_relationships: List of recommended data relationships
        
    Streaming:
        streaming_enabled: Whether streaming is enabled
        stream_chunks: Text chunks for streaming
        
    Response:
        final_response: Final formatted response for user
        status: Overall status (success, error, processing)
        
    Error Handling:
        errors: List of error messages
        debug_mode: Whether debug mode is enabled
        
    Context & Pipeline:
        context: Shared context (embedder, retrievers, generator, etc.)
        current_step: Current processing step
    """
    
    # Session Management
    session_id: str
    session_start: str
    conversation_history: List[Dict[str, Any]]
    user_preferences: Dict[str, Any]
    
    # Query Processing
    query: str
    rephrased_question: str
    
    # Intent Classification
    intent: str  # "TEXT_TO_SQL" | "GENERAL" | "USER_GUIDE" | "MISLEADING_QUERY"
    intent_reasoning: str
    confidence_score: float
    
    # Database Context
    project_id: str
    db_schemas: List[str]
    retrieved_tables: List[str]
    instructions: List[str]
    
    # SQL Processing
    generated_sql: str
    sql_reasoning: str
    sql_answer: str
    extracted_tables: List[str]
    sql_valid: bool
    correction_attempts: int
    previous_sql: str
    is_followup: bool
    
    # Assistance & Visualization
    assistance_response: str
    assistance_reasoning: str
    chart_schema: Dict[str, Any]
    chart_type: str
    chart_reasoning: str
    needs_visualization: bool
    preferred_chart_type: str
    chart_adjustment_instructions: str
    
    # Recommendations
    recommended_questions: List[str]
    recommended_relationships: List[Dict[str, Any]]
    
    # Streaming
    streaming_enabled: bool
    stream_chunks: List[str]
    
    # Response
    final_response: Dict[str, Any]
    status: str  # "success" | "error" | "processing"
    response_type: str
    
    # Error Handling
    errors: List[str]
    debug_mode: bool
    
    # Context & Pipeline
    context: Dict[str, Any]
    current_step: str
