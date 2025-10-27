"""
Document Store Service for finx-ai-service.

Provides a unified interface for document storage operations across all graphs and pipelines.
Wraps the DocumentStoreProvider to offer high-level document store functionality.
"""

import logging
from typing import Any, Dict, List, Optional

from src.core.provider import DocumentStoreProvider

logger = logging.getLogger(__name__)


class DocumentStoreService:
    """
    Unified document store service for all graphs and pipelines.
    
    Provides a high-level interface for document operations including:
    - Document writing
    - Document retrieval
    - Document deletion
    - Document filtering
    """
    
    def __init__(self, provider: DocumentStoreProvider):
        """
        Initialize document store service.
        
        Args:
            provider: DocumentStoreProvider instance for document operations
        """
        self.provider = provider
        logger.info(f"DocumentStoreService initialized with provider: {provider.__class__.__name__}")
    
    async def write_documents(
        self,
        documents: List[Dict[str, Any]],
        policy: str = "OVERWRITE",
    ) -> Dict[str, Any]:
        """
        Write documents to the document store.
        
        Args:
            documents: List of documents to write
            policy: Duplicate policy (OVERWRITE, SKIP, FAIL)
            
        Returns:
            Dictionary with write results
        """
        try:
            logger.info(f"Writing {len(documents)} documents to store")
            
            from haystack.components.writers import DocumentWriter
            from haystack.document_stores.types import DuplicatePolicy
            
            doc_store = self.provider.get_store()
            
            # Convert policy string to DuplicatePolicy enum
            policy_enum = DuplicatePolicy[policy.upper()]
            
            writer = DocumentWriter(
                document_store=doc_store,
                policy=policy_enum,
            )
            
            result = await writer.run(documents=documents)
            
            logger.info(f"Successfully wrote {len(documents)} documents")
            return result
            
        except Exception as e:
            logger.error(f"Document writing failed: {str(e)}", exc_info=True)
            raise
    
    async def retrieve_documents(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve documents from the document store.
        
        Args:
            query: Query string
            top_k: Number of top results to return
            filters: Optional filters to apply
            
        Returns:
            List of retrieved documents
        """
        try:
            logger.info(f"Retrieving documents with query: {query}")
            
            retriever = self.provider.get_retriever()
            result = await retriever.run(
                query=query,
                top_k=top_k,
                filters=filters,
            )
            
            documents = result.get("documents", [])
            logger.info(f"Retrieved {len(documents)} documents")
            
            return documents
            
        except Exception as e:
            logger.error(f"Document retrieval failed: {str(e)}", exc_info=True)
            raise
    
    def get_store(self):
        """
        Get the underlying document store.
        
        Returns:
            Document store instance
        """
        return self.provider.get_store()


__all__ = [
    "DocumentStoreService",
]

