"""
Normalize Response Node for Question Recommendation Graph.
"""

import logging
import orjson
import re
from typing import Any, Dict

from src.langgraph.nodes.base import node_error_handler, add_error
from src.graphs.question_recommend.state import QuestionRecommendState

logger = logging.getLogger(__name__)


@node_error_handler
async def normalize_response_node(state: QuestionRecommendState) -> Dict[str, Any]:
    """
    Normalize and parse LLM response.
    
    This node:
    1. Takes raw LLM response
    2. Extracts JSON from response
    3. Parses and validates structure
    4. Stores normalized questions in state
    
    Args:
        state: Current pipeline state with raw_response
        
    Returns:
        Updated state with questions
    """
    if state.get("status") == "failed":
        logger.warning("Skipping normalization due to previous failure")
        return {"status": "failed"}
    
    logger.info("Normalizing LLM response")
    
    try:
        raw_response = state.get("raw_response", "{}")
        
        # Try to extract JSON from markdown code blocks if present
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', raw_response, re.DOTALL)
        if json_match:
            raw_response = json_match.group(1)
            logger.info("Extracted JSON from code block")
        
        # Clean up the response
        raw_response = raw_response.replace("\n", " ")
        raw_response = " ".join(raw_response.split())
        
        # Parse JSON
        try:
            parsed = orjson.loads(raw_response.strip())
            logger.info(f"Successfully parsed JSON with {len(parsed.get('questions', []))} questions")
        except orjson.JSONDecodeError as e:
            logger.error(f"JSON parsing failed: {e}")
            logger.error(f"Failed text: {raw_response[:500]}")
            parsed = {"questions": []}
        
        # Validate structure
        questions = parsed.get("questions", [])
        if not isinstance(questions, list):
            logger.warning("Questions field is not a list, converting")
            questions = [questions] if questions else []
        
        return {
            "questions": questions,
            "normalized_response": parsed,
            "status": "completed",
            "current_step": "normalize_response",
        }
    except Exception as e:
        logger.error(f"Response normalization failed: {str(e)}")
        return add_error(state, f"Response normalization failed: {str(e)}")


__all__ = [
    "normalize_response_node",
]

