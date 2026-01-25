# import os
# import sys
# import asyncio
# from pathlib import Path
# from dotenv import load_dotenv
# sys.path.insert(0, str(Path(__file__).parent))

# from src.workflows.retrieval.db_schema_retrieval import (
#     DBSchemaRetrievalPipeline,
#     retrieve_relevant_schemas
# )


# class RetrievalPipelineDemo:
#     """Demo class for retrieval pipeline."""
    
#     def __init__(
#         self,
#         qdrant_url: str = "http://localhost:6333",
#         collection_name: str = "db_schema_demo",
#         api_key: str = None
#     ):
#         self.qdrant_url = qdrant_url
#         self.collection_name = collection_name
#         self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        
#         # Initialize pipeline
#         self.pipeline = DBSchemaRetrievalPipeline(
#             qdrant_url=qdrant_url,
#             collection_name=collection_name,
#             gemini_api_key=self.api_key,
#             table_retrieval_size=10,
#             enable_column_pruning=False  # Start without pruning
#         )
    
#     def print_header(self, title: str, width: int = 80):
#         """Print section header."""
#         print("\n" + "=" * width)
#         print(title.center(width))
#         print("=" * width + "\n")
    
#     def print_section(self, title: str, width: int = 80):
#         """Print subsection."""
#         print("\n" + "-" * width)
#         print(title)
#         print("-" * width)
    
#     def print_retrieval_result(self, result):
#         """Print retrieval result summary."""
#         print(f"\n📊 Retrieval Statistics:")
#         print(f"   Tables found: {result.table_count}")
#         print(f"   Total columns: {result.column_count}")
#         print(f"   Token count: {result.original_token_count}")
#         print(f"   Was pruned: {result.was_pruned}")
        
#         if result.has_calculated_field:
#             print(f"   ⚠️  Contains calculated fields")
#         if result.has_metric:
#             print(f"   📈 Contains metrics")
#         if result.has_json_field:
#             print(f"   📋 Contains JSON fields")
    
#     def print_ddl(self, ddl_result, index: int = None):
#         """Print a DDL result."""
#         if index:
#             print(f"\n{index}. Table: {ddl_result['table_name']}")
#         else:
#             print(f"\nTable: {ddl_result['table_name']}")
        
#         print("-" * 60)
#         print(ddl_result['table_ddl'])
    
#     async def demo_basic_retrieval(self):
#         """Demo 1: Basic schema retrieval."""
#         self.print_header("DEMO 1: Basic Schema Retrieval")
        
#         queries = [
#             "customer information and contact details",
#             "order and transaction data with amounts",
#             "user authentication and login credentials",
#         ]
        
#         for query in queries:
#             self.print_section(f"Query: '{query}'")
            
#             try:
#                 result = await self.pipeline.run(query=query)
#                 self.print_retrieval_result(result)
                
#                 if result.retrieval_results:
#                     print(f"\n📋 Retrieved Tables:")
#                     for idx, ddl in enumerate(result.retrieval_results[:3], 1):
#                         self.print_ddl(ddl, idx)
#                 else:
#                     print("\n⚠️  No tables found.")
                    
#             except Exception as e:
#                 print(f"❌ Error: {e}")
#                 import traceback
#                 traceback.print_exc()
    
#     async def demo_filtered_retrieval(self):
#         """Demo 2: Retrieval with filters."""
#         self.print_header("DEMO 2: Filtered Retrieval")
        
#         test_cases = [
#             {
#                 "name": "Filter by database",
#                 "query": "all customer data",
#                 "database": "ecommerce",
#                 "project_id": None
#             },
#             {
#                 "name": "Specific project",
#                 "query": "user information",
#                 "database": None,
#                 "project_id": "demo_project"
#             }
#         ]
        
#         for test in test_cases:
#             self.print_section(test["name"])
#             print(f"Query: '{test['query']}'")
#             if test['database']:
#                 print(f"Database filter: {test['database']}")
#             if test['project_id']:
#                 print(f"Project filter: {test['project_id']}")
            
#             try:
#                 result = await self.pipeline.run(
#                     query=test["query"],
#                     database=test.get("database"),
#                     project_id=test.get("project_id")
#                 )
                
#                 self.print_retrieval_result(result)
                
#                 if result.retrieval_results:
#                     print(f"\n📋 Top 2 Tables:")
#                     for idx, ddl in enumerate(result.retrieval_results[:2], 1):
#                         self.print_ddl(ddl, idx)
                        
#             except Exception as e:
#                 print(f"❌ Error: {e}")
    
#     async def demo_specific_tables(self):
#         """Demo 3: Retrieve specific tables."""
#         self.print_header("DEMO 3: Retrieve Specific Tables")
        
#         specific_tables = ["customers", "orders", "products"]
        
#         self.print_section(f"Requesting specific tables: {', '.join(specific_tables)}")
        
#         try:
#             result = await self.pipeline.run(
#                 query="",  # No query needed for specific tables
#                 tables=specific_tables,
#                 database="ecommerce"
#             )
            
#             self.print_retrieval_result(result)
            
#             if result.retrieval_results:
#                 print(f"\n📋 Retrieved Schemas:")
#                 for ddl in result.retrieval_results:
#                     self.print_ddl(ddl)
#             else:
#                 print("\n⚠️  Requested tables not found.")
                
#         except Exception as e:
#             print(f"❌ Error: {e}")
    
#     async def demo_with_history(self):
#         """Demo 4: Context-aware retrieval with history."""
#         self.print_header("DEMO 4: Context-Aware Retrieval with History")
        
#         # Simulate a conversation
#         conversation = [
#             {
#                 "history": [
#                     "Tổng số lượng thẻ được phát hành",
#                     "Tổng số lượng thẻ được kích hoạt"
#                 ],
#                 "query": "Danh sách thẻ được kích hoạt từ tháng 02-2025 đến nay"
#             }
#         ]
        
#         for idx, turn in enumerate(conversation, 1):
#             self.print_section(f"Turn {idx}")
            
#             if turn['history']:
#                 print("Previous context:")
#                 for h in turn['history']:
#                     print(f"  - {h}")
            
#             print(f"\nCurrent query: '{turn['query']}'")
            
#             try:
#                 result = await self.pipeline.run(
#                     query=turn['query'],
#                     histories=turn['history']
#                 )
                
#                 self.print_retrieval_result(result)
                
#                 if result.retrieval_results:
#                     print(f"\n📋 Relevant tables for this turn:")
#                     for ddl in result.retrieval_results[:2]:
#                         print(f"  - {ddl['table_name']}")
                        
#             except Exception as e:
#                 print(f"❌ Error: {e}")
    
#     async def demo_column_details(self):
#         """Demo 5: Show detailed column information."""
#         self.print_header("DEMO 5: Detailed Column Information")
        
#         query = "customer email and phone contact information"
        
#         self.print_section(f"Query: '{query}'")
#         print("Retrieving with full column details...")
        
#         try:
#             result = await self.pipeline.run(query=query)
            
#             if result.db_schemas:
#                 print(f"\n📊 Found {len(result.db_schemas)} tables with detailed column info:")
                
#                 for schema in result.db_schemas[:2]:  # Show first 2
#                     print(f"\n{'='*60}")
#                     print(f"Table: {schema['database']}.{schema['name']}")
#                     print(f"Type: {schema['type']}")
#                     print(f"Description: {schema.get('description', 'N/A')}")
#                     print(f"\nColumns ({len(schema['columns'])}):")
                    
#                     for col in schema['columns'][:5]:  # Show first 5 columns
#                         print(f"\n  📌 {col['name']} ({col['type']})")
#                         if col.get('description'):
#                             print(f"     Description: {col['description']}")
                        
#                         constraints = []
#                         if col.get('primary_key'):
#                             constraints.append("PRIMARY KEY")
#                         if col.get('foreign_key'):
#                             constraints.append("FOREIGN KEY")
#                             if col.get('foreign_key_reference'):
#                                 constraints.append(f"→ {col['foreign_key_reference']}")
#                         if not col.get('nullable', True):
#                             constraints.append("NOT NULL")
                        
#                         if constraints:
#                             print(f"     Constraints: {', '.join(constraints)}")
                    
#                     if len(schema['columns']) > 5:
#                         print(f"\n  ... and {len(schema['columns']) - 5} more columns")
#             else:
#                 print("\n⚠️  No schemas found.")
                
#         except Exception as e:
#             print(f"❌ Error: {e}")
    
#     async def demo_quick_function(self):
#         """Demo 6: Using convenience function."""
#         self.print_header("DEMO 6: Quick Retrieval Function")
        
#         query = "product inventory and stock levels"
        
#         self.print_section("Using retrieve_relevant_schemas() convenience function")
#         print(f"Query: '{query}'")
        
#         try:
#             result = await retrieve_relevant_schemas(
#                 query=query,
#                 collection_name=self.collection_name,
#                 qdrant_url=self.qdrant_url,
#                 gemini_api_key=self.api_key,
#                 table_retrieval_size=5
#             )
            
#             self.print_retrieval_result(result)
            
#             if result.retrieval_results:
#                 print(f"\n📋 Tables found:")
#                 for ddl in result.retrieval_results:
#                     print(f"  - {ddl['table_name']}")
                    
#         except Exception as e:
#             print(f"❌ Error: {e}")


# async def main():
#     """Run all demos."""
#     print("\n" + "=" * 80)
#     print("DATABASE SCHEMA RETRIEVAL PIPELINE DEMO".center(80))
#     print("Complete Retrieval with Context & Filtering".center(80))
#     print("=" * 80)
    
#     # Check prerequisites
#     print("\nChecking prerequisites...")
#     load_dotenv()
#     api_key = os.getenv("GOOGLE_API_KEY")
#     if not api_key:
#         print("⚠️  Warning: GOOGLE_API_KEY not set")
#         print("   Set it with: export GOOGLE_API_KEY='your-key'")
#         return
#     else:
#         print("✓ GOOGLE_API_KEY found")
    
#     qdrant_url = "http://localhost:6333"
#     collection_name = "db_schema_demo"
    
#     print(f"✓ Qdrant URL: {qdrant_url}")
#     print(f"✓ Collection: {collection_name}")
#     print("\n" + "=" * 80)
    
#     try:
#         # Initialize demo
#         demo = RetrievalPipelineDemo(
#             qdrant_url=qdrant_url,
#             collection_name=collection_name,
#             api_key=api_key
#         )
        
#         # Run demos
#         # await demo.demo_basic_retrieval()
#         # await demo.demo_filtered_retrieval()
#         # await demo.demo_specific_tables()
#         await demo.demo_with_history()
#         # await demo.demo_column_details()
#         # await demo.demo_quick_function()
        
#         # Final summary
#         print("\n" + "=" * 80)
#         print("ALL DEMOS COMPLETED".center(80))
#         print("=" * 80)
#         print("\n✅ Retrieval pipeline demos completed successfully!")
#         print("\nKey Features Demonstrated:")
#         print("  ✓ Semantic search for relevant tables")
#         print("  ✓ Filtering by database/project")
#         print("  ✓ Specific table retrieval")
#         print("  ✓ Context-aware search with history")
#         print("  ✓ Detailed column metadata access")
#         print("  ✓ Convenience functions for quick use")
#         print("\nNext Steps:")
#         print("  1. Integrate with SQL generation pipeline")
#         print("  2. Add LLM-based column pruning")
#         print("  3. Implement caching for repeated queries")
#         print("=" * 80 + "\n")
        
#     except Exception as e:
#         print(f"\n❌ Error running demos: {e}")
#         import traceback
#         traceback.print_exc()


# if __name__ == "__main__":
#     asyncio.run(main())
from src.workflows.retrieval.db_schema_retrieval import DBSchemaRetrievalPipeline
import google.generativeai as genai
from dotenv import load_dotenv
import os
import asyncio


class GeminiGenerator:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
    async def __call__(self, prompt: str, system_prompt: str):
        response = await asyncio.to_thread(
            self.model.generate_content,
            f"{system_prompt}\n\n{prompt}",
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json"
            )
        )
        return {"replies": [response.text]}


async def main():
    load_dotenv()
    
    # Initialize pipeline
    pipeline = DBSchemaRetrievalPipeline(
        collection_name="db_schema_demo",  # Match indexing collection name
        enable_column_pruning=True,    # Enable pruning
        context_window_size=1000,      # Token threshold
    )
    
    llm = GeminiGenerator(os.getenv("GOOGLE_API_KEY"))
    
    # Run with pruning
    result = await pipeline.run(
        query="Danh sách thẻ được kích hoạt từ tháng 02-2025 đến nay",
        llm_generator=llm  # ← Pass LLM generator
    )
    
    print(f"Was pruned: {result.was_pruned}")
    print(f"Tokens: {result.original_token_count}")
    print(f"Tables found: {result.table_count}")
    print(f"Columns: {result.column_count}")
    
    if result.retrieval_results:
        print(f"\n📋 Retrieved {len(result.retrieval_results)} tables:")
        for ddl_result in result.retrieval_results:
            print(f"\n{'='*60}")
            print(f"Table: {ddl_result['table_name']}")
            print(f"{'='*60}")
            print(ddl_result['table_ddl'])


if __name__ == "__main__":
    asyncio.run(main())