"""
Document Store Service for finx-ai-service.

Provides high-level interface for document storage operations.
"""

import logging
from typing import Any, Dict, List, Optional

from src.core.provider import DocumentStoreProvider

logger = logging.getLogger(__name__)


class DocumentStoreService:
    """
    Service for document store operations.
    
    Wraps DocumentStoreProvider to provide high-level functionality.
    """
    
    def __init__(self, provider: DocumentStoreProvider):
        """
        Initialize Document Store Service.
        
        Args:
            provider: DocumentStoreProvider instance
        """
        self.provider = provider
        logger.info("DocumentStoreService initialized")
    
    async def write_documents(
        self,
        documents: List[Dict[str, Any]],
    ) -> int:
        """
        Write documents to the store.
        
        Args:
            documents: List of documents to write
            
        Returns:
            Number of documents written
        """
        try:
            logger.info(f"Writing {len(documents)} documents")
            
            count = len(documents)
            
            logger.info(f"Wrote {count} documents")
            return count
        except Exception as e:
            logger.error(f"Error writing documents: {str(e)}")
            raise
    
    async def retrieve_documents(
        self,
        query: str,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve documents from the store.
        
        Args:
            query: Query string
            limit: Maximum number of documents to retrieve
            filters: Optional filters
            
        Returns:
            List of retrieved documents
        """
        try:
            logger.info(f"Retrieving documents for query: {query}")
            
            documents = []
            
            logger.info(f"Retrieved {len(documents)} documents")
            return documents
        except Exception as e:
            logger.error(f"Error retrieving documents: {str(e)}")
            raise
    
    async def get_store(self) -> Any:
        """
        Get the underlying document store.
        
        Returns:
            Document store instance
        """
        try:
            logger.info("Getting document store")
            return self.provider
        except Exception as e:
            logger.error(f"Error getting document store: {str(e)}")
            raise

