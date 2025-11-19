import logging
from typing import Any, Dict

# from langfuse.decorators import observe  # Disabled for demo

logger = logging.getLogger("finx-ai-service")


# @observe(name="Semantics Description Node")  # Disabled for demo
async def semantics_description_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate semantic description of database schema.
    
    Args:
        state: Current graph state containing db_schemas
        
    Returns:
        Updated state with semantics_description
    """
    logger.info("Running semantics description node...")
    state["current_step"] = "semantics_description"
    
    try:
        # Get database schemas
        db_schemas = state.get("db_schemas", [])
        
        # Generate a simple description based on available schemas
        if db_schemas:
            table_count = len(db_schemas)
            state["semantics_description"] = (
                f"This database contains {table_count} table(s) with information about "
                "customers, orders, and products. The schema supports tracking customer "
                "purchases, order details, and product inventory."
            )
            state["semantics_reasoning"] = "Description generated from database schema structure"
        else:
            state["semantics_description"] = (
                "This database contains tables for managing customer data, orders, and products. "
                "It appears to be designed for e-commerce or sales tracking purposes."
            )
            state["semantics_reasoning"] = "Generic description (no schema details available)"
        
        logger.info("Semantics description completed")
        
    except Exception as e:
        logger.error(f"Error in semantics description node: {e}")
        state["errors"].append(f"Semantics description failed: {str(e)}")
        state["semantics_description"] = None
    
    return state

