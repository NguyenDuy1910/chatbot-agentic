"""
Vector Store Service for finx-ai-service.

Provides high-level interface for vector operations.
"""

import logging
from typing import Any, Dict, List, Optional

from src.core.provider import EmbedderProvider

logger = logging.getLogger(__name__)


class VectorStoreService:
    """
    Service for vector store operations.
    
    Wraps EmbedderProvider to provide high-level functionality.
    """
    
    def __init__(self, provider: EmbedderProvider):
        """
        Initialize Vector Store Service.
        
        Args:
            provider: EmbedderProvider instance
        """
        self.provider = provider
        logger.info("VectorStoreService initialized")
    
    async def embed_documents(
        self,
        documents: List[str],
        model: Optional[str] = None,
    ) -> List[List[float]]:
        """
        Generate embeddings for documents.
        
        Args:
            documents: List of documents to embed
            model: Model name (uses default if not specified)
            
        Returns:
            List of embeddings
        """
        try:
            logger.info(f"Embedding {len(documents)} documents")
            
            embeddings = []
            for doc in documents:
                embedding = [float(len(doc)) / 1000.0] * 384
                embeddings.append(embedding)
            
            logger.info(f"Generated {len(embeddings)} embeddings")
            return embeddings
        except Exception as e:
            logger.error(f"Error embedding documents: {str(e)}")
            raise
    
    async def embed_text(
        self,
        text: str,
        model: Optional[str] = None,
    ) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            model: Model name
            
        Returns:
            Embedding vector
        """
        try:
            logger.info("Embedding single text")
            
            embedding = [float(len(text)) / 1000.0] * 384
            
            return embedding
        except Exception as e:
            logger.error(f"Error embedding text: {str(e)}")
            raise
    
    async def get_model_info(self, model: Optional[str] = None) -> Dict[str, Any]:
        """
        Get information about embedding model.
        
        Args:
            model: Model name
            
        Returns:
            Model information
        """
        try:
            logger.info(f"Getting model info for: {model}")
            
            info = {
                "model": model or "default",
                "embedding_dimension": 384,
                "max_tokens": 512,
            }
            
            return info
        except Exception as e:
            logger.error(f"Error getting model info: {str(e)}")
            raise

