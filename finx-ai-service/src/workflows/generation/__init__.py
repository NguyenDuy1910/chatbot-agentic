"""
Workflow Generation Module.

This module contains all workflow graphs for the AI service.

Each workflow is now consolidated into a single file for better maintainability:
- intent_recommendation.py: Intent classification and recommendations
- sql_processing.py: SQL generation, validation, and correction
- assistance_visualization.py: User assistance and chart visualization
"""

# Import from new single-file structure
from .intent_recommendation import (
    IntentRecommendationGraph,
    IntentRecommendationState,
    create_initial_state as create_initial_intent_recommendation_state,
    create_graph as create_intent_recommendation_graph,
)
from .sql_processing import (
    SQLProcessingGraph,
    SQLProcessingState,
    create_initial_state as create_initial_sql_processing_state,
    create_graph as create_sql_processing_graph,
)
from .assistance_visualization import (
    AssistanceVisualizationGraph,
    AssistanceVisualizationState,
    create_initial_state as create_initial_assistance_visualization_state,
    create_graph as create_assistance_visualization_graph,
)

__all__ = [
    # Intent & Recommendation
    "IntentRecommendationGraph",
    "IntentRecommendationState",
    "create_initial_intent_recommendation_state",
    "create_intent_recommendation_graph",
    # SQL Processing
    "SQLProcessingGraph",
    "SQLProcessingState",
    "create_initial_sql_processing_state",
    "create_sql_processing_graph",
    # Assistance & Visualization
    "AssistanceVisualizationGraph",
    "AssistanceVisualizationState",
    "create_initial_assistance_visualization_state",
    "create_assistance_visualization_graph",
]

