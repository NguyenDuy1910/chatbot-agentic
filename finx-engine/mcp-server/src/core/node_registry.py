"""
Node registry and utilities for managing LangGraph nodes.

Provides utilities for registering, discovering, and managing
nodes across different graphs in the application.
"""

import logging
from typing import Callable, Dict, List, Optional, Any
from functools import wraps

logger = logging.getLogger(__name__)


class NodeRegistry:
    """
    Registry for managing LangGraph nodes across the application.
    
    Provides centralized node registration, discovery, and metadata
    management to support dynamic graph construction and node reuse.
    """
    
    _nodes: Dict[str, Dict[str, Any]] = {}
    _graphs: Dict[str, List[str]] = {}
    
    @classmethod
    def register_node(
        cls,
        name: str,
        node_func: Callable,
        graph_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Callable:
        """
        Register a node function in the registry.
        
        Args:
            name: Unique name for the node
            node_func: The node function to register
            graph_name: Optional graph this node belongs to
            metadata: Optional metadata about the node
            
        Returns:
            The original node function (for use as decorator)
        """
        if name in cls._nodes:
            logger.warning(f"Overwriting existing node: {name}")
        
        cls._nodes[name] = {
            "func": node_func,
            "graph": graph_name,
            "metadata": metadata or {},
        }
        
        if graph_name:
            if graph_name not in cls._graphs:
                cls._graphs[graph_name] = []
            if name not in cls._graphs[graph_name]:
                cls._graphs[graph_name].append(name)
        
        logger.info(f"Registered node: {name}")
        return node_func
    
    @classmethod
    def get_node(cls, name: str) -> Optional[Callable]:
        """
        Get a registered node function by name.
        
        Args:
            name: Name of the node
            
        Returns:
            Node function or None if not found
        """
        if name not in cls._nodes:
            logger.warning(f"Node not found: {name}")
            return None
        
        return cls._nodes[name]["func"]
    
    @classmethod
    def get_nodes_for_graph(cls, graph_name: str) -> Dict[str, Callable]:
        """
        Get all nodes registered for a specific graph.
        
        Args:
            graph_name: Name of the graph
            
        Returns:
            Dictionary of node names to node functions
        """
        node_names = cls._graphs.get(graph_name, [])
        return {
            name: cls._nodes[name]["func"]
            for name in node_names
            if name in cls._nodes
        }
    
    @classmethod
    def list_nodes(cls, graph_name: Optional[str] = None) -> List[str]:
        """
        List all registered nodes, optionally filtered by graph.
        
        Args:
            graph_name: Optional graph name to filter by
            
        Returns:
            List of node names
        """
        if graph_name:
            return cls._graphs.get(graph_name, [])
        return list(cls._nodes.keys())
    
    @classmethod
    def get_node_metadata(cls, name: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a registered node.
        
        Args:
            name: Name of the node
            
        Returns:
            Metadata dictionary or None if not found
        """
        if name not in cls._nodes:
            return None
        
        return cls._nodes[name]["metadata"]
    
    @classmethod
    def clear(cls) -> None:
        """Clear all registered nodes and graphs."""
        cls._nodes.clear()
        cls._graphs.clear()
        logger.info("Node registry cleared")


def register_node(
    name: str,
    graph_name: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Callable:
    """
    Decorator to register a node function.
    
    Usage:
        @register_node("my_node", graph_name="my_graph")
        async def my_node(state: Dict[str, Any]) -> Dict[str, Any]:
            ...
    
    Args:
        name: Unique name for the node
        graph_name: Optional graph this node belongs to
        metadata: Optional metadata about the node
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        return NodeRegistry.register_node(
            name=name,
            node_func=func,
            graph_name=graph_name,
            metadata=metadata,
        )
    
    return decorator


__all__ = [
    "NodeRegistry",
    "register_node",
]

