"""
Workflow Configuration

This module contains runtime configuration for workflows.
Values can be overridden via environment variables or configuration files.
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class SQLProcessingConfig:
    """Configuration for SQL Processing workflow."""
    
    # SQL correction settings
    max_correction_attempts: int = 3
    enable_sql_validation: bool = True
    enable_sql_diagnosis: bool = True
    
    # SQL execution settings
    should_execute_by_default: bool = False
    execution_timeout_seconds: int = 30
    
    # SQL generation settings
    enable_reasoning: bool = True
    enable_followup_detection: bool = True
    
    @classmethod
    def from_env(cls) -> "SQLProcessingConfig":
        """Create configuration from environment variables."""
        return cls(
            max_correction_attempts=int(os.getenv("SQL_MAX_CORRECTION_ATTEMPTS", "3")),
            enable_sql_validation=os.getenv("SQL_ENABLE_VALIDATION", "true").lower() == "true",
            enable_sql_diagnosis=os.getenv("SQL_ENABLE_DIAGNOSIS", "true").lower() == "true",
            should_execute_by_default=os.getenv("SQL_EXECUTE_BY_DEFAULT", "false").lower() == "true",
            execution_timeout_seconds=int(os.getenv("SQL_EXECUTION_TIMEOUT", "30")),
            enable_reasoning=os.getenv("SQL_ENABLE_REASONING", "true").lower() == "true",
            enable_followup_detection=os.getenv("SQL_ENABLE_FOLLOWUP", "true").lower() == "true",
        )


@dataclass
class IntentRecommendationConfig:
    """Configuration for Intent & Recommendation workflow."""
    
    # Question recommendation settings
    max_questions: int = 5
    enable_question_recommendation: bool = True
    
    # Relationship recommendation settings
    enable_relationship_recommendation: bool = True
    
    # Semantics description settings
    enable_semantics_description: bool = True
    
    # Intent classification settings
    enable_ai_classification: bool = True
    classification_confidence_threshold: float = 0.7
    
    @classmethod
    def from_env(cls) -> "IntentRecommendationConfig":
        """Create configuration from environment variables."""
        return cls(
            max_questions=int(os.getenv("INTENT_MAX_QUESTIONS", "5")),
            enable_question_recommendation=os.getenv("INTENT_ENABLE_QUESTIONS", "true").lower() == "true",
            enable_relationship_recommendation=os.getenv("INTENT_ENABLE_RELATIONSHIPS", "true").lower() == "true",
            enable_semantics_description=os.getenv("INTENT_ENABLE_SEMANTICS", "true").lower() == "true",
            enable_ai_classification=os.getenv("INTENT_ENABLE_AI", "true").lower() == "true",
            classification_confidence_threshold=float(os.getenv("INTENT_CONFIDENCE_THRESHOLD", "0.7")),
        )


@dataclass
class AssistanceVisualizationConfig:
    """Configuration for Assistance & Visualization workflow."""
    
    # Assistance settings
    enable_streaming: bool = True
    
    # Chart generation settings
    enable_chart_generation: bool = True
    enable_chart_adjustment: bool = True
    default_chart_type: Optional[str] = None
    
    # Visualization detection settings
    auto_detect_visualization: bool = True
    
    @classmethod
    def from_env(cls) -> "AssistanceVisualizationConfig":
        """Create configuration from environment variables."""
        return cls(
            enable_streaming=os.getenv("ASSIST_ENABLE_STREAMING", "true").lower() == "true",
            enable_chart_generation=os.getenv("ASSIST_ENABLE_CHARTS", "true").lower() == "true",
            enable_chart_adjustment=os.getenv("ASSIST_ENABLE_CHART_ADJUST", "true").lower() == "true",
            default_chart_type=os.getenv("ASSIST_DEFAULT_CHART_TYPE"),
            auto_detect_visualization=os.getenv("ASSIST_AUTO_DETECT_VIZ", "true").lower() == "true",
        )


@dataclass
class OrchestratorConfig:
    """Configuration for Master Orchestrator workflow."""
    
    # Session settings
    enable_session_history: bool = True
    max_history_entries: int = 10
    
    # User preferences
    default_language: str = "English"
    enable_streaming_by_default: bool = True
    max_recommendations: int = 5
    
    # Error handling
    enable_graceful_degradation: bool = True
    debug_mode: bool = False
    
    # Analytics
    enable_analytics: bool = True
    track_processing_time: bool = True
    
    @classmethod
    def from_env(cls) -> "OrchestratorConfig":
        """Create configuration from environment variables."""
        return cls(
            enable_session_history=os.getenv("ORCH_ENABLE_HISTORY", "true").lower() == "true",
            max_history_entries=int(os.getenv("ORCH_MAX_HISTORY", "10")),
            default_language=os.getenv("ORCH_DEFAULT_LANGUAGE", "English"),
            enable_streaming_by_default=os.getenv("ORCH_ENABLE_STREAMING", "true").lower() == "true",
            max_recommendations=int(os.getenv("ORCH_MAX_RECOMMENDATIONS", "5")),
            enable_graceful_degradation=os.getenv("ORCH_GRACEFUL_DEGRADATION", "true").lower() == "true",
            debug_mode=os.getenv("ORCH_DEBUG_MODE", "false").lower() == "true",
            enable_analytics=os.getenv("ORCH_ENABLE_ANALYTICS", "true").lower() == "true",
            track_processing_time=os.getenv("ORCH_TRACK_TIME", "true").lower() == "true",
        )


@dataclass
class WorkflowConfig:
    """Master configuration for all workflows."""
    
    sql_processing: SQLProcessingConfig = field(default_factory=SQLProcessingConfig)
    intent_recommendation: IntentRecommendationConfig = field(default_factory=IntentRecommendationConfig)
    assistance_visualization: AssistanceVisualizationConfig = field(default_factory=AssistanceVisualizationConfig)
    orchestrator: OrchestratorConfig = field(default_factory=OrchestratorConfig)
    
    @classmethod
    def from_env(cls) -> "WorkflowConfig":
        """Create complete configuration from environment variables."""
        return cls(
            sql_processing=SQLProcessingConfig.from_env(),
            intent_recommendation=IntentRecommendationConfig.from_env(),
            assistance_visualization=AssistanceVisualizationConfig.from_env(),
            orchestrator=OrchestratorConfig.from_env(),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "sql_processing": self.sql_processing.__dict__,
            "intent_recommendation": self.intent_recommendation.__dict__,
            "assistance_visualization": self.assistance_visualization.__dict__,
            "orchestrator": self.orchestrator.__dict__,
        }


# Global configuration instance (can be overridden)
_config: Optional[WorkflowConfig] = None


def get_workflow_config() -> WorkflowConfig:
    """Get the global workflow configuration."""
    global _config
    if _config is None:
        _config = WorkflowConfig.from_env()
    return _config


def set_workflow_config(config: WorkflowConfig) -> None:
    """Set the global workflow configuration."""
    global _config
    _config = config


def reset_workflow_config() -> None:
    """Reset configuration to default (reload from environment)."""
    global _config
    _config = None


__all__ = [
    "SQLProcessingConfig",
    "IntentRecommendationConfig",
    "AssistanceVisualizationConfig",
    "OrchestratorConfig",
    "WorkflowConfig",
    "get_workflow_config",
    "set_workflow_config",
    "reset_workflow_config",
]

