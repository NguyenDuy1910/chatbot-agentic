import logging
from typing import Any, Dict

from src.langgraph.nodes.base import node_error_handler, add_error
from src.graphs.question_recommend.state import QuestionRecommendState

logger = logging.getLogger(__name__)


@node_error_handler
async def build_prompt_node(state: QuestionRecommendState) -> Dict[str, Any]:
    """
    Build prompt for question generation.
    
    This node:
    1. Takes context documents and parameters
    2. Builds prompt using template
    3. Stores prompt in state
    
    Args:
        state: Current pipeline state with contexts and parameters
        
    Returns:
        Updated state with prompt_text
    """
    logger.info("Building prompt for question recommendation")
    
    try:
        from haystack.components.builders.prompt_builder import PromptBuilder
        
        # Define prompt template
        user_prompt_template = """
{% if previous_questions %}
Previous Questions: {{previous_questions}}
{% endif %}

{% if categories %}
Categories: {{categories}}
{% endif %}

{% if documents %}
### DATABASE SCHEMA ###
{% for document in documents %}
    {{ document }}
{% endfor %}
{% endif %}

Please generate {{max_questions}} insightful questions for each of the {{max_categories}} categories based on the provided data model. Both the questions and category names should be translated into {{language}}. The output format should maintain the structure but with localized text.
"""
        
        prompt_builder = PromptBuilder(template=user_prompt_template)
        
        result = prompt_builder.run(
            documents=state.get("contexts", []),
            previous_questions=state.get("previous_questions", []),
            categories=state.get("categories", []),
            language=state.get("language", "en"),
            max_questions=state.get("max_questions", 5),
            max_categories=state.get("max_categories", 3),
        )
        
        prompt_text = result.get("prompt", "")
        logger.info(f"Prompt built successfully ({len(prompt_text)} chars)")
        
        return {
            "prompt_text": prompt_text,
            "prompt_variables": {
                "language": state.get("language", "en"),
                "max_questions": state.get("max_questions", 5),
                "max_categories": state.get("max_categories", 3),
            },
            "status": "generating",
            "current_step": "build_prompt",
        }
    except Exception as e:
        logger.error(f"Prompt building failed: {str(e)}")
        return add_error(state, f"Prompt building failed: {str(e)}")


__all__ = [
    "build_prompt_node",
]

