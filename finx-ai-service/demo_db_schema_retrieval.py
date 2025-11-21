"""
Demo: DB Schema Retrieval Pipeline
Shows step-by-step flow with real LLM and vector database
"""

import asyncio
import logging
import os
from typing import Dict, Any

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
from dotenv import load_dotenv
from src.workflows.retrieval.db_schema_retrieval import DBSchemaRetrievalPipeline
from src.core.providers.gemini_provider import GeminiProvider

# async def create_llm_generator():
#     """Create real LLM generator"""
#     from src.core.providers.llm_factory import LLMProviderFactory
    
#     print("\nInitializing LLM Provider...")
    
#     model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
#     print(f"Using model: {model_name}")
    
#     provider = LLMProviderFactory.create_provider(
#         provider_type="gemini",
#         api_key=os.getenv("GEMINI_API_KEY"),
#         model=model_name
#     )
    
#     async def llm_generator(prompt: str, system_prompt: str = None) -> Dict[str, Any]:
#         print("\n" + "="*80)
#         print("STEP 4: LLM COLUMN PRUNING")
#         print("="*80)
        
#         print(f"\nSystem Prompt Length: {len(system_prompt) if system_prompt else 0} chars")
#         print(f"User Prompt Length: {len(prompt)} chars")
#         print("\nCalling LLM to analyze schema and select relevant columns...")
        
#         messages = []
#         if system_prompt:
#             messages.append({"role": "system", "content": system_prompt})
#         messages.append({"role": "user", "content": prompt})
        
#         response = await provider.generate(
#             messages=messages,
#             temperature=0.0,
#             response_format={"type": "json_object"}
#         )
        
#         print(f"\nLLM Response received: {len(response.get('replies', [''])[0])} chars")
        
#         return response
    
#     return llm_generator


async def demo_basic_retrieval():
    """Demo 1: Basic retrieval without pruning"""
    print("\n")
    print("#" * 80)
    print("# DEMO 1: BASIC RETRIEVAL (NO COLUMN PRUNING)")
    print("#" * 80)
    
    pipeline = DBSchemaRetrievalPipeline(
        qdrant_url=os.getenv("QDRANT_URL", "http://localhost:6333"),
        collection_name=os.getenv("COLLECTION_NAME", "db_schema"),
        gemini_api_key=os.getenv("GEMINI_API_KEY"),
        table_retrieval_size=5,
        enable_column_pruning=False
    )
    
    query = "Show all customer transactions"
    
    print(f"\nQuery: '{query}'")
    print(f"Column Pruning: DISABLED")
    
    print("\n" + "="*80)
    print("STEP 1: SEMANTIC SEARCH FOR TABLES")
    print("="*80)
    
    result = await pipeline.run(query=query)
    
    print("\n" + "="*80)
    print("STEP 2: BUILD DB SCHEMAS")
    print("="*80)
    print(f"\nRetrieved {result.table_count} tables")
    print(f"Total columns: {result.column_count}")
    
    print("\n" + "="*80)
    print("FINAL RESULT (FULL SCHEMAS)")
    print("="*80)
    
    for i, retrieval in enumerate(result.retrieval_results, 1):
        print(f"\n--- Table {i}: {retrieval['table_name']} ---")
        print(retrieval['table_ddl'])


async def demo_with_column_pruning():
    """Demo 2: Retrieval with LLM column pruning"""
    print("\n")
    print("#" * 80)
    print("# DEMO 2: RETRIEVAL WITH LLM COLUMN PRUNING")
    print("#" * 80)
    
    pipeline = DBSchemaRetrievalPipeline(
        qdrant_url=os.getenv("QDRANT_URL", "http://localhost:6333"),
        collection_name=os.getenv("COLLECTION_NAME", "db_schema_demo"),
        gemini_api_key=os.getenv("GOOGLE_API_KEY"),
        table_retrieval_size=5,
        enable_column_pruning=True,
        context_window_size=1000
    )
    
    # Initialize GeminiProvider with proper configuration
    # Using gemini-1.5-flash instead of 2.0-flash-exp due to better quota limits
    llm_gen = GeminiProvider(
        model="gemini-2.0-flash",
        api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.0
    )
    
    query = "Show me total card transactions created in the last 30 days"
    
    print(f"\nQuery: '{query}'")
    print(f"Column Pruning: ENABLED")
    print(f"Context Window: 1000 tokens")
    
    print("\n" + "="*80)
    print("STEP 1: SEMANTIC SEARCH FOR TABLES")
    print("="*80)
    
    result = await pipeline.run(
        query=query,
        llm_generator=llm_gen
    )
    
    print("\n" + "="*80)
    print("STEP 2: BUILD DB SCHEMAS")
    print("="*80)
    print(f"\nRetrieved {result.table_count} tables")
    print(f"Total columns: {result.column_count}")
    
    print("\n" + "="*80)
    print("STEP 3: CHECK TOKEN COUNT")
    print("="*80)
    print(f"\nOriginal token count: {result.original_token_count}")
    print(f"Context window size: 1000")
    print(f"Needs pruning: {'YES' if result.original_token_count > 1000 else 'NO'}")
    
    print("\n" + "="*80)
    print("STEP 5: REBUILD DDL WITH SELECTED COLUMNS")
    print("="*80)
    print(f"\nPruning applied: {result.was_pruned}")
    
    print("\n" + "="*80)
    print("FINAL RESULT (PRUNED SCHEMAS)")
    print("="*80)
    
    for i, retrieval in enumerate(result.retrieval_results, 1):
        print(f"\n--- Table {i}: {retrieval['table_name']} ---")
        print(retrieval['table_ddl'])
    
    print("\n" + "="*80)
    print("COMPARISON")
    print("="*80)
    print(f"Original columns: {result.column_count}")
    print(f"After pruning: Only relevant columns kept")
    print(f"Token reduction: ~{100 - (len(str(result.retrieval_results)) / result.original_token_count * 100):.0f}%")


async def demo_with_filters():
    """Demo 3: Retrieval with filters"""
    print("\n")
    print("#" * 80)
    print("# DEMO 3: RETRIEVAL WITH FILTERS")
    print("#" * 80)
    
    pipeline = DBSchemaRetrievalPipeline(
        qdrant_url=os.getenv("QDRANT_URL", "http://localhost:6333"),
        collection_name=os.getenv("COLLECTION_NAME", "db_schema"),
        gemini_api_key=os.getenv("GEMINI_API_KEY"),
        table_retrieval_size=5,
        enable_column_pruning=True
    )
    
    query = "Get order information"
    project_id = os.getenv("PROJECT_ID")
    database = os.getenv("DATABASE_NAME")
    
    print(f"\nQuery: '{query}'")
    if project_id:
        print(f"Project ID: {project_id}")
    if database:
        print(f"Database: {database}")
    
    print("\n" + "="*80)
    print("STEP 1: SEMANTIC SEARCH WITH FILTERS")
    print("="*80)
    
    result = await pipeline.run(
        query=query,
        project_id=project_id,
        database=database
    )
    
    print("\n" + "="*80)
    print("FINAL RESULT")
    print("="*80)
    print(f"\nTables found: {result.table_count}")
    
    for schema in result.db_schemas:
        print(f"\n{schema['database']}.{schema['name']}")
        print(f"  Type: {schema['type']}")
        print(f"  Columns: {len(schema['columns'])}")


async def demo_with_history():
    """Demo 4: Retrieval with conversation history"""
    print("\n")
    print("#" * 80)
    print("# DEMO 4: RETRIEVAL WITH CONVERSATION HISTORY")
    print("#" * 80)
    
    pipeline = DBSchemaRetrievalPipeline(
        qdrant_url=os.getenv("QDRANT_URL", "http://localhost:6333"),
        collection_name=os.getenv("COLLECTION_NAME", "db_schema"),
        gemini_api_key=os.getenv("GEMINI_API_KEY"),
        table_retrieval_size=5,
        enable_column_pruning=False
    )
    
    histories = [
        "Show me customer information",
        "Now include their orders"
    ]
    current_query = "And their total spending"
    
    print("\nConversation History:")
    for i, hist in enumerate(histories, 1):
        print(f"  {i}. {hist}")
    print(f"\nCurrent Query: {current_query}")
    
    print("\n" + "="*80)
    print("STEP 1: COMBINE QUERY WITH HISTORY")
    print("="*80)
    combined = pipeline._combine_query_with_history(current_query, histories)
    print(f"\nCombined query for search:\n{combined}")
    
    print("\n" + "="*80)
    print("STEP 2: SEMANTIC SEARCH")
    print("="*80)
    
    result = await pipeline.run(
        query=current_query,
        histories=histories
    )
    
    print("\n" + "="*80)
    print("FINAL RESULT")
    print("="*80)
    print(f"\nTables found: {result.table_count} (considering conversation context)")
    
    for schema in result.db_schemas:
        print(f"  - {schema['name']}: {len(schema['columns'])} columns")


async def main():
    """Run all demos"""
    load_dotenv()
    print("\n" + "="*80)
    print("ENVIRONMENT VARIABLES CHECK")
    print("="*80)
    
    required_vars = {
        "GEMINI_API_KEY": os.getenv("GOOGLE_API_KEY"),
        "QDRANT_URL": os.getenv("QDRANT_URL", "http://localhost:6333"),
        "COLLECTION_NAME": os.getenv("COLLECTION_NAME", "db_schema_demo"),
    }
    
    for var, value in required_vars.items():
        status = "SET" if value else "NOT SET"
        display_value = value if var != "GEMINI_API_KEY" else ("***" if value else "NOT SET")
        print(f"{var}: {display_value} [{status}]")
    
    if not required_vars["GEMINI_API_KEY"]:
        print("\nERROR: GEMINI_API_KEY is required!")
        print("Set it with: export GEMINI_API_KEY='your-api-key'")
        return
    
    demos = [
        # ("Basic Retrieval", demo_basic_retrieval),
        ("With Column Pruning", demo_with_column_pruning),
        # ("With Filters", demo_with_filters),
        # ("With History", demo_with_history),
    ]
    
    print("\n")
    print("="*80)
    print("DB SCHEMA RETRIEVAL PIPELINE - STEP BY STEP DEMOS")
    print("="*80)
    print("\nAvailable Demos:")
    for i, (name, _) in enumerate(demos, 1):
        print(f"  {i}. {name}")
    
    print("\n" + "-"*80)
    input("Press Enter to start demos...")
    
    for name, demo_func in demos:
        await demo_func()
        print("\n" + "-"*80)
        input(f"Press Enter to continue to next demo...")
    
    print("\n")
    print("="*80)
    print("ALL DEMOS COMPLETED")
    print("="*80)
    
    print("\nKey Takeaways:")
    print("  1. Pipeline retrieves tables using semantic search")
    print("  2. Builds full DDL statements for all tables")
    print("  3. Checks if token count exceeds threshold")
    print("  4. If yes, uses LLM to intelligently prune columns")
    print("  5. Returns optimized schemas for SQL generation")


if __name__ == "__main__":
    asyncio.run(main())
