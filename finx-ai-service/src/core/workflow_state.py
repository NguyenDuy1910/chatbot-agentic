"""
Common Workflow State Management

This module provides a unified state management system for all workflows.
It extends BaseState with common fields used across different workflow types.
"""

from typing import Any, Dict, List, Optional, TypedDict, Union

from src.core.base_state import BaseState


class LLMExecutionInfo(TypedDict, total=False):
    """Information about LLM execution."""
    prompt: str
    system_prompt: Optional[str]
    response: str
    model: Optional[str]
    tokens_used: Optional[int]
    latency_ms: Optional[float]
    timestamp: Optional[str]


class ToolExecutionInfo(TypedDict, total=False):
    """Information about tool execution."""
    tool_name: str
    tool_input: Dict[str, Any]
    tool_output: Any
    execution_time_ms: Optional[float]
    success: bool
    error: Optional[str]


class RetrievalInfo(TypedDict, total=False):
    """Information about retrieval operations."""
    query: str
    retrieved_documents: List[Dict[str, Any]]
    retrieval_scores: List[float]
    top_k: int
    retrieval_method: Optional[str]


class ValidationInfo(TypedDict, total=False):
    """Information about validation results."""
    is_valid: bool
    validation_errors: List[str]
    validation_warnings: List[str]
    validation_rules: List[str]
    validation_timestamp: Optional[str]


class WorkflowState(BaseState):
    """
    Extended state for workflows with common fields across all workflow types.
    
    This state includes:
    - User input and query processing
    - LLM interaction tracking
    - Tool execution tracking
    - Retrieval and context management
    - Validation and quality control
    - Retry and correction logic
    
    Inherit from this state for specific workflow types.
    """
    
    # ============================================================================
    # INPUT & QUERY
    # ============================================================================
    query: str  # User's input query
    project_id: Optional[str]  # Project identifier
    session_id: Optional[str]  # Session identifier for conversation tracking
    user_id: Optional[str]  # User identifier
    
    # ============================================================================
    # CONVERSATION CONTEXT
    # ============================================================================
    histories: List[Dict[str, Any]]  # Conversation history
    is_followup: bool  # Whether this is a follow-up query
    previous_response: Optional[Dict[str, Any]]  # Previous workflow response
    
    # ============================================================================
    # CONFIGURATION
    # ============================================================================
    configuration: Dict[str, Any]  # Workflow-specific configuration
    language: str  # Response language (default: "English")
    
    # ============================================================================
    # LLM INTERACTION
    # ============================================================================
    llm_executions: List[LLMExecutionInfo]  # Track all LLM calls
    current_prompt: Optional[str]  # Current prompt being processed
    current_system_prompt: Optional[str]  # Current system prompt
    llm_response: Optional[str]  # Latest LLM response
    llm_reasoning: Optional[str]  # LLM reasoning/explanation
    
    # ============================================================================
    # TOOL EXECUTION
    # ============================================================================
    tool_executions: List[ToolExecutionInfo]  # Track all tool calls
    available_tools: List[str]  # Available tools for this workflow
    tool_results: Dict[str, Any]  # Results from tool executions
    
    # ============================================================================
    # RETRIEVAL & CONTEXT
    # ============================================================================
    retrieval_info: Optional[RetrievalInfo]  # Information about retrieval
    retrieved_context: List[Dict[str, Any]]  # Retrieved context/documents
    context_sources: List[str]  # Sources of context (DB, vector store, etc.)
    
    # ============================================================================
    # DATABASE CONTEXT (for SQL workflows)
    # ============================================================================
    db_schemas: List[str]  # Database schemas
    retrieved_tables: List[str]  # Retrieved table names
    sql_samples: List[Dict[str, str]]  # SQL example samples
    sql_functions: List[Any]  # Available SQL functions
    
    # ============================================================================
    # VALIDATION & QUALITY CONTROL
    # ============================================================================
    validation_info: Optional[ValidationInfo]  # Validation results
    quality_score: Optional[float]  # Overall quality score (0-1)
    
    # ============================================================================
    # RETRY & CORRECTION LOGIC
    # ============================================================================
    retry_count: int  # Number of retry attempts
    max_retries: int  # Maximum allowed retries
    correction_history: List[Dict[str, Any]]  # History of corrections
    
    # ============================================================================
    # OUTPUT & RESPONSE
    # ============================================================================
    response: Optional[Dict[str, Any]]  # Final response
    response_type: Optional[str]  # Type of response
    formatted_output: Optional[str]  # Formatted output for display
    
    # ============================================================================
    # PERFORMANCE METRICS
    # ============================================================================
    step_timings: Dict[str, float]  # Time taken for each step (ms)
    total_llm_tokens: int  # Total tokens used by LLM
    total_latency_ms: float  # Total workflow latency


def create_workflow_state(
    query: str,
    project_id: Optional[str] = None,
    session_id: Optional[str] = None,
    user_id: Optional[str] = None,
    histories: Optional[List[Dict[str, Any]]] = None,
    is_followup: bool = False,
    previous_response: Optional[Dict[str, Any]] = None,
    configuration: Optional[Dict[str, Any]] = None,
    language: str = "English",
    db_schemas: Optional[List[str]] = None,
    max_retries: int = 3,
    **kwargs
) -> WorkflowState:
    """
    Factory function to create a WorkflowState with sensible defaults.
    
    Args:
        query: User's input query
        project_id: Optional project identifier
        session_id: Optional session identifier
        user_id: Optional user identifier
        histories: Optional conversation history
        is_followup: Whether this is a follow-up query
        previous_response: Previous workflow response
        configuration: Workflow-specific configuration
        language: Response language
        db_schemas: Database schemas (for SQL workflows)
        max_retries: Maximum retry attempts
        **kwargs: Additional custom fields
        
    Returns:
        WorkflowState: Initialized workflow state
    """
    state = WorkflowState(
        # Input & Query
        query=query,
        project_id=project_id,
        session_id=session_id,
        user_id=user_id,
        
        # Conversation Context
        histories=histories or [],
        is_followup=is_followup,
        previous_response=previous_response,
        
        # Configuration
        configuration=configuration or {},
        language=language,
        
        # LLM Interaction
        llm_executions=[],
        current_prompt=None,
        current_system_prompt=None,
        llm_response=None,
        llm_reasoning=None,
        
        # Tool Execution
        tool_executions=[],
        available_tools=[],
        tool_results={},
        
        # Retrieval & Context
        retrieval_info=None,
        retrieved_context=[],
        context_sources=[],
        
        # Database Context
        db_schemas=db_schemas or [],
        retrieved_tables=[],
        sql_samples=[],
        sql_functions=[],
        
        # Validation
        validation_info=None,
        quality_score=None,
        
        # Retry & Correction
        retry_count=0,
        max_retries=max_retries,
        correction_history=[],
        
        # Output
        response=None,
        response_type=None,
        formatted_output=None,
        
        # Performance Metrics
        step_timings={},
        total_llm_tokens=0,
        total_latency_ms=0.0,
        
        # Base State fields
        errors=[],
        warnings=[],
        status="pending",
        current_step="",
        metadata={},
        context={},
    )
    
    # Add any additional custom fields
    for key, value in kwargs.items():
        if key not in state:
            state[key] = value
    
    return state


class SQLWorkflowState(WorkflowState):
    """
    Specialized state for SQL generation workflows.
    Extends WorkflowState with SQL-specific fields.
    """
    
    # SQL Generation
    sql_reasoning: Optional[str]
    generated_sql: Optional[str]
    sql_generation_prompt: Optional[str]
    
    # Follow-up SQL
    followup_sql_reasoning: Optional[str]
    followup_generated_sql: Optional[str]
    previous_sql: Optional[str]
    
    # SQL Validation & Correction
    is_valid_sql: bool
    validation_errors: List[str]
    diagnosed_issues: Optional[Dict[str, Any]]
    correction_attempts: int
    max_correction_attempts: int
    corrected_sql: Optional[str]
    regenerated_sql: Optional[str]
    
    # SQL Execution
    should_execute: bool
    execution_results: Optional[Any]
    execution_error: Optional[str]
    dry_run_results: Optional[Dict[str, Any]]
    extracted_tables: List[str]
    
    # SQL Answer Processing
    sql_question_analysis: Optional[Dict[str, Any]]
    formatted_answer: Optional[str]
    answer_reasoning: Optional[str]
    
    # Database Features
    has_calculated_field: bool
    has_metric: bool
    has_json_field: bool
    instructions: List[Dict[str, Any]]


class IntentClassificationState(WorkflowState):
    """
    Specialized state for intent classification workflows.
    Extends WorkflowState with intent-specific fields.
    """
    
    # Intent Classification
    intent: Optional[str]  # Classified intent
    intent_reasoning: Optional[str]  # Reasoning for intent
    confidence_score: float  # Confidence score (0-1)
    classification_prompt: Optional[str]  # Prompt used for classification
    
    # Query Rephrasing
    rephrased_question: Optional[str]  # Rephrased version of query
    original_query: Optional[str]  # Original query for reference


class RetrievalWorkflowState(WorkflowState):
    """
    Specialized state for retrieval workflows.
    Extends WorkflowState with retrieval-specific fields.
    """
    
    # Query Processing
    processed_query: Optional[str]  # Processed/cleaned query
    query_embedding: Optional[List[float]]  # Query embedding vector
    
    # Retrieval Configuration
    top_k: int  # Number of documents to retrieve
    similarity_threshold: float  # Minimum similarity score
    retrieval_method: str  # Method used for retrieval
    
    # Retrieved Data
    documents: List[Dict[str, Any]]  # Retrieved documents
    document_ids: List[str]  # Document IDs
    similarity_scores: List[float]  # Similarity scores
    
    # Filters
    filters: Optional[Dict[str, Any]]  # Filters applied to retrieval
    

class AssistanceWorkflowState(WorkflowState):
    """
    Specialized state for user assistance workflows.
    Extends WorkflowState with assistance-specific fields.
    """
    
    # User Guide & Documentation
    relevant_docs: List[Dict[str, Any]]  # Relevant documentation
    doc_snippets: List[str]  # Documentation snippets
    
    # Answer Generation
    answer: Optional[str]  # Generated answer
    answer_sources: List[str]  # Sources used in answer
    answer_confidence: float  # Confidence in answer
    
    # Visualization
    visualization_data: Optional[Dict[str, Any]]  # Data for visualization
    chart_config: Optional[Dict[str, Any]]  # Chart configuration


# Helper function to convert between state types
def extend_state(
    base_state: WorkflowState,
    target_state_class: type,
    **additional_fields
) -> Union[SQLWorkflowState, IntentClassificationState, RetrievalWorkflowState, AssistanceWorkflowState]:
    """
    Convert a WorkflowState to a specialized state type.
    
    Args:
        base_state: Base workflow state
        target_state_class: Target state class to convert to
        **additional_fields: Additional fields for the target state
        
    Returns:
        Specialized state instance
    """
    # Create new state with base fields
    new_state = target_state_class(**base_state)
    
    # Add additional fields
    for key, value in additional_fields.items():
        new_state[key] = value
    
    return new_state
