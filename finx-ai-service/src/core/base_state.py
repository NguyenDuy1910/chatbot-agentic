"""
Base state definition for all LangGraph pipelines.

Provides common state fields and metadata for all graphs.
"""

from typing import Any, Dict, List, Optional, TypedDict


class PipelineMetadata(TypedDict, total=False):
    """Metadata for pipeline execution tracking."""
    
    execution_id: str
    start_time: float
    end_time: Optional[float]
    duration: Optional[float]
    step_count: int
    current_step: str
    tags: Dict[str, str]


class BaseState(TypedDict, total=False):
    """
    Base state for all LangGraph pipelines.
    
    All graph-specific states should extend this base state
    to ensure consistent error handling and observability.
    """
    
    # Error and warning tracking
    errors: List[str]
    warnings: List[str]
    
    # Status tracking
    status: str  # "pending", "processing", "completed", "failed"
    current_step: str
    
    # Metadata
    metadata: PipelineMetadata
    
    # Additional context
    context: Dict[str, Any]

