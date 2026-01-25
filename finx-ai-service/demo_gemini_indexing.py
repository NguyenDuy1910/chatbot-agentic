import os
import sys
import asyncio
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent))
from src.workflows.indexing.db_schema import (
    DBSchemaIndexingGraph,
    index_mdl_schema
)
import google.generativeai as genai
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

class GeminiIndexingDemo:
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        qdrant_url: str = "http://localhost:6333",
        collection_name: str = "db_schema_demo"
    ):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.qdrant_url = qdrant_url
        self.collection_name = collection_name
        
        if self.api_key:
            genai.configure(api_key=self.api_key)
        
        self.qdrant_client = QdrantClient(url=qdrant_url)
    
    def print_header(self, title: str, width: int = 80):
        print("\n" + "=" * width)
        print(title.center(width))
        print("=" * width + "\n")
    
    def print_section(self, title: str, width: int = 80):
        print("\n" + "-" * width)
        print(title)
        print("-" * width)
    
    async def demo_basic_indexing(
        self,
        mdl_file: str = "../finx-engine/data/mdls.json",
        chunk_by: str = "table"
    ):
        self.print_header("DEMO 1: Basic Schema Indexing")
        
        print(f"MDL file: {mdl_file}")
        print(f"Chunking strategy: {chunk_by}")
        print(f"Qdrant URL: {self.qdrant_url}")
        print(f"Collection: {self.collection_name}")
        print(f"Embedding model: Google text-embedding-004")
        
        mdl_path = Path(mdl_file)
        if not mdl_path.exists():
            print(f"MDL file not found: {mdl_file}")
            return
        
        self.print_section("MDL File Preview")
        with open(mdl_path, 'r') as f:
            mdl_data = json.load(f)
        
        print(f"Datasources found: {list(mdl_data.keys())}")
        for ds_id, ds_data in mdl_data.items():
            database = ds_data.get('database', 'unknown')
            models = ds_data.get('models', [])
            print(f"  - {ds_id}: {database} ({len(models)} tables)")
        
        self.print_section("Running Indexing Workflow")
        
        try:
            graph = DBSchemaIndexingGraph(
                mdl_file_path=str(mdl_path),
                chunk_by=chunk_by,
                gemini_api_key=self.api_key,
                gemini_model="models/text-embedding-004",
                qdrant_url=self.qdrant_url,
                qdrant_collection=self.collection_name,
                vector_size=768,
                recreate_collection=True
            )
            
            graph.build()
            result = await graph.run(project_id="demo_project")
            
            self.print_section("Indexing Results")
            print(f"Status: {result.get('status')}")
            print(f"Tables processed: {result.get('table_count', 0)}")
            print(f"Columns processed: {result.get('column_count', 0)}")
            print(f"Documents indexed: {result.get('indexed_count', 0)}")
            
            if result.get('errors'):
                print("\nErrors encountered:")
                for error in result['errors']:
                    print(f"   - {error}")
            else:
                print(f"\nSuccessfully indexed {result.get('indexed_count', 0)} documents!")
            
            return result
            
        except Exception as e:
            print(f"Indexing failed: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def demo_semantic_search(self, query: str = "customer information"):
        self.print_header("DEMO 2: Semantic Search")
        
        print(f"Query: '{query}'")
        
        if not self.api_key:
            print("Cannot perform search without API key")
            return
        
        try:
            self.print_section("Generating Query Embedding")
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=query,
                task_type="retrieval_query"
            )
            query_embedding = result['embedding']
            print(f"Generated {len(query_embedding)}-dimensional embedding")
            
            self.print_section("Searching Vector Database")
            search_results = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=5
            )
            
            print(f"Found {len(search_results)} relevant results:\n")
            
            for idx, hit in enumerate(search_results, 1):
                score = hit.score
                payload = hit.payload
                
                print(f"{idx}. Score: {score:.4f}")
                print(f"   Type: {payload.get('type')}")
                print(f"   Database: {payload.get('database')}")
                print(f"   Table: {payload.get('table_name')}")
                
                if payload.get('type') == 'column_schema':
                    print(f"   Column: {payload.get('column_name')} ({payload.get('column_type')})")
                    print(f"   Description: {payload.get('column_description', 'N/A')}")
                else:
                    print(f"   Columns: {', '.join(payload.get('column_names', []))[:100]}")
                
                print()
            
        except Exception as e:
            print(f"Search failed: {e}")
            import traceback
            traceback.print_exc()
    
    async def demo_advanced_queries(self):
        self.print_header("DEMO 3: Multiple Search Queries")
        
        queries = [
            "customer information",
            "order and transaction data",
            "user authentication and passwords",
            "financial records",
            "product inventory"
        ]
        
        for query in queries:
            print(f"\nQuery: '{query}'")
            
            if not self.api_key:
                print("Cannot perform search without API key")
                continue
            
            try:
                result = genai.embed_content(
                    model="models/text-embedding-004",
                    content=query,
                    task_type="retrieval_query"
                )
                query_embedding = result['embedding']
                
                search_results = self.qdrant_client.search(
                    collection_name=self.collection_name,
                    query_vector=query_embedding,
                    limit=3
                )
                
                print(f"   Top result: {search_results[0].payload.get('table_name')} "
                      f"(score: {search_results[0].score:.4f})")
                
            except Exception as e:
                print(f"   Query failed: {e}")
    
    async def demo_column_level_indexing(
        self,
        mdl_file: str = "../finx-engine/data/mdls.json"
    ):
        self.print_header("DEMO 4: Column-Level Indexing")
        
        print("This demo indexes each column as a separate document,")
        print("allowing for more precise semantic search.")
        
        collection_name = f"{self.collection_name}_columns"
        
        try:
            result = await index_mdl_schema(
                mdl_file_path=mdl_file,
                project_id="demo_column",
                chunk_by="column",
                gemini_api_key=self.api_key,
                gemini_model="models/text-embedding-004",
                qdrant_url=self.qdrant_url,
                qdrant_collection=collection_name,
                vector_size=768,
                recreate_collection=True
            )
            
            self.print_section("Column-Level Indexing Results")
            print(f"Status: {result.get('status')}")
            print(f"Documents indexed: {result.get('indexed_count', 0)}")
            print(f"   (One document per column)")
            
            if self.api_key:
                self.print_section("Column-Level Search Example")
                query = "email address field"
                
                result = genai.embed_content(
                    model="models/text-embedding-004",
                    content=query,
                    task_type="retrieval_query"
                )
                
                search_results = self.qdrant_client.search(
                    collection_name=collection_name,
                    query_vector=result['embedding'],
                    limit=5
                )
                
                print(f"Query: '{query}'\n")
                for idx, hit in enumerate(search_results, 1):
                    payload = hit.payload
                    print(f"{idx}. {payload.get('table_name')}.{payload.get('column_name')}")
                    print(f"   Type: {payload.get('column_type')}")
                    print(f"   Score: {hit.score:.4f}\n")
            
        except Exception as e:
            print(f"Column-level indexing failed: {e}")
    
    def demo_collection_stats(self):
        self.print_header("Collection Statistics")
        
        try:
            # Use HTTP API directly to avoid Pydantic validation issues
            import requests
            response = requests.get(f"{self.qdrant_url}/collections/{self.collection_name}")
            
            if response.status_code == 200:
                collection_info = response.json()["result"]
                
                print(f"Collection: {self.collection_name}")
                print(f"Total vectors: {collection_info.get('points_count', 'N/A')}")
                
                # Handle different vector config structures
                vectors_config = collection_info.get('config', {}).get('params', {}).get('vectors', {})
                if isinstance(vectors_config, dict):
                    print(f"Vector dimension: {vectors_config.get('size', 'N/A')}")
                    print(f"Distance metric: {vectors_config.get('distance', 'N/A')}")
                
                print(f"Index status: {collection_info.get('status', 'N/A')}")
            else:
                print(f"Failed to get collection stats: HTTP {response.status_code}")
            
        except Exception as e:
            print(f"Failed to get collection stats: {e}")


async def main():
    print("\n" + "=" * 80)
    print("GEMINI EMBEDDING INDEXING DEMO".center(80))
    print("Database Schema Semantic Search".center(80))
    print("=" * 80)
    load_dotenv()
    print("\nChecking Prerequisites...")
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        print("GOOGLE_API_KEY found")
    else:
        print("GOOGLE_API_KEY not set (will use mock embeddings)")
    
    try:
        demo = GeminiIndexingDemo(
            api_key=api_key,
            qdrant_url="http://localhost:6333",
            collection_name="db_schema_demo"
        )
        print("Demo initialized")
    except Exception as e:
        print(f"Failed to initialize: {e}")
        return
    
    mdl_file = "../finx-engine/data/mdls.json"
    
    await demo.demo_basic_indexing(mdl_file=mdl_file, chunk_by="table")
    await asyncio.sleep(1)
    
    if api_key:
        await demo.demo_semantic_search(query="Thông tin chứa dữ liệu về các thẻ vật lý đã được phát hành.")
        # await demo.demo_advanced_queries()
    
    # demo.demo_collection_stats()
    
    print("\n" + "=" * 80)
    print("DEMO COMPLETED".center(80))
    print("=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
