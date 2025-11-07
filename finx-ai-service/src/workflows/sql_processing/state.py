"""
State definition for SQL Processing Graph.

This module defines the state schema for the SQL generation, correction, and answer processing workflow.
"""

from typing import Any, Dict, List, Optional, TypedDict

from src.core.base_state import BaseState


class SQLProcessingState(BaseState):
    """
    State for SQL Processing workflow.
    
    This state tracks the entire pipeline from SQL generation through correction
    to answer processing, including reasoning, validation, and error correction.
    """
    
    # ============= Input =============
    query: str  # User's question
    project_id: Optional[str]
    is_followup: bool  # Whether this is a follow-up question
    previous_sql: Optional[str]  # Previous SQL for follow-up questions
    histories: List[Dict[str, Any]]  # Conversation history
    configuration: Optional[Dict[str, Any]]  # User configuration
    
    # ============= Database Context =============
    db_schemas: List[str]  # Database schemas in DDL format
    retrieved_tables: List[str]  # Retrieved table names
    has_calculated_field: bool  # Schema contains calculated fields
    has_metric: bool  # Schema contains metrics
    has_json_field: bool  # Schema contains JSON fields
    
    # ============= SQL Samples & Instructions =============
    sql_samples: List[Dict[str, str]]  # Few-shot examples
    instructions: List[Dict[str, Any]]  # User instructions
    sql_functions: List[Any]  # Available SQL functions
    
    # ============= Core SQL Generation =============
    sql_reasoning: Optional[str]  # Reasoning before SQL generation
    generated_sql: Optional[str]  # Generated SQL query
    sql_generation_prompt: Optional[str]  # Prompt used (for debugging)
    
    # ============= Follow-up SQL Generation =============
    followup_sql_reasoning: Optional[str]  # Reasoning for follow-up
    followup_generated_sql: Optional[str]  # Follow-up SQL query
    
    # ============= SQL Quality & Correction =============
    is_valid_sql: bool  # SQL validation status
    validation_errors: List[str]  # Validation error messages
    diagnosed_issues: Optional[Dict[str, Any]]  # Diagnosed SQL issues
    correction_attempts: int  # Number of correction attempts
    max_correction_attempts: int  # Maximum allowed attempts
    corrected_sql: Optional[str]  # Corrected SQL query
    regenerated_sql: Optional[str]  # Regenerated SQL (if correction fails)
    
    # ============= SQL Tables Extraction =============
    extracted_tables: List[str]  # Tables extracted from SQL
    
    # ============= SQL Execution =============
    should_execute: bool  # Whether to execute SQL
    execution_results: Optional[Any]  # Query execution results
    execution_error: Optional[str]  # Execution error message
    dry_run_results: Optional[Dict[str, Any]]  # Dry run results
    
    # ============= SQL Answer Processing =============
    sql_question_analysis: Optional[Dict[str, Any]]  # Question analysis
    formatted_answer: Optional[str]  # Natural language answer
    answer_reasoning: Optional[str]  # Reasoning for answer
    
    # ============= Final Response =============
    response: Optional[Dict[str, Any]]  # Final formatted response
    response_type: Optional[str]  # Response type


def create_initial_sql_processing_state(
    query: str,
    project_id: Optional[str] = None,
    is_followup: bool = False,
    previous_sql: Optional[str] = None,
    histories: Optional[List[Dict[str, Any]]] = None,
    configuration: Optional[Dict[str, Any]] = None,
    db_schemas: Optional[List[str]] = None,
    should_execute: bool = False,
    max_correction_attempts: int = 3,
) -> SQLProcessingState:
    """
    Create initial state for SQL Processing workflow.
    
    Args:
        query: User's question
        project_id: Optional project identifier
        is_followup: Whether this is a follow-up question
        previous_sql: Previous SQL for follow-up questions
        histories: Conversation history
        configuration: User configuration
        db_schemas: Database schemas
        should_execute: Whether to execute SQL
        max_correction_attempts: Maximum correction attempts
        
    Returns:
        Initial SQLProcessingState
    """
    return SQLProcessingState(
        # Input
        query=query,
        project_id=project_id,
        is_followup=is_followup,
        previous_sql=previous_sql,
        histories=histories or [],
        configuration=configuration or {},
        
        # Database context
        db_schemas=db_schemas or [],
        retrieved_tables=[],
        has_calculated_field=False,
        has_metric=False,
        has_json_field=False,
        
        # SQL samples & instructions
        sql_samples=[],
        instructions=[],
        sql_functions=[],
        
        # Core SQL generation
        sql_reasoning=None,
        generated_sql=None,
        sql_generation_prompt=None,
        
        # Follow-up SQL generation
        followup_sql_reasoning=None,
        followup_generated_sql=None,
        
        # SQL quality & correction
        is_valid_sql=False,
        validation_errors=[],
        diagnosed_issues=None,
        correction_attempts=0,
        max_correction_attempts=max_correction_attempts,
        corrected_sql=None,
        regenerated_sql=None,
        
        # SQL tables extraction
        extracted_tables=[],
        
        # SQL execution
        should_execute=should_execute,
        execution_results=None,
        execution_error=None,
        dry_run_results=None,
        
        # SQL answer processing
        sql_question_analysis=None,
        formatted_answer=None,
        answer_reasoning=None,
        
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

