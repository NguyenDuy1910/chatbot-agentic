import logging
from typing import Any, Dict, List

import orjson
from langchain_core.prompts import PromptTemplate
from langfuse.decorators import observe
from pydantic import BaseModel

from src.workflows.common import clean_up_new_lines
from src.utils import trace_cost

logger = logging.getLogger("finx-ai-service")


system_prompt = """
You are an expert in data analysis and SQL query generation. Given a data model specification, optionally a user's question, and a list of categories, your task is to generate insightful, specific questions that can be answered using the provided data model. Each question should be accompanied by a brief explanation of its relevance or importance.

### JSON Output Structure

Output all questions in the following JSON format:

```json
{
    "questions": [
        {
            "question": "<generated question>",
            "category": "<category of the question>"
        },
        ...
    ]
}
```

### Guidelines for Generating Questions

1. **If Categories Are Provided:**

   - **Randomly select categories** from the list and ensure no single category dominates the output.
   - Ensure a balanced distribution of questions across all provided categories.
   - For each generated question, **randomize the category selection** to avoid a fixed order.

2. **Incorporate Diverse Analysis Techniques:**

   - Use a mix of the following analysis techniques for each category:
     - **Drill-down:** Delve into detailed levels of data.
     - **Roll-up:** Aggregate data to higher levels.
     - **Slice and Dice:** Analyze data from different perspectives.
     - **Trend Analysis:** Identify patterns or changes over time.
     - **Comparative Analysis:** Compare segments, groups, or time periods.

3. **If a User Question is Provided:**

   - Generate questions that are closely related to the user's previous question, ensuring that the new questions build upon or provide deeper insights into the original query.
   - Use **random category selection** to introduce diverse perspectives while maintaining a focus on the context of the previous question.
   - Apply the analysis techniques above to enhance the relevance and depth of the generated questions.

4. **If No User Question is Provided:**

   - Ensure questions cover different aspects of the data model.
   - Randomly distribute questions across all categories to ensure variety.

5. **General Guidelines for All Questions:**
   - Ensure questions can be answered using the data model.
   - Mix simple and complex questions.
   - Avoid open-ended questions - each should have a definite answer.
   - Incorporate time-based analysis where relevant.
   - Combine multiple analysis techniques when appropriate for deeper insights.

### Categories of Questions

1. **Descriptive Questions**  
   Summarize historical data.
   - Example: _"What was the total sales volume for each product last quarter?"_

2. **Segmentation Questions**  
   Identify meaningful data segments.
   - Example: _"Which customer segments contributed most to revenue growth?"_

3. **Comparative Questions**  
   Compare data across segments or periods.
   - Example: _"How did Product A perform compared to Product B last year?"_

4. **Data Quality/Accuracy Questions**  
   Assess data reliability and completeness.
   - Example: _"Are there inconsistencies in the sales records for Q1?"_
"""

user_prompt_template = """{previous_questions_section}

{categories_section}

Data Model:
{db_schemas}

Please generate {max_questions} insightful questions.
"""


class QuestionRecommendationResult(BaseModel):
    questions: List[Dict[str, str]]


QUESTION_RECOMMENDATION_MODEL_KWARGS = {
    "response_format": {
        "type": "json_schema",
        "json_schema": {
            "name": "question_recommendation",
            "schema": QuestionRecommendationResult.model_json_schema(),
        },
    }
}


# @observe(name="Question Recommendation Node")  # Disabled for demo
async def question_recommendation_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate recommended questions based on database schema.
    
    This node:
    1. Builds prompt with database schemas and optional context
    2. Generates recommended questions using LLM
    3. Categorizes questions
    
    Args:
        state: Current graph state containing db_schemas, query, etc.
        
    Returns:
        Updated state with recommended_questions
    """
    logger.info("Running question recommendation node...")
    state["current_step"] = "question_recommendation"
    
    try:
        # Extract inputs from state
        db_schemas = state.get("db_schemas", [])
        query = state.get("query", "")
        intent = state.get("intent", "TEXT_TO_SQL")
        categories = state.get("categories", [
            "Descriptive Questions",
            "Segmentation Questions",
            "Comparative Questions",
            "Data Quality/Accuracy Questions"
        ])
        max_questions = state.get("metadata", {}).get("max_questions", 5)
        
        # Check if we have pipeline components
        context = state.get("context", {})
        generator = context.get("generator")
        
        if not generator:
            # DEMO MODE: Generate simple sample questions
            logger.info("Running in demo mode (no pipeline) - generating sample questions")
            
            sample_questions = []
            if intent == "TEXT_TO_SQL":
                sample_questions = [
                    {"category": "Descriptive", "question": "What is the total number of customers in the database?"},
                    {"category": "Comparative", "question": "How do sales compare across different regions?"},
                    {"category": "Segmentation", "question": "Which customer segment has the highest average order value?"},
                    {"category": "Trends", "question": "What are the monthly sales trends for this year?"},
                    {"category": "Data Quality", "question": "Are there any customers with missing contact information?"}
                ]
            elif intent == "USER_GUIDE":
                sample_questions = [
                    {"category": "Getting Started", "question": "How do I write a basic SELECT query?"},
                    {"category": "Joins", "question": "How can I join multiple tables together?"},
                    {"category": "Aggregation", "question": "What are the common aggregate functions I can use?"},
                    {"category": "Filtering", "question": "How do I filter data with WHERE clauses?"},
                    {"category": "Best Practices", "question": "What are SQL query optimization tips?"}
                ]
            else:
                sample_questions = [
                    {"category": "General", "question": "What tables are available in this database?"},
                    {"category": "General", "question": "What kind of data does this database contain?"},
                    {"category": "General", "question": "How are the tables related to each other?"}
                ]
            
            state["recommended_questions"] = sample_questions[:max_questions]
            state["question_recommendation_reasoning"] = f"Generated {len(sample_questions[:max_questions])} sample questions for {intent} intent"
            logger.info(f"Demo mode: Generated {len(state['recommended_questions'])} sample questions")
            return state
        
        # FULL MODE: Use pipeline generator
        
        # Build prompt
        try:
            # Build sections conditionally
            previous_questions_section = ""
            if query:
                previous_questions_section = f"Previous Questions: {query}"
            
            categories_section = ""
            if categories:
                categories_section = f"Categories: {', '.join(categories)}"
            
            db_schemas_text = "\n".join(db_schemas)
            
            # Format prompt
            prompt_text = user_prompt_template.format(
                previous_questions_section=previous_questions_section,
                categories_section=categories_section,
                db_schemas=db_schemas_text,
                max_questions=max_questions,
            )
            prompt_text = clean_up_new_lines(prompt_text)
        except Exception as e:
            logger.error(f"Error building prompt template: {e}")
            raise
        
        # Generate recommendations
        recommendation_result = await generator(
            prompt=prompt_text,
            system_prompt=system_prompt,
            response_format=QUESTION_RECOMMENDATION_MODEL_KWARGS.get("response_format")
        )
        
        # Post-process results
        try:
            results = orjson.loads(recommendation_result.get("replies")[0])
            state["recommended_questions"] = results.get("questions", [])
            logger.info(f"Generated {len(state['recommended_questions'])} recommended questions")
        except Exception as e:
            logger.warning(f"Failed to parse question recommendations: {e}")
            state["recommended_questions"] = []
            state["warnings"].append(f"Failed to parse question recommendations: {str(e)}")
        
    except Exception as e:
        logger.error(f"Error in question recommendation node: {e}")
        state["errors"].append(f"Question recommendation failed: {str(e)}")
        state["recommended_questions"] = []
    
    return state

