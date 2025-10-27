"""
SQL Tables Extraction Node.

Extract table names from SQL query
Adapted from src/generation/sql_tables_extraction.py
"""

import logging
from typing import Any, Dict

from langfuse.decorators import observe

logger = logging.getLogger("wren-ai-service")


@observe(name="SQL Tables Extraction Node")
async def sql_tables_extraction_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract table names from SQL query
    
    Args:
        state: Current graph state
        
    Returns:
        Updated state with extracted_tables
    """
    logger.info("Running sql_tables_extraction node...")
    state["current_step"] = "sql_tables_extraction"
    
    try:
        logger.warning("SQL Tables Extraction node not yet implemented - using placeholder")
        
    except Exception as e:
        logger.error(f"Error in sql_tables_extraction node: {e}")
        state["errors"].append(f"SQL Tables Extraction failed: {str(e)}")
    
    return state
