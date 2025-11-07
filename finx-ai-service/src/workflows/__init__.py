"""
Graph implementations for finx-ai-service.

This module contains all graph implementations for different agents.

LangGraph-based graphs (3 main graphs):
1. SQL Processing Graph - SQL generation, correction, and answer processing
2. Intent & Recommendation Graph - Intent classification and recommendations
3. Assistance & Visualization Graph - User assistance and chart visualization
"""

# LangGraph-based graphs
from .assistance_visualization import (
    AssistanceVisualizationGraph,
    AssistanceVisualizationState,
    create_initial_assistance_visualization_state,
)
from .intent_recommendation import (
    IntentRecommendationGraph,
    IntentRecommendationState,
    create_initial_intent_recommendation_state,
)
from .sql_processing import (
    SQLProcessingGraph,
    SQLProcessingState,
    create_initial_sql_processing_state,
)

__all__ = [
    # LangGraph-based graphs
    "SQLProcessingGraph",
    "SQLProcessingState",
    "create_initial_sql_processing_state",
    "IntentRecommendationGraph",
    "IntentRecommendationState",
    "create_initial_intent_recommendation_state",
    "AssistanceVisualizationGraph",
    "AssistanceVisualizationState",
    "create_initial_assistance_visualization_state",
]

