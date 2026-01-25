import logging
import re
from typing import Any, Dict, List, Optional, Tuple

import orjson
import sqlparse
from langgraph.graph import END
from langfuse.decorators import observe

from src.core.base_graph import BaseGraph
from src.core.base_state import BaseState
from src.workflows.common import clean_up_new_lines
from src.workflows.tools.sql_execution import clean_generation_result, squish_sql
from src.workflows.config import (
    get_workflow_config,
    WORKFLOW_LOGGER_NAME,
)
from src.workflows.prompts import render_prompt

logger = logging.getLogger(WORKFLOW_LOGGER_NAME)


class SQLProcessingState(BaseState):
    
    # Input
    query: str
    project_id: Optional[str]
    is_followup: bool
    previous_sql: Optional[str]
    histories: List[Dict[str, Any]]
    configuration: Optional[Dict[str, Any]]
    
    # Database Context
    db_schemas: List[str]
    retrieved_tables: List[str]
    has_calculated_field: bool
    has_metric: bool
    has_json_field: bool
    
    # SQL Samples & Instructions
    sql_samples: List[Dict[str, str]]
    instructions: List[Dict[str, Any]]
    sql_functions: List[Any]
    
    # Core SQL Generation
    sql_reasoning: Optional[str]
    generated_sql: Optional[str]
    sql_generation_prompt: Optional[str]
    
    # Follow-up SQL Generation
    followup_sql_reasoning: Optional[str]
    followup_generated_sql: Optional[str]
    
    # SQL Quality & Correction
    is_valid_sql: bool
    validation_errors: List[str]
    diagnosed_issues: Optional[Dict[str, Any]]
    correction_attempts: int
    max_correction_attempts: int
    corrected_sql: Optional[str]
    regenerated_sql: Optional[str]
    
    # SQL Tables Extraction
    extracted_tables: List[str]
    
    # SQL Execution
    should_execute: bool
    execution_results: Optional[Any]
    execution_error: Optional[str]
    dry_run_results: Optional[Dict[str, Any]]
    
    # SQL Answer Processing
    sql_question_analysis: Optional[Dict[str, Any]]
    formatted_answer: Optional[str]
    answer_reasoning: Optional[str]
    
    # Final Response
    response: Optional[Dict[str, Any]]
    response_type: Optional[str]


def create_initial_state(
    query: str,
    project_id: Optional[str] = None,
    is_followup: bool = False,
    previous_sql: Optional[str] = None,
    histories: Optional[List[Dict[str, Any]]] = None,
    configuration: Optional[Dict[str, Any]] = None,
    db_schemas: Optional[List[str]] = None,
    should_execute: bool = False,
) -> SQLProcessingState:
    """Create initial state for workflow."""
    config = get_workflow_config()
    
    return SQLProcessingState(
        query=query,
        project_id=project_id,
        is_followup=is_followup,
        previous_sql=previous_sql,
        histories=histories or [],
        configuration=configuration or {},
        db_schemas=db_schemas or [],
        retrieved_tables=[],
        has_calculated_field=False,
        has_metric=False,
        has_json_field=False,
        sql_samples=[],
        instructions=[],
        sql_functions=[],
        sql_reasoning=None,
        generated_sql=None,
        sql_generation_prompt=None,
        followup_sql_reasoning=None,
        followup_generated_sql=None,
        is_valid_sql=False,
        validation_errors=[],
        diagnosed_issues=None,
        correction_attempts=0,
        max_correction_attempts=config.sql_processing.max_correction_attempts,
        corrected_sql=None,
        regenerated_sql=None,
        extracted_tables=[],
        should_execute=should_execute,
        execution_results=None,
        execution_error=None,
        dry_run_results=None,
        sql_question_analysis=None,
        formatted_answer=None,
        answer_reasoning=None,
        response=None,
        response_type=None,
        errors=[],
        warnings=[],
        status="pending",
        current_step="",
        metadata={},
        context={},
    )


@observe(name="SQL Reasoning Node")
async def sql_reasoning_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Generate reasoning about how to construct SQL query."""
    logger.info("Running SQL reasoning node")
    state["current_step"] = "sql_reasoning"
    
    try:
        query = state.get("query", "")
        db_schemas = state.get("db_schemas", [])
        sql_samples = state.get("sql_samples", [])
        instructions = state.get("instructions", [])
        context = state.get("context", {})
        generator = context.get("generator")
        
        if not generator:
            logger.warning("No LLM generator found in context")
            state["sql_reasoning"] = "No reasoning - LLM generator not available"
            return state
        
        # Build reasoning prompt
        system_prompt = render_prompt("sql_processing/reasoning_system.jinja2")
        user_prompt = render_prompt(
            "sql_processing/reasoning_user.jinja2",
            context={
                "query": query,
                "db_schemas": db_schemas,
                "sql_samples": sql_samples,
                "instructions": instructions,
            }
        )
        
        user_prompt = clean_up_new_lines(user_prompt)
        
        # Generate reasoning
        reasoning_response = await generator(
            prompt=user_prompt,
            system_prompt=system_prompt,
        )
        
        # Extract reasoning text
        if isinstance(reasoning_response, dict):
            reasoning = reasoning_response.get("replies", [""])[0]
        else:
            reasoning = str(reasoning_response)
        
        state["sql_reasoning"] = reasoning.strip()
        logger.info(f"SQL reasoning generated: {len(reasoning)} characters")
        
    except Exception as e:
        logger.error(f"Error in sql_reasoning: {e}", exc_info=True)
        state["errors"].append(f"SQL Reasoning failed: {str(e)}")
        state["sql_reasoning"] = f"Error generating reasoning: {str(e)}"
    
    return state


@observe(name="SQL Generation Node")
async def sql_generation_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Generate SQL query based on reasoning and context."""
    logger.info("Running SQL generation node")
    state["current_step"] = "sql_generation"
    
    try:
        query = state.get("query", "")
        db_schemas = state.get("db_schemas", [])
        sql_reasoning = state.get("sql_reasoning", "")
        sql_samples = state.get("sql_samples", [])
        instructions = state.get("instructions", [])
        sql_functions = state.get("sql_functions", [])
        context = state.get("context", {})
        generator = context.get("generator")
        
        if not generator:
            logger.error("No LLM generator found in context")
            state["errors"].append("SQL Generation failed: No LLM generator")
            return state
        
        # Build generation prompt
        system_prompt = render_prompt("sql_processing/generation_system.jinja2")
        user_prompt = render_prompt(
            "sql_processing/generation_user.jinja2",
            context={
                "query": query,
                "reasoning": sql_reasoning,
                "db_schemas": db_schemas,
                "sql_samples": sql_samples,
                "instructions": instructions,
                "sql_functions": sql_functions,
            }
        )
        
        user_prompt = clean_up_new_lines(user_prompt)
        state["sql_generation_prompt"] = user_prompt
        
        # Generate SQL
        sql_response = await generator(
            prompt=user_prompt,
            system_prompt=system_prompt,
        )
        
        # Extract and clean SQL
        if isinstance(sql_response, dict):
            raw_sql = sql_response.get("replies", [""])[0]
        else:
            raw_sql = str(sql_response)
        
        # Clean the generated SQL
        cleaned_sql = clean_generation_result(raw_sql).strip()
        state["generated_sql"] = cleaned_sql
        
        logger.info(f"SQL generated successfully: {len(cleaned_sql)} characters")
        
    except Exception as e:
        logger.error(f"Error in sql_generation: {e}", exc_info=True)
        state["errors"].append(f"SQL Generation failed: {str(e)}")
        state["generated_sql"] = None
    
    return state


@observe(name="Follow-up SQL Reasoning Node")
async def followup_sql_reasoning_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Generate reasoning for follow-up SQL query modification."""
    logger.info("Running follow-up SQL reasoning node")
    state["current_step"] = "followup_sql_reasoning"
    
    try:
        query = state.get("query", "")
        previous_sql = state.get("previous_sql", "")
        histories = state.get("histories", [])
        db_schemas = state.get("db_schemas", [])
        context = state.get("context", {})
        generator = context.get("generator")
        
        if not generator:
            logger.warning("No LLM generator found in context")
            state["followup_sql_reasoning"] = "No reasoning - LLM generator not available"
            return state
        
        if not previous_sql:
            logger.warning("No previous SQL found for follow-up")
            state["followup_sql_reasoning"] = "No previous SQL to modify"
            return state
        
        # Build follow-up reasoning prompt
        system_prompt = render_prompt("sql_processing/followup_reasoning_system.jinja2")
        user_prompt = render_prompt(
            "sql_processing/followup_reasoning_user.jinja2",
            context={
                "query": query,
                "previous_sql": previous_sql,
                "histories": histories,
                "db_schemas": db_schemas,
            }
        )
        
        user_prompt = clean_up_new_lines(user_prompt)
        
        # Generate reasoning
        reasoning_response = await generator(
            prompt=user_prompt,
            system_prompt=system_prompt,
        )
        
        # Extract reasoning text
        if isinstance(reasoning_response, dict):
            reasoning = reasoning_response.get("replies", [""])[0]
        else:
            reasoning = str(reasoning_response)
        
        state["followup_sql_reasoning"] = reasoning.strip()
        logger.info(f"Follow-up SQL reasoning generated: {len(reasoning)} characters")
        
    except Exception as e:
        logger.error(f"Error in followup_sql_reasoning: {e}", exc_info=True)
        state["errors"].append(f"Follow-up SQL Reasoning failed: {str(e)}")
        state["followup_sql_reasoning"] = f"Error generating reasoning: {str(e)}"
    
    return state


@observe(name="Follow-up SQL Generation Node")
async def followup_sql_generation_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Generate modified SQL query for follow-up request."""
    logger.info("Running follow-up SQL generation node")
    state["current_step"] = "followup_sql_generation"
    
    try:
        query = state.get("query", "")
        previous_sql = state.get("previous_sql", "")
        followup_reasoning = state.get("followup_sql_reasoning", "")
        histories = state.get("histories", [])
        db_schemas = state.get("db_schemas", [])
        context = state.get("context", {})
        generator = context.get("generator")
        
        if not generator:
            logger.error("No LLM generator found in context")
            state["errors"].append("Follow-up SQL Generation failed: No LLM generator")
            return state
        
        if not previous_sql:
            logger.error("No previous SQL found for follow-up")
            state["errors"].append("Follow-up SQL Generation failed: No previous SQL")
            return state
        
        # Build follow-up generation prompt
        system_prompt = render_prompt("sql_processing/followup_generation_system.jinja2")
        user_prompt = render_prompt(
            "sql_processing/followup_generation_user.jinja2",
            context={
                "query": query,
                "previous_sql": previous_sql,
                "reasoning": followup_reasoning,
                "histories": histories,
                "db_schemas": db_schemas,
            }
        )
        
        user_prompt = clean_up_new_lines(user_prompt)
        
        # Generate SQL
        sql_response = await generator(
            prompt=user_prompt,
            system_prompt=system_prompt,
        )
        
        # Extract and clean SQL
        if isinstance(sql_response, dict):
            raw_sql = sql_response.get("replies", [""])[0]
        else:
            raw_sql = str(sql_response)
        
        # Clean the generated SQL
        cleaned_sql = clean_generation_result(raw_sql).strip()
        state["followup_generated_sql"] = cleaned_sql
        
        logger.info(f"Follow-up SQL generated successfully: {len(cleaned_sql)} characters")
        
    except Exception as e:
        logger.error(f"Error in followup_sql_generation: {e}", exc_info=True)
        state["errors"].append(f"Follow-up SQL Generation failed: {str(e)}")
        state["followup_generated_sql"] = None
    
    return state


@observe(name="SQL Diagnosis Node")
async def sql_diagnosis_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Diagnose issues with invalid SQL."""
    logger.info("Running SQL diagnosis node")
    state["current_step"] = "sql_diagnosis"
    
    try:
        sql = (
            state.get("generated_sql") or
            state.get("followup_generated_sql") or
            state.get("corrected_sql")
        )
        validation_errors = state.get("validation_errors", [])
        db_schemas = state.get("db_schemas", [])
        query = state.get("query", "")
        context = state.get("context", {})
        generator = context.get("generator")
        
        if not generator:
            logger.warning("No LLM generator found in context")
            state["diagnosed_issues"] = {
                "issues": validation_errors,
                "suggestions": ["No LLM available for detailed diagnosis"]
            }
            return state
        
        # Build diagnosis prompt
        system_prompt = render_prompt("sql_processing/diagnosis_system.jinja2")
        user_prompt = render_prompt(
            "sql_processing/diagnosis_user.jinja2",
            context={
                "sql": sql or "",
                "errors": validation_errors,
                "query": query,
                "db_schemas": db_schemas,
            }
        )
        
        user_prompt = clean_up_new_lines(user_prompt)
        
        # Get diagnosis from LLM
        diagnosis_response = await generator(
            prompt=user_prompt,
            system_prompt=system_prompt,
            response_format={"type": "json_object"}
        )
        
        # Parse diagnosis
        if isinstance(diagnosis_response, dict):
            diagnosis_text = diagnosis_response.get("replies", [""])[0]
        else:
            diagnosis_text = str(diagnosis_response)
        
        try:
            diagnosed_issues = orjson.loads(diagnosis_text)
        except Exception as parse_error:
            logger.warning(f"Failed to parse diagnosis JSON: {parse_error}")
            diagnosed_issues = {
                "issues": validation_errors,
                "suggestions": [diagnosis_text]
            }
        
        state["diagnosed_issues"] = diagnosed_issues
        logger.info(f"SQL diagnosis completed: {len(diagnosed_issues.get('issues', []))} issues found")
        
    except Exception as e:
        logger.error(f"Error in sql_diagnosis: {e}", exc_info=True)
        state["errors"].append(f"SQL Diagnosis failed: {str(e)}")
        state["diagnosed_issues"] = {"issues": state.get("validation_errors", []), "suggestions": []}
    
    return state


@observe(name="SQL Correction Node")
async def sql_correction_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Correct SQL based on diagnosed issues."""
    logger.info("Running SQL correction node")
    state["current_step"] = "sql_correction"
    
    try:
        sql = (
            state.get("generated_sql") or
            state.get("followup_generated_sql") or
            state.get("corrected_sql")
        )
        diagnosed_issues = state.get("diagnosed_issues", {})
        db_schemas = state.get("db_schemas", [])
        query = state.get("query", "")
        context = state.get("context", {})
        generator = context.get("generator")
        
        state["correction_attempts"] += 1
        attempt_num = state["correction_attempts"]
        
        if not generator:
            logger.error("No LLM generator found in context")
            state["errors"].append("SQL Correction failed: No LLM generator")
            state["corrected_sql"] = sql  # Keep original
            return state
        
        # Build correction prompt
        system_prompt = render_prompt("sql_processing/correction_system.jinja2")
        user_prompt = render_prompt(
            "sql_processing/correction_user.jinja2",
            context={
                "sql": sql or "",
                "issues": diagnosed_issues.get("issues", []),
                "suggestions": diagnosed_issues.get("suggestions", []),
                "query": query,
                "db_schemas": db_schemas,
                "attempt": attempt_num,
            }
        )
        
        user_prompt = clean_up_new_lines(user_prompt)
        
        # Get corrected SQL from LLM
        correction_response = await generator(
            prompt=user_prompt,
            system_prompt=system_prompt,
        )
        
        # Extract and clean corrected SQL
        if isinstance(correction_response, dict):
            raw_sql = correction_response.get("replies", [""])[0]
        else:
            raw_sql = str(correction_response)
        
        # Clean the corrected SQL
        corrected_sql = clean_generation_result(raw_sql).strip()
        state["corrected_sql"] = corrected_sql
        
        logger.info(f"SQL correction attempt #{attempt_num} completed: {len(corrected_sql)} characters")
        
    except Exception as e:
        logger.error(f"Error in sql_correction: {e}", exc_info=True)
        state["errors"].append(f"SQL Correction failed: {str(e)}")
        state["correction_attempts"] += 1
        # Keep the original SQL if correction fails
        state["corrected_sql"] = sql
    
    return state


@observe(name="SQL Regeneration Node")
async def sql_regeneration_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Regenerate SQL from scratch after max correction attempts exceeded."""
    logger.info("Running SQL regeneration node (max correction attempts exceeded)")
    state["current_step"] = "sql_regeneration"
    
    try:
        query = state.get("query", "")
        db_schemas = state.get("db_schemas", [])
        validation_errors = state.get("validation_errors", [])
        diagnosed_issues = state.get("diagnosed_issues", {})
        sql_samples = state.get("sql_samples", [])
        instructions = state.get("instructions", [])
        context = state.get("context", {})
        generator = context.get("generator")
        
        if not generator:
            logger.error("No LLM generator found in context")
            state["errors"].append("SQL Regeneration failed: No LLM generator")
            return state
        
        # Build regeneration prompt with emphasis on avoiding previous errors
        system_prompt = render_prompt("sql_processing/regeneration_system.jinja2")
        user_prompt = render_prompt(
            "sql_processing/regeneration_user.jinja2",
            context={
                "query": query,
                "db_schemas": db_schemas,
                "previous_errors": validation_errors,
                "diagnosed_issues": diagnosed_issues,
                "sql_samples": sql_samples,
                "instructions": instructions,
            }
        )
        
        user_prompt = clean_up_new_lines(user_prompt)
        
        # Regenerate SQL from scratch
        regen_response = await generator(
            prompt=user_prompt,
            system_prompt=system_prompt,
        )
        
        # Extract and clean regenerated SQL
        if isinstance(regen_response, dict):
            raw_sql = regen_response.get("replies", [""])[0]
        else:
            raw_sql = str(regen_response)
        
        # Clean the regenerated SQL
        regenerated_sql = clean_generation_result(raw_sql).strip()
        state["regenerated_sql"] = regenerated_sql
        # Also update generated_sql so validation can pick it up
        state["generated_sql"] = regenerated_sql
        
        logger.info(f"SQL regenerated successfully: {len(regenerated_sql)} characters")
        
    except Exception as e:
        logger.error(f"Error in sql_regeneration: {e}", exc_info=True)
        state["errors"].append(f"SQL Regeneration failed: {str(e)}")
        state["regenerated_sql"] = None
    
    return state


def extract_table_names_from_sql(sql: str) -> List[str]:
    """
    Extract table names from SQL query using sqlparse.
    
    Args:
        sql: SQL query string
        
    Returns:
        List of unique table names found in the query
    """
    if not sql:
        return []
    
    try:
        # Parse the SQL
        parsed = sqlparse.parse(sql)
        if not parsed:
            return []
        
        tables = set()
        
        for statement in parsed:
            # Extract table names from FROM and JOIN clauses
            from_seen = False
            for token in statement.tokens:
                # Check for FROM keyword
                if token.ttype is sqlparse.tokens.Keyword and token.value.upper() == 'FROM':
                    from_seen = True
                    continue
                
                # Check for JOIN keywords
                if token.ttype is sqlparse.tokens.Keyword and 'JOIN' in token.value.upper():
                    from_seen = True
                    continue
                
                # If we've seen FROM or JOIN, look for identifiers
                if from_seen:
                    if isinstance(token, sqlparse.sql.IdentifierList):
                        for identifier in token.get_identifiers():
                            table_name = str(identifier.get_real_name() or identifier.get_name())
                            if table_name and table_name.upper() not in ('SELECT', 'WHERE', 'GROUP', 'ORDER', 'HAVING'):
                                tables.add(table_name.strip('`"[]'))
                    elif isinstance(token, sqlparse.sql.Identifier):
                        table_name = str(token.get_real_name() or token.get_name())
                        if table_name and table_name.upper() not in ('SELECT', 'WHERE', 'GROUP', 'ORDER', 'HAVING'):
                            tables.add(table_name.strip('`"[]'))
                    elif token.ttype is sqlparse.tokens.Name:
                        table_name = token.value.strip()
                        if table_name and table_name.upper() not in ('SELECT', 'WHERE', 'GROUP', 'ORDER', 'HAVING', 'AS'):
                            tables.add(table_name.strip('`"[]'))
                    
                    # Reset flag after keywords like WHERE, GROUP BY, etc.
                    if token.ttype is sqlparse.tokens.Keyword and token.value.upper() in ('WHERE', 'GROUP', 'ORDER', 'HAVING', 'LIMIT'):
                        from_seen = False
        
        return sorted(list(tables))
    
    except Exception as e:
        logger.warning(f"Error extracting table names from SQL: {e}")
        return []


@observe(name="SQL Tables Extraction Node")
async def sql_tables_extraction_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Extract table names from the generated SQL query."""
    logger.info("Running SQL tables extraction node")
    state["current_step"] = "sql_tables_extraction"
    
    try:
        sql = (
            state.get("generated_sql") or
            state.get("followup_generated_sql") or
            state.get("corrected_sql") or
            state.get("regenerated_sql")
        )
        
        if not sql:
            logger.warning("No SQL found to extract tables from")
            state["extracted_tables"] = []
            return state
        
        # Extract table names from SQL
        extracted_tables = extract_table_names_from_sql(sql)
        state["extracted_tables"] = extracted_tables
        
        logger.info(f"Extracted {len(extracted_tables)} table(s): {', '.join(extracted_tables)}")
        
    except Exception as e:
        logger.error(f"Error in sql_tables_extraction: {e}", exc_info=True)
        state["errors"].append(f"SQL Tables Extraction failed: {str(e)}")
        state["extracted_tables"] = []
    
    return state


@observe(name="SQL Question Node")
async def sql_question_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze the SQL question to understand what answer is expected."""
    logger.info("Running SQL question analysis node")
    state["current_step"] = "sql_question"
    
    try:
        query = state.get("query", "")
        sql = (
            state.get("generated_sql") or
            state.get("followup_generated_sql") or
            state.get("corrected_sql") or
            state.get("regenerated_sql")
        )
        execution_results = state.get("execution_results")
        db_schemas = state.get("db_schemas", [])
        context = state.get("context", {})
        generator = context.get("generator")
        
        if not generator:
            logger.warning("No LLM generator found in context")
            state["sql_question_analysis"] = {
                "question_type": "unknown",
                "expected_format": "table",
                "requires_aggregation": False,
            }
            return state
        
        # Build question analysis prompt
        system_prompt = render_prompt("sql_processing/question_analysis_system.jinja2")
        user_prompt = render_prompt(
            "sql_processing/question_analysis_user.jinja2",
            context={
                "query": query,
                "sql": sql or "",
                "db_schemas": db_schemas,
            }
        )
        
        user_prompt = clean_up_new_lines(user_prompt)
        
        # Get question analysis from LLM
        analysis_response = await generator(
            prompt=user_prompt,
            system_prompt=system_prompt,
            response_format={"type": "json_object"}
        )
        
        # Parse analysis
        if isinstance(analysis_response, dict):
            analysis_text = analysis_response.get("replies", [""])[0]
        else:
            analysis_text = str(analysis_response)
        
        try:
            analysis = orjson.loads(analysis_text)
        except Exception as parse_error:
            logger.warning(f"Failed to parse question analysis JSON: {parse_error}")
            analysis = {
                "question_type": "general",
                "expected_format": "table",
                "requires_aggregation": "COUNT" in (sql or "").upper() or "SUM" in (sql or "").upper(),
            }
        
        state["sql_question_analysis"] = analysis
        logger.info(f"Question analysis completed: type={analysis.get('question_type', 'unknown')}")
        
    except Exception as e:
        logger.error(f"Error in sql_question: {e}", exc_info=True)
        state["errors"].append(f"SQL Question failed: {str(e)}")
        state["sql_question_analysis"] = {
            "question_type": "unknown",
            "expected_format": "table",
        }
    
    return state


@observe(name="SQL Answer Node")
async def sql_answer_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a natural language answer based on SQL execution results."""
    logger.info("Running SQL answer generation node")
    state["current_step"] = "sql_answer"
    
    try:
        query = state.get("query", "")
        sql = (
            state.get("generated_sql") or
            state.get("followup_generated_sql") or
            state.get("corrected_sql") or
            state.get("regenerated_sql")
        )
        execution_results = state.get("execution_results")
        question_analysis = state.get("sql_question_analysis", {})
        context = state.get("context", {})
        generator = context.get("generator")
        
        # If no execution results, provide SQL-only answer
        if not execution_results:
            logger.info("No execution results available, providing SQL-only answer")
            state["formatted_answer"] = f"Generated SQL query:\n\n```sql\n{sql}\n```"
            state["answer_reasoning"] = "SQL generated but not executed"
            return state
        
        if not generator:
            logger.warning("No LLM generator found in context")
            state["formatted_answer"] = f"SQL executed successfully. Results: {execution_results}"
            state["answer_reasoning"] = "No LLM available for natural language answer"
            return state
        
        # Build answer generation prompt
        system_prompt = render_prompt("sql_processing/answer_system.jinja2")
        user_prompt = render_prompt(
            "sql_processing/answer_user.jinja2",
            context={
                "query": query,
                "sql": sql or "",
                "execution_results": execution_results,
                "question_analysis": question_analysis,
            }
        )
        
        user_prompt = clean_up_new_lines(user_prompt)
        
        # Generate natural language answer
        answer_response = await generator(
            prompt=user_prompt,
            system_prompt=system_prompt,
        )
        
        # Extract answer
        if isinstance(answer_response, dict):
            answer = answer_response.get("replies", [""])[0]
        else:
            answer = str(answer_response)
        
        state["formatted_answer"] = answer.strip()
        state["answer_reasoning"] = f"Answer generated based on {question_analysis.get('question_type', 'general')} question type"
        
        logger.info(f"Natural language answer generated: {len(answer)} characters")
        
    except Exception as e:
        logger.error(f"Error in sql_answer: {e}", exc_info=True)
        state["errors"].append(f"SQL Answer failed: {str(e)}")
        # Provide fallback answer
        if execution_results:
            state["formatted_answer"] = f"Query executed successfully with results: {execution_results}"
        else:
            state["formatted_answer"] = "Query generated but answer formatting failed"
        state["answer_reasoning"] = f"Error: {str(e)}"
    
    return state

class SQLProcessingGraph(BaseGraph):
    """SQL Processing graph with validation and correction retry logic."""

    def __init__(self):
        super().__init__("sql_processing")

    def get_state_schema(self) -> type:
        return SQLProcessingState

    def _add_nodes(self) -> None:
        self.graph.add_node("sql_reasoning_node", sql_reasoning_node)
        self.graph.add_node("sql_generation_node", sql_generation_node)
        self.graph.add_node("followup_sql_reasoning_node", followup_sql_reasoning_node)
        self.graph.add_node("followup_sql_generation_node", followup_sql_generation_node)
        self.graph.add_node("sql_validation_node", self._sql_validation_node)
        self.graph.add_node("sql_diagnosis_node", sql_diagnosis_node)
        self.graph.add_node("sql_correction_node", sql_correction_node)
        self.graph.add_node("sql_regeneration_node", sql_regeneration_node)
        self.graph.add_node("sql_tables_extraction_node", sql_tables_extraction_node)
        self.graph.add_node("sql_question_node", sql_question_node)
        self.graph.add_node("sql_answer_node", sql_answer_node)
        self.graph.add_node("format_response_node", self._format_response_node)

    def _add_edges(self) -> None:
        self.graph.set_entry_point("check_followup_node")
        self.graph.add_node("check_followup_node", self._check_followup_node)
        
        self.graph.add_conditional_edges(
            "check_followup_node",
            self._route_by_followup,
            {
                "followup": "followup_sql_reasoning_node",
                "new_query": "sql_reasoning_node",
            }
        )

        # Follow-up path
        self.graph.add_edge("followup_sql_reasoning_node", "followup_sql_generation_node")
        self.graph.add_edge("followup_sql_generation_node", "sql_validation_node")

        # New query path
        self.graph.add_edge("sql_reasoning_node", "sql_generation_node")
        self.graph.add_edge("sql_generation_node", "sql_validation_node")

        # Validation routing (with retry loop)
        self.graph.add_conditional_edges(
            "sql_validation_node",
            self._route_after_validation,
            {
                "valid": "sql_tables_extraction_node",
                "invalid": "sql_diagnosis_node",
                "max_retries": "sql_regeneration_node",
            }
        )
        
        self.graph.add_edge("sql_diagnosis_node", "sql_correction_node")
        self.graph.add_edge("sql_correction_node", "sql_validation_node")
        self.graph.add_edge("sql_regeneration_node", "sql_validation_node")
        self.graph.add_edge("sql_tables_extraction_node", "sql_question_node")
        self.graph.add_edge("sql_question_node", "sql_answer_node")
        self.graph.add_edge("sql_answer_node", "format_response_node")
        self.graph.add_edge("format_response_node", END)

    def _route_by_followup(self, state: Dict[str, Any]) -> str:
        return "followup" if state.get("is_followup", False) else "new_query"

    def _route_after_validation(self, state: Dict[str, Any]) -> str:
        is_valid = state.get("is_valid_sql", False)
        correction_attempts = state.get("correction_attempts", 0)
        max_attempts = state.get("max_correction_attempts", 3)

        if is_valid:
            return "valid"
        elif correction_attempts >= max_attempts:
            return "max_retries"
        else:
            return "invalid"

    async def _check_followup_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        state["current_step"] = "check_followup_node"
        return state

    def _validate_sql_syntax(self, sql: str) -> Tuple[bool, List[str]]:

        if not sql or not sql.strip():
            return False, ["Empty SQL query"]
        
        errors = []
        
        try:
            # Try to parse the SQL
            parsed = sqlparse.parse(sql)
            
            if not parsed:
                return False, ["Failed to parse SQL query"]
            
            # Check for basic SQL structure
            sql_upper = sql.upper()
            
            # Check if it looks like a SELECT statement (most common case)
            if 'SELECT' in sql_upper:
                if 'FROM' not in sql_upper:
                    errors.append("SELECT statement missing FROM clause")
            
            # Check for unmatched parentheses
            if sql.count('(') != sql.count(')'):
                errors.append("Unmatched parentheses in SQL query")
            
            # Check for unmatched quotes
            single_quotes = sql.count("'") - sql.count("\\'")
            if single_quotes % 2 != 0:
                errors.append("Unmatched single quotes in SQL query")
            
            # Check for multiple statements (security concern)
            if len(parsed) > 1:
                errors.append("Multiple SQL statements detected - only one statement allowed")
            
            # Check for dangerous keywords (basic SQL injection prevention)
            dangerous_patterns = [
                r';\s*DROP\s+TABLE',
                r';\s*DELETE\s+FROM',
                r';\s*TRUNCATE',
                r';\s*ALTER\s+TABLE',
            ]
            for pattern in dangerous_patterns:
                if re.search(pattern, sql_upper):
                    errors.append(f"Potentially dangerous SQL pattern detected")
                    break
            
            # If we have any errors, it's invalid
            if errors:
                return False, errors
            
            # All checks passed
            return True, []
            
        except Exception as e:
            return False, [f"SQL parsing error: {str(e)}"]
    
    async def _sql_validation_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Validate SQL syntax and structure."""
        logger.info("Running SQL validation node")
        state["current_step"] = "sql_validation_node"
        
        try:
            sql = (
                state.get("generated_sql") or
                state.get("followup_generated_sql") or
                state.get("corrected_sql") or
                state.get("regenerated_sql")
            )
            
            if not sql:
                logger.warning("No SQL found to validate")
                state["is_valid_sql"] = False
                state["validation_errors"] = ["No SQL generated"]
                return state
            
            # Validate SQL syntax
            is_valid, errors = self._validate_sql_syntax(sql)
            
            state["is_valid_sql"] = is_valid
            state["validation_errors"] = errors
            
            if is_valid:
                logger.info("SQL validation passed")
            else:
                logger.warning(f"SQL validation failed: {', '.join(errors)}")
            
        except Exception as e:
            logger.error(f"Error in SQL validation: {e}", exc_info=True)
            state["is_valid_sql"] = False
            state["validation_errors"] = [f"Validation error: {str(e)}"]
        
        return state

    async def _format_response_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        state["current_step"] = "format_response_node"
        try:
            response = {
                "sql": state.get("generated_sql") or state.get("followup_generated_sql") or state.get("corrected_sql"),
                "reasoning": state.get("sql_reasoning") or state.get("followup_sql_reasoning"),
                "answer": state.get("formatted_answer"),
                "extracted_tables": state.get("extracted_tables", []),
                "is_valid": state.get("is_valid_sql", False),
                "correction_attempts": state.get("correction_attempts", 0),
            }
            
            if state.get("execution_results"):
                response["execution_results"] = state["execution_results"]
            
            state["response"] = response
            state["response_type"] = "sql_generated"
            state["status"] = "completed"
        except Exception as e:
            logger.error(f"Error formatting response: {e}")
            state["errors"].append(f"Response formatting failed: {str(e)}")
            state["status"] = "failed"
        return state


def create_graph() -> SQLProcessingGraph:
    graph = SQLProcessingGraph()
    graph.build()
    return graph

