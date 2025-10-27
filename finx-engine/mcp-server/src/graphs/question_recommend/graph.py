"""
Question Recommendation Graph implementation.

Inherits from BaseGraph and implements the question recommendation pipeline.
"""

import logging
from typing import Type, TypedDict

from langgraph.graph import END

from src.core.base_graph import BaseGraph
from src.langgraph.nodes.base import create_conditional_router
from src.graphs.question_recommend.state import QuestionRecommendState
from src.graphs.question_recommend.nodes import (
    build_prompt_node,
    generate_questions_node,
    normalize_response_node,
)

logger = logging.getLogger(__name__)


class QuestionRecommendGraph(BaseGraph):
    """
    Question Recommendation Graph implementation.
    
    Inherits from BaseGraph and implements the question recommendation pipeline:
    Build Prompt → Generate Questions → Normalize Response
    
    This graph generates recommended questions based on database schema context
    and user-specified categories.
    """
    
    def __init__(self):
        """Initialize the Question Recommendation graph."""
        super().__init__(name="question_recommend")
    
    def get_state_schema(self) -> Type[TypedDict]:
        """
        Get the state schema for this graph.
        
        Returns:
            QuestionRecommendState TypedDict class
        """
        return QuestionRecommendState
    
    def _add_nodes(self) -> None:
        """Add all nodes to the graph."""
        logger.info("Adding nodes to Question Recommendation graph")
        
        self.graph.add_node("build_prompt", build_prompt_node)
        self.graph.add_node("generate_questions", generate_questions_node)
        self.graph.add_node("normalize_response", normalize_response_node)
    
    def _add_edges(self) -> None:
        """Add all edges to the graph."""
        logger.info("Adding edges to Question Recommendation graph")
        
        # Main pipeline flow
        self.graph.add_edge("build_prompt", "generate_questions")
        
        # Conditional edges with error handling
        self.graph.add_conditional_edges(
            "generate_questions",
            create_conditional_router("normalize_response", "error_handler"),
            {
                "normalize_response": "normalize_response",
                "error_handler": "error_handler",
            }
        )
        
        self.graph.add_conditional_edges(
            "normalize_response",
            create_conditional_router(END, "error_handler"),
            {
                END: END,
                "error_handler": "error_handler",
            }
        )
        
        # Error handler always ends
        self.graph.add_edge("error_handler", END)
        
        # Set entry point
        self.graph.set_entry_point("build_prompt")
    
    def get_description(self) -> str:
        """
        Get a human-readable description of the graph.
        
        Returns:
            Description string
        """
        return """
Question Recommendation Pipeline
=================================

Purpose: Generate recommended questions based on database schema context

Flow:
1. build_prompt
   - Input: Contexts, categories, language, parameters
   - Output: Formatted prompt for LLM
   - Error: Prompt building failed

2. generate_questions
   - Input: Built prompt
   - Output: Raw LLM response
   - Error: LLM generation failed

3. normalize_response
   - Input: Raw LLM response
   - Output: Parsed and validated questions
   - Error: Response normalization failed

Error Handler:
- Catches errors from any node
- Logs error details
- Returns failed status

Success Criteria:
- Questions successfully generated and parsed
- No errors in pipeline
- Status = "completed"
"""


def create_question_recommend_graph() -> QuestionRecommendGraph:
    """
    Factory function to create and build a Question Recommendation graph.
    
    Returns:
        Built QuestionRecommendGraph instance
    """
    graph = QuestionRecommendGraph()
    graph.build()
    return graph


__all__ = [
    "QuestionRecommendGraph",
    "create_question_recommend_graph",
]

