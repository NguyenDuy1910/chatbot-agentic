"""
Base state definition and schema for all LangGraph pipelines.

Provides a common foundation for state management across all graphs,
ensuring consistent error handling, metadata tracking, and observability.
"""

from typing import TypedDict, List, Optional, Any, Dict


class PipelineMetadata(TypedDict, total=False):
    """
    Common metadata for all pipelines.
    
    Tracks execution context, timing, and observability information
    across all graph executions.
    """
    trace_id: str
    start_time: float
    end_time: Optional[float]
    duration_seconds: Optional[float]
    pipeline_name: str
    version: str


class BaseState(TypedDict, total=False):
    """
    Base state definition for all LangGraph pipelines.
    
    Provides common fields for error handling, status tracking,
    and observability that all graph-specific states should extend.
    
    Graph-specific states should inherit from this class and add
    their own fields for processing stages and outputs.
    
    Example:
        class MyGraphState(BaseState):
            # Graph-specific inputs
            input_data: str
            
            # Graph-specific processing stages
            processed_data: Optional[str]
            
            # Graph-specific outputs
            result: Optional[Dict[str, Any]]
    """
    
    # ===== METADATA & ERROR HANDLING =====
    errors: List[str]
    warnings: List[str]
    status: str  # "pending", "processing", "completed", "failed"
    current_step: str
    
    # ===== OBSERVABILITY =====
    metadata: Optional[PipelineMetadata]


__all__ = [
    "BaseState",
    "PipelineMetadata",
]

