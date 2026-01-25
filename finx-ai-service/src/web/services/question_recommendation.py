import logging
import uuid
from typing import Any, Dict, List, Literal, Optional

from cachetools import TTLCache
from pydantic import BaseModel, Field

from src.core.base_graph import BaseGraph
from src.web.services import BaseRequest
from src.workflows.generation import create_initial_intent_recommendation_state

logger = logging.getLogger(__name__)


class QuestionRecommendationRequest(BaseRequest):
    """Request for question recommendations."""

    query: Optional[str] = Field(
        default="", description="Optional previous question for context"
    )
    categories: Optional[List[str]] = Field(
        default=None, description="Categories for question generation"
    )
    max_questions: int = Field(default=5, ge=1, le=20)


class QuestionRecommendationResponse(BaseModel):
    """Response containing recommended questions."""

    query_id: str


class RecommendedQuestion(BaseModel):
    """A single recommended question."""

    question: str
    category: str


class QuestionRecommendationResult(BaseModel):
    """Result of question recommendation."""

    query_id: str
    status: Literal[
        "processing",
        "finished",
        "failed",
    ]
    intent: Optional[Literal["TEXT_TO_SQL", "GENERAL", "USER_GUIDE", "MISLEADING_QUERY"]] = None
    recommended_questions: List[RecommendedQuestion] = Field(default_factory=list)
    recommended_relationships: List[Dict[str, Any]] = Field(default_factory=list)
    semantics_description: Optional[str] = None
    error: Optional[str] = None
    trace_id: Optional[str] = None


class QuestionRecommendationService:
    """Service for generating question recommendations using Intent Recommendation workflow."""

    def __init__(
        self,
        base_workflow: Dict[str, BaseGraph],
        maxsize: int = 1_000_000,
        ttl: int = 300,
    ):
        self._base_workflow = base_workflow
        self._results: TTLCache = TTLCache(maxsize=maxsize, ttl=ttl)

    async def recommend(
        self,
        request: QuestionRecommendationRequest,
        db_schemas: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> QuestionRecommendationResponse:
        """
        Generate question recommendations using Intent Recommendation workflow.

        Args:
            request: The recommendation request
            db_schemas: Database schemas for context
            context: Additional context (e.g., generator, retriever)

        Returns:
            QuestionRecommendationResponse with query_id
        """
        query_id = str(uuid.uuid4())
        request.query_id = query_id

        # Initialize result with "processing" status
        self._results[query_id] = QuestionRecommendationResult(
            query_id=query_id,
            status="processing",
            trace_id=query_id,
        )

        # Start async processing
        try:
            # Create initial state for Intent Recommendation workflow
            initial_state = create_initial_intent_recommendation_state(
                query=request.query or "",
                project_id=request.project_id,
                histories=[],
                configuration=request.configurations.model_dump(),
                db_schemas=db_schemas or [],
            )

            # Add metadata for question recommendation
            initial_state["metadata"] = {
                "max_questions": request.max_questions,
            }

            if request.categories:
                initial_state["categories"] = request.categories

            # Add context
            if context:
                initial_state["context"] = context

            # Execute workflow asynchronously
            import asyncio

            asyncio.create_task(
                self._execute_workflow(query_id, initial_state, "intent_recommendation")
            )

        except Exception as e:
            logger.error(
                f"Error starting question recommendation workflow: {e}", exc_info=True
            )
            self._results[query_id] = QuestionRecommendationResult(
                query_id=query_id,
                status="failed",
                error=str(e),
                trace_id=query_id,
            )

        return QuestionRecommendationResponse(query_id=query_id)

    async def _execute_workflow(
        self, query_id: str, initial_state: Dict[str, Any], workflow_name: str
    ) -> None:
        """Execute workflow and update results."""
        try:
            # Get workflow
            workflow = self._base_workflow.get(workflow_name)
            if not workflow:
                raise ValueError(f"Workflow '{workflow_name}' not found")

            # Execute workflow
            result = await workflow.execute(initial_state)

            # Map workflow result to QuestionRecommendationResult
            response = self._map_workflow_result(result, query_id)
            self._results[query_id] = response

        except Exception as e:
            logger.error(
                f"Error executing workflow for {query_id}: {e}", exc_info=True
            )
            self._results[query_id] = QuestionRecommendationResult(
                query_id=query_id,
                status="failed",
                error=str(e),
                trace_id=query_id,
            )

    def _map_workflow_result(
        self, result: Dict[str, Any], query_id: str
    ) -> QuestionRecommendationResult:
        """Map workflow result to QuestionRecommendationResult."""
        status = result.get("status", "finished")
        if status == "completed":
            status = "finished"

        # Map recommended questions
        recommended_questions = []
        for q in result.get("recommended_questions", []):
            if isinstance(q, dict):
                recommended_questions.append(
                    RecommendedQuestion(
                        question=q.get("question", ""),
                        category=q.get("category", "General"),
                    )
                )

        return QuestionRecommendationResult(
            query_id=query_id,
            status=status,
            intent=result.get("intent"),
            recommended_questions=recommended_questions,
            recommended_relationships=result.get("recommended_relationships", []),
            semantics_description=result.get("semantics_description"),
            error="; ".join(result.get("errors", [])) if result.get("errors") else None,
            trace_id=query_id,
        )

    async def get_result(self, query_id: str) -> Optional[QuestionRecommendationResult]:
        """Get result for a query_id."""
        return self._results.get(query_id)

    async def get_questions(
        self,
        db_schemas: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None,
        max_questions: int = 5,
        categories: Optional[List[str]] = None,
        project_id: Optional[str] = None,
    ) -> List[RecommendedQuestion]:
        """
        Synchronously get question recommendations.

        This is a convenience method that waits for the workflow to complete.

        Args:
            db_schemas: Database schemas for context
            context: Additional context (e.g., generator, retriever)
            max_questions: Maximum number of questions to generate
            categories: Categories for question generation
            project_id: Project ID

        Returns:
            List of recommended questions
        """
        import asyncio

        from src.web.services import Configuration

        # Create request
        request = QuestionRecommendationRequest(
            query="",
            project_id=project_id,
            max_questions=max_questions,
            categories=categories,
            configurations=Configuration(),
        )

        # Start recommendation
        response = await self.recommend(request, db_schemas, context)

        # Wait for completion
        max_wait = 30  # seconds
        wait_time = 0
        while wait_time < max_wait:
            result = await self.get_result(response.query_id)
            if result and result.status in ["finished", "failed"]:
                if result.status == "finished":
                    return result.recommended_questions
                else:
                    logger.error(f"Question recommendation failed: {result.error}")
                    return []

            await asyncio.sleep(0.5)
            wait_time += 0.5

        logger.warning("Question recommendation timed out")
        return []

