import logging
import uuid
from typing import Any, AsyncGenerator, Dict, List, Literal, Optional

from cachetools import TTLCache
from pydantic import BaseModel, Field

from src.core.base_graph import BaseGraph
from src.web.services import BaseRequest

logger = logging.getLogger(__name__)


class AskHistory(BaseModel):
    sql: str
    question: str


class AskRequest(BaseRequest):
    query: str
    # don't recommend to use id as a field name, but it's used in the older version of API spec
    # so we need to support as a choice, and will remove it in the future
    histories: Optional[List[AskHistory]] = Field(default_factory=list)
    ignore_sql_generation_reasoning: bool = False
    enable_column_pruning: bool = False
    use_dry_plan: bool = False
    allow_dry_plan_fallback: bool = True
    custom_instruction: Optional[str] = None


class AskResponse(BaseModel):
    query_id: str


class StopAskResponse(BaseModel):
    query_id: str


class AskResult(BaseModel):
    query_id: str
    status: Literal[
        "understanding",
        "classifying",
        "searching",
        "planning",
        "generating",
        "correcting",
        "finished",
        "failed",
        "stopped",
    ]


class AskError(BaseModel):
    code: int
    message: str


class _AskResultResponse(BaseModel):
    status: Literal[
        "understanding",
        "classifying",
        "searching",
        "planning",
        "generating",
        "correcting",
        "finished",
        "failed",
        "stopped",
    ]
    rephrased_question: Optional[str] = None
    intent: Optional[Literal["TEXT_TO_SQL", "GENERAL", "USER_GUIDE", "MISLEADING_QUERY"]] = None
    intent_reasoning: Optional[str] = None
    confidence_score: Optional[float] = None
    sql_generation_reasoning: Optional[str] = None
    type: Optional[Literal["GENERAL", "TEXT_TO_SQL"]] = None
    retrieved_tables: Optional[List[str]] = None
    response: Optional[Any] = None
    invalid_sql: Optional[str] = None
    error: Optional[AskError] = None
    trace_id: Optional[str] = None
    is_followup: bool = False
    general_type: Optional[
        Literal["MISLEADING_QUERY", "DATA_ASSISTANCE", "USER_GUIDE"]
    ] = None
    sql: Optional[str] = None
    formatted_answer: Optional[str] = None


class AskResultResponse(_AskResultResponse):
    is_followup: Optional[bool] = Field(False, exclude=True)
    general_type: Optional[
        Literal["MISLEADING_QUERY", "DATA_ASSISTANCE", "USER_GUIDE"]
    ] = Field(None, exclude=True)


class AskService:
    """Service for handling ask queries using SQL Processing workflow."""

    def __init__(
        self,
        base_workflow: Dict[str, BaseGraph],
        allow_intent_classification: bool = True,
        allow_sql_generation_reasoning: bool = True,
        allow_sql_functions_retrieval: bool = True,
        enable_column_pruning: bool = False,
        max_sql_correction_retries: int = 3,
        should_execute_by_default: bool = False,
        execution_timeout_seconds: int = 30,
        maxsize: int = 1_000_000,
        ttl: int = 120,
    ):
        self._base_workflow = base_workflow
        self._ask_results: TTLCache = TTLCache(maxsize=maxsize, ttl=ttl)
        self._allow_intent_classification = allow_intent_classification
        self._allow_sql_generation_reasoning = allow_sql_generation_reasoning
        self._allow_sql_functions_retrieval = allow_sql_functions_retrieval
        self._enable_column_pruning = enable_column_pruning
        self._max_sql_correction_retries = max_sql_correction_retries
        self._should_execute_by_default = should_execute_by_default
        self._execution_timeout_seconds = execution_timeout_seconds

    async def ask(
        self,
        request: AskRequest,
        db_schemas: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> AskResponse:
        """
        Process an ask request with intent classification and routing.

        Args:
            request: The ask request
            db_schemas: Database schemas for SQL generation
            context: Additional context (e.g., generator, retriever)

        Returns:
            AskResponse with query_id
        """
        query_id = str(uuid.uuid4())
        request.query_id = query_id

        # Initialize result with "understanding" status
        self._ask_results[query_id] = AskResultResponse(
            status="understanding",
            trace_id=query_id,
        )

        # Start async processing
        try:
            # Determine if this is a follow-up query
            is_followup = len(request.histories) > 0

            # Execute workflow asynchronously (fire and forget)
            import asyncio

            asyncio.create_task(
                self._execute_workflow_with_intent_routing(
                    query_id=query_id,
                    request=request,
                    db_schemas=db_schemas or [],
                    context=context,
                    is_followup=is_followup,
                )
            )

        except Exception as e:
            logger.error(f"Error starting ask workflow: {e}", exc_info=True)
            self._ask_results[query_id] = AskResultResponse(
                status="failed",
                error=AskError(code=500, message=str(e)),
                trace_id=query_id,
            )

        return AskResponse(query_id=query_id)

    @staticmethod
    def _build_intent_state(
        query: str,
        project_id: str,
        db_schemas: Optional[List[str]] = None,
        histories: Optional[List[Dict[str, str]]] = None,
        configuration: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Build intent recommendation state from params."""
        return {
            "query": query,
            "project_id": project_id,
            "histories": histories or [],
            "configuration": configuration or {},
            "db_schemas": db_schemas or [],
            "context": context or {},
            "intent": None,
            "rephrased_question": None,
            "intent_reasoning": None,
            "confidence_score": None,
            "errors": [],
            "warnings": [],
            "status": "pending",
            "current_step": "",
            "metadata": {},
        }

    @staticmethod
    def _build_sql_state(
        query: str,
        project_id: str,
        db_schemas: Optional[List[str]] = None,
        is_followup: bool = False,
        previous_sql: Optional[str] = None,
        histories: Optional[List[Dict[str, str]]] = None,
        configuration: Optional[Dict[str, Any]] = None,
        should_execute: bool = False,
        max_correction_retries: int = 3,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Build SQL processing state from params."""
        return {
            "query": query,
            "project_id": project_id,
            "is_followup": is_followup,
            "previous_sql": previous_sql,
            "histories": histories or [],
            "configuration": configuration or {},
            "db_schemas": db_schemas or [],
            "should_execute": should_execute,
            "context": context or {},
            "retrieved_tables": [],
            "has_calculated_field": False,
            "has_metric": False,
            "has_json_field": False,
            "sql_samples": [],
            "instructions": [],
            "sql_functions": [],
            "sql_reasoning": None,
            "generated_sql": None,
            "sql_generation_prompt": None,
            "followup_sql_reasoning": None,
            "followup_generated_sql": None,
            "is_valid_sql": None,
            "sql_validation_error": None,
            "sql_diagnosis": None,
            "corrected_sql": None,
            "sql_correction_reasoning": None,
            "correction_retry_count": 0,
            "max_correction_retries": max_correction_retries,
            "extracted_tables": [],
            "sql_question": None,
            "formatted_answer": None,
            "answer_reasoning": None,
            "execution_results": None,
            "execution_error": None,
            "response": None,
            "response_type": None,
            "errors": [],
            "warnings": [],
            "status": "pending",
            "current_step": "",
            "metadata": {},
        }

    @staticmethod
    def _build_assistance_state(
        query: str,
        project_id: str,
        intent: Optional[str] = None,
        db_schemas: Optional[List[str]] = None,
        histories: Optional[List[Dict[str, str]]] = None,
        configuration: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Build assistance/visualization state from params."""
        return {
            "query": query,
            "project_id": project_id,
            "intent": intent,
            "histories": histories or [],
            "configuration": configuration or {},
            "db_schemas": db_schemas or [],
            "context": context or {},
            "sql": None,
            "sql_results": None,
            "assistance_type": None,
            "assistance_response": None,
            "assistance_reasoning": None,
            "is_streaming": False,
            "chart_type": None,
            "chart_schema": None,
            "chart_reasoning": None,
            "sample_data": None,
            "sample_column_values": None,
            "vega_schema": None,
            "remove_data_from_chart_schema": False,
            "adjustment_instructions": None,
            "adjusted_chart": None,
            "adjustment_reasoning": None,
            "response": None,
            "response_type": None,
            "errors": [],
            "warnings": [],
            "status": "pending",
            "current_step": "",
            "metadata": {},
        }

    async def _execute_workflow_with_intent_routing(
        self,
        query_id: str,
        request: AskRequest,
        db_schemas: List[str],
        context: Optional[Dict[str, Any]],
        is_followup: bool,
    ) -> None:
        """Execute workflow with intent classification and routing."""
        try:
            # Step 1: Intent Classification
            logger.info(f"Starting intent classification for query {query_id}")
            self._ask_results[query_id] = AskResultResponse(
                status="classifying",
                trace_id=query_id,
            )

            # Build intent state directly (no need for create_initial_* function)
            intent_state = self._build_intent_state(
                query=request.query,
                project_id=request.project_id,
                db_schemas=db_schemas,
                histories=[{"sql": h.sql, "question": h.question} for h in request.histories],
                configuration=request.configurations.model_dump() if request.configurations else {},
                context=context,
            )

            # Execute intent classification workflow
            intent_workflow = self._base_workflow.get("intent_recommendation")
            if not intent_workflow:
                raise ValueError("Intent recommendation workflow not found")

            # Ensure graph is built before execution
            if intent_workflow.compiled_graph is None:
                logger.info("Building intent recommendation graph before execution")
                intent_workflow.build()

            intent_result = await intent_workflow.execute(intent_state)
            
            # Extract intent information
            intent = intent_result.get("intent", "TEXT_TO_SQL")
            rephrased_question = intent_result.get("rephrased_question", request.query)
            intent_reasoning = intent_result.get("intent_reasoning", "")
            confidence_score = intent_result.get("confidence_score", 0.0)

            logger.info(f"Intent classified as: {intent} (confidence: {confidence_score:.2%})")

            # Update result with intent info
            current = self._ask_results[query_id]
            self._ask_results[query_id] = AskResultResponse(
                **current.model_dump(),
                intent=intent,
                rephrased_question=rephrased_question,
                intent_reasoning=intent_reasoning,
                confidence_score=confidence_score,
            )

            # Step 2: Route to appropriate workflow based on intent
            if intent == "MISLEADING_QUERY":
                # Direct response for misleading queries
                logger.info("Handling misleading query - returning direct response")
                self._ask_results[query_id] = AskResultResponse(
                    status="finished",
                    intent=intent,
                    rephrased_question=rephrased_question,
                    intent_reasoning=intent_reasoning,
                    confidence_score=confidence_score,
                    type="GENERAL",
                    general_type="MISLEADING_QUERY",
                    response={"message": intent_reasoning},
                    formatted_answer=intent_reasoning,
                    trace_id=query_id,
                )
            
            elif intent == "TEXT_TO_SQL":
                # Route to SQL Processing workflow
                logger.info("Routing to SQL Processing workflow")
                await self._execute_sql_processing_workflow(
                    query_id=query_id,
                    request=request,
                    db_schemas=db_schemas,
                    context=context,
                    is_followup=is_followup,
                    rephrased_question=rephrased_question,
                    intent_reasoning=intent_reasoning,
                    confidence_score=confidence_score,
                )
            
            elif intent in ["GENERAL", "USER_GUIDE"]:
                # Route to Assistance/Visualization workflow
                logger.info(f"Routing to Assistance/Visualization workflow for {intent}")
                await self._execute_assistance_workflow(
                    query_id=query_id,
                    request=request,
                    db_schemas=db_schemas,
                    context=context,
                    intent=intent,
                    rephrased_question=rephrased_question,
                    intent_reasoning=intent_reasoning,
                    confidence_score=confidence_score,
                )

        except Exception as e:
            logger.error(f"Error in intent routing for {query_id}: {e}", exc_info=True)
            self._ask_results[query_id] = AskResultResponse(
                status="failed",
                error=AskError(code=500, message=str(e)),
                trace_id=query_id,
            )

    async def _execute_sql_processing_workflow(
        self,
        query_id: str,
        request: AskRequest,
        db_schemas: List[str],
        context: Optional[Dict[str, Any]],
        is_followup: bool,
        rephrased_question: str,
        intent_reasoning: str,
        confidence_score: float,
    ) -> None:
        """Execute SQL processing workflow."""
        try:
            self._ask_results[query_id] = AskResultResponse(
                status="searching",
                intent="TEXT_TO_SQL",
                rephrased_question=rephrased_question,
                intent_reasoning=intent_reasoning,
                confidence_score=confidence_score,
                trace_id=query_id,
            )

            # Build SQL state directly (no need for create_initial_* function)
            previous_sql = request.histories[-1].sql if is_followup and request.histories else None

            sql_state = self._build_sql_state(
                query=rephrased_question,
                project_id=request.project_id,
                db_schemas=db_schemas,
                is_followup=is_followup,
                previous_sql=previous_sql,
                histories=[{"sql": h.sql, "question": h.question} for h in request.histories],
                configuration=request.configurations.model_dump() if request.configurations else {},
                should_execute=self._should_execute_by_default,
                max_correction_retries=self._max_sql_correction_retries,
                context=context,
            )

            # Execute SQL processing workflow
            workflow = self._base_workflow.get("sql_processing")
            if not workflow:
                raise ValueError("SQL processing workflow not found")

            # Ensure graph is built before execution
            if workflow.compiled_graph is None:
                logger.info("Building SQL processing graph before execution")
                workflow.build()

            result = await workflow.execute(sql_state)

            # Map result
            response = self._map_workflow_result(result, query_id, "TEXT_TO_SQL")
            # Preserve intent information
            response.intent = "TEXT_TO_SQL"
            response.rephrased_question = rephrased_question
            response.intent_reasoning = intent_reasoning
            response.confidence_score = confidence_score
            self._ask_results[query_id] = response

        except Exception as e:
            logger.error(f"Error in SQL processing for {query_id}: {e}", exc_info=True)
            self._ask_results[query_id] = AskResultResponse(
                status="failed",
                error=AskError(code=500, message=str(e)),
                trace_id=query_id,
            )

    async def _execute_assistance_workflow(
        self,
        query_id: str,
        request: AskRequest,
        db_schemas: List[str],
        context: Optional[Dict[str, Any]],
        intent: str,
        rephrased_question: str,
        intent_reasoning: str,
        confidence_score: float,
    ) -> None:
        """Execute assistance/visualization workflow."""
        try:
            self._ask_results[query_id] = AskResultResponse(
                status="searching",
                intent=intent,
                rephrased_question=rephrased_question,
                intent_reasoning=intent_reasoning,
                confidence_score=confidence_score,
                trace_id=query_id,
            )

            # Build assistance state directly (no need for create_initial_* function)
            assistance_state = self._build_assistance_state(
                query=rephrased_question,
                project_id=request.project_id,
                intent=intent,
                db_schemas=db_schemas,
                histories=[{"sql": h.sql, "question": h.question} for h in request.histories],
                configuration=request.configurations.model_dump() if request.configurations else {},
                context=context,
            )

            # Execute assistance workflow
            workflow = self._base_workflow.get("assistance_visualization")
            if not workflow:
                raise ValueError("Assistance/visualization workflow not found")

            # Ensure graph is built before execution
            if workflow.compiled_graph is None:
                logger.info("Building assistance/visualization graph before execution")
                workflow.build()

            result = await workflow.execute(assistance_state)

            # Map result
            response = self._map_workflow_result(result, query_id, intent)
            # Preserve intent information
            response.intent = intent
            response.rephrased_question = rephrased_question
            response.intent_reasoning = intent_reasoning
            response.confidence_score = confidence_score
            self._ask_results[query_id] = response

        except Exception as e:
            logger.error(f"Error in assistance workflow for {query_id}: {e}", exc_info=True)
            self._ask_results[query_id] = AskResultResponse(
                status="failed",
                error=AskError(code=500, message=str(e)),
                trace_id=query_id,
            )

    async def _execute_workflow(
        self, query_id: str, initial_state: Dict[str, Any], workflow_name: str
    ) -> None:
        """Execute workflow and update results (legacy method)."""
        try:
            # Update status to searching
            self._ask_results[query_id] = AskResultResponse(
                status="searching",
                trace_id=query_id,
            )

            # Get workflow
            workflow = self._base_workflow.get(workflow_name)
            if not workflow:
                raise ValueError(f"Workflow '{workflow_name}' not found")

            # Ensure graph is built before execution
            if workflow.compiled_graph is None:
                logger.info(f"Building {workflow_name} graph before execution")
                workflow.build()

            # Execute workflow
            result = await workflow.execute(initial_state)

            # Map workflow result to AskResultResponse
            response = self._map_workflow_result(result, query_id)
            self._ask_results[query_id] = response

        except Exception as e:
            logger.error(f"Error executing workflow for {query_id}: {e}", exc_info=True)
            self._ask_results[query_id] = AskResultResponse(
                status="failed",
                error=AskError(code=500, message=str(e)),
                trace_id=query_id,
            )

    def _map_workflow_result(
        self, result: Dict[str, Any], query_id: str, workflow_type: Optional[str] = None
    ) -> AskResultResponse:
        """Map workflow result to AskResultResponse."""
        status = result.get("status", "finished")
        if status == "completed":
            status = "finished"

        # Base response fields
        response_data = {
            "status": status,
            "trace_id": query_id,
            "rephrased_question": result.get("rephrased_question"),
            "intent_reasoning": result.get("intent_reasoning"),
            "retrieved_tables": result.get("retrieved_tables", []),
            "response": result.get("response"),
            "formatted_answer": result.get("formatted_answer"),
            "is_followup": result.get("is_followup", False),
        }

        # Handle errors
        if result.get("errors"):
            response_data["error"] = AskError(
                code=500, message="; ".join(result.get("errors", []))
            )

        # Workflow-specific mapping
        if workflow_type == "TEXT_TO_SQL" or result.get("generated_sql") or result.get("corrected_sql"):
            response_data.update({
                "type": "TEXT_TO_SQL",
                "sql_generation_reasoning": result.get("sql_reasoning"),
                "sql": result.get("generated_sql") or result.get("corrected_sql"),
                "invalid_sql": result.get("generated_sql")
                if not result.get("is_valid_sql")
                else None,
            })
        elif workflow_type in ["GENERAL", "USER_GUIDE"] or result.get("general_type"):
            response_data.update({
                "type": "GENERAL",
                "general_type": result.get("general_type") or workflow_type,
            })
        else:
            # Default to TEXT_TO_SQL for backward compatibility
            response_data["type"] = "TEXT_TO_SQL"

        return AskResultResponse(**response_data)

    async def get_result(self, query_id: str) -> Optional[AskResultResponse]:
        """Get result for a query_id."""
        return self._ask_results.get(query_id)

    async def stop(self, query_id: str) -> StopAskResponse:
        """Stop a running query."""
        # Update status to stopped
        if query_id in self._ask_results:
            current = self._ask_results[query_id]
            self._ask_results[query_id] = AskResultResponse(
                **current.model_dump(),
                status="stopped",
            )
        return StopAskResponse(query_id=query_id)

    async def stream_result(
        self, query_id: str
    ) -> AsyncGenerator[AskResultResponse, None]:
        """Stream results for a query_id."""
        import asyncio

        last_status = None
        max_wait = 60  # Maximum wait time in seconds
        wait_time = 0

        while wait_time < max_wait:
            result = self._ask_results.get(query_id)
            if result:
                # Yield if status changed or it's a terminal status
                if result.status != last_status:
                    yield result
                    last_status = result.status

                # Stop if terminal status
                if result.status in ["finished", "failed", "stopped"]:
                    break

            await asyncio.sleep(0.5)
            wait_time += 0.5

        # Final yield
        final_result = self._ask_results.get(query_id)
        if final_result and final_result.status != last_status:
            yield final_result

    # ========== Direct Execution Methods (No State Management Required) ==========

    async def execute_intent_classification(
        self,
        query: str,
        project_id: str,
        db_schemas: Optional[List[str]] = None,
        histories: Optional[List[Dict[str, str]]] = None,
        configuration: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute intent classification workflow directly - just pass params!

        Args:
            query: User query
            project_id: Project ID
            db_schemas: Database schemas (optional)
            histories: Query histories (optional)
            configuration: Configuration dict (optional)
            context: Additional context (optional)

        Returns:
            Intent classification result with fields:
            - intent: TEXT_TO_SQL | GENERAL | USER_GUIDE | MISLEADING_QUERY
            - rephrased_question: Rephrased query
            - intent_reasoning: Why this intent was chosen
            - confidence_score: Confidence (0-1)
        """
        # Build state from params
        state = self._build_intent_state(
            query=query,
            project_id=project_id,
            db_schemas=db_schemas,
            histories=histories,
            configuration=configuration,
            context=context,
        )

        # Get workflow
        workflow = self._base_workflow.get("intent_recommendation")
        if not workflow:
            raise ValueError("Intent recommendation workflow not found")

        # Ensure graph is built
        if workflow.compiled_graph is None:
            workflow.build()

        # Execute and return
        return await workflow.execute(state)

    async def execute_sql_processing(
        self,
        query: str,
        project_id: str,
        db_schemas: Optional[List[str]] = None,
        is_followup: bool = False,
        previous_sql: Optional[str] = None,
        histories: Optional[List[Dict[str, str]]] = None,
        configuration: Optional[Dict[str, Any]] = None,
        should_execute: Optional[bool] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute SQL processing workflow directly - just pass params!

        Args:
            query: User query
            project_id: Project ID
            db_schemas: Database schemas (optional)
            is_followup: Is this a follow-up query (default: False)
            previous_sql: Previous SQL for follow-up (optional)
            histories: Query histories (optional)
            configuration: Configuration dict (optional)
            should_execute: Should execute SQL (default: from service config)
            context: Additional context (optional)

        Returns:
            SQL processing result with fields:
            - generated_sql: Generated SQL query
            - sql_reasoning: Why this SQL was generated
            - is_valid_sql: Whether SQL is valid
            - corrected_sql: Corrected SQL (if validation failed)
            - execution_results: Query results (if executed)
            - formatted_answer: Natural language answer
        """
        # Build state from params
        state = self._build_sql_state(
            query=query,
            project_id=project_id,
            db_schemas=db_schemas,
            is_followup=is_followup,
            previous_sql=previous_sql,
            histories=histories,
            configuration=configuration,
            should_execute=should_execute if should_execute is not None else self._should_execute_by_default,
            max_correction_retries=self._max_sql_correction_retries,
            context=context,
        )

        # Get workflow
        workflow = self._base_workflow.get("sql_processing")
        if not workflow:
            raise ValueError("SQL processing workflow not found")

        # Ensure graph is built
        if workflow.compiled_graph is None:
            workflow.build()

        # Execute and return
        return await workflow.execute(state)

    async def execute_assistance(
        self,
        query: str,
        project_id: str,
        intent: Optional[str] = None,
        db_schemas: Optional[List[str]] = None,
        histories: Optional[List[Dict[str, str]]] = None,
        configuration: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute assistance/visualization workflow directly - just pass params!

        Args:
            query: User query
            project_id: Project ID
            intent: Intent type - GENERAL or USER_GUIDE (optional)
            db_schemas: Database schemas (optional)
            histories: Query histories (optional)
            configuration: Configuration dict (optional)
            context: Additional context (optional)

        Returns:
            Assistance result with fields:
            - assistance_response: Natural language response
            - assistance_reasoning: Why this response was generated
            - chart_schema: Chart configuration (if visualization)
            - vega_schema: Vega-Lite spec (if visualization)
        """
        # Build state from params
        state = self._build_assistance_state(
            query=query,
            project_id=project_id,
            intent=intent,
            db_schemas=db_schemas,
            histories=histories,
            configuration=configuration,
            context=context,
        )

        # Get workflow
        workflow = self._base_workflow.get("assistance_visualization")
        if not workflow:
            raise ValueError("Assistance/visualization workflow not found")

        # Ensure graph is built
        if workflow.compiled_graph is None:
            workflow.build()

        # Execute and return
        return await workflow.execute(state)

    async def execute_workflow_by_name(
        self,
        workflow_name: str,
        state: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Execute any workflow by name with custom state.

        Args:
            workflow_name: Name of workflow (intent_recommendation, sql_processing, assistance_visualization)
            state: Complete state dictionary

        Returns:
            Workflow execution result
        """
        # Get workflow
        workflow = self._base_workflow.get(workflow_name)
        if not workflow:
            raise ValueError(f"Workflow '{workflow_name}' not found")

        # Ensure graph is built
        if workflow.compiled_graph is None:
            workflow.build()

        # Execute
        return await workflow.execute(state)