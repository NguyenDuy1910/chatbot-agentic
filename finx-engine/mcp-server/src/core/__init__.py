"""
Core abstractions and utilities for finx-ai-service.

This module provides the foundational abstractions and utilities used across
all graphs and pipelines in the application.

Core Components:
- BaseGraph: Abstract base class for all LangGraph-based graphs
- BaseState: Base state definition for all pipelines
- NodeRegistry: Registry for managing and discovering nodes
- Providers: Abstract provider interfaces for LLM, embeddings, and document storage

Architecture:
- All graphs should inherit from BaseGraph
- All graph states should extend BaseState
- Nodes can be registered using NodeRegistry for discovery and reuse
- Providers offer a consistent interface for external services

Usage:
    from src.core import BaseGraph, BaseState, NodeRegistry
    from src.core.provider import LLMProvider, EmbedderProvider, DocumentStoreProvider
    
    # Create a custom graph
    class MyGraph(BaseGraph):
        def get_state_schema(self):
            return MyState
        
        def _add_nodes(self):
            self.graph.add_node("step1", step1_node)
        
        def _add_edges(self):
            self.graph.add_edge("step1", END)
    
    # Register nodes
    @register_node("my_node", graph_name="my_graph")
    async def my_node(state):
        ...
"""

from .base_graph import BaseGraph
from .base_state import BaseState, PipelineMetadata
from .node_registry import NodeRegistry, register_node
from .provider import LLMProvider, EmbedderProvider, DocumentStoreProvider

__all__ = [
    # Base abstractions
    "BaseGraph",
    "BaseState",
    "PipelineMetadata",
    # Node registry
    "NodeRegistry",
    "register_node",
    # Providers
    "LLMProvider",
    "EmbedderProvider",
    "DocumentStoreProvider",
]

