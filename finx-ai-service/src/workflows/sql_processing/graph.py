import logging
from typing import Any, Dict, Type, TypedDict

from langgraph.graph import END

from src.core.base_graph import BaseGraph
from .state import SQLProcessingState

logger = logging.getLogger(__name__)


class SQLProcessingGraph(BaseGraph):
    """
    LangGraph for SQL Processing.
    
    Workflow:
    1. Check if follow-up question
       - Yes: Follow-up SQL Reasoning -> Follow-up SQL Generation
       - No: SQL Reasoning -> SQL Generation
    2. SQL Validation
       - Valid: SQL Tables Extraction -> SQL Question -> SQL Answer -> End
       - Invalid: SQL Diagnosis -> SQL Correction -> Retry (or Regeneration if max retries)
    
    The graph supports:
    - Follow-up question handling
    - SQL validation and correction with retry loops
    - SQL regeneration when correction fails
    - Answer generation from SQL results
    """
    
    def __init__(self):
        """Initialize the SQL Processing Graph."""
        super().__init__("sql_processing")
    
    def get_state_schema(self) -> Type[TypedDict]:
        """Get the state schema for this graph."""
        return SQLProcessingState
    
    def _add_nodes(self) -> None:
        """Add all processing nodes to the graph."""
        from .nodes import (
            sql_generation_node,
            sql_reasoning_node,
            followup_sql_generation_node,
            followup_sql_reasoning_node,
            sql_correction_node,
            sql_diagnosis_node,
            sql_regeneration_node,
            sql_tables_extraction_node,
            sql_answer_node,
            sql_question_node,
        )
        
        # Core SQL generation nodes
        self.graph.add_node("sql_reasoning", sql_reasoning_node)
        self.graph.add_node("sql_generation", sql_generation_node)
        self.graph.add_node("followup_sql_reasoning", followup_sql_reasoning_node)
        self.graph.add_node("followup_sql_generation", followup_sql_generation_node)
        
        # SQL quality & correction nodes
        self.graph.add_node("sql_validation", self._sql_validation_node)
        self.graph.add_node("sql_diagnosis", sql_diagnosis_node)
        self.graph.add_node("sql_correction", sql_correction_node)
        self.graph.add_node("sql_regeneration", sql_regeneration_node)
        
        # SQL answer processing nodes
        self.graph.add_node("sql_tables_extraction", sql_tables_extraction_node)
        self.graph.add_node("sql_question", sql_question_node)
        self.graph.add_node("sql_answer", sql_answer_node)
        
        # Helper nodes
        self.graph.add_node("format_response", self._format_response_node)
    
    def _add_edges(self) -> None:
        """Define workflow with conditional routing."""
        
        # ========== Entry Point ==========
        self.graph.set_entry_point("check_followup")
        self.graph.add_node("check_followup", self._check_followup_node)
        
        # ========== Follow-up Routing ==========
        self.graph.add_conditional_edges(
            "check_followup",
            self._route_by_followup,
            {
                "followup": "followup_sql_reasoning",
                "new_query": "sql_reasoning",
            }
        )
        
        # ========== Follow-up Path ==========
        self.graph.add_edge("followup_sql_reasoning", "followup_sql_generation")
        self.graph.add_edge("followup_sql_generation", "sql_validation")
        
        # ========== New Query Path ==========
        self.graph.add_edge("sql_reasoning", "sql_generation")
        self.graph.add_edge("sql_generation", "sql_validation")
        
        # ========== Validation Routing (with Retry Loop) ==========
        self.graph.add_conditional_edges(
            "sql_validation",
            self._route_after_validation,
            {
                "valid": "sql_tables_extraction",
                "invalid": "sql_diagnosis",
                "max_retries": "sql_regeneration",
            }
        )
        
        # ========== Correction Retry Loop ==========
        self.graph.add_edge("sql_diagnosis", "sql_correction")
        self.graph.add_edge("sql_correction", "sql_validation")  # Loop back to validation
        
        # ========== Regeneration Path ==========
        self.graph.add_edge("sql_regeneration", "sql_validation")
        
        # ========== Answer Processing Path ==========
        self.graph.add_edge("sql_tables_extraction", "sql_question")
        self.graph.add_edge("sql_question", "sql_answer")
        self.graph.add_edge("sql_answer", "format_response")
        
        # ========== Final Step ==========
        self.graph.add_edge("format_response", END)
    
    # ==================== Routing Functions ====================
    
    def _route_by_followup(self, state: Dict[str, Any]) -> str:
        """Route based on whether this is a follow-up question."""
        is_followup = state.get("is_followup", False)
        
        if is_followup:
            logger.info("Routing to follow-up SQL generation")
            return "followup"
        else:
            logger.info("Routing to new SQL generation")
            return "new_query"
    
    def _route_after_validation(self, state: Dict[str, Any]) -> str:
        """Route after SQL validation based on validity and retry attempts."""
        is_valid = state.get("is_valid_sql", False)
        correction_attempts = state.get("correction_attempts", 0)
        max_attempts = state.get("max_correction_attempts", 3)
        
        if is_valid:
            logger.info("SQL validation passed")
            return "valid"
        elif correction_attempts >= max_attempts:
            logger.warning(f"Max correction attempts ({max_attempts}) reached, regenerating SQL")
            return "max_retries"
        else:
            logger.info(f"SQL validation failed, attempting correction (attempt {correction_attempts + 1}/{max_attempts})")
            return "invalid"
    
    # ==================== Helper Nodes ====================
    
    async def _check_followup_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Check if this is a follow-up question."""
        state["current_step"] = "check_followup"
        logger.info(f"Checking if follow-up question: {state.get('is_followup', False)}")
        return state
    
    async def _sql_validation_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Validate generated SQL."""
        logger.info("Validating SQL...")
        state["current_step"] = "sql_validation"
        
        try:
            sql = state.get("generated_sql") or state.get("followup_generated_sql") or state.get("corrected_sql")
            
            if sql:
                state["is_valid_sql"] = True
                state["validation_errors"] = []
                logger.info("SQL validation passed (placeholder)")
            else:
                state["is_valid_sql"] = False
                state["validation_errors"] = ["No SQL generated"]
                logger.warning("SQL validation failed: No SQL generated")
                
        except Exception as e:
            logger.error(f"Error in SQL validation: {e}")
            state["is_valid_sql"] = False
            state["validation_errors"] = [str(e)]
        
        return state
    
    async def _format_response_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Format final response."""
        logger.info("Formatting SQL processing response...")
        state["current_step"] = "format_response"
        
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
            
            logger.info("SQL processing response formatted successfully")
            
        except Exception as e:
            logger.error(f"Error formatting response: {e}")
            state["errors"].append(f"Response formatting failed: {str(e)}")
            state["status"] = "failed"
        
        return state


# Factory function for easy graph creation
def create_sql_processing_graph() -> SQLProcessingGraph:
    """
    Create and build a SQL Processing graph.
    
    Returns:
        Built SQLProcessingGraph ready for execution
    """
    graph = SQLProcessingGraph()
    graph.build()
    return graph

