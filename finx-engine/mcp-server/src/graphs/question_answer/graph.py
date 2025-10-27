"""
Question Answer (DB Schema Indexing) Graph implementation.

Inherits from BaseGraph and implements the DB schema indexing pipeline.
"""

import logging
from typing import Type, TypedDict

from langgraph.graph import END

from src.core.base_graph import BaseGraph
from src.langgraph.nodes.base import create_conditional_router
from src.graphs.question_answer.state import QuestionAnswerState
from src.graphs.question_answer.nodes import (
    validate_mdl_node,
    chunk_mdl_node,
    embed_documents_node,
    clean_documents_node,
    write_documents_node,
)

logger = logging.getLogger(__name__)


class QuestionAnswerGraph(BaseGraph):
    """
    Question Answer (DB Schema Indexing) Graph implementation.
    
    Inherits from BaseGraph and implements the DB schema indexing pipeline:
    Validate MDL → Chunk DDL → Embed Documents → Clean → Write to Store
    
    This graph indexes database schemas into a vector store for retrieval
    and question answering.
    """
    
    def __init__(self):
        """Initialize the Question Answer graph."""
        super().__init__(name="question_answer")
    
    def get_state_schema(self) -> Type[TypedDict]:
        """
        Get the state schema for this graph.
        
        Returns:
            QuestionAnswerState TypedDict class
        """
        return QuestionAnswerState
    
    def _add_nodes(self) -> None:
        """Add all nodes to the graph."""
        logger.info("Adding nodes to Question Answer graph")
        
        self.graph.add_node("validate_mdl", validate_mdl_node)
        self.graph.add_node("chunk_mdl", chunk_mdl_node)
        self.graph.add_node("embed_documents", embed_documents_node)
        self.graph.add_node("clean_documents", clean_documents_node)
        self.graph.add_node("write_documents", write_documents_node)
    
    def _add_edges(self) -> None:
        """Add all edges to the graph."""
        logger.info("Adding edges to Question Answer graph")
        
        # Main pipeline flow
        self.graph.add_edge("validate_mdl", "chunk_mdl")
        
        # Conditional edges with error handling
        self.graph.add_conditional_edges(
            "chunk_mdl",
            create_conditional_router("embed_documents", "error_handler"),
            {
                "embed_documents": "embed_documents",
                "error_handler": "error_handler",
            }
        )
        
        self.graph.add_conditional_edges(
            "embed_documents",
            create_conditional_router("clean_documents", "error_handler"),
            {
                "clean_documents": "clean_documents",
                "error_handler": "error_handler",
            }
        )
        
        self.graph.add_conditional_edges(
            "clean_documents",
            create_conditional_router("write_documents", "error_handler"),
            {
                "write_documents": "write_documents",
                "error_handler": "error_handler",
            }
        )
        
        self.graph.add_conditional_edges(
            "write_documents",
            create_conditional_router(END, "error_handler"),
            {
                END: END,
                "error_handler": "error_handler",
            }
        )
        
        # Error handler always ends
        self.graph.add_edge("error_handler", END)
        
        # Set entry point
        self.graph.set_entry_point("validate_mdl")
    
    def get_description(self) -> str:
        """
        Get a human-readable description of the graph.
        
        Returns:
            Description string
        """
        return """
DB Schema Indexing Pipeline
===========================

Purpose: Index database schemas into vector store for retrieval

Flow:
1. validate_mdl
   - Input: MDL string
   - Output: Validated MDL dictionary
   - Error: Invalid MDL format

2. chunk_mdl
   - Input: Validated MDL
   - Output: List of DDL chunks
   - Error: Chunking failed

3. embed_documents
   - Input: DDL chunks
   - Output: Embedded documents
   - Error: Embedding failed

4. clean_documents
   - Input: Embedded documents
   - Output: Cleaned documents
   - Error: Cleaning failed

5. write_documents
   - Input: Cleaned documents
   - Output: Indexed documents in store
   - Error: Writing failed

Error Handler:
- Catches errors from any node
- Logs error details
- Returns failed status

Success Criteria:
- All documents successfully indexed
- No errors in pipeline
- Status = "completed"
"""


def create_question_answer_graph() -> QuestionAnswerGraph:
    """
    Factory function to create and build a Question Answer graph.
    
    Returns:
        Built QuestionAnswerGraph instance
    """
    graph = QuestionAnswerGraph()
    graph.build()
    return graph


__all__ = [
    "QuestionAnswerGraph",
    "create_question_answer_graph",
]

