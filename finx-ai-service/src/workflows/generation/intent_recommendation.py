"""Intent Recommendation Workflow - handles intent classification and recommendations."""

import logging
from typing import Any, Dict, List, Literal, Optional

import orjson
from langgraph.graph import END
from pydantic import BaseModel

from src.core.base_graph import BaseGraph
from src.core.base_state import BaseState
from src.workflows.common import clean_up_new_lines
from src.workflows.config import (
    get_workflow_config,
    WORKFLOW_LOGGER_NAME,
    QUESTION_CATEGORIES,
    INTENT_TEXT_TO_SQL,
    INTENT_USER_GUIDE,
    DEFAULT_AI_CONFIDENCE,
    DEFAULT_FALLBACK_CONFIDENCE,
    ERROR_INTENT_CLASSIFICATION_FAILED,
    ERROR_QUESTION_RECOMMENDATION_FAILED,
)
from src.workflows.prompts import render_prompt

logger = logging.getLogger(WORKFLOW_LOGGER_NAME)


class IntentRecommendationState(BaseState):
    
    # Input
    query: str
    project_id: Optional[str]
    histories: List[Dict[str, Any]]
    configuration: Optional[Dict[str, Any]]
    
    # Database Context
    db_schemas: List[str]
    retrieved_tables: List[str]
    
    # Intent Classification
    intent: Optional[Literal["TEXT_TO_SQL", "GENERAL", "USER_GUIDE", "MISLEADING_QUERY"]]
    intent_reasoning: Optional[str]
    rephrased_question: Optional[str]
    confidence_score: float
    classification_prompt: Optional[str]
    
    # Question Recommendation
    recommended_questions: List[Dict[str, str]]
    question_recommendation_reasoning: Optional[str]
    categories: List[str]
    
    # Relationship Recommendation
    recommended_relationships: List[Dict[str, Any]]
    relationship_reasoning: Optional[str]
    
    # Semantics Description
    semantics_description: Optional[str]
    semantics_reasoning: Optional[str]
    
    # Final Response
    response: Optional[Dict[str, Any]]
    response_type: Optional[str]


def create_initial_state(
    query: str,
    project_id: Optional[str] = None,
    histories: Optional[List[Dict[str, Any]]] = None,
    configuration: Optional[Dict[str, Any]] = None,
    db_schemas: Optional[List[str]] = None,
) -> IntentRecommendationState:
    return IntentRecommendationState(
        query=query,
        project_id=project_id,
        histories=histories or [],
        configuration=configuration or {},
        db_schemas=db_schemas or [],
        retrieved_tables=[],
        intent=None,
        intent_reasoning=None,
        rephrased_question=None,
        confidence_score=0.0,
        classification_prompt=None,
        recommended_questions=[],
        question_recommendation_reasoning=None,
        categories=[],
        recommended_relationships=[],
        relationship_reasoning=None,
        semantics_description=None,
        semantics_reasoning=None,
        response=None,
        response_type=None,
        errors=[],
        warnings=[],
        status="pending",
        current_step="",
        metadata={},
        context={},
    )


class IntentClassificationResult(BaseModel):
    rephrased_question: str
    results: Literal["MISLEADING_QUERY", "TEXT_TO_SQL", "GENERAL", "USER_GUIDE"]
    reasoning: str


class QuestionRecommendationResult(BaseModel):
    questions: List[Dict[str, str]]


def _get_demo_questions(intent: str, max_questions: int) -> List[Dict[str, str]]:
    if intent == INTENT_TEXT_TO_SQL:
        questions = [
            {"category": "Descriptive", "question": "What is the total number of customers in the database?"},
            {"category": "Comparative", "question": "How do sales compare across different regions?"},
            {"category": "Segmentation", "question": "Which customer segment has the highest average order value?"},
            {"category": "Trends", "question": "What are the monthly sales trends for this year?"},
            {"category": "Data Quality", "question": "Are there any customers with missing contact information?"}
        ]
    elif intent == INTENT_USER_GUIDE:
        questions = [
            {"category": "Getting Started", "question": "How do I write a basic SELECT query?"},
            {"category": "Joins", "question": "How can I join multiple tables together?"},
            {"category": "Aggregation", "question": "What are the common aggregate functions I can use?"},
            {"category": "Filtering", "question": "How do I filter data with WHERE clauses?"},
            {"category": "Best Practices", "question": "What are SQL query optimization tips?"}
        ]
    else:
        questions = [
            {"category": "General", "question": "What tables are available in this database?"},
            {"category": "General", "question": "What kind of data does this database contain?"},
            {"category": "General", "question": "How are the tables related to each other?"}
        ]
    return questions[:max_questions]


# ============================================================================
# NODE FUNCTIONS
# ============================================================================

async def intent_classification_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Classify user intent based on query and database schema."""
    logger.info("Running intent classification node")
    state["current_step"] = "intent_classification"

    try:
        query = state.get("query", "")
        histories = state.get("histories", [])
        configuration = state.get("configuration", {})
        db_schemas = state.get("db_schemas", [])
        context = state.get("context", {})
        generator = context.get("generator")

        language = (
            configuration.get("language", "English")
            if isinstance(configuration, dict)
            else getattr(configuration, "language", "English")
        )

        system_prompt = render_prompt("intent_recommendation/classification_system.jinja2")
        user_prompt = render_prompt(
            "intent_recommendation/classification_user.jinja2",
            context={
                "db_schemas": db_schemas or [],
                "sql_samples": state.get("sql_samples", []),
                "instructions": state.get("instructions", []),
                "docs": state.get("docs", []),
                "histories": histories,
                "query": query,
                "language": language,
            }
        )

        user_prompt = clean_up_new_lines(user_prompt)

        classification_result = await generator(
            prompt=user_prompt,
            system_prompt=system_prompt,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "intent_classification",
                    "schema": IntentClassificationResult.model_json_schema(),
                },
            }
        )

        try:
            results = orjson.loads(classification_result.get("replies")[0])
            state["rephrased_question"] = results["rephrased_question"]
            state["intent"] = results["results"]
            state["intent_reasoning"] = results["reasoning"]
            state["confidence_score"] = DEFAULT_AI_CONFIDENCE
        except Exception as e:
            logger.warning(f"Failed to parse classification result: {e}")
            state["rephrased_question"] = query
            state["intent"] = INTENT_TEXT_TO_SQL
            state["intent_reasoning"] = "Failed to classify intent"
            state["confidence_score"] = DEFAULT_FALLBACK_CONFIDENCE

        state["db_schemas"] = db_schemas
        state["retrieved_tables"] = []
        state["classification_prompt"] = user_prompt

        logger.info(f"Classified intent: {state['intent']} (confidence: {state.get('confidence_score', 0):.0%})")

    except Exception as e:
        logger.error(f"{ERROR_INTENT_CLASSIFICATION_FAILED}: {e}")
        state["errors"].append(f"{ERROR_INTENT_CLASSIFICATION_FAILED}: {str(e)}")
        state["intent"] = INTENT_TEXT_TO_SQL
        state["rephrased_question"] = state.get("query", "")

    return state


async def question_recommendation_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Generate recommended questions based on database schema."""
    logger.info("Running question recommendation node")
    state["current_step"] = "question_recommendation"

    try:
        db_schemas = state.get("db_schemas", [])
        query = state.get("query", "")
        intent = state.get("intent", INTENT_TEXT_TO_SQL)
        categories = state.get("categories", QUESTION_CATEGORIES)

        config = get_workflow_config()
        max_questions = state.get("metadata", {}).get(
            "max_questions",
            config.intent_recommendation.max_questions
        )

        context = state.get("context", {})
        generator = context.get("generator")

        if not generator:
            state["recommended_questions"] = _get_demo_questions(intent, max_questions)
            return state

        system_prompt = render_prompt("intent_recommendation/questions_system.jinja2")
        user_prompt = render_prompt(
            "intent_recommendation/questions_user.jinja2",
            context={
                "previous_question": query if query else None,
                "categories": categories,
                "db_schemas": db_schemas,
                "max_questions": max_questions,
            }
        )

        user_prompt = clean_up_new_lines(user_prompt)

        recommendation_result = await generator(
            prompt=user_prompt,
            system_prompt=system_prompt,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "question_recommendation",
                    "schema": QuestionRecommendationResult.model_json_schema(),
                },
            }
        )

        try:
            results = orjson.loads(recommendation_result.get("replies")[0])
            state["recommended_questions"] = results.get("questions", [])
            logger.info(f"Generated {len(state['recommended_questions'])} questions")
        except Exception as e:
            logger.warning(f"Failed to parse recommendations: {e}")
            state["recommended_questions"] = []
            state["warnings"].append(f"Failed to parse recommendations: {str(e)}")

    except Exception as e:
        logger.error(f"{ERROR_QUESTION_RECOMMENDATION_FAILED}: {e}")
        state["errors"].append(f"{ERROR_QUESTION_RECOMMENDATION_FAILED}: {str(e)}")
        state["recommended_questions"] = []

    return state


async def semantics_description_node(state: Dict[str, Any]) -> Dict[str, Any]:
    state["current_step"] = "semantics_description"
    try:
        db_schemas = state.get("db_schemas", [])
        # TODO: Implement semantic description generation
        state["semantics_description"] = None
        state["semantics_reasoning"] = None

        logger.info("Semantics description completed")

    except Exception as e:
        logger.error(f"Error in semantics description: {e}")
        state["errors"].append(f"Semantics description failed: {str(e)}")
        state["semantics_description"] = None

    return state


async def relationship_recommendation_node(state: Dict[str, Any]) -> Dict[str, Any]:
    state["current_step"] = "relationship_recommendation"
    try:
        # TODO: Implement relationship recommendation logic
        state["recommended_relationships"] = []
        state["relationship_reasoning"] = None
    except Exception as e:
        logger.error(f"Error in relationship recommendation: {e}")
        state["errors"].append(f"Relationship recommendation failed: {str(e)}")
        state["recommended_relationships"] = []
    return state


class IntentRecommendationGraph(BaseGraph):
    """Intent Classification and Recommendations graph."""

    def __init__(self):
        super().__init__("intent_recommendation")

    def get_state_schema(self) -> type:
        return IntentRecommendationState

    def _add_nodes(self) -> None:
        self.graph.add_node("intent_classification", intent_classification_node)
        self.graph.add_node("question_recommendation", question_recommendation_node)
        self.graph.add_node("relationship_recommendation", relationship_recommendation_node)
        self.graph.add_node("generate_semantics_description", semantics_description_node)
        self.graph.add_node("format_response", self._format_response_node)

    def _add_edges(self) -> None:
        self.graph.set_entry_point("intent_classification")
        
        self.graph.add_conditional_edges(
            "intent_classification",
            self._route_by_intent,
            {
                "text2sql_recommendation": "question_recommendation",
                "general_recommendation": "generate_semantics_description",
                "user_guide_recommendation": "question_recommendation",
                "misleading_end": "format_response",
            }
        )
        
        self.graph.add_edge("question_recommendation", "format_response")
        self.graph.add_edge("generate_semantics_description", "relationship_recommendation")
        self.graph.add_edge("relationship_recommendation", "format_response")
        self.graph.add_edge("format_response", END)

    def _route_by_intent(self, state: Dict[str, Any]) -> str:
        intent = state.get("intent", "TEXT_TO_SQL")
        
        route_map = {
            "TEXT_TO_SQL": "text2sql_recommendation",
            "GENERAL": "general_recommendation",
            "USER_GUIDE": "user_guide_recommendation",
            "MISLEADING_QUERY": "misleading_end",
        }
        
        return route_map.get(intent, "text2sql_recommendation")

    async def _format_response_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        state["current_step"] = "format_response"
        try:
            intent = state.get("intent", "TEXT_TO_SQL")

            response = {
                "intent": intent,
                "rephrased_question": state.get("rephrased_question", ""),
                "intent_reasoning": state.get("intent_reasoning", ""),
                "confidence_score": state.get("confidence_score", 0.0),
            }

            if state.get("recommended_questions"):
                response["recommended_questions"] = state["recommended_questions"]

            if state.get("recommended_relationships"):
                response["recommended_relationships"] = state["recommended_relationships"]

            if state.get("semantics_description"):
                response["semantics_description"] = state["semantics_description"]

            response["metadata"] = {
                "db_schemas_count": len(state.get("db_schemas", [])),
                "retrieved_tables": state.get("retrieved_tables", []),
            }

            state["response"] = response
            state["response_type"] = f"intent_{intent.lower()}"
            state["status"] = "completed"
        except Exception as e:
            logger.error(f"Error formatting response: {e}")
            state["errors"].append(f"Response formatting failed: {str(e)}")
            state["response"] = {"intent": state.get("intent", "TEXT_TO_SQL"), "error": "Failed to format response"}
            state["status"] = "failed"

        return state


def create_graph() -> IntentRecommendationGraph:
    graph = IntentRecommendationGraph()
    graph.build()
    return graph

