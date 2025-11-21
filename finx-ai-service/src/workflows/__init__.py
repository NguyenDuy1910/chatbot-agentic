"""
Graph implementations for finx-ai-service.

This module contains all graph implementations for different agents.

LangGraph-based graphs (3 main graphs):
1. SQL Processing Graph - SQL generation, correction, and answer processing
2. Intent & Recommendation Graph - Intent classification and recommendations
3. Assistance & Visualization Graph - User assistance and chart visualization
"""

# Import from generation module (new single-file structure)
from .generation import (
    AssistanceVisualizationGraph,
    AssistanceVisualizationState,
    create_initial_assistance_visualization_state,
    create_assistance_visualization_graph,
    IntentRecommendationGraph,
    IntentRecommendationState,
    create_initial_intent_recommendation_state,
    create_intent_recommendation_graph,
    SQLProcessingGraph,
    SQLProcessingState,
    create_initial_sql_processing_state,
    create_sql_processing_graph,
)

__all__ = [
    # LangGraph-based graphs
    "SQLProcessingGraph",
    "SQLProcessingState",
    "create_initial_sql_processing_state",
    "create_sql_processing_graph",
    "IntentRecommendationGraph",
    "IntentRecommendationState",
    "create_initial_intent_recommendation_state",
    "create_intent_recommendation_graph",
    "AssistanceVisualizationGraph",
    "AssistanceVisualizationState",
    "create_initial_assistance_visualization_state",
    "create_assistance_visualization_graph",
]

