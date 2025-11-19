"""
Base classes for workflow features and nodes.

Provides standardized interfaces for implementing features as LangGraph graphs
and individual processing nodes.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Optional, Type, TypedDict

from langgraph.graph import StateGraph, END

logger = logging.getLogger(__name__)


class FeatureNode(ABC):
    """Base class for individual feature nodes."""

    @abstractmethod
    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the node with given state."""
        pass


class FeatureGraph(ABC):
    """Base class for feature graphs composed of nodes."""

    def __init__(self, name: str):
        """Initialize feature graph."""
        self.name = name
        self.graph: Optional[StateGraph] = None
        self.compiled_graph = None
        logger.info(f"Initializing feature graph: {name}")

    @abstractmethod
    def get_state_schema(self) -> Type[TypedDict]:
        """Get the state schema for this graph."""
        pass

    @abstractmethod
    def _add_nodes(self) -> None:
        """Add all nodes to the graph."""
        pass

    @abstractmethod
    def _add_edges(self) -> None:
        """Define graph flow and edges."""
        pass

    def build(self) -> "FeatureGraph":
        """Build the graph."""
        logger.info(f"Building feature graph: {self.name}")
        state_schema = self.get_state_schema()
        self.graph = StateGraph(state_schema)
        self._add_nodes()
        self._add_edges()
        self.compiled_graph = self.graph.compile()
        logger.info(f"Feature graph {self.name} built successfully")
        return self

    def get_compiled_graph(self):
        """Get the compiled graph."""
        if self.compiled_graph is None:
            raise RuntimeError(f"Graph '{self.name}' not built. Call build() first.")
        return self.compiled_graph

    async def execute(self, initial_state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the graph."""
        if self.compiled_graph is None:
            raise RuntimeError(f"Graph '{self.name}' not built. Call build() first.")
        logger.info(f"Executing feature graph: {self.name}")
        result = await self.compiled_graph.ainvoke(initial_state)
        logger.info(f"Feature graph {self.name} executed successfully")
        return result


__all__ = ["FeatureNode", "FeatureGraph"]

