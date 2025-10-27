"""
LangGraph-based graph implementations for finx-ai-service.

This module provides graph implementations organized by agent/pipeline type,
each with their own state definitions and nodes.

Architecture:
- Each graph inherits from BaseGraph
- Each graph has its own state definition extending BaseState
- Each graph organizes its nodes in a dedicated nodes/ subdirectory
- Shared utilities and base classes are in src/core/

Usage:
    from src.graphs.question_recommend import QuestionRecommendGraph
    from src.graphs.question_answer import QuestionAnswerGraph
    
    # Create and build graphs
    qr_graph = QuestionRecommendGraph()
    qr_graph.build()
    
    qa_graph = QuestionAnswerGraph()
    qa_graph.build()
    
    # Execute graphs
    result = await qr_graph.execute(initial_state)
    result = await qa_graph.execute(initial_state)
"""

from .question_recommend import QuestionRecommendGraph, QuestionRecommendState
from .question_answer import QuestionAnswerGraph, QuestionAnswerState

__all__ = [
    # Question Recommend Graph
    "QuestionRecommendGraph",
    "QuestionRecommendState",
    # Question Answer Graph
    "QuestionAnswerGraph",
    "QuestionAnswerState",
]

