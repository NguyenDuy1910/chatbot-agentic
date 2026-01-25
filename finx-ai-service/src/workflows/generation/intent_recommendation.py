import logging
from typing import Any, Dict, List, Literal, Optional

import orjson
from langgraph.graph import END
from pydantic import BaseModel

from src.core.base_graph import BaseGraph
from src.core.base_state import BaseState
from src.workflows.common import clean_up_new_lines
from src.workflows.config import (
    WORKFLOW_LOGGER_NAME,
    INTENT_TEXT_TO_SQL,
    DEFAULT_AI_CONFIDENCE,
    DEFAULT_FALLBACK_CONFIDENCE,
    ERROR_INTENT_CLASSIFICATION_FAILED,
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


# ============================================================================
# NODE FUNCTIONS
# ============================================================================

async def intent_classification_node(state: Dict[str, Any]) -> Dict[str, Any]:
    
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





class IntentRecommendationGraph(BaseGraph):
    """Intent Classification and Recommendations graph."""

    def __init__(self):
        super().__init__("intent_recommendation")

    def get_state_schema(self) -> type:
        return IntentRecommendationState

    def _add_nodes(self) -> None:
        self.graph.add_node("intent_classification", intent_classification_node)
        self.graph.add_node("format_response", self._format_response_node)

    def _add_edges(self) -> None:
        self.graph.set_entry_point("intent_classification")
        self.graph.add_edge("intent_classification", "format_response")
        self.graph.add_edge("format_response", END)



    async def _format_response_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Format the intent classification response."""
        state["current_step"] = "format_response"
        try:
            intent = state.get("intent", "TEXT_TO_SQL")

            response = {
                "intent": intent,
                "rephrased_question": state.get("rephrased_question", ""),
                "intent_reasoning": state.get("intent_reasoning", ""),
                "confidence_score": state.get("confidence_score", 0.0),
                "metadata": {
                    "db_schemas_count": len(state.get("db_schemas", [])),
                    "retrieved_tables": state.get("retrieved_tables", []),
                }
            }

            state["response"] = response
            state["response_type"] = f"intent_{intent.lower()}"
            state["status"] = "completed"
            
            logger.info(f"Intent classification completed: {intent}")
            
        except Exception as e:
            logger.error(f"Error formatting response: {e}")
            state["errors"].append(f"Response formatting failed: {str(e)}")
            state["response"] = {
                "intent": state.get("intent", "TEXT_TO_SQL"), 
                "error": "Failed to format response"
            }
            state["status"] = "failed"

        return state


def create_graph() -> IntentRecommendationGraph:
    graph = IntentRecommendationGraph()
    graph.build()
    return graph

