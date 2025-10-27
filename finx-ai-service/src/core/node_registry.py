"""
Node registry for managing and discovering nodes across graphs.

Provides utilities for registering, discovering, and managing nodes
in a centralized registry.
"""

import logging
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class NodeRegistry:
    """
    Centralized registry for managing nodes across all graphs.
    
    Supports:
    - Node registration with metadata
    - Node discovery by name or graph
    - Node reuse across multiple graphs
    """
    
    _instance = None
    _nodes: Dict[str, Dict[str, Any]] = {}
    _graph_nodes: Dict[str, List[str]] = {}
    
    def __new__(cls):
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def register(
        cls,
        node_name: str,
        node_func: Callable,
        graph_name: Optional[str] = None,
        description: str = "",
        tags: Optional[List[str]] = None,
    ) -> None:
        """
        Register a node in the registry.
        
        Args:
            node_name: Name of the node
            node_func: Callable function for the node
            graph_name: Optional graph name for organization
            description: Description of what the node does
            tags: Optional list of tags for categorization
        """
        registry = cls()
        
        node_info = {
            "name": node_name,
            "func": node_func,
            "graph": graph_name,
            "description": description,
            "tags": tags or [],
        }
        
        registry._nodes[node_name] = node_info
        
        if graph_name:
            if graph_name not in registry._graph_nodes:
                registry._graph_nodes[graph_name] = []
            registry._graph_nodes[graph_name].append(node_name)
        
        logger.info(f"Registered node: {node_name} (graph: {graph_name})")
    
    @classmethod
    def get_node(cls, node_name: str) -> Optional[Callable]:
        """
        Get a node function by name.
        
        Args:
            node_name: Name of the node
            
        Returns:
            Node function or None if not found
        """
        registry = cls()
        node_info = registry._nodes.get(node_name)
        return node_info["func"] if node_info else None
    
    @classmethod
    def get_nodes_by_graph(cls, graph_name: str) -> List[str]:
        """
        Get all nodes registered for a specific graph.
        
        Args:
            graph_name: Name of the graph
            
        Returns:
            List of node names for the graph
        """
        registry = cls()
        return registry._graph_nodes.get(graph_name, [])
    
    @classmethod
    def get_all_nodes(cls) -> Dict[str, Dict[str, Any]]:
        """
        Get all registered nodes.
        
        Returns:
            Dictionary of all registered nodes
        """
        registry = cls()
        return registry._nodes.copy()
    
    @classmethod
    def clear(cls) -> None:
        """Clear all registered nodes."""
        registry = cls()
        registry._nodes.clear()
        registry._graph_nodes.clear()
        logger.info("Cleared node registry")


def register_node(
    node_name: str,
    graph_name: Optional[str] = None,
    description: str = "",
    tags: Optional[List[str]] = None,
):
    """
    Decorator for registering nodes.
    
    Usage:
        @register_node("my_node", graph_name="my_graph")
        async def my_node(state):
            return state
    
    Args:
        node_name: Name of the node
        graph_name: Optional graph name
        description: Description of the node
        tags: Optional tags for categorization
    """
    def decorator(func: Callable) -> Callable:
        NodeRegistry.register(
            node_name=node_name,
            node_func=func,
            graph_name=graph_name,
            description=description,
            tags=tags,
        )
        return func
    
    return decorator

