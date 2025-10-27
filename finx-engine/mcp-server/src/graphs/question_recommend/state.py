"""
State definition for Question Recommendation Graph.

Extends BaseState with question recommendation-specific fields.
"""

from typing import TypedDict, List, Optional, Any, Dict

from src.core.base_state import BaseState


class QuestionRecommendState(BaseState):
    """
    State for Question Recommendation Pipeline.

    Flow: Build Prompt → Generate Questions → Normalize Response
    
    Extends BaseState with question recommendation-specific fields
    for tracking inputs, processing stages, and outputs.
    """
    # ===== INPUTS =====
    contexts: List[str]
    previous_questions: List[str]
    categories: List[str]
    language: str
    max_questions: int
    max_categories: int

    # ===== PROCESSING STAGES =====
    # Stage 1: Prompt Building
    prompt_text: Optional[str]
    prompt_variables: Optional[Dict[str, Any]]

    # Stage 2: Generation
    raw_response: Optional[str]
    generation_metadata: Optional[Dict[str, Any]]

    # ===== OUTPUT =====
    questions: Optional[List[Dict[str, str]]]
    normalized_response: Optional[Dict[str, Any]]

    # ===== PROVIDERS (injected at runtime) =====
    llm_provider: Optional[Any]


__all__ = [
    "QuestionRecommendState",
]

