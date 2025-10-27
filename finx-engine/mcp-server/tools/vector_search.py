"""
Vector Database Search Tool for MCP
Provides tools to search and retrieve information from vector database
"""

import logging
import json
from typing import Any, Dict, List, Callable
from providers.vector_db import VectorDatabaseProvider


logger = logging.getLogger(__name__)


class VectorSearchTool:
    """MCP tool for vector database search operations"""
    
    def __init__(
        self,
        vector_db_provider: VectorDatabaseProvider,
        embedder: Callable[[str], List[float]] = None
    ):
        """Initialize vector search tool"""
        self.provider = vector_db_provider
        self.embedder = embedder
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Get MCP tool definitions for vector search operations"""
        return [
            {
                "name": "vector_search_similar",
                "description": "Search for similar vectors in the database",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query_vector": {
                            "type": "array",
                            "items": {"type": "number"},
                            "description": "Query vector for similarity search"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results (default: 10)",
                            "default": 10
                        },
                        "score_threshold": {
                            "type": "number",
                            "description": "Minimum similarity score (0-1, default: 0.5)",
                            "default": 0.5
                        }
                    },
                    "required": ["query_vector"]
                }
            },
            {
                "name": "vector_search_by_text",
                "description": "Search vector database by text query",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "Text to search for"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results (default: 10)",
                            "default": 10
                        },
                        "score_threshold": {
                            "type": "number",
                            "description": "Minimum similarity score (0-1, default: 0.5)",
                            "default": 0.5
                        }
                    },
                    "required": ["text"]
                }
            },
            {
                "name": "vector_get_collection_info",
                "description": "Get information about the vector collection",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            }
        ]
    
    def search_similar(
        self,
        query_vector: List[float],
        limit: int = 10,
        score_threshold: float = 0.5
    ) -> Dict[str, Any]:
        """
        Search for similar vectors
        
        Args:
            query_vector: Query vector
            limit: Maximum results
            score_threshold: Minimum similarity score
            
        Returns:
            Search results
        """
        if not self.provider.is_available():
            return {
                "success": False,
                "error": "Vector database provider not available",
                "results": []
            }
        
        try:
            results = self.provider.search_similar(
                query_vector=query_vector,
                limit=limit,
                score_threshold=score_threshold
            )
            
            return {
                "success": True,
                "count": len(results),
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Error in vector_search_similar: {e}")
            return {
                "success": False,
                "error": str(e),
                "results": []
            }
    
    def search_by_text(
        self,
        text: str,
        limit: int = 10,
        score_threshold: float = 0.5
    ) -> Dict[str, Any]:
        """
        Search by text query
        
        Args:
            text: Text to search for
            limit: Maximum results
            score_threshold: Minimum similarity score
            
        Returns:
            Search results
        """
        if not self.provider.is_available():
            return {
                "success": False,
                "error": "Vector database provider not available",
                "results": []
            }
        
        if not self.embedder:
            return {
                "success": False,
                "error": "Embedder not configured",
                "results": []
            }
        
        try:
            results = self.provider.search_by_text(
                text=text,
                embedder=self.embedder,
                limit=limit,
                score_threshold=score_threshold
            )
            
            return {
                "success": True,
                "query": text,
                "count": len(results),
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Error in vector_search_by_text: {e}")
            return {
                "success": False,
                "error": str(e),
                "results": []
            }
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get collection information"""
        if not self.provider.is_available():
            return {
                "success": False,
                "error": "Vector database provider not available"
            }
        
        try:
            info = self.provider.get_collection_info()
            
            if info:
                return {
                    "success": True,
                    "collection": info
                }
            else:
                return {
                    "success": False,
                    "error": "Could not retrieve collection info"
                }
                
        except Exception as e:
            logger.error(f"Error in vector_get_collection_info: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def handle_tool_call(self, tool_name: str, tool_input: Dict[str, Any]) -> str:
        """Handle MCP tool calls"""
        try:
            if tool_name == "vector_search_similar":
                result = self.search_similar(**tool_input)
            elif tool_name == "vector_search_by_text":
                result = self.search_by_text(**tool_input)
            elif tool_name == "vector_get_collection_info":
                result = self.get_collection_info()
            else:
                result = {"error": f"Unknown tool: {tool_name}"}
            
            return json.dumps(result)
            
        except Exception as e:
            logger.error(f"Error handling tool call {tool_name}: {e}")
            return json.dumps({"error": str(e)})

