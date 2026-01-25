import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse

from src.web.constants.config import ERROR_MESSAGES, SRC_LOG_LEVELS
from src.web.services import (
    AskService,
    AskRequest,
    AskResponse,
    AskResultResponse,
    StopAskResponse,
)
from src.web.utils.auth import get_verified_user

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["API"])

router = APIRouter()

# Global ask service instance (will be initialized in main.py)
_ask_service: Optional[AskService] = None


def set_ask_service(service: AskService):
    """Set the global ask service instance."""
    global _ask_service
    _ask_service = service


def get_ask_service() -> AskService:
    """Get the global ask service instance."""
    if _ask_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Ask service not initialized"
        )
    return _ask_service


@router.post("/", response_model=AskResponse)
async def ask_question(
    request: AskRequest,
    current_user=Depends(get_verified_user)
):
    """
    Submit a question to the AI assistant.
    
    This endpoint processes user questions with intent classification and routing:
    - TEXT_TO_SQL: Generates and executes SQL queries
    - GENERAL: Provides general data assistance
    - USER_GUIDE: Provides user guide assistance
    - MISLEADING_QUERY: Handles misleading or unclear queries
    
    Returns a query_id that can be used to poll for results.
    """
    try:
        service = get_ask_service()
        
        # TODO: Get db_schemas from user's connections/projects
        db_schemas = []
        
        # TODO: Build context with generator, retriever, etc.
        context = {}
        
        response = await service.ask(
            request=request,
            db_schemas=db_schemas,
            context=context
        )
        
        log.info(f"Ask request submitted by user {current_user.id}: query_id={response.query_id}")
        return response
        
    except Exception as e:
        log.error(f"Error processing ask request for user {current_user.id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.INTERNAL_SERVER_ERROR
        )


@router.get("/{query_id}", response_model=AskResultResponse)
async def get_ask_result(
    query_id: str,
    current_user=Depends(get_verified_user)
):
    """
    Get the result of a previously submitted question.
    
    Poll this endpoint to get the current status and results of your query.
    
    Status values:
    - understanding: Initial processing
    - classifying: Classifying intent
    - searching: Searching for relevant data
    - planning: Planning SQL generation
    - generating: Generating SQL
    - correcting: Correcting SQL errors
    - finished: Query completed successfully
    - failed: Query failed
    - stopped: Query was stopped by user
    """
    try:
        service = get_ask_service()
        result = await service.get_result(query_id)
        
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Query not found or expired"
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error fetching ask result {query_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.INTERNAL_SERVER_ERROR
        )


@router.post("/{query_id}/stop", response_model=StopAskResponse)
async def stop_ask_query(
    query_id: str,
    current_user=Depends(get_verified_user)
):
    """
    Stop a running query.
    
    This will mark the query as stopped and prevent further processing.
    """
    try:
        service = get_ask_service()
        response = await service.stop(query_id)
        
        log.info(f"Query {query_id} stopped by user {current_user.id}")
        return response
        
    except Exception as e:
        log.error(f"Error stopping query {query_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.INTERNAL_SERVER_ERROR
        )

