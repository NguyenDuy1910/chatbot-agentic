"""
Workflow Constants

This module contains all constant values used across workflows.
Centralizing constants here makes them easier to maintain and modify.
"""

from typing import List, Literal

# ==================== Intent Types ====================

IntentType = Literal["TEXT_TO_SQL", "GENERAL", "USER_GUIDE", "MISLEADING_QUERY"]

INTENT_TEXT_TO_SQL: IntentType = "TEXT_TO_SQL"
INTENT_GENERAL: IntentType = "GENERAL"
INTENT_USER_GUIDE: IntentType = "USER_GUIDE"
INTENT_MISLEADING_QUERY: IntentType = "MISLEADING_QUERY"

ALL_INTENT_TYPES: List[IntentType] = [
    INTENT_TEXT_TO_SQL,
    INTENT_GENERAL,
    INTENT_USER_GUIDE,
    INTENT_MISLEADING_QUERY,
]

# ==================== Question Categories ====================

QUESTION_CATEGORIES = [
    "Descriptive Questions",
    "Segmentation Questions",
    "Comparative Questions",
    "Data Quality/Accuracy Questions",
]

# ==================== Keyword Lists ====================

# Keywords that indicate a follow-up question
FOLLOWUP_KEYWORDS = [
    "also",
    "and",
    "what about",
    "how about",
    "show me more",
    "previous",
    "that",
    "this",
    "those",
    "these",
]

# Keywords that indicate visualization is needed
VISUALIZATION_KEYWORDS = [
    "chart",
    "graph",
    "plot",
    "visualize",
    "show",
    "trend",
    "distribution",
    "comparison",
    "over time",
]

# ==================== Default Confidence Scores ====================

DEFAULT_AI_CONFIDENCE = 0.9
DEFAULT_FALLBACK_CONFIDENCE = 0.5

# ==================== Response Types ====================

RESPONSE_TYPE_SQL_GENERATED = "sql_generated"
RESPONSE_TYPE_INTENT_TEXT_TO_SQL = "intent_text_to_sql"
RESPONSE_TYPE_INTENT_GENERAL = "intent_general"
RESPONSE_TYPE_INTENT_USER_GUIDE = "intent_user_guide"
RESPONSE_TYPE_INTENT_MISLEADING = "intent_misleading_query"

# ==================== Status Values ====================

STATUS_PENDING = "pending"
STATUS_IN_PROGRESS = "in_progress"
STATUS_COMPLETED = "completed"
STATUS_FAILED = "failed"
STATUS_SUCCESS = "success"
STATUS_ERROR = "error"

# ==================== Logger Names ====================

# Standardized logger name for all workflows
WORKFLOW_LOGGER_NAME = "finx-ai-service.workflows"

# ==================== Error Messages ====================

ERROR_INTENT_CLASSIFICATION_FAILED = "Intent classification failed"
ERROR_SQL_GENERATION_FAILED = "SQL Generation failed"
ERROR_SQL_REASONING_FAILED = "SQL Reasoning failed"
ERROR_QUESTION_RECOMMENDATION_FAILED = "Question recommendation failed"
ERROR_RELATIONSHIP_RECOMMENDATION_FAILED = "Relationship recommendation failed"
ERROR_SEMANTICS_DESCRIPTION_FAILED = "Semantics description failed"
ERROR_DATA_ASSISTANCE_FAILED = "Data Assistance failed"
ERROR_CHART_GENERATION_FAILED = "Chart Generation failed"
ERROR_RESPONSE_FORMATTING_FAILED = "Response formatting failed"
ERROR_SESSION_INITIALIZATION_FAILED = "Session initialization failed"

# ==================== User-Friendly Messages ====================

MESSAGE_MISLEADING_QUERY = (
    "I'm here to help with data analysis. "
    "Could you ask a question related to your data?"
)

MESSAGE_ERROR_CLASSIFICATION = (
    "I'm having trouble understanding your question. Could you rephrase it?"
)

MESSAGE_ERROR_SQL = (
    "I couldn't generate a valid SQL query. Could you provide more details?"
)

MESSAGE_ERROR_GENERIC = (
    "Please try again or contact support if the issue persists."
)

# ==================== Streaming Configuration ====================

DEFAULT_CHUNK_SIZE = 50  # words per chunk for streaming

# ==================== Language Defaults ====================

DEFAULT_LANGUAGE = "English"

# ==================== Relationship Types ====================

RELATIONSHIP_TYPE_ONE_TO_MANY = "one-to-many"
RELATIONSHIP_TYPE_MANY_TO_MANY = "many-to-many"
RELATIONSHIP_TYPE_ONE_TO_ONE = "one-to-one"
RELATIONSHIP_TYPE_GROUPING = "grouping"

# ==================== Chart Types ====================

CHART_TYPE_BAR = "bar"
CHART_TYPE_LINE = "line"
CHART_TYPE_PIE = "pie"
CHART_TYPE_SCATTER = "scatter"
CHART_TYPE_AREA = "area"

# ==================== Export ====================

__all__ = [
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

