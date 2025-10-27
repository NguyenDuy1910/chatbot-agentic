"""
Write Documents Node for Question Answer (DB Schema Indexing) Graph.
"""

import logging
from typing import Any, Dict

from src.langgraph.nodes.base import node_error_handler, add_error
from src.graphs.question_answer.state import QuestionAnswerState

logger = logging.getLogger(__name__)


@node_error_handler
async def write_documents_node(state: QuestionAnswerState) -> Dict[str, Any]:
    """
    Write documents to document store.
    
    This node:
    1. Takes cleaned documents
    2. Writes to configured document store
    3. Stores write result in state
    
    Args:
        state: Current pipeline state with cleaned_documents
        
    Returns:
        Updated state with indexed_documents
    """
    if state.get("status") == "failed":
        logger.warning("Skipping writing due to previous failure")
        return {"status": "failed"}
    
    logger.info(f"Writing {len(state.get('chunks', []))} documents to store")
    
    try:
        from haystack.components.writers import DocumentWriter
        from haystack.document_stores.types import DuplicatePolicy
        
        document_store_provider = state.get("document_store_provider")
        if not document_store_provider:
            raise ValueError("Document store provider not available in state")
        
        doc_store = document_store_provider.get_store()
        writer = DocumentWriter(
            document_store=doc_store,
            policy=DuplicatePolicy.OVERWRITE,
        )
        
        result = await writer.run(documents=state.get("chunks", []))
        
        logger.info(f"Successfully wrote documents to store")
        
        return {
            "indexed_documents": state.get("chunks", []),
            "write_result": result,
            "status": "completed",
            "current_step": "write_documents",
        }
    except Exception as e:
        logger.error(f"Writing failed: {str(e)}")
        return add_error(state, f"Writing failed: {str(e)}")


__all__ = [
    "write_documents_node",
]

