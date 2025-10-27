import logging
from typing import Optional, List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from config import MCPServerConfig


logger = logging.getLogger(__name__)


class VectorDatabaseProvider:
    """Provider for vector database operations"""
    
    def __init__(self, config: MCPServerConfig):
        """Initialize vector database provider"""
        self.config = config
        self.client = None
        self.collection_name = config.qdrant_collection_name
        
        try:
            self.client = QdrantClient(
                url=config.qdrant_url,
                api_key=config.qdrant_api_key
            )
            logger.info(f"Vector database provider initialized: {config.qdrant_url}")
        except Exception as e:
            logger.error(f"Failed to initialize vector database: {e}")
            self.client = None
    
    def is_available(self) -> bool:
        """Check if vector database provider is available"""
        return self.client is not None
    
    def search_similar(
        self,
        query_vector: List[float],
        limit: int = 10,
        score_threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors in the database
        
        Args:
            query_vector: Query vector
            limit: Maximum number of results
            score_threshold: Minimum similarity score
            
        Returns:
            List of similar documents
        """
        if not self.is_available():
            logger.warning("Vector database provider not available")
            return []
        
        try:
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit,
                score_threshold=score_threshold
            )
            
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "id": result.id,
                    "score": result.score,
                    "payload": result.payload
                })
            
            logger.info(f"Found {len(formatted_results)} similar vectors")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching similar vectors: {e}")
            return []
    
    def search_by_text(
        self,
        text: str,
        embedder,
        limit: int = 10,
        score_threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Search by text (requires embedder to convert text to vector)
        
        Args:
            text: Text to search for
            embedder: Embedder function to convert text to vector
            limit: Maximum results
            score_threshold: Minimum similarity score
            
        Returns:
            List of similar documents
        """
        try:
            # Convert text to vector using embedder
            query_vector = embedder(text)
            
            # Search using the vector
            return self.search_similar(query_vector, limit, score_threshold)
            
        except Exception as e:
            logger.error(f"Error searching by text: {e}")
            return []
    
    def get_collection_info(self) -> Optional[Dict[str, Any]]:
        """Get information about the collection"""
        if not self.is_available():
            logger.warning("Vector database provider not available")
            return None
        
        try:
            collection_info = self.client.get_collection(self.collection_name)
            
            return {
                "name": self.collection_name,
                "points_count": collection_info.points_count,
                "vectors_count": collection_info.vectors_count,
                "config": {
                    "distance": str(collection_info.config.params.distance),
                    "vector_size": collection_info.config.params.vectors.size
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return None
    
    def store_document(
        self,
        doc_id: str,
        vector: List[float],
        metadata: Dict[str, Any]
    ) -> bool:
        """
        Store a document with its vector
        
        Args:
            doc_id: Document ID
            vector: Document vector
            metadata: Document metadata
            
        Returns:
            Success status
        """
        if not self.is_available():
            logger.warning("Vector database provider not available")
            return False
        
        try:
            point = PointStruct(
                id=hash(doc_id) % (10 ** 8),
                vector=vector,
                payload=metadata
            )
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            
            logger.info(f"Stored document: {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing document: {e}")
            return False
    
    def delete_document(self, doc_id: str) -> bool:
        """
        Delete a document from the database
        
        Args:
            doc_id: Document ID
            
        Returns:
            Success status
        """
        if not self.is_available():
            logger.warning("Vector database provider not available")
            return False
        
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=[hash(doc_id) % (10 ** 8)]
            )
            
            logger.info(f"Deleted document: {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            return False

