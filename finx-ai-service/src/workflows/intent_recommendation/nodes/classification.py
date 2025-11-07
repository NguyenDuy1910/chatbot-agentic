import ast
import logging
from typing import Any, Dict, Literal, Optional, List

import orjson
from langchain_core.prompts import PromptTemplate
from langfuse.decorators import observe
from pydantic import BaseModel

from src.workflows.common import build_table_ddl, clean_up_new_lines
from src.utils import trace_cost

logger = logging.getLogger("finx-ai-service")


def construct_instructions(instructions: List[str]) -> str:
    """
    Temporary helper to construct instructions string.
    Replace with actual implementation when available.
    """
    if not instructions:
        return ""
    return "\n".join(f"- {inst}" for inst in instructions)


intent_classification_system_prompt = """
### Task ###
You are an expert detective specializing in intent classification. Combine the user's current question and previous questions to determine their true intent based on the provided database schema. Classify the intent into one of these categories: `MISLEADING_QUERY`, `TEXT_TO_SQL`, `GENERAL`, or `USER_GUIDE`. Additionally, provide a concise reasoning (maximum 20 words) for your classification.

### Instructions ###
- **Follow the user's previous questions:** If there are previous questions, try to understand the user's current question as following the previous questions.
- **Follow the user's instructions:** If there are instructions, strictly follow the instructions.
- **Consider Context of Inputs:** Combine the user's current question, their previous questions, and the user's instructions together to identify the user's true intent.
- **Rephrase Question:** Rewrite follow-up questions into full standalone questions using prior conversation context.
- **Concise Reasoning:** The reasoning must be clear, concise, and limited to 20 words.
- **Language Consistency:** Use the same language as specified in the user's output language for the rephrased question and reasoning.
- **Vague Queries:** If the question is vague or does not related to a table or property from the schema, classify it as `MISLEADING_QUERY`.
- **Incomplete Queries:** If the question is related to the database schema but references unspecified values (e.g., "the following", "these", "those") without providing them, classify as `GENERAL`.
- **Time-related Queries:** Don't rephrase time-related information in the user's question.

### Intent Definitions ###

<TEXT_TO_SQL>
**When to Use:**  
- The user's inputs are about modifying SQL from previous questions.
- The user's inputs are related to the database schema and requires an SQL query.
- The question (or related previous query) includes references to specific tables, columns, or data details.
- The question includes **complete information** with specific tables, columns, or data values needed for execution.
- The question provides **all necessary parameters** to generate executable SQL.

**Requirements:**
- Must have complete filter criteria, specific values, or clear references to previous context.
- Include specific table and column names from the schema in your reasoning or modifying SQL from previous questions.
- Reference phrases from the user's inputs that clearly relate to the schema.

**Examples:**  
- "What is the total sales for last quarter?"
- "Show me all customers who purchased product X."
- "List the top 10 products by revenue."
</TEXT_TO_SQL>

<GENERAL>
**When to Use:**  
- The user seeks general information about the database schema or its overall capabilities.
- The query references **missing information** (e.g., "the following items" without listing them).
- The query contains **placeholder references** that cannot be resolved from context.
- The query is **incomplete for SQL generation** despite mentioning database concepts.

**Requirements:**  
- Incorporate phrases from the user's inputs that indicate incompleteness or lack of relevance to the database schema.
- Identify missing parameters, unspecified references, or incomplete filter criteria.

**Examples:**
- "What is the dataset about?"
- "Tell me more about the database."
- "How can I analyze customer behavior with this data?"
- "Show me orders for these products" (without specifying which products)
- "Filter by the criteria I mentioned" (without previous context defining criteria)
</GENERAL>

<USER_GUIDE>
**When to Use:**  
- The user's inputs pertains to Finx AI's features, usage, or capabilities.
- The query relates directly to content in the user guide.

**Examples:**  
- "What can Finx AI do?"
- "How can I reset a project?"
- "How can I delete a project?"
- "How can I connect to other databases?"
- "How do I draw a chart?"
</USER_GUIDE>

<MISLEADING_QUERY>
**When to Use:**  
- The user's inputs is irrelevant to the database schema or includes SQL code.
- The user's inputs lacks specific details (like table names or columns) needed to generate an SQL query.
- It appears off-topic or is simply a casual conversation starter.

**Requirements:**  
- Incorporate phrases from the user's inputs that indicate lack of relevance to the database schema.

**Examples:**  
- "How are you?"
- "What's the weather like today?"
- "Tell me a joke."
</MISLEADING_QUERY>

### Output Format ###
Return your response as a JSON object with the following structure:

{
    "rephrased_question": "<rephrased question in full standalone question if there are previous questions, otherwise the original question>",
    "reasoning": "<brief chain-of-thought reasoning (max 20 words)>",
    "results": "MISLEADING_QUERY" | "TEXT_TO_SQL" | "GENERAL" | "USER_GUIDE"
}
"""

intent_classification_user_prompt_template = """
### DATABASE SCHEMA ###
{% for db_schema in db_schemas %}
    {{ db_schema }}
{% endfor %}

{% if sql_samples %}
### SQL SAMPLES ###
{% for sql_sample in sql_samples %}
Question:
{{sql_sample.question}}
SQL:
{{sql_sample.sql}}
{% endfor %}
{% endif %}

{% if instructions %}
### USER INSTRUCTIONS ###
{% for instruction in instructions %}
{{ loop.index }}. {{ instruction }}
{% endfor %}
{% endif %}

### USER GUIDE ###
{% for doc in docs %}
- {{doc.path}}: {{doc.content}}
{% endfor %}

### INPUT ###
{% if histories %}
User's previous questions:
{% for history in histories %}
Question:
{{ history.question }}
SQL:
{{ history.sql }}
{% endfor %}
{% endif %}

User's current question: {{query}}
Output Language: {{ language }}

Let's think step by step
"""


class IntentClassificationResult(BaseModel):
    rephrased_question: str
    results: Literal["MISLEADING_QUERY", "TEXT_TO_SQL", "GENERAL", "USER_GUIDE"]
    reasoning: str


INTENT_CLASSIFICATION_MODEL_KWARGS = {
    "response_format": {
        "type": "json_schema",
        "json_schema": {
            "name": "intent_classification",
            "schema": IntentClassificationResult.model_json_schema(),
        },
    }
}


# @observe(name="Intent Classification Node")  # Disabled for demo
async def intent_classification_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Classify user intent based on query and database schema.
    
    This node:
    1. Retrieves relevant database schemas using embeddings
    2. Constructs prompts with schema, history, and instructions
    3. Classifies intent using LLM
    4. Rephrases question if needed
    
    Args:
        state: Current graph state containing query, project_id, histories, etc.
        
    Returns:
        Updated state with intent, rephrased_question, intent_reasoning, and db_schemas
    """
    logger.info("Running intent classification node...")
    state["current_step"] = "intent_classification"
    
    try:
        # Extract inputs from state
        query = state.get("query", "")
        project_id = state.get("project_id")
        histories = state.get("histories", [])
        configuration = state.get("configuration", {})
        db_schemas = state.get("db_schemas", [])
        
        # Check if we have pipeline components (for full mode) or run in simple demo mode
        context = state.get("context", {})
        generator = context.get("generator")
        
        # For intent classification, we only need generator (not embedder/retrievers)
        if not generator:
            # DEMO MODE: Simple classification using keyword-based logic
            logger.info("Running in demo mode (no generator) - using simple classification")
            
            # Simple intent classification logic based on keywords
            query_lower = query.lower()
            
            # Check for misleading queries
            if any(word in query_lower for word in ["weather", "stock", "news", "sports", "movie"]):
                state["intent"] = "MISLEADING_QUERY"
                state["intent_reasoning"] = "Query is not related to database analysis"
                state["confidence_score"] = 0.95
            # Check for general/exploration queries
            elif any(phrase in query_lower for phrase in ["what data", "show me data", "what tables", "what can"]):
                state["intent"] = "GENERAL"
                state["intent_reasoning"] = "User wants to explore available data"
                state["confidence_score"] = 0.85
            # Check for user guide queries
            elif any(word in query_lower for word in ["how to", "how do", "help", "guide", "tutorial", "learn"]):
                state["intent"] = "USER_GUIDE"
                state["intent_reasoning"] = "User needs guidance or instructions"
                state["confidence_score"] = 0.90
            # Default to TEXT_TO_SQL for data queries
            else:
                state["intent"] = "TEXT_TO_SQL"
                state["intent_reasoning"] = "Query appears to request specific data analysis"
                state["confidence_score"] = 0.80
            
            state["rephrased_question"] = query
            state["classification_prompt"] = None
            logger.info(f"Demo mode classification: {state['intent']} ({state['confidence_score']:.0%})")
            return state
        
        # AI MODE: Use LLM for intent classification (simplified - no retrieval)
        logger.info("Using AI for intent classification (simplified mode - no retrieval)")
        
        # Build prompt manually (PromptTemplate doesn't support full Jinja2)
        language = configuration.get("language", "English") if isinstance(configuration, dict) else getattr(configuration, "language", "English")
        
        # Build sections
        db_schemas_section = "\n".join(f"    {schema}" for schema in db_schemas) if db_schemas else "    No database schemas provided"
        
        sql_samples_section = ""
        if state.get("sql_samples"):
            sql_samples_section = "### SQL SAMPLES ###\n"
            for sample in state.get("sql_samples", []):
                sql_samples_section += f"Question:\n{sample.get('question')}\nSQL:\n{sample.get('sql')}\n\n"
        
        instructions_section = ""
        if state.get("instructions"):
            instructions_section = "### USER INSTRUCTIONS ###\n"
            for i, inst in enumerate(state.get("instructions", []), 1):
                instructions_section += f"{i}. {inst}\n"
        
        docs_section = ""
        # No docs in simplified mode
        
        histories_section = ""
        if histories:
            histories_section = "User's previous questions:\n"
            for hist in histories:
                histories_section += f"Question:\n{hist.get('question')}\nSQL:\n{hist.get('sql', 'N/A')}\n\n"
        
        # Construct final prompt
        prompt_text = f"""### DATABASE SCHEMA ###
{db_schemas_section}

{sql_samples_section}

{instructions_section}

{docs_section}

### INPUT ###
{histories_section}

User's current question: {query}
Output Language: {language}

Let's think step by step
"""
        prompt_text = clean_up_new_lines(prompt_text)
        
        # Classify intent using AI
        classification_result = await generator(
            prompt=prompt_text,
            system_prompt=intent_classification_system_prompt,
            response_format=INTENT_CLASSIFICATION_MODEL_KWARGS.get("response_format")
        )
        
        # Post-process results
        try:
            results = orjson.loads(classification_result.get("replies")[0])
            state["rephrased_question"] = results["rephrased_question"]
            state["intent"] = results["results"]
            state["intent_reasoning"] = results["reasoning"]
            state["confidence_score"] = 0.9  # Default confidence for AI classification
        except Exception as e:
            logger.warning(f"Failed to parse intent classification result: {e}, defaulting to TEXT_TO_SQL")
            state["rephrased_question"] = query
            state["intent"] = "TEXT_TO_SQL"
            state["intent_reasoning"] = "Failed to classify intent"
            state["confidence_score"] = 0.5
        
        state["db_schemas"] = db_schemas
        state["retrieved_tables"] = []
        state["classification_prompt"] = prompt_text
        
        logger.info(f"AI classified intent as: {state['intent']} (confidence: {state.get('confidence_score', 0):.0%})")
        
    except Exception as e:
        logger.error(f"Error in intent classification node: {e}")
        state["errors"].append(f"Intent classification failed: {str(e)}")
        state["intent"] = "TEXT_TO_SQL"  # Default fallback
        state["rephrased_question"] = state.get("query", "")
    
    return state
