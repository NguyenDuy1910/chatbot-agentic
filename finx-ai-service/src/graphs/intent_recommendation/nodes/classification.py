import ast
import logging
from typing import Any, Dict, Literal, Optional, List

import orjson
from langchain_core.prompts import PromptTemplate
from langfuse.decorators import observe
from pydantic import BaseModel

from src.graphs.common import build_table_ddl, clean_up_new_lines
# from src.graphs.generation.utils.sql import construct_instructions
from src.utils import trace_cost
# from src.web.v1.services import Configuration
# from src.web.v1.services.ask import AskHistory

logger = logging.getLogger("finx-ai-service")


# Temporary helper function (placeholder for construct_instructions)
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
- The user's inputs pertains to Wren AI's features, usage, or capabilities.
- The query relates directly to content in the user guide.

**Examples:**  
- "What can Wren AI do?"
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
        has_pipeline = all(k in context for k in ["embedder", "generator"])
        
        if not has_pipeline:
            # DEMO MODE: Simple classification using direct LLM call
            logger.info("Running in demo mode (no pipeline) - using simple classification")
            
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
        
        # FULL MODE: Use pipeline components
        embedder = context.get("embedder")
        table_retriever = context.get("table_retriever")
        dbschema_retriever = context.get("dbschema_retriever")
        generator = context.get("generator")
        wren_ai_docs = context.get("wren_ai_docs", [])
        
        # Step 1: Generate embedding
        previous_query_summaries = (
            [history.get("question", "") for history in histories] if histories else []
        )
        combined_query = "\n".join(previous_query_summaries) + "\n" + query
        embedding_result = await embedder.run(combined_query)
        
        # Step 2: Retrieve relevant tables
        table_filters = {
            "operator": "AND",
            "conditions": [
                {"field": "type", "operator": "==", "value": "TABLE_DESCRIPTION"},
            ],
        }
        if project_id:
            table_filters["conditions"].append(
                {"field": "project_id", "operator": "==", "value": project_id}
            )
        
        table_results = await table_retriever.run(
            query_embedding=embedding_result.get("embedding"),
            filters=table_filters,
        )
        
        # Step 3: Retrieve database schemas
        tables = table_results.get("documents", [])
        table_names = []
        for table in tables:
            content = ast.literal_eval(table.content)
            table_names.append(content["name"])
        
        logger.info(f"Retrieved table names: {table_names}")
        
        table_name_conditions = [
            {"field": "name", "operator": "==", "value": table_name}
            for table_name in table_names
        ]
        
        dbschema_filters = {
            "operator": "AND",
            "conditions": [
                {"field": "type", "operator": "==", "value": "TABLE_SCHEMA"},
                {"operator": "OR", "conditions": table_name_conditions},
            ],
        }
        if project_id:
            dbschema_filters["conditions"].append(
                {"field": "project_id", "operator": "==", "value": project_id}
            )
        
        dbschema_results = await dbschema_retriever.run(
            query_embedding=embedding_result.get("embedding"),
            filters=dbschema_filters
        )
        
        # Step 4: Construct DB schemas in DDL format
        db_schemas_dict = {}
        for document in dbschema_results["documents"]:
            content = ast.literal_eval(document.content)
            if content["type"] == "TABLE":
                if document.meta["name"] not in db_schemas_dict:
                    db_schemas_dict[document.meta["name"]] = content
                else:
                    db_schemas_dict[document.meta["name"]] = {
                        **content,
                        "columns": db_schemas_dict[document.meta["name"]].get("columns", []),
                    }
            elif content["type"] == "TABLE_COLUMNS":
                if document.meta["name"] not in db_schemas_dict:
                    db_schemas_dict[document.meta["name"]] = {"columns": content["columns"]}
                else:
                    if "columns" not in db_schemas_dict[document.meta["name"]]:
                        db_schemas_dict[document.meta["name"]]["columns"] = content["columns"]
                    else:
                        db_schemas_dict[document.meta["name"]]["columns"] += content["columns"]
        
        # Remove incomplete schemas
        db_schemas_dict = {k: v for k, v in db_schemas_dict.items() if "type" in v and "columns" in v}
        
        db_schemas_in_ddl = []
        for table_schema in list(db_schemas_dict.values()):
            if table_schema["type"] == "TABLE":
                ddl, _, _ = build_table_ddl(table_schema)
                db_schemas_in_ddl.append(ddl)
        
        # Step 5: Build prompt
        prompt_template = PromptTemplate.from_template(intent_classification_user_prompt_template)
        language = configuration.get("language", "English") if isinstance(configuration, dict) else getattr(configuration, "language", "English")
        
        prompt_text = prompt_template.format(
            query=query,
            language=language,
            db_schemas=db_schemas_in_ddl,
            histories=histories,
            sql_samples=state.get("sql_samples", []),
            instructions=construct_instructions(instructions=state.get("instructions", [])),
            docs=wren_ai_docs,
        )
        prompt_text = clean_up_new_lines(prompt_text)
        
        # Step 6: Classify intent
        classification_result = await generator(prompt=prompt_text)
        
        # Step 7: Post-process results
        try:
            results = orjson.loads(classification_result.get("replies")[0])
            state["rephrased_question"] = results["rephrased_question"]
            state["intent"] = results["results"]
            state["intent_reasoning"] = results["reasoning"]
        except Exception as e:
            logger.warning(f"Failed to parse intent classification result: {e}, defaulting to TEXT_TO_SQL")
            state["rephrased_question"] = query
            state["intent"] = "TEXT_TO_SQL"
            state["intent_reasoning"] = "Failed to classify intent"
        
        state["db_schemas"] = db_schemas_in_ddl
        state["retrieved_tables"] = table_names
        state["classification_prompt"] = prompt_text
        
        logger.info(f"Intent classified as: {state['intent']}")
        
    except Exception as e:
        logger.error(f"Error in intent classification node: {e}")
        state["errors"].append(f"Intent classification failed: {str(e)}")
        state["intent"] = "TEXT_TO_SQL"  # Default fallback
        state["rephrased_question"] = state.get("query", "")
    
    return state

