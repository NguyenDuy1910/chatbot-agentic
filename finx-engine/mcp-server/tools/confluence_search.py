"""
Confluence Search Tool for MCP
Provides tools to search and retrieve information from Confluence
"""

import logging
import json
from typing import Any, Dict, List
from providers.confluence import ConfluenceProvider


logger = logging.getLogger(__name__)


class ConfluenceSearchTool:
    """MCP tool for Confluence search operations"""
    
    def __init__(self, confluence_provider: ConfluenceProvider):
        """Initialize Confluence search tool"""
        self.provider = confluence_provider
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Get MCP tool definitions for Confluence operations"""
        return [
            {
                "name": "confluence_search",
                "description": "Search for content in Confluence by text query",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query text"
                        },
                        "space_key": {
                            "type": "string",
                            "description": "Optional Confluence space key to limit search"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results (default: 10)",
                            "default": 10
                        },
                        "content_type": {
                            "type": "string",
                            "description": "Type of content: page, blogpost (default: page)",
                            "default": "page"
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "confluence_get_page",
                "description": "Get full content of a Confluence page",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "page_id": {
                            "type": "string",
                            "description": "Confluence page ID"
                        }
                    },
                    "required": ["page_id"]
                }
            },
            {
                "name": "confluence_search_by_label",
                "description": "Search for Confluence pages by label",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "label": {
                            "type": "string",
                            "description": "Label to search for"
                        },
                        "space_key": {
                            "type": "string",
                            "description": "Optional space key to limit search"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results (default: 10)",
                            "default": 10
                        }
                    },
                    "required": ["label"]
                }
            }
        ]
    
    def search_content(
        self,
        query: str,
        space_key: str = None,
        limit: int = 10,
        content_type: str = "page"
    ) -> Dict[str, Any]:
        """
        Search for content in Confluence
        
        Args:
            query: Search query
            space_key: Optional space key
            limit: Maximum results
            content_type: Type of content
            
        Returns:
            Search results
        """
        if not self.provider.is_available():
            return {
                "success": False,
                "error": "Confluence provider not available",
                "results": []
            }
        
        try:
            results = self.provider.search_content(
                query=query,
                space_key=space_key,
                limit=limit,
                content_type=content_type
            )
            
            return {
                "success": True,
                "query": query,
                "count": len(results),
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Error in confluence_search: {e}")
            return {
                "success": False,
                "error": str(e),
                "results": []
            }
    
    def get_page(self, page_id: str) -> Dict[str, Any]:
        """
        Get full content of a Confluence page
        
        Args:
            page_id: Page ID
            
        Returns:
            Page content
        """
        if not self.provider.is_available():
            return {
                "success": False,
                "error": "Confluence provider not available"
            }
        
        try:
            page = self.provider.get_page_content(page_id)
            
            if page:
                return {
                    "success": True,
                    "page": page
                }
            else:
                return {
                    "success": False,
                    "error": f"Page not found: {page_id}"
                }
                
        except Exception as e:
            logger.error(f"Error in confluence_get_page: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def search_by_label(
        self,
        label: str,
        space_key: str = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Search for pages by label
        
        Args:
            label: Label to search for
            space_key: Optional space key
            limit: Maximum results
            
        Returns:
            Search results
        """
        if not self.provider.is_available():
            return {
                "success": False,
                "error": "Confluence provider not available",
                "results": []
            }
        
        try:
            results = self.provider.search_by_label(
                label=label,
                space_key=space_key,
                limit=limit
            )
            
            return {
                "success": True,
                "label": label,
                "count": len(results),
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Error in confluence_search_by_label: {e}")
            return {
                "success": False,
                "error": str(e),
                "results": []
            }
    
    async def handle_tool_call(self, tool_name: str, tool_input: Dict[str, Any]) -> str:
        """Handle MCP tool calls"""
        try:
            if tool_name == "confluence_search":
                result = self.search_content(**tool_input)
            elif tool_name == "confluence_get_page":
                result = self.get_page(**tool_input)
            elif tool_name == "confluence_search_by_label":
                result = self.search_by_label(**tool_input)
            else:
                result = {"error": f"Unknown tool: {tool_name}"}
            
            return json.dumps(result)
            
        except Exception as e:
            logger.error(f"Error handling tool call {tool_name}: {e}")
            return json.dumps({"error": str(e)})

