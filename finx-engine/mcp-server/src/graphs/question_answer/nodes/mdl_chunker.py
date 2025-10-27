"""
Chunk MDL Node for Question Answer (DB Schema Indexing) Graph.
"""

import logging
from typing import Any, Dict

from src.langgraph.nodes.base import node_error_handler, add_error
from src.graphs.question_answer.state import QuestionAnswerState

logger = logging.getLogger(__name__)


@node_error_handler
async def chunk_mdl_node(state: QuestionAnswerState) -> Dict[str, Any]:
    """
    Chunk validated MDL into DDL commands and documents.
    
    This node:
    1. Takes validated MDL
    2. Chunks into DDL commands
    3. Converts to Document objects
    4. Stores chunks in state
    
    Args:
        state: Current pipeline state with validated_mdl
        
    Returns:
        Updated state with chunks
    """
    if state.get("status") == "failed":
        logger.warning("Skipping chunking due to previous failure")
        return {"status": "failed"}
    
    logger.info(f"Chunking MDL for project: {state.get('project_id', 'unknown')}")
    
    try:
        from src.pipelines.indexing.db_schema import DDLChunker
        
        chunker = DDLChunker()
        result = await chunker.run(
            mdl=state["validated_mdl"],
            column_batch_size=state.get("column_batch_size", 50),
            project_id=state.get("project_id"),
        )
        
        chunks = result.get("documents", [])
        logger.info(f"Created {len(chunks)} chunks from MDL")
        
        return {
            "chunks": chunks,
            "status": "embedding",
            "current_step": "chunk_mdl",
        }
    except Exception as e:
        logger.error(f"Chunking failed: {str(e)}")
        return add_error(state, f"Chunking failed: {str(e)}")


__all__ = [
    "chunk_mdl_node",
]

