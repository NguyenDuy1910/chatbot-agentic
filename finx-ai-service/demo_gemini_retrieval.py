"""
Demo script for DB Schema Retrieval

This script demonstrates how to search and retrieve indexed database schemas
from Qdrant vector store.

Prerequisites:
- Run demo_gemini_indexing.py first to index schemas
- Qdrant running at http://localhost:6333
- GOOGLE_API_KEY environment variable set
"""

import os
import sys
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from src.workflows.indexing.retrieval import (
    DBSchemaRetriever,
    SearchMode,
    search_schemas,
    find_table
)


class RetrievalDemo:
    """Demo class for retrieval operations."""
    
    def __init__(
        self,
        qdrant_url: str = "http://localhost:6333",
        collection_name: str = "db_schema_demo",
        api_key: str = None
    ):
        self.qdrant_url = qdrant_url
        self.collection_name = collection_name
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        
        # Initialize retriever
        self.retriever = DBSchemaRetriever(
            qdrant_url=qdrant_url,
            collection_name=collection_name,
            gemini_api_key=self.api_key
        )
    
    def print_header(self, title: str, width: int = 80):
        """Print section header."""
        print("\n" + "=" * width)
        print(title.center(width))
        print("=" * width + "\n")
    
    def print_section(self, title: str, width: int = 80):
        """Print subsection."""
        print("\n" + "-" * width)
        print(title)
        print("-" * width)
    
    def print_result(self, result, index: int = None):
        """Print a single search result."""
        if index:
            print(f"\n{index}. {result.database}.{result.table_name}")
        else:
            print(f"\n{result.database}.{result.table_name}")
        
        print(f"   Score: {result.score:.4f}", end="")
        if result.vector_score:
            print(f" (vector: {result.vector_score:.4f}, keyword: {result.keyword_score:.4f})")
        else:
            print()
        
        print(f"   Type: {result.table_type}")
        print(f"   Columns: {result.column_count}")
        
        if result.table_description:
            print(f"   Description: {result.table_description}")
        
        if result.primary_keys:
            print(f"   Primary Keys: {', '.join(result.primary_keys)}")
        
        if result.foreign_keys:
            print(f"   Foreign Keys: {', '.join(result.foreign_keys)}")
    
    async def demo_basic_search(self):
        """Demo 1: Basic semantic search."""
        self.print_header("DEMO 1: Basic Semantic Search")
        
        queries = [
            "customer information",
            "order and transaction data",
            "user authentication",
            "product inventory"
        ]
        
        for query in queries:
            self.print_section(f"Query: '{query}'")
            
            try:
                results = await self.retriever.search(
                    query=query,
                    limit=3,
                    mode=SearchMode.VECTOR
                )
                
                if results:
                    print(f"Found {len(results)} results:")
                    for idx, result in enumerate(results, 1):
                        self.print_result(result, idx)
                else:
                    print("No results found.")
                    
            except Exception as e:
                print(f"Error: {e}")
    
    async def demo_hybrid_search(self):
        """Demo 2: Hybrid search (vector + keyword)."""
        self.print_header("DEMO 2: Hybrid Search (Vector + Keyword)")
        
        query = "customer email address"
        
        self.print_section(f"Query: '{query}'")
        print("Comparing Vector-only vs Hybrid search...\n")
        
        # Vector-only search
        print("Vector-only results:")
        vector_results = await self.retriever.search(
            query=query,
            limit=3,
            mode=SearchMode.VECTOR
        )
        
        for idx, result in enumerate(vector_results, 1):
            print(f"  {idx}. {result.table_name} (score: {result.score:.4f})")
        
        # Hybrid search
        print("\nHybrid search results:")
        hybrid_results = await self.retriever.search(
            query=query,
            limit=3,
            mode=SearchMode.HYBRID
        )
        
        for idx, result in enumerate(hybrid_results, 1):
            print(f"  {idx}. {result.table_name} (score: {result.score:.4f})")
            print(f"      Vector: {result.vector_score:.4f}, Keyword: {result.keyword_score:.4f}")
    
    async def demo_filtered_search(self):
        """Demo 3: Search with metadata filters."""
        self.print_header("DEMO 3: Filtered Search")
        
        # Get collection stats first
        stats = self.retriever.get_collection_stats()
        print(f"Collection: {stats.get('collection_name')}")
        print(f"Total indexed: {stats.get('total_points', 0)} tables")
        print()
        
        # Search with filters
        test_cases = [
            {
                "name": "Filter by database",
                "query": "user data",
                "filters": {"database": "ecommerce"}
            },
            {
                "name": "Tables with primary keys",
                "query": "main tables",
                "filters": {"has_primary_key": True}
            },
            {
                "name": "Tables with foreign keys (relationships)",
                "query": "related tables",
                "filters": {"has_foreign_key": True}
            }
        ]
        
        for test in test_cases:
            self.print_section(test["name"])
            print(f"Query: '{test['query']}'")
            print(f"Filters: {test['filters']}")
            
            try:
                results = await self.retriever.search(
                    query=test["query"],
                    limit=3,
                    filters=test["filters"]
                )
                
                if results:
                    for idx, result in enumerate(results, 1):
                        self.print_result(result, idx)
                else:
                    print("No results found.")
                    
            except Exception as e:
                print(f"Error: {e}")
    
    async def demo_table_lookup(self):
        """Demo 4: Find specific table by name."""
        self.print_header("DEMO 4: Table Lookup by Name")
        
        table_names = ["customers", "orders", "users"]
        
        for table_name in table_names:
            self.print_section(f"Looking up table: '{table_name}'")
            
            try:
                results = await self.retriever.search_by_table_name(table_name)
                
                if results:
                    result = results[0]
                    self.print_result(result)
                    
                    # Show columns
                    if result.columns_metadata:
                        print(f"\n   Columns ({len(result.columns_metadata)}):")
                        for col in result.columns_metadata[:5]:  # Show first 5
                            col_info = f"     - {col['name']} ({col['type']})"
                            if col.get('primary_key'):
                                col_info += " [PK]"
                            if col.get('foreign_key'):
                                col_info += " [FK]"
                            if col.get('description'):
                                col_info += f": {col['description']}"
                            print(col_info)
                        
                        if len(result.columns_metadata) > 5:
                            print(f"     ... and {len(result.columns_metadata) - 5} more")
                else:
                    print(f"Table '{table_name}' not found.")
                    
            except Exception as e:
                print(f"Error: {e}")
    
    async def demo_column_search(self):
        """Demo 5: Search by column keyword."""
        self.print_header("DEMO 5: Search by Column Keyword")
        
        keywords = ["email", "price", "status", "date"]
        
        for keyword in keywords:
            self.print_section(f"Finding tables with '{keyword}' columns")
            
            try:
                results = await self.retriever.search_by_column_keyword(
                    keyword=keyword,
                    limit=3
                )
                
                if results:
                    print(f"Found {len(results)} tables:")
                    for idx, (table, matching_cols) in enumerate(results, 1):
                        print(f"\n{idx}. {table.database}.{table.table_name}")
                        print(f"   Matching columns ({len(matching_cols)}):")
                        for col in matching_cols:
                            print(f"     - {col['name']} ({col['type']})")
                            if col.get('description'):
                                print(f"       {col['description']}")
                else:
                    print(f"No tables found with '{keyword}' columns.")
                    
            except Exception as e:
                print(f"Error: {e}")
    
    async def demo_related_tables(self):
        """Demo 6: Find related tables."""
        self.print_header("DEMO 6: Find Related Tables")
        
        # This requires having indexed data with relationships
        test_table = "orders"
        test_database = "ecommerce"
        
        self.print_section(f"Finding tables related to '{test_table}'")
        
        try:
            related = await self.retriever.get_related_tables(
                table_name=test_table,
                database=test_database,
                limit=5
            )
            
            if related:
                print(f"Found {len(related)} related tables:")
                for idx, result in enumerate(related, 1):
                    self.print_result(result, idx)
            else:
                print(f"No related tables found for '{test_table}'")
                print("(This may be because the table doesn't exist or has no clear relationships)")
                
        except Exception as e:
            print(f"Error: {e}")
    
    async def demo_advanced_queries(self):
        """Demo 7: Advanced query patterns."""
        self.print_header("DEMO 7: Advanced Query Patterns")
        
        queries = [
            {
                "name": "Find audit tables",
                "query": "audit log history tracking",
                "description": "Tables that track changes or history"
            },
            {
                "name": "Find lookup/reference tables",
                "query": "lookup reference static data configuration",
                "description": "Small tables with static reference data"
            },
            {
                "name": "Find transaction tables",
                "query": "transaction payment order financial",
                "description": "Tables storing transaction data"
            },
            {
                "name": "Find user-related security tables",
                "query": "user authentication password credential security",
                "description": "Authentication and security tables"
            }
        ]
        
        for query_info in queries:
            self.print_section(query_info["name"])
            print(f"Description: {query_info['description']}")
            print(f"Query: '{query_info['query']}'")
            
            try:
                results = await self.retriever.search(
                    query=query_info["query"],
                    limit=3,
                    mode=SearchMode.HYBRID,
                    min_score=0.5  # Only show good matches
                )
                
                if results:
                    for idx, result in enumerate(results, 1):
                        self.print_result(result, idx)
                else:
                    print("No high-confidence results found.")
                    
            except Exception as e:
                print(f"Error: {e}")


async def main():
    """Run all demos."""
    print("\n" + "=" * 80)
    print("DATABASE SCHEMA RETRIEVAL DEMO".center(80))
    print("Semantic Search with Qdrant + Google Gemini".center(80))
    print("=" * 80)
    
    # Check prerequisites
    print("\nChecking prerequisites...")
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("⚠️  Warning: GOOGLE_API_KEY not set")
        print("   Set it with: export GOOGLE_API_KEY='your-key'")
        print("   Some features may not work.\n")
    else:
        print("✓ GOOGLE_API_KEY found")
    
    qdrant_url = "http://localhost:6333"
    collection_name = "db_schema_demo"
    
    print(f"✓ Qdrant URL: {qdrant_url}")
    print(f"✓ Collection: {collection_name}")
    print("\n" + "=" * 80)
    
    try:
        # Initialize demo
        demo = RetrievalDemo(
            qdrant_url=qdrant_url,
            collection_name=collection_name,
            api_key=api_key
        )
        
        # Check if collection exists
        stats = demo.retriever.get_collection_stats()
        if not stats or stats.get('total_points', 0) == 0:
            print("\n⚠️  Warning: Collection is empty or doesn't exist")
            print("   Run 'python demo_gemini_indexing.py' first to index schemas")
            return
        
        print(f"\n✓ Collection has {stats.get('total_points', 0)} indexed tables")
        
        # Run demos
        await demo.demo_basic_search()
        await demo.demo_hybrid_search()
        await demo.demo_filtered_search()
        await demo.demo_table_lookup()
        await demo.demo_column_search()
        await demo.demo_related_tables()
        await demo.demo_advanced_queries()
        
        # Final summary
        print("\n" + "=" * 80)
        print("DEMO COMPLETED".center(80))
        print("=" * 80)
        print("\n✅ All retrieval demos completed successfully!")
        print("\nNext steps:")
        print("  1. Try your own queries by modifying the demo script")
        print("  2. Integrate retrieval into your application")
        print("  3. See retrieval.py for full API documentation")
        print("=" * 80 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error running demos: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
