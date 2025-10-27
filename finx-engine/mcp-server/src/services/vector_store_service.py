"""
Vector Store Service for finx-ai-service.

Provides a unified interface for vector database operations across all graphs and pipelines.
Wraps the EmbedderProvider to offer high-level vector store functionality.
"""

import logging
from typing import Any, Dict, List, Optional

from src.core.provider import EmbedderProvider

logger = logging.getLogger(__name__)


class VectorStoreService:
    """
    Unified vector store service for all graphs and pipelines.
    
    Provides a high-level interface for vector operations including:
    - Document embedding
    - Text embedding
    - Vector search
    - Similarity computation
    """
    
    def __init__(self, provider: EmbedderProvider):
        """
        Initialize vector store service.
        
        Args:
            provider: EmbedderProvider instance for embedding operations
        """
        self.provider = provider
        logger.info(f"VectorStoreService initialized with provider: {provider.__class__.__name__}")
    
    async def embed_documents(
        self,
        documents: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Embed a list of documents.
        
        Args:
            documents: List of documents to embed
            
        Returns:
            Dictionary with embedding results
        """
        try:
            logger.info(f"Embedding {len(documents)} documents")
            
            embedder = self.provider.get_document_embedder()
            result = await embedder.run(documents=documents)
            
            logger.info(f"Successfully embedded {len(documents)} documents")
            return result
            
        except Exception as e:
            logger.error(f"Document embedding failed: {str(e)}", exc_info=True)
            raise
    
    async def embed_text(
        self,
        text: str,
    ) -> List[float]:
        """
        Embed a single text string.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        try:
            logger.info(f"Embedding text with length: {len(text)}")
            
            embedder = self.provider.get_text_embedder()
            result = await embedder.run(text=text)
            
            embedding = result.get("embedding", [])
            logger.info(f"Successfully embedded text, vector size: {len(embedding)}")
            
            return embedding
            
        except Exception as e:
            logger.error(f"Text embedding failed: {str(e)}", exc_info=True)
            raise
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the configured embedding model.
        
        Returns:
            Dictionary with model information
        """
        return {
            "model": self.provider.get_model(),
        }
    
    def get_model(self) -> str:
        """
        Get the embedding model name.
        
        Returns:
            Model name string
        """
        return self.provider.get_model()


__all__ = [
    "VectorStoreService",
]

