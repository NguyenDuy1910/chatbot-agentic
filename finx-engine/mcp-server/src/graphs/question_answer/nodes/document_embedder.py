"""
Embed Documents Node for Question Answer (DB Schema Indexing) Graph.
"""

import logging
from typing import Any, Dict

from src.langgraph.nodes.base import node_error_handler, add_error
from src.graphs.question_answer.state import QuestionAnswerState

logger = logging.getLogger(__name__)


@node_error_handler
async def embed_documents_node(state: QuestionAnswerState) -> Dict[str, Any]:
    """
    Embed documents using embedder provider.
    
    This node:
    1. Takes chunked documents
    2. Embeds using configured embedder
    3. Stores embeddings in state
    
    Args:
        state: Current pipeline state with chunks
        
    Returns:
        Updated state with embeddings
    """
    if state.get("status") == "failed":
        logger.warning("Skipping embedding due to previous failure")
        return {"status": "failed"}
    
    logger.info(f"Embedding {len(state.get('chunks', []))} documents")
    
    try:
        embedder_provider = state.get("embedder_provider")
        if not embedder_provider:
            raise ValueError("Embedder provider not available in state")
        
        embedder = embedder_provider.get_document_embedder()
        result = await embedder.run(documents=state["chunks"])
        
        logger.info("Document embedding completed")
        
        return {
            "embeddings": result,
            "status": "cleaning",
            "current_step": "embed_documents",
        }
    except Exception as e:
        logger.error(f"Embedding failed: {str(e)}")
        return add_error(state, f"Embedding failed: {str(e)}")


__all__ = [
    "embed_documents_node",
]

