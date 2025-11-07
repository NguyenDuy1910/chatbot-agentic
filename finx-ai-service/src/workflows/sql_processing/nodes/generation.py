"""
SQL Generation Node.

Generate SQL query from natural language question
Adapted from src/generation/sql_generation.py
"""

import logging
from typing import Any, Dict

from langfuse.decorators import observe

logger = logging.getLogger("wren-ai-service")


@observe(name="SQL Generation Node")
async def sql_generation_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate SQL query from natural language question
    
    Args:
        state: Current graph state
        
    Returns:
        Updated state with generated_sql
    """
    logger.info("Running sql_generation node...")
    state["current_step"] = "sql_generation"
    
    try:
        logger.warning("SQL Generation node not yet implemented - using placeholder")
        
    except Exception as e:
        logger.error(f"Error in sql_generation node: {e}")
        state["errors"].append(f"SQL Generation failed: {str(e)}")
    
    return state
