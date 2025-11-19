from typing import Any, Dict, List, Literal, Optional, TypedDict

from src.core.base_state import BaseState


class IntentRecommendationState(BaseState):
    """
    State for Intent & Recommendation workflow.
    
    This state tracks intent classification and various recommendation types
    including question recommendations, relationship recommendations, and semantics descriptions.
    """
    
    # ============= Input =============
    query: str  # User's question
    project_id: Optional[str]
    histories: List[Dict[str, Any]]  # Conversation history
    configuration: Optional[Dict[str, Any]]  # User configuration (language, etc.)
    
    # ============= Database Context =============
    db_schemas: List[str]  # Database schemas in DDL format
    retrieved_tables: List[str]  # Retrieved table names
    
    # ============= Intent Classification =============
    intent: Optional[Literal["TEXT_TO_SQL", "GENERAL", "USER_GUIDE", "MISLEADING_QUERY"]]
    intent_reasoning: Optional[str]  # Reasoning for intent classification
    rephrased_question: Optional[str]  # Rephrased question for better context
    confidence_score: float  # Confidence score for intent classification
    classification_prompt: Optional[str]  # Prompt used (for debugging)
    
    # ============= Question Recommendation =============
    recommended_questions: List[Dict[str, str]]  # Recommended questions with categories
    question_recommendation_reasoning: Optional[str]  # Reasoning for recommendations
    categories: List[str]  # Categories for question recommendations
    
    # ============= Relationship Recommendation =============
    recommended_relationships: List[Dict[str, Any]]  # Recommended table relationships
    relationship_reasoning: Optional[str]  # Reasoning for relationship recommendations
    
    # ============= Semantics Description =============
    semantics_description: Optional[str]  # Description of schema semantics
    semantics_reasoning: Optional[str]  # Reasoning for semantics description
    
    # ============= Final Response =============
    response: Optional[Dict[str, Any]]  # Final formatted response
    response_type: Optional[str]  # Response type


def create_initial_intent_recommendation_state(
    query: str,
    project_id: Optional[str] = None,
    histories: Optional[List[Dict[str, Any]]] = None,
    configuration: Optional[Dict[str, Any]] = None,
    db_schemas: Optional[List[str]] = None,
) -> IntentRecommendationState:
    """
    Create initial state for Intent & Recommendation workflow.
    
    Args:
        query: User's question
        project_id: Optional project identifier
        histories: Conversation history
        configuration: User configuration
        db_schemas: Database schemas
        
    Returns:
        Initial IntentRecommendationState
    """
    return IntentRecommendationState(
        # Input
        query=query,
        project_id=project_id,
        histories=histories or [],
        configuration=configuration or {},
        
        # Database context
        db_schemas=db_schemas or [],
        retrieved_tables=[],
        
        # Intent classification
        intent=None,
        intent_reasoning=None,
        rephrased_question=None,
        confidence_score=0.0,
        classification_prompt=None,
        
        # Question recommendation
        recommended_questions=[],
        question_recommendation_reasoning=None,
        categories=[],
        
        # Relationship recommendation
        recommended_relationships=[],
        relationship_reasoning=None,
        
        # Semantics description
        semantics_description=None,
        semantics_reasoning=None,
        
        # Response
        response=None,
        response_type=None,
        
        # Base state fields
        errors=[],
        warnings=[],
        status="pending",
        current_step="",
        metadata={},
        context={},
    )

