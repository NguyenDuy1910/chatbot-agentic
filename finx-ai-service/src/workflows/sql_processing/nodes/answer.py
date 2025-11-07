"""
SQL Answer Node.

Generate natural language answer from SQL results
Adapted from src/generation/sql_answer.py
"""

import logging
from typing import Any, Dict

from langfuse.decorators import observe

logger = logging.getLogger("wren-ai-service")


@observe(name="SQL Answer Node")
async def sql_answer_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate natural language answer from SQL results
    
    Args:
        state: Current graph state
        
    Returns:
        Updated state with formatted_answer
    """
    logger.info("Running sql_answer node...")
    state["current_step"] = "sql_answer"
    
    try:
        logger.warning("SQL Answer node not yet implemented - using placeholder")
        
    except Exception as e:
        logger.error(f"Error in sql_answer node: {e}")
        state["errors"].append(f"SQL Answer failed: {str(e)}")
    
    return state
