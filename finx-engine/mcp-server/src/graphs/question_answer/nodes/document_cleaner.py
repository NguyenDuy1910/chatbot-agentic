"""
Clean Documents Node for Question Answer (DB Schema Indexing) Graph.
"""

import logging
from typing import Any, Dict

from src.langgraph.nodes.base import node_error_handler, add_error
from src.graphs.question_answer.state import QuestionAnswerState

logger = logging.getLogger(__name__)


@node_error_handler
async def clean_documents_node(state: QuestionAnswerState) -> Dict[str, Any]:
    """
    Clean documents before writing to store.
    
    This node:
    1. Takes embedded documents
    2. Cleans old documents from store
    3. Prepares documents for writing
    
    Args:
        state: Current pipeline state with embeddings
        
    Returns:
        Updated state with cleaned_documents
    """
    if state.get("status") == "failed":
        logger.warning("Skipping cleaning due to previous failure")
        return {"status": "failed"}
    
    logger.info(f"Cleaning documents for project: {state.get('project_id', 'unknown')}")
    
    try:
        from src.pipelines.indexing import DocumentCleaner
        
        document_store_provider = state.get("document_store_provider")
        if not document_store_provider:
            raise ValueError("Document store provider not available in state")
        
        doc_store = document_store_provider.get_store()
        cleaner = DocumentCleaner([doc_store])
        
        # Clean old documents
        await cleaner.run(project_id=state.get("project_id"))
        
        logger.info("Document cleaning completed")
        
        return {
            "cleaned_documents": state.get("chunks", []),
            "status": "writing",
            "current_step": "clean_documents",
        }
    except Exception as e:
        logger.error(f"Cleaning failed: {str(e)}")
        return add_error(state, f"Cleaning failed: {str(e)}")


__all__ = [
    "clean_documents_node",
]

