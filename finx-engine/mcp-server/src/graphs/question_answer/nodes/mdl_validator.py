"""
Validate MDL Node for Question Answer (DB Schema Indexing) Graph.
"""

import logging
from typing import Any, Dict

from src.langgraph.nodes.base import node_error_handler, add_error
from src.graphs.question_answer.state import QuestionAnswerState

logger = logging.getLogger(__name__)


@node_error_handler
async def validate_mdl_node(state: QuestionAnswerState) -> Dict[str, Any]:
    """
    Validate MDL string and convert to structured format.
    
    This node:
    1. Takes raw MDL string input
    2. Validates MDL structure
    3. Converts to internal representation
    4. Stores validated MDL in state
    
    Args:
        state: Current pipeline state with mdl_str
        
    Returns:
        Updated state with validated_mdl
    """
    logger.info(f"Validating MDL for project: {state.get('project_id', 'unknown')}")
    
    try:
        # Import here to avoid circular imports
        from src.pipelines.indexing import MDLValidator
        
        validator = MDLValidator()
        result = validator.run(mdl=state["mdl_str"])
        
        logger.info("MDL validation successful")
        
        return {
            "validated_mdl": result["mdl"],
            "status": "chunking",
            "current_step": "validate_mdl",
        }
    except Exception as e:
        logger.error(f"MDL validation failed: {str(e)}")
        return add_error(state, f"MDL validation failed: {str(e)}")


__all__ = [
    "validate_mdl_node",
]

