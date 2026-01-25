"""
Workflow Configuration Package

This package provides centralized configuration and constants for all workflows.

Usage:
    from src.workflows.config import get_workflow_config, INTENT_TEXT_TO_SQL
    
    config = get_workflow_config()
    max_attempts = config.sql_processing.max_correction_attempts
"""

from .workflow_config import (
    SQLProcessingConfig,
    IntentRecommendationConfig,
    AssistanceVisualizationConfig,
    OrchestratorConfig,
    WorkflowConfig,
    get_workflow_config,
    set_workflow_config,
    reset_workflow_config,
)

from .workflow_constants import (
    # Intent types
    IntentType,
    INTENT_TEXT_TO_SQL,
    INTENT_GENERAL,
    INTENT_USER_GUIDE,
    INTENT_MISLEADING_QUERY,
    ALL_INTENT_TYPES,
    # Categories
    QUESTION_CATEGORIES,
    # Keywords
    FOLLOWUP_KEYWORDS,
    VISUALIZATION_KEYWORDS,
    # Confidence
    DEFAULT_AI_CONFIDENCE,
    DEFAULT_FALLBACK_CONFIDENCE,
    # Response types
    RESPONSE_TYPE_SQL_GENERATED,
    RESPONSE_TYPE_INTENT_TEXT_TO_SQL,
    RESPONSE_TYPE_INTENT_GENERAL,
    RESPONSE_TYPE_INTENT_USER_GUIDE,
    RESPONSE_TYPE_INTENT_MISLEADING,
    # Status
    STATUS_PENDING,
    STATUS_IN_PROGRESS,
    STATUS_COMPLETED,
    STATUS_FAILED,
    STATUS_SUCCESS,
    STATUS_ERROR,
    # Logger
    WORKFLOW_LOGGER_NAME,
    # Errors
    ERROR_INTENT_CLASSIFICATION_FAILED,
    ERROR_SQL_GENERATION_FAILED,
    ERROR_SQL_REASONING_FAILED,
    ERROR_QUESTION_RECOMMENDATION_FAILED,
    ERROR_RELATIONSHIP_RECOMMENDATION_FAILED,
    ERROR_SEMANTICS_DESCRIPTION_FAILED,
    ERROR_DATA_ASSISTANCE_FAILED,
    ERROR_CHART_GENERATION_FAILED,
    ERROR_RESPONSE_FORMATTING_FAILED,
    ERROR_SESSION_INITIALIZATION_FAILED,
    # Messages
    MESSAGE_MISLEADING_QUERY,
    MESSAGE_ERROR_CLASSIFICATION,
    MESSAGE_ERROR_SQL,
    MESSAGE_ERROR_GENERIC,
    # Streaming
    DEFAULT_CHUNK_SIZE,
    # Language
    DEFAULT_LANGUAGE,
    # Relationships
    RELATIONSHIP_TYPE_ONE_TO_MANY,
    RELATIONSHIP_TYPE_MANY_TO_MANY,
    RELATIONSHIP_TYPE_ONE_TO_ONE,
    RELATIONSHIP_TYPE_GROUPING,
    # Charts
    CHART_TYPE_BAR,
    CHART_TYPE_LINE,
    CHART_TYPE_PIE,
    CHART_TYPE_SCATTER,
    CHART_TYPE_AREA,
)

__all__ = [
    # Config classes
    "SQLProcessingConfig",
    "IntentRecommendationConfig",
    "AssistanceVisualizationConfig",
    "OrchestratorConfig",
    "WorkflowConfig",
    "get_workflow_config",
    "set_workflow_config",
    "reset_workflow_config",
    # Intent types
    "IntentType",
    "INTENT_TEXT_TO_SQL",
    "INTENT_GENERAL",
    "INTENT_USER_GUIDE",
    "INTENT_MISLEADING_QUERY",
    "ALL_INTENT_TYPES",
    # Categories
    "QUESTION_CATEGORIES",
    # Keywords
    "FOLLOWUP_KEYWORDS",
    "VISUALIZATION_KEYWORDS",
    # Confidence
    "DEFAULT_AI_CONFIDENCE",
    "DEFAULT_FALLBACK_CONFIDENCE",
    # Response types
    "RESPONSE_TYPE_SQL_GENERATED",
    "RESPONSE_TYPE_INTENT_TEXT_TO_SQL",
    "RESPONSE_TYPE_INTENT_GENERAL",
    "RESPONSE_TYPE_INTENT_USER_GUIDE",
    "RESPONSE_TYPE_INTENT_MISLEADING",
    # Status
    "STATUS_PENDING",
    "STATUS_IN_PROGRESS",
    "STATUS_COMPLETED",
    "STATUS_FAILED",
    "STATUS_SUCCESS",
    "STATUS_ERROR",
    # Logger
    "WORKFLOW_LOGGER_NAME",
    # Errors
    "ERROR_INTENT_CLASSIFICATION_FAILED",
    "ERROR_SQL_GENERATION_FAILED",
    "ERROR_SQL_REASONING_FAILED",
    "ERROR_QUESTION_RECOMMENDATION_FAILED",
    "ERROR_RELATIONSHIP_RECOMMENDATION_FAILED",
    "ERROR_SEMANTICS_DESCRIPTION_FAILED",
    "ERROR_DATA_ASSISTANCE_FAILED",
    "ERROR_CHART_GENERATION_FAILED",
    "ERROR_RESPONSE_FORMATTING_FAILED",
    "ERROR_SESSION_INITIALIZATION_FAILED",
    # Messages
    "MESSAGE_MISLEADING_QUERY",
    "MESSAGE_ERROR_CLASSIFICATION",
    "MESSAGE_ERROR_SQL",
    "MESSAGE_ERROR_GENERIC",
    # Streaming
    "DEFAULT_CHUNK_SIZE",
    # Language
    "DEFAULT_LANGUAGE",
    # Relationships
    "RELATIONSHIP_TYPE_ONE_TO_MANY",
    "RELATIONSHIP_TYPE_MANY_TO_MANY",
    "RELATIONSHIP_TYPE_ONE_TO_ONE",
    "RELATIONSHIP_TYPE_GROUPING",
    # Charts
    "CHART_TYPE_BAR",
    "CHART_TYPE_LINE",
    "CHART_TYPE_PIE",
    "CHART_TYPE_SCATTER",
    "CHART_TYPE_AREA",
]

