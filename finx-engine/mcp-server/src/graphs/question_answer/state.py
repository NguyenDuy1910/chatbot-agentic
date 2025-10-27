"""
State definition for Question Answer (DB Schema Indexing) Graph.

Extends BaseState with DB schema indexing-specific fields.
"""

from typing import TypedDict, List, Optional, Any, Dict

from src.core.base_state import BaseState


class QuestionAnswerState(BaseState):
    """
    State for DB Schema Indexing Pipeline.

    Flow: Validate MDL → Chunk DDL → Embed Documents → Clean → Write to Store
    
    Extends BaseState with DB schema indexing-specific fields
    for tracking inputs, processing stages, and outputs.
    """
    # ===== INPUTS =====
    mdl_str: str
    project_id: Optional[str]
    column_batch_size: int

    # ===== PROCESSING STAGES =====
    # Stage 1: Validation
    validated_mdl: Optional[Dict[str, Any]]

    # Stage 2: Chunking
    chunks: Optional[List[Dict[str, Any]]]

    # Stage 3: Embedding
    embeddings: Optional[Dict[str, Any]]

    # Stage 4: Cleaning
    cleaned_documents: Optional[List[Dict[str, Any]]]

    # ===== OUTPUT =====
    indexed_documents: Optional[List[Dict[str, Any]]]
    write_result: Optional[Dict[str, Any]]

    # ===== PROVIDERS (injected at runtime) =====
    embedder_provider: Optional[Any]
    document_store_provider: Optional[Any]


__all__ = [
    "QuestionAnswerState",
]

