import json
import logging
import uuid
from typing import Any, Dict, List, Optional, Type, TypedDict
from pathlib import Path

from langgraph.graph import END
import google.generativeai as gemini_client
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from src.workflows.base import FeatureGraph, FeatureNode

logger = logging.getLogger(__name__)


# State schema for the indexing workflow
class DBSchemaIndexingState(TypedDict, total=False):
    """State for database schema indexing workflow."""
    
    # Input
    mdl_file_path: str
    datasource_id: Optional[str]
    project_id: Optional[str]
    
    # Intermediate data
    mdl_data: Dict[str, Any]
    documents: List[Dict[str, Any]]
    embeddings: List[List[float]]
    
    # Output/Metadata
    indexed_count: int
    table_count: int
    column_count: int
    errors: List[str]
    status: str


class LoadMDLNode(FeatureNode):
    """Node to load and parse MDL JSON file."""
    
    def __init__(self, mdl_file_path: Optional[str] = None):
        """
        Initialize LoadMDL node.
        
        Args:
            mdl_file_path: Default path to MDL JSON file
        """
        self.default_mdl_path = mdl_file_path
        logger.info("LoadMDLNode initialized")
    
    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Load and parse MDL file.
        
        Args:
            state: Current state
            
        Returns:
            Updated state with mdl_data
        """
        try:
            mdl_path = state.get("mdl_file_path", self.default_mdl_path)
            
            if not mdl_path:
                raise ValueError("No MDL file path provided")
            
            logger.info(f"Loading MDL from: {mdl_path}")
            
            # Load JSON file
            with open(mdl_path, 'r', encoding='utf-8') as f:
                mdl_data = json.load(f)
            
            # Extract datasource_id from state or from first entry
            datasource_id = state.get("datasource_id")
            if not datasource_id and mdl_data:
                # Get first datasource ID from the JSON
                datasource_id = next(iter(mdl_data.keys()))
            
            logger.info(f"Loaded MDL data for datasource: {datasource_id}")
            logger.info(f"Found {len(mdl_data)} datasource(s)")
            
            return {
                "mdl_data": mdl_data,
                "datasource_id": datasource_id,
                "status": "mdl_loaded"
            }
            
        except FileNotFoundError:
            error_msg = f"MDL file not found: {mdl_path}"
            logger.error(error_msg)
            return {
                "errors": state.get("errors", []) + [error_msg],
                "status": "error"
            }
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON in MDL file: {str(e)}"
            logger.error(error_msg)
            return {
                "errors": state.get("errors", []) + [error_msg],
                "status": "error"
            }
        except Exception as e:
            error_msg = f"Error loading MDL: {str(e)}"
            logger.error(error_msg)
            return {
                "errors": state.get("errors", []) + [error_msg],
                "status": "error"
            }


class ChunkSchemaNode(FeatureNode):
    """Node to chunk schema data into documents for embedding."""
    
    def __init__(self, chunk_by: str = "table"):
        """
        Initialize ChunkSchema node.
        
        Args:
            chunk_by: Chunking strategy - "table" (one doc per table) or 
                     "column" (one doc per column)
        """
        self.chunk_by = chunk_by
        logger.info(f"ChunkSchemaNode initialized with strategy: {chunk_by}")
    
    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Chunk schema data into documents.
        
        Args:
            state: Current state with mdl_data
            
        Returns:
            Updated state with documents list
        """
        try:
            mdl_data = state.get("mdl_data", {})
            datasource_id = state.get("datasource_id")
            project_id = state.get("project_id", "default")
            
            if not mdl_data:
                raise ValueError("No MDL data to process")
            
            documents = []
            table_count = 0
            column_count = 0
            
            # Process each datasource
            for ds_id, ds_data in mdl_data.items():
                if datasource_id and ds_id != datasource_id:
                    continue
                
                database = ds_data.get("database", "unknown")
                models = ds_data.get("models", [])
                
                logger.info(f"Processing datasource: {ds_id}, database: {database}")
                logger.info(f"Found {len(models)} tables/models")
                
                for model in models:
                    table_name = model.get("name", "unknown")
                    table_desc = model.get("description", "")
                    table_type = model.get("type", "table")
                    columns = model.get("columns", [])
                    
                    table_count += 1
                    column_count += len(columns)
                    
                    if self.chunk_by == "table":
                        # Create one document per table
                        doc = self._create_table_document(
                            datasource_id=ds_id,
                            database=database,
                            table_name=table_name,
                            table_desc=table_desc,
                            table_type=table_type,
                            columns=columns,
                            project_id=project_id
                        )
                        documents.append(doc)
                    
                    elif self.chunk_by == "column":
                        # Create one document per column
                        for column in columns:
                            doc = self._create_column_document(
                                datasource_id=ds_id,
                                database=database,
                                table_name=table_name,
                                table_desc=table_desc,
                                column=column,
                                project_id=project_id
                            )
                            documents.append(doc)
            
            logger.info(f"Created {len(documents)} documents from {table_count} tables, {column_count} columns")
            
            return {
                "documents": documents,
                "table_count": table_count,
                "column_count": column_count,
                "status": "chunked"
            }
            
        except Exception as e:
            error_msg = f"Error chunking schema: {str(e)}"
            logger.error(error_msg)
            return {
                "errors": state.get("errors", []) + [error_msg],
                "status": "error"
            }
    
    def _create_table_document(
        self,
        datasource_id: str,
        database: str,
        table_name: str,
        table_desc: str,
        table_type: str,
        columns: List[Dict[str, Any]],
        project_id: str
    ) -> Dict[str, Any]:
        """Create a document for a table."""
        
        # Build comprehensive text content for embedding
        content_parts = [
            f"Database: {database}",
            f"Table: {table_name}",
            f"Type: {table_type}",
        ]
        
        if table_desc:
            content_parts.append(f"Description: {table_desc}")
        
        # Add column information
        content_parts.append(f"\nColumns ({len(columns)}):")
        for col in columns:
            col_name = col.get("name", "")
            col_type = col.get("type", "")
            col_desc = col.get("description", "")
            col_nullable = col.get("nullable", True)
            col_pk = col.get("primary_key", False)
            col_fk = col.get("foreign_key", False)
            
            col_info = f"  - {col_name} ({col_type})"
            
            if col_pk:
                col_info += " [PRIMARY KEY]"
            if col_fk:
                col_info += " [FOREIGN KEY]"
            if not col_nullable:
                col_info += " [NOT NULL]"
            
            if col_desc:
                col_info += f": {col_desc}"
            
            content_parts.append(col_info)
        
        content = "\n".join(content_parts)
        
        # Extract column names for metadata
        column_names = [col.get("name", "") for col in columns]
        primary_keys = [col.get("name") for col in columns if col.get("primary_key")]
        foreign_keys = [col.get("name") for col in columns if col.get("foreign_key")]
        
        # Build detailed column metadata with descriptions
        columns_metadata = []
        for col in columns:
            col_meta = {
                "name": col.get("name", ""),
                "type": col.get("type", ""),
                "description": col.get("description", ""),
                "nullable": col.get("nullable", True),
                "primary_key": col.get("primary_key", False),
                "foreign_key": col.get("foreign_key", False),
                "foreign_key_reference": col.get("foreign_key_reference")
            }
            columns_metadata.append(col_meta)
        
        # Create searchable text from all column descriptions
        column_descriptions_text = " | ".join([
            f"{col.get('name', '')}: {col.get('description', '')}" 
            for col in columns 
            if col.get('description')
        ])
        
        return {
            "content": content,
            "metadata": {
                "type": "table_schema",
                "datasource_id": datasource_id,
                "database": database,
                "table_name": table_name,
                "table_type": table_type,
                "table_description": table_desc,
                "column_count": len(columns),
                "column_names": column_names,
                "primary_keys": primary_keys,
                "foreign_keys": foreign_keys,
                "columns_metadata": columns_metadata,  # NEW: Full column details
                "column_descriptions": column_descriptions_text,  # NEW: Searchable descriptions
                "project_id": project_id
            }
        }
    
    def _create_column_document(
        self,
        datasource_id: str,
        database: str,
        table_name: str,
        table_desc: str,
        column: Dict[str, Any],
        project_id: str
    ) -> Dict[str, Any]:
        """Create a document for a single column."""
        
        col_name = column.get("name", "")
        col_type = column.get("type", "")
        col_desc = column.get("description", "")
        col_nullable = column.get("nullable", True)
        col_pk = column.get("primary_key", False)
        col_fk = column.get("foreign_key", False)
        col_fk_ref = column.get("foreign_key_reference")
        
        # Build content for embedding
        content_parts = [
            f"Database: {database}",
            f"Table: {table_name}",
            f"Column: {col_name}",
            f"Data Type: {col_type}",
        ]
        
        if col_desc:
            content_parts.append(f"Description: {col_desc}")
        
        if table_desc:
            content_parts.append(f"Table Description: {table_desc}")
        
        # Add constraints
        constraints = []
        if col_pk:
            constraints.append("PRIMARY KEY")
        if col_fk:
            constraints.append("FOREIGN KEY")
            if col_fk_ref:
                constraints.append(f"References: {col_fk_ref}")
        if not col_nullable:
            constraints.append("NOT NULL")
        
        if constraints:
            content_parts.append(f"Constraints: {', '.join(constraints)}")
        
        content = "\n".join(content_parts)
        
        return {
            "content": content,
            "metadata": {
                "type": "column_schema",
                "datasource_id": datasource_id,
                "database": database,
                "table_name": table_name,
                "column_name": col_name,
                "column_type": col_type,
                "column_description": col_desc,
                "is_primary_key": col_pk,
                "is_foreign_key": col_fk,
                "is_nullable": col_nullable,
                "foreign_key_reference": col_fk_ref,
                "project_id": project_id
            }
        }


class EmbedDocumentsNode(FeatureNode):
    """Node to generate embeddings for documents using Google Gemini."""
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        model_name: str = "models/text-embedding-004"
    ):
        """
        Initialize EmbedDocuments node.
        
        Args:
            api_key: Google API key (if None, uses environment variable)
            model_name: Gemini embedding model name
        """
        self.api_key = api_key
        self.model_name = model_name
        
        # Configure Gemini client
        if api_key:
            gemini_client.configure(api_key=api_key)
        
        logger.info(f"EmbedDocumentsNode initialized with model: {model_name}")
    
    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate embeddings for documents.
        
        Args:
            state: Current state with documents
            
        Returns:
            Updated state with embeddings
        """
        try:
            documents = state.get("documents", [])
            
            if not documents:
                raise ValueError("No documents to embed")
            
            logger.info(f"Generating embeddings for {len(documents)} documents")
            
            # Extract text content from documents
            texts = [doc["content"] for doc in documents]
            
            # Generate embeddings
            embeddings = []
            
            # Process in batches to avoid rate limits
            batch_size = 100
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                logger.info(f"Embedding batch {i // batch_size + 1} ({len(batch_texts)} docs)")
                
                # Generate embeddings for batch
                batch_embeddings = await self._generate_embeddings(batch_texts)
                embeddings.extend(batch_embeddings)
            
            logger.info(f"Generated {len(embeddings)} embeddings")
            
            return {
                "embeddings": embeddings,
                "status": "embedded"
            }
            
        except Exception as e:
            error_msg = f"Error generating embeddings: {str(e)}"
            logger.error(error_msg)
            return {
                "errors": state.get("errors", []) + [error_msg],
                "status": "error"
            }
    
    async def _generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings using Google Gemini.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        try:
            embeddings = []
            
            for text in texts:
                # Generate embedding using Gemini
                result = gemini_client.embed_content(
                    model=self.model_name,
                    content=text,
                    task_type="retrieval_document"
                )
                
                embeddings.append(result['embedding'])
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Error calling Gemini API: {str(e)}")
            logger.warning("Falling back to dummy embeddings")
            # Return dummy embeddings as fallback
            return [[0.0] * 768 for _ in texts]


class IndexDocumentsNode(FeatureNode):
    """Node to index documents into Qdrant vector store."""
    
    def __init__(
        self,
        qdrant_url: str = "http://localhost:6333",
        collection_name: str = "db_schema",
        vector_size: int = 768,
        recreate_collection: bool = False
    ):
        """
        Initialize IndexDocuments node.
        
        Args:
            qdrant_url: URL of Qdrant server
            collection_name: Name of the collection to store documents
            vector_size: Dimension of embedding vectors
            recreate_collection: Whether to recreate collection if it exists
        """
        self.qdrant_url = qdrant_url
        self.collection_name = collection_name
        self.vector_size = vector_size
        self.recreate_collection = recreate_collection
        
        # Initialize Qdrant client
        self.client = QdrantClient(url=qdrant_url)
        
        # Create or recreate collection
        self._setup_collection()
        
        logger.info(f"IndexDocumentsNode initialized with collection: {collection_name}")
    
    def _setup_collection(self):
        """Setup Qdrant collection."""
        try:
            collections = self.client.get_collections().collections
            collection_exists = any(c.name == self.collection_name for c in collections)
            
            if collection_exists and self.recreate_collection:
                logger.info(f"Deleting existing collection: {self.collection_name}")
                self.client.delete_collection(self.collection_name)
                collection_exists = False
            
            if not collection_exists:
                logger.info(f"Creating collection: {self.collection_name}")
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=Distance.COSINE
                    )
                )
            else:
                logger.info(f"Using existing collection: {self.collection_name}")
                
        except Exception as e:
            logger.error(f"Error setting up collection: {str(e)}")
            raise
    
    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Index documents into Qdrant.
        
        Args:
            state: Current state with documents and embeddings
            
        Returns:
            Updated state with indexing results
        """
        try:
            documents = state.get("documents", [])
            embeddings = state.get("embeddings", [])
            
            if not documents:
                raise ValueError("No documents to index")
            
            if len(documents) != len(embeddings):
                raise ValueError(
                    f"Mismatch between documents ({len(documents)}) "
                    f"and embeddings ({len(embeddings)})"
                )
            
            logger.info(f"Indexing {len(documents)} documents into Qdrant")
            
            # Prepare points for Qdrant
            points = []
            for idx, (doc, embedding) in enumerate(zip(documents, embeddings)):
                point = PointStruct(
                    id=str(uuid.uuid4()),  # Generate unique ID
                    vector=embedding,
                    payload={
                        "content": doc["content"],
                        **doc["metadata"]
                    }
                )
                points.append(point)
            
            # Upsert points to Qdrant
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            
            indexed_count = len(points)
            logger.info(f"Successfully indexed {indexed_count} documents to Qdrant")
            
            return {
                "indexed_count": indexed_count,
                "status": "indexed"
            }
            
        except Exception as e:
            error_msg = f"Error indexing documents: {str(e)}"
            logger.error(error_msg)
            return {
                "errors": state.get("errors", []) + [error_msg],
                "status": "error"
            }


class DBSchemaIndexingGraph(FeatureGraph):
    """
    Graph workflow for indexing database schema metadata.
    
    This workflow:
    1. Loads MDL JSON file containing schema metadata
    2. Chunks schema data into documents (by table or column)
    3. Generates embeddings using Google Gemini
    4. Indexes documents into Qdrant vector store
    """
    
    def __init__(
        self,
        mdl_file_path: Optional[str] = None,
        chunk_by: str = "table",
        gemini_api_key: Optional[str] = None,
        gemini_model: str = "models/text-embedding-004",
        qdrant_url: str = "http://localhost:6333",
        qdrant_collection: str = "db_schema",
        vector_size: int = 768,
        recreate_collection: bool = False
    ):
        """
        Initialize DB Schema Indexing Graph.
        
        Args:
            mdl_file_path: Default path to MDL JSON file
            chunk_by: Chunking strategy - "table" or "column"
            gemini_api_key: Google Gemini API key (if None, uses env var)
            gemini_model: Gemini embedding model name
            qdrant_url: URL of Qdrant server
            qdrant_collection: Name of Qdrant collection
            vector_size: Dimension of embedding vectors
            recreate_collection: Whether to recreate collection if exists
        """
        super().__init__(name="db_schema_indexing")
        
        self.mdl_file_path = mdl_file_path
        self.chunk_by = chunk_by
        
        # Initialize nodes
        self.load_mdl_node = LoadMDLNode(mdl_file_path)
        self.chunk_schema_node = ChunkSchemaNode(chunk_by)
        self.embed_documents_node = EmbedDocumentsNode(
            api_key=gemini_api_key,
            model_name=gemini_model
        )
        self.index_documents_node = IndexDocumentsNode(
            qdrant_url=qdrant_url,
            collection_name=qdrant_collection,
            vector_size=vector_size,
            recreate_collection=recreate_collection
        )
        
        logger.info(
            f"DBSchemaIndexingGraph initialized: chunk_by={chunk_by}, "
            f"model={gemini_model}, collection={qdrant_collection}"
        )
    
    def get_state_schema(self) -> Type[TypedDict]:
        """Get the state schema for this graph."""
        return DBSchemaIndexingState
    
    def _add_nodes(self) -> None:
        """Add all nodes to the graph."""
        self.graph.add_node("load_mdl", self.load_mdl_node.execute)
        self.graph.add_node("chunk_schema", self.chunk_schema_node.execute)
        self.graph.add_node("embed_documents", self.embed_documents_node.execute)
        self.graph.add_node("index_documents", self.index_documents_node.execute)
    
    def _add_edges(self) -> None:
        """Define graph flow and edges."""
        # Set entry point
        self.graph.set_entry_point("load_mdl")
        
        # Define linear flow
        self.graph.add_edge("load_mdl", "chunk_schema")
        self.graph.add_edge("chunk_schema", "embed_documents")
        self.graph.add_edge("embed_documents", "index_documents")
        
        # End after indexing
        self.graph.add_edge("index_documents", END)
    
    async def run(
        self,
        mdl_file_path: Optional[str] = None,
        datasource_id: Optional[str] = None,
        project_id: Optional[str] = "default"
    ) -> Dict[str, Any]:
        """
        Run the indexing workflow.
        
        Args:
            mdl_file_path: Path to MDL JSON file (overrides default)
            datasource_id: Specific datasource ID to process
            project_id: Project identifier for organization
            
        Returns:
            Result state with indexing statistics
        """
        initial_state = {
            "mdl_file_path": mdl_file_path or self.mdl_file_path,
            "datasource_id": datasource_id,
            "project_id": project_id,
            "errors": [],
            "indexed_count": 0,
            "table_count": 0,
            "column_count": 0,
            "status": "initialized"
        }
        
        result = await self.execute(initial_state)
        
        # Log final results
        if result.get("status") == "indexed":
            logger.info(
                f"Indexing completed: {result.get('indexed_count')} documents indexed "
                f"from {result.get('table_count')} tables, "
                f"{result.get('column_count')} columns"
            )
        else:
            logger.warning(f"Indexing ended with status: {result.get('status')}")
            if result.get("errors"):
                logger.error(f"Errors: {result['errors']}")
        
        return result


# Convenience function for quick usage
async def index_mdl_schema(
    mdl_file_path: str,
    datasource_id: Optional[str] = None,
    project_id: str = "default",
    chunk_by: str = "table",
    gemini_api_key: Optional[str] = None,
    gemini_model: str = "models/text-embedding-004",
    qdrant_url: str = "http://localhost:6333",
    qdrant_collection: str = "db_schema",
    vector_size: int = 768,
    recreate_collection: bool = False
) -> Dict[str, Any]:
    """
    Index MDL schema into Qdrant vector store using Google Gemini embeddings.
    
    Args:
        mdl_file_path: Path to MDL JSON file
        datasource_id: Specific datasource ID to process
        project_id: Project identifier
        chunk_by: Chunking strategy - "table" or "column"
        gemini_api_key: Google Gemini API key (if None, uses env var)
        gemini_model: Gemini embedding model name
        qdrant_url: URL of Qdrant server
        qdrant_collection: Name of Qdrant collection
        vector_size: Dimension of embedding vectors
        recreate_collection: Whether to recreate collection if exists
        
    Returns:
        Indexing result with statistics
    """
    graph = DBSchemaIndexingGraph(
        mdl_file_path=mdl_file_path,
        chunk_by=chunk_by,
        gemini_api_key=gemini_api_key,
        gemini_model=gemini_model,
        qdrant_url=qdrant_url,
        qdrant_collection=qdrant_collection,
        vector_size=vector_size,
        recreate_collection=recreate_collection
    )
    
    graph.build()
    
    return await graph.run(
        datasource_id=datasource_id,
        project_id=project_id
    )
