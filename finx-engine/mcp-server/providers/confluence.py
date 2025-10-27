"""
Confluence Integration Provider
Handles searching and retrieving information from Confluence
"""

import logging
from typing import Optional, List, Dict, Any
from atlassian import Confluence
from config import MCPServerConfig


logger = logging.getLogger(__name__)


class ConfluenceProvider:
    """Provider for Confluence integration"""
    
    def __init__(self, config: MCPServerConfig):
        """Initialize Confluence provider"""
        self.config = config
        self.confluence = None
        
        if config.confluence_url and config.confluence_username and config.confluence_api_token:
            try:
                self.confluence = Confluence(
                    url=config.confluence_url,
                    username=config.confluence_username,
                    password=config.confluence_api_token
                )
                logger.info(f"Confluence provider initialized: {config.confluence_url}")
            except Exception as e:
                logger.error(f"Failed to initialize Confluence: {e}")
                self.confluence = None
        else:
            logger.warning("Confluence configuration incomplete - provider disabled")
    
    def is_available(self) -> bool:
        """Check if Confluence provider is available"""
        return self.confluence is not None
    
    def search_content(
        self,
        query: str,
        space_key: Optional[str] = None,
        limit: int = 10,
        content_type: str = "page"
    ) -> List[Dict[str, Any]]:
        """
        Search for content in Confluence
        
        Args:
            query: Search query
            space_key: Optional space key to limit search
            limit: Maximum number of results
            content_type: Type of content (page, blogpost, etc.)
            
        Returns:
            List of search results
        """
        if not self.is_available():
            logger.warning("Confluence provider not available")
            return []
        
        try:
            # Build CQL query
            cql = f'text ~ "{query}" AND type = {content_type}'
            if space_key or self.config.confluence_space_key:
                space = space_key or self.config.confluence_space_key
                cql += f' AND space = {space}'
            
            results = self.confluence.cql(cql, limit=limit)
            
            formatted_results = []
            for result in results.get("results", []):
                formatted_results.append({
                    "id": result.get("id"),
                    "title": result.get("title"),
                    "type": result.get("type"),
                    "url": result.get("_links", {}).get("webui", ""),
                    "space": result.get("space", {}).get("key", ""),
                    "excerpt": result.get("excerpt", "")
                })
            
            logger.info(f"Found {len(formatted_results)} Confluence results for: {query}")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching Confluence: {e}")
            return []
    
    def get_page_content(self, page_id: str) -> Optional[Dict[str, Any]]:
        """
        Get full content of a Confluence page
        
        Args:
            page_id: Page ID
            
        Returns:
            Page content with metadata
        """
        if not self.is_available():
            logger.warning("Confluence provider not available")
            return None
        
        try:
            page = self.confluence.get_page_by_id(
                page_id,
                expand="body.storage,metadata.labels"
            )
            
            return {
                "id": page.get("id"),
                "title": page.get("title"),
                "content": page.get("body", {}).get("storage", {}).get("value", ""),
                "labels": [label.get("name") for label in page.get("metadata", {}).get("labels", {}).get("results", [])],
                "url": page.get("_links", {}).get("webui", ""),
                "created": page.get("history", {}).get("createdDate", ""),
                "updated": page.get("history", {}).get("lastUpdated", {}).get("when", "")
            }
            
        except Exception as e:
            logger.error(f"Error getting page content: {e}")
            return None
    
    def search_by_label(
        self,
        label: str,
        space_key: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for content by label
        
        Args:
            label: Label to search for
            space_key: Optional space key
            limit: Maximum results
            
        Returns:
            List of pages with the label
        """
        if not self.is_available():
            logger.warning("Confluence provider not available")
            return []
        
        try:
            cql = f'label = "{label}"'
            if space_key or self.config.confluence_space_key:
                space = space_key or self.config.confluence_space_key
                cql += f' AND space = {space}'
            
            results = self.confluence.cql(cql, limit=limit)
            
            formatted_results = []
            for result in results.get("results", []):
                formatted_results.append({
                    "id": result.get("id"),
                    "title": result.get("title"),
                    "type": result.get("type"),
                    "url": result.get("_links", {}).get("webui", ""),
                    "space": result.get("space", {}).get("key", "")
                })
            
            logger.info(f"Found {len(formatted_results)} pages with label: {label}")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching by label: {e}")
            return []

