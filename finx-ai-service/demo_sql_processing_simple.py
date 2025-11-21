"""
Simple SQL Processing Demo

A minimal example showing how to use DB Schema Retrieval and SQL Processing together.

Usage:
    python demo_sql_processing_simple.py
"""

import asyncio
import logging
import os
from typing import Optional

from src.core.providers import create_llm_provider
from src.services.llm_service import LLMService
from src.workflows.retrieval.db_schema_retrieval import DBSchemaRetrievalPipeline
from src.workflows.generation.sql_processing import create_graph, create_initial_state

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def simple_demo(
    query: str,
    project_id: Optional[str] = None,
    database: Optional[str] = None,
):
    """
    Simple demo showing the complete pipeline.
    
    Args:
        query: Natural language query
        project_id: Optional project ID
        database: Optional database name
    """
    print("\n" + "=" * 60)
    print(f"Query: {query}")
    print("=" * 60)
    
    # Step 1: Initialize components
    print("\n[1/5] Initializing components...")
    
    # Schema retrieval pipeline
    schema_retriever = DBSchemaRetrievalPipeline(
        qdrant_url="http://localhost:6333",
        collection_name="db_schema",
        table_retrieval_size=5,
        enable_column_pruning=True,
    )
    
    # LLM service for generation
    llm_provider = create_llm_provider(
        provider_type="gemini",
        model="gemini-2.0-flash-exp",
        temperature=0.1,
    )
    llm_service = LLMService(llm_provider)
    
    # SQL processing graph
    sql_graph = create_graph()
    
    # Create LLM generator function
    async def llm_generator(prompt, system_prompt=None, response_format=None, **kwargs):
        response = await llm_service.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            response_format=response_format,
            **kwargs
        )
        return {"replies": [response]}
    
    # Step 2: Retrieve relevant database schemas
    print("\n[2/5] Retrieving database schemas...")
    retrieval_result = await schema_retriever.run(
        query=query,
        project_id=project_id,
        database=database,
        llm_generator=llm_generator,
    )
    
    print(f"  Retrieved {retrieval_result.table_count} table(s)")
    print(f"  Total columns: {retrieval_result.column_count}")
    print(f"  Schema pruned: {retrieval_result.was_pruned}")
    
    if not retrieval_result.retrieval_results:
        print("\n  ERROR: No relevant schemas found!")
        return
    
    # Extract schema DDLs
    db_schemas = [result['table_ddl'] for result in retrieval_result.retrieval_results]
    
    print("\n  Retrieved tables:")
    for schema in retrieval_result.db_schemas:
        print(f"    - {schema['name']}")
    
    # Step 3: Create SQL processing state
    print("\n[3/5] Creating SQL processing state...")
    initial_state = create_initial_state(
        query=query,
        project_id=project_id,
        db_schemas=db_schemas,
    )
    initial_state["context"] = {"generator": llm_generator}
    
    # Step 4: Run SQL processing workflow
    print("\n[4/5] Generating SQL query...")
    final_state = await sql_graph.ainvoke(initial_state)
    
    # Step 5: Display results
    print("\n[5/5] Results:")
    print("-" * 60)
    
    # Get final SQL
    final_sql = (
        final_state.get("corrected_sql") or
        final_state.get("regenerated_sql") or
        final_state.get("generated_sql")
    )
    
    # Get reasoning
    reasoning = final_state.get("sql_reasoning", "")
    
    # Display
    is_valid = final_state.get("is_valid_sql", False)
    print(f"\nValid SQL: {is_valid}")
    
    if final_sql:
        print("\nGenerated SQL:")
        print("```sql")
        print(final_sql)
        print("```")
    else:
        print("\nNo SQL generated!")
    
    if reasoning:
        print("\nReasoning:")
        print(reasoning[:300] + "..." if len(reasoning) > 300 else reasoning)
    
    # Show corrections if any
    corrections = final_state.get("correction_attempts", 0)
    if corrections > 0:
        print(f"\nCorrection attempts: {corrections}")
    
    # Show extracted tables
    extracted_tables = final_state.get("extracted_tables", [])
    if extracted_tables:
        print(f"\nExtracted tables: {', '.join(extracted_tables)}")
    
    # Show errors if any
    errors = final_state.get("errors", [])
    if errors:
        print("\nErrors:")
        for error in errors:
            print(f"  - {error}")
    
    validation_errors = final_state.get("validation_errors", [])
    if validation_errors and not is_valid:
        print("\nValidation errors:")
        for error in validation_errors:
            print(f"  - {error}")
    
    print("\n" + "=" * 60)


async def main():
    """
    Run simple demos with different query types.
    """
    print("\n" + "=" * 60)
    print("SIMPLE SQL PROCESSING DEMO")
    print("=" * 60)
    
    # Example queries to demonstrate
    queries = [
        {
            "query": "Show me all customers from California",
            "database": "customers",
            "description": "Simple SELECT with WHERE clause"
        },
        {
            "query": "What are the top 5 products by sales?",
            "database": "sales",
            "description": "Aggregation with ORDER BY and LIMIT"
        },
        {
            "query": "Count how many orders were placed last month",
            "database": "orders",
            "description": "COUNT with date filtering"
        },
    ]
    
    for i, example in enumerate(queries, 1):
        print(f"\n\nExample {i}: {example['description']}")
        
        try:
            await simple_demo(
                query=example["query"],
                database=example.get("database"),
                project_id="demo_project",
            )
        except Exception as e:
            logger.error(f"Example {i} failed: {e}", exc_info=True)
            print(f"\nError: {e}")
    
    print("\n\nDemo completed!")


if __name__ == "__main__":
    """
    Run the simple demo.
    
    Prerequisites:
    - Qdrant running on localhost:6333
    - Database schemas indexed in collection 'db_schema'
    - GEMINI_API_KEY environment variable set
    
    To run:
        python demo_sql_processing_simple.py
    """
    
    # Check if API key is set
    if not os.getenv("GEMINI_API_KEY"):
        print("WARNING: GEMINI_API_KEY environment variable not set!")
        print("Set it with: export GEMINI_API_KEY='your-api-key'")
    
    asyncio.run(main())
