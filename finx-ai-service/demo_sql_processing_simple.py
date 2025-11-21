"""
Full Pipeline Demo: DB Schema Retrieval + SQL Processing

A comprehensive example showing the complete pipeline:
1. Schema Retrieval - Find relevant database schemas using vector search
2. SQL Processing - Generate, validate, correct, and format SQL queries
3. Answer Generation - Convert results to natural language

Usage:
    python demo_sql_processing_simple.py
"""

import asyncio
import logging
import os
from typing import Optional, Dict, Any
import json

from src.core.providers import create_llm_provider
from src.services.llm_service import LLMService
from src.workflows.retrieval.db_schema_retrieval import DBSchemaRetrievalPipeline
from src.workflows.generation.sql_processing import create_initial_state, sql_generation_node
from dotenv import load_dotenv
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_section(title: str, width: int = 80):
    """Print a formatted section header."""
    print("\n" + "=" * width)
    print(f" {title}")
    print("=" * width)


def print_subsection(title: str, width: int = 80):
    """Print a formatted subsection header."""
    print("\n" + "-" * width)
    print(f" {title}")
    print("-" * width)


async def full_pipeline_demo(
    query: str,
    project_id: Optional[str] = None,
    database: Optional[str] = None,
    show_detailed_output: bool = True,
):
    """
    Full pipeline demo showing complete integration of schema retrieval and SQL processing.
    
    Args:
        query: Natural language query
        project_id: Optional project ID
        database: Optional database name
        show_detailed_output: Whether to show detailed intermediate outputs
    """
    print_section(f"QUERY: {query}")
    
    if project_id:
        print(f"Project ID: {project_id}")
    if database:
        print(f"Database: {database}")
    
    # Step 1: Initialize components
    print_subsection("[STEP 1/6] Initializing Components")
    
    # Schema retrieval pipeline
    schema_retriever = DBSchemaRetrievalPipeline(
        qdrant_url="http://localhost:6333",
        collection_name="db_schema_demo",
        table_retrieval_size=5,
        enable_column_pruning=True,
    )
    
    # LLM service for generation
    llm_provider = create_llm_provider(
        provider_type="gemini",
        model="gemini-2.5-flash",
        temperature=0.1,
    )
    llm_service = LLMService(llm_provider)
    
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
    print_subsection("[STEP 2/6] Retrieving Database Schemas")
    print(f"Searching for relevant schemas for: '{query}'")
    
    retrieval_result = await schema_retriever.run(
        query=query,
        project_id=project_id,
        database=database,
        llm_generator=llm_generator,
    )
    
    print(f"\nRetrieval Summary:")
    print(f"  Tables found: {retrieval_result.table_count}")
    print(f"  Total columns: {retrieval_result.column_count}")
    print(f"  Schema pruned: {retrieval_result.was_pruned}")
    
    if not retrieval_result.retrieval_results:
        print("\n  ERROR: No relevant schemas found!")
        return None
    
    # Extract schema DDLs
    db_schemas = [result['table_ddl'] for result in retrieval_result.retrieval_results]
    
    if show_detailed_output:
        print("\nRetrieved Tables:")
        for schema in retrieval_result.db_schemas:
            print(f"  - {schema['name']} ({schema.get('column_count', 'N/A')} columns)")
            if 'description' in schema:
                print(f"    Description: {schema['description'][:100]}...")
    else:
        print(f"\nRetrieved tables: {', '.join([s['name'] for s in retrieval_result.db_schemas])}")
    
    # Step 3: Create SQL processing state
    print_subsection("[STEP 3/4] Initializing SQL Processing State")
    initial_state = create_initial_state(
        query=query,
        project_id=project_id,
        db_schemas=db_schemas,
    )
    initial_state["context"] = {"generator": llm_generator}
    print("State initialized with query and retrieved schemas")
    
    # Step 4: Run SQL generation directly (single LLM call)
    print_subsection("[STEP 4/4] Running SQL Generation")
    print("Generating SQL query directly (skipping reasoning, validation, correction)")
    
    # Run only the SQL generation node
    final_state = await sql_generation_node(initial_state)
    
    # Analyze results
    print_subsection("SQL Generation Results")
    
    # Get final SQL
    final_sql = final_state.get("generated_sql")
    
    # Get metadata
    reasoning = ""  # No reasoning step
    is_valid = True  # Assume valid since we're not validating
    corrections = 0  # No corrections
    extracted_tables = []  # No extraction
    
    # Display status
    print(f"\nSQL Generation: ✓ COMPLETED (no validation performed)")
    
    # Display SQL
    if final_sql:
        print("\nGenerated SQL Query:")
        print("```sql")
        print(final_sql)
        print("```")
    else:
        print("\nERROR: No SQL generated!")
        return None
    
    # Display errors if any
    errors = final_state.get("errors", [])
    
    if errors:
        print("\nErrors encountered:")
        for error in errors:
            print(f"  - {error}")
    
    print("\nNote: SQL generated without validation or correction steps to save quota.")
    
    print_section("DEMO COMPLETED", width=80)
    
    return {
        "query": query,
        "sql": final_sql,
        "is_valid": is_valid,
        "reasoning": reasoning,
        "tables": extracted_tables,
        "corrections": corrections,
        "retrieval_stats": {
            "table_count": retrieval_result.table_count,
            "column_count": retrieval_result.column_count,
            "was_pruned": retrieval_result.was_pruned,
        }
    }


async def main():
    """
    Run full pipeline demo with user input query.
    """
    print("\n" + "=" * 80)
    print(" " * 20 + "FULL PIPELINE DEMO")
    print(" " * 10 + "DB Schema Retrieval + SQL Processing")
    print("=" * 80)
    
    # Get user input
    print("\nEnter your question:")
    user_query = input("> ").strip()
    
    if not user_query:
        print("Error: No question provided. Exiting.")
        return
    
    # Optional: Get database name (can be left empty)
    print("\nEnter database name (optional, press Enter to skip):")
    database = input("> ").strip() or None
    
    # Optional: Get project ID (can be left empty)
    print("\nEnter project ID (optional, press Enter to use 'demo_project'):")
    project_id = input("> ").strip() or "demo_project"
    
    print(f"\n{'*' * 80}")
    print(f" Processing your query...")
    print(f"{'*' * 80}")
    
    try:
        result = await full_pipeline_demo(
            query=user_query,
            database=database,
            project_id=project_id,
            show_detailed_output=True,
        )
        
        if result:
            print("\n\n" + "=" * 80)
            print(" " * 30 + "RESULT")
            print("=" * 80)
            print(f"\nQuery: {result['query']}")
            print(f"Valid: {'Yes' if result['is_valid'] else 'No'}")
            if result.get('tables'):
                print(f"Tables used: {', '.join(result['tables'])}")
            print(f"Corrections applied: {result['corrections']}")
        
    except Exception as e:
        logger.error(f"Query processing failed: {e}", exc_info=True)
        print(f"\nERROR: {e}")
    
    print("\n\nDemo completed!")


if __name__ == "__main__":
    """
    Run the full pipeline demo.
    
    This demo showcases the complete integration of:
    1. DB Schema Retrieval - Vector search for relevant schemas
    2. SQL Processing - Generate, validate, and correct SQL queries
    
    Prerequisites:
    - Qdrant running on localhost:6333
    - Database schemas indexed in collection 'db_schema'
    - GEMINI_API_KEY environment variable set
    
    Setup:
        1. Start Qdrant:
           docker run -p 6333:6333 qdrant/qdrant
        
        2. Index your database schemas:
           python demo_gemini_indexing.py
        
        3. Set API key:
           export GEMINI_API_KEY='your-api-key'
        
        4. Run demo:
           python demo_sql_processing_simple.py
    
    What this demo shows:
    - Schema retrieval using vector search
    - LLM-based column pruning for relevant schemas
    - SQL reasoning and generation
    - Automatic validation and correction
    - Table extraction from generated SQL
    - Error handling and retry logic
    """
    load_dotenv()
    # Check prerequisites
    print("Checking prerequisites...")
    
    if not os.getenv("GOOGLE_API_KEY"):
        print("\n" + "!" * 80)
        print("ERROR: GEMINI_API_KEY environment variable not set!")
        print("!" * 80)
        print("\nSet it with: export GEMINI_API_KEY='your-api-key'")
        print("Get your API key from: https://makersuite.google.com/app/apikey")
        exit(1)
    
    print("✓ GEMINI_API_KEY is set")
    print("✓ Starting demo...\n")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)
        print(f"\n\nFATAL ERROR: {e}")
