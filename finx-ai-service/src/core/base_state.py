from typing import Any, Dict, List, Optional, TypedDict


class PipelineMetadata(TypedDict, total=False):
    
    execution_id: str
    start_time: float
    end_time: Optional[float]
    duration: Optional[float]
    step_count: int
    current_step: str
    tags: Dict[str, str]


class BaseState(TypedDict, total=False):
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

