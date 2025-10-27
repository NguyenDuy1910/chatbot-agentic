import logging
from typing import Any, Dict

from src.langgraph.nodes.base import node_error_handler, add_error
from src.graphs.question_recommend.state import QuestionRecommendState

logger = logging.getLogger(__name__)


@node_error_handler
async def generate_questions_node(state: QuestionRecommendState) -> Dict[str, Any]:
    """
    Generate questions using LLM.
    
    This node:
    1. Takes built prompt
    2. Calls LLM provider
    3. Stores raw response in state
    
    Args:
        state: Current pipeline state with prompt_text
        
    Returns:
        Updated state with raw_response
    """
    if state.get("status") == "failed":
        logger.warning("Skipping generation due to previous failure")
        return {"status": "failed"}
    
    logger.info("Generating questions using LLM")
    
    try:
        llm_provider = state.get("llm_provider")
        if not llm_provider:
            raise ValueError("LLM provider not available in state")
        
        generator = llm_provider.get_generator(
            system_prompt="You are an expert in data analysis and SQL query generation."
        )
        
        result = await generator(prompt=state.get("prompt_text", ""))
        
        raw_response = result.get("replies", ["{}"])[0]
        logger.info(f"LLM generation completed ({len(raw_response)} chars)")
        
        return {
            "raw_response": raw_response,
            "generation_metadata": {
                "model": llm_provider.get_model(),
                "response_length": len(raw_response),
            },
            "status": "normalizing",
            "current_step": "generate_questions",
        }
    except Exception as e:
        logger.error(f"Question generation failed: {str(e)}")
        return add_error(state, f"Question generation failed: {str(e)}")


__all__ = [
    "generate_questions_node",
]

