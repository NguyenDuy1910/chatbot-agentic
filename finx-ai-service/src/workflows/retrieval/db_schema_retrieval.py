import logging
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass

import orjson
from langfuse.decorators import observe

from src.workflows.indexing.retrieval import DBSchemaRetriever, SearchMode

logger = logging.getLogger(__name__)


# System prompt for table/column selection
TABLE_COLUMNS_SELECTION_SYSTEM_PROMPT = """
### TASK ###
You are a highly skilled data analyst. Your goal is to examine the provided database schema, interpret the posed question, and identify the specific columns from the relevant tables required to construct an accurate SQL query.

The database schema includes tables, columns, primary keys, foreign keys, relationships, and any relevant constraints.

### INSTRUCTIONS ###
1. Carefully analyze the schema and identify the essential tables and columns needed to answer the question.
2. For each table, provide a clear and concise reasoning for why specific columns are selected.
3. List each reason as part of a step-by-step chain of thought, justifying the inclusion of each column.
4. The number of columns chosen must match the number of reasoning.
5. Final chosen columns must be only column names, don't prefix it with table names.
6. If the chosen column is a child column of a STRUCT type column, choose the parent column instead of the child column.

### FINAL ANSWER FORMAT ###
Please provide your response as a JSON object, structured as follows:

{
    "results": [
        {
            "table_selection_reason": "Reason for selecting tablename1",
            "table_contents": {
              "chain_of_thought_reasoning": [
                  "Reason 1 for selecting column1",
                  "Reason 2 for selecting column2",
                  ...
              ],
              "columns": ["column1", "column2", ...]
            },
            "table_name":"tablename1",
        },
        {
            "table_selection_reason": "Reason for selecting tablename2",
            "table_contents": {
              "chain_of_thought_reasoning": [
                  "Reason 1 for selecting column1",
                  "Reason 2 for selecting column2",
                  ...
              ],
              "columns": ["column1", "column2", ...]
            },
            "table_name":"tablename2"
        }
    ]
}

### ADDITIONAL NOTES ###
- Each table key must list only the columns relevant to answering the question.
- Provide a reasoning list (`chain_of_thought_reasoning`) for each table, explaining why each column is necessary.
- Provide the reason of selecting the table in (`table_selection_reason`) for each table.
- Be logical, concise, and ensure the output strictly follows the required JSON format.
- Match Column names with the definition in the database schema.
- Match Table names with the definition in the database schema.

Good luck!
"""

TABLE_COLUMNS_SELECTION_USER_PROMPT_TEMPLATE = """
### Database Schema ###

{% for db_schema in db_schemas %}
{{ db_schema }}
{% endfor %}

### INPUT ###
{{ question }}
"""


@dataclass
class RetrievalResult:
    """Result from schema retrieval."""
    db_schemas: List[Dict[str, Any]]
    retrieval_results: List[Dict[str, str]]  # table_name, table_ddl
    table_count: int
    column_count: int
    was_pruned: bool = False
    original_token_count: int = 0


class DBSchemaRetrievalPipeline:
    """Pipeline for retrieving relevant database schemas with optional LLM-based column pruning."""
    
    def __init__(
        self,
        qdrant_url: str = "http://localhost:6333",
        collection_name: str = "db_schema",
        gemini_api_key: Optional[str] = None,
        gemini_model: str = "models/text-embedding-004",
        table_retrieval_size: int = 10,
        enable_column_pruning: bool = True,
        context_window_size: int = 2000,
    ):
        self.table_retrieval_size = table_retrieval_size
        self.enable_column_pruning = enable_column_pruning
        self.context_window_size = context_window_size
        
        self.retriever = DBSchemaRetriever(
            qdrant_url=qdrant_url,
            collection_name=collection_name,
            gemini_api_key=gemini_api_key,
            gemini_model=gemini_model
        )
    
    @observe(name="DB Schema Retrieval Pipeline")
    async def run(
        self,
        query: str,
        project_id: Optional[str] = None,
        database: Optional[str] = None,
        tables: Optional[List[str]] = None,
        histories: Optional[List[str]] = None,
        llm_generator: Optional[Any] = None,
    ) -> RetrievalResult:
        combined_query = self._combine_query_with_history(query, histories)
        filters = self._build_filters(project_id, database)
        
        # Retrieve relevant tables
        if tables:
            search_results = await self._retrieve_specific_tables(tables, database, filters)
        else:
            search_results = await self.retriever.search(
                query=combined_query,
                limit=self.table_retrieval_size,
                mode=SearchMode.HYBRID,
                filters=filters, 
                min_score=0.2
            )
        
        if not search_results:
            return RetrievalResult(
                db_schemas=[],
                retrieval_results=[],
                table_count=0,
                column_count=0
            )
        
        db_schemas = self._build_db_schemas_from_results(search_results)
        initial_ddls, token_count = self._build_initial_ddls(db_schemas)
        
        # needs_pruning = (
        #     self.enable_column_pruning and
        #     token_count > self.context_window_size and
        #     llm_generator is not None
        # )
        needs_pruning = True
        
        if needs_pruning:
            try:
                selected_columns = await self._prune_columns_with_llm(
                    query=query,
                    db_schemas=db_schemas,
                    llm_generator=llm_generator
                )
                
                retrieval_results = []
                for schema in db_schemas:
                    table_name = schema['name']
                    columns = selected_columns.get(table_name, [])
                    if columns:
                        ddl = self._build_table_ddl(schema, selected_columns=set(columns))
                        retrieval_results.append({'table_name': table_name, 'table_ddl': ddl})
                
                was_pruned = True
            except Exception as e:
                logger.error(f"Error during column pruning: {e}", exc_info=True)
                retrieval_results = initial_ddls
                was_pruned = False
        else:
            retrieval_results = initial_ddls
            was_pruned = False
        
        return RetrievalResult(
            db_schemas=db_schemas,
            retrieval_results=retrieval_results,
            table_count=len(db_schemas),
            column_count=sum(len(schema.get('columns', [])) for schema in db_schemas),
            was_pruned=was_pruned,
            original_token_count=token_count
        )
    
    def _combine_query_with_history(self, query: str, histories: Optional[List[str]]) -> str:
        """Combine current query with previous queries for better context."""
        if not histories:
            return query
        return f"{chr(10).join(histories)}\n{query}"
    
    def _build_filters(self, project_id: Optional[str], database: Optional[str]) -> Optional[Dict[str, Any]]:
        """Build filters for retrieval."""
        filters = {}
        if project_id:
            filters['project_id'] = project_id
        if database:
            filters['database'] = database
        return filters if filters else None
    
    async def _retrieve_specific_tables(
        self, table_names: List[str], database: Optional[str], filters: Optional[Dict[str, Any]]
    ) -> List[Any]:
        """Retrieve specific tables by name."""
        results = []
        for table_name in table_names:
            table_results = await self.retriever.search_by_table_name(table_name=table_name, database=database)
            results.extend(table_results)
        return results
    
    def _build_db_schemas_from_results(self, search_results: List[Any]) -> List[Dict[str, Any]]:
        """Build structured DB schemas from search results."""
        return [
            {
                'name': result.table_name,
                'database': result.database,
                'type': result.table_type.upper(),
                'description': result.table_description,
                'columns': result.columns_metadata,
                'primary_keys': result.primary_keys,
                'foreign_keys': result.foreign_keys,
            }
            for result in search_results
        ]
    
    def _build_initial_ddls(self, db_schemas: List[Dict[str, Any]]) -> Tuple[List[Dict[str, str]], int]:
        """Build DDL statements for all schemas and estimate token count."""
        ddls = [
            {'table_name': schema['name'], 'table_ddl': self._build_table_ddl(schema)}
            for schema in db_schemas
        ]
        all_ddl_text = '\n'.join([d['table_ddl'] for d in ddls])
        token_count = len(all_ddl_text) // 4  # Rough estimate: 1 token ≈ 4 chars
        return ddls, token_count
    
    def _build_table_ddl(self, schema: Dict[str, Any], selected_columns: Optional[set] = None) -> str:
        """Build CREATE TABLE DDL statement."""
        table_name = schema['name']
        columns = schema.get('columns', [])
        
        if selected_columns:
            columns = [col for col in columns if col['name'] in selected_columns]
        
        column_defs = []
        for col in columns:
            col_def = f"  {col['name']} {col['type']}"
            if col.get('primary_key'):
                col_def += " PRIMARY KEY"
            if not col.get('nullable', True):
                col_def += " NOT NULL"
            if col.get('description'):
                col_def += f"  -- {col['description']}"
            column_defs.append(col_def)
        
        ddl = f"CREATE TABLE {table_name} (\n{','.join(column_defs)}\n);"
        
        if schema.get('description'):
            ddl = f"-- {schema['description']}\n{ddl}"
        
        return ddl
    
    async def _prune_columns_with_llm(
        self, query: str, db_schemas: List[Dict[str, Any]], llm_generator: Any
    ) -> Dict[str, List[str]]:
        """Use LLM to select relevant columns for each table."""
        schema_ddls = [self._build_table_ddl(schema) for schema in db_schemas]
        logger.info(f"Schema DDLs: {schema_ddls}")
        
        # Properly render the template by replacing Jinja2 placeholders
        schema_section = "\n\n".join(schema_ddls)
        prompt = f"""### Database Schema ###

{schema_section}

### INPUT ###
{query}
"""
        logger.info(f"LLM Prompt (first 10000 chars): {prompt[:10000]}")
        
        response = await llm_generator(
            prompt=prompt,
            system_prompt=TABLE_COLUMNS_SELECTION_SYSTEM_PROMPT,
            response_format={"type": "json_object"}
        )
        
        try:
            # Handle both dict and string response formats
            if isinstance(response, dict):
                response_text = response.get('replies', [''])[0] if 'replies' in response else str(response)
            else:
                response_text = str(response)
            
            # Clean up response if it's wrapped in markdown code blocks
            if response_text.strip().startswith('```'):
                # Remove markdown code block markers
                response_text = response_text.strip()
                if response_text.startswith('```json'):
                    response_text = response_text[7:]
                elif response_text.startswith('```'):
                    response_text = response_text[3:]
                if response_text.endswith('```'):
                    response_text = response_text[:-3]
                response_text = response_text.strip()
            
            logger.info(f"LLM Response (first 200 chars): {response_text[:10000]}")
            
            result = orjson.loads(response_text)
            return {
                table['table_name']: table['table_contents']['columns']
                for table in result['results']
            }
        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")
            # Safe error logging that handles both dict and string responses
            if isinstance(response, dict):
                raw_resp = response.get('replies', [''])[0][:500] if 'replies' in response else str(response)[:500]
            else:
                raw_resp = str(response)[:500]
            logger.error(f"Raw response: {raw_resp}")
            return {
                schema['name']: [col['name'] for col in schema.get('columns', [])]
                for schema in db_schemas
            }