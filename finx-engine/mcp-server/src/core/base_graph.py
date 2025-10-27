import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, TypedDict, Type

from langgraph.graph import StateGraph, END

logger = logging.getLogger(__name__)


class BaseGraph(ABC):
    """
    Abstract base class for all LangGraph-based graphs.
    
    Provides a standardized interface for creating and managing
    LangGraph StateGraphs with consistent patterns for:
    - State schema definition
    - Node registration
    - Edge configuration
    - Error handling
    - Execution
    
    Subclasses should:
    1. Define their state schema as a TypedDict
    2. Implement _add_nodes() to register all nodes
    3. Implement _add_edges() to configure graph flow
    4. Optionally override _configure_error_handling()
    
    Example:
        class MyGraph(BaseGraph):
            def get_state_schema(self) -> Type[TypedDict]:
                return MyGraphState
            
            def _add_nodes(self) -> None:
                self.graph.add_node("step1", step1_node)
                self.graph.add_node("step2", step2_node)
            
            def _add_edges(self) -> None:
                self.graph.add_edge("step1", "step2")
                self.graph.add_edge("step2", END)
    """
    
    def __init__(self, name: str):
        """
        Initialize the base graph.
        
        Args:
            name: Name of the graph for logging and identification
        """
        self.name = name
        self.graph: StateGraph = None
        self.compiled_graph = None
        logger.info(f"Initializing graph: {name}")
    
    @abstractmethod
    def get_state_schema(self) -> Type[TypedDict]:
        """
        Get the TypedDict state schema for this graph.
        
        Returns:
            TypedDict class defining the state structure
        """
        pass
    
    @abstractmethod
    def _add_nodes(self) -> None:
        """
        Add all nodes to the graph.
        
        Subclasses must implement this to register all nodes
        that will be used in the graph.
        """
        pass
    
    @abstractmethod
    def _add_edges(self) -> None:
        """
        Add all edges to the graph.
        
        Subclasses must implement this to configure the flow
        between nodes, including conditional edges and error handling.
        """
        pass
    
    def _configure_error_handling(self) -> None:
        """
        Configure error handling for the graph.
        
        Default implementation adds an error_handler node.
        Subclasses can override to customize error handling.
        """
        from src.langgraph.nodes.base import error_handler_node
        
        if "error_handler" not in self.graph.nodes:
            self.graph.add_node("error_handler", error_handler_node)
    
    def build(self) -> "BaseGraph":
        """
        Build the graph by creating StateGraph and adding nodes/edges.
        
        Returns:
            Self for method chaining
        """
        logger.info(f"Building graph: {self.name}")
        
        # Create StateGraph with state schema
        state_schema = self.get_state_schema()
        self.graph = StateGraph(state_schema)
        
        # Add nodes and edges
        self._add_nodes()
        self._configure_error_handling()
        self._add_edges()
        
        # Compile graph
        self.compiled_graph = self.graph.compile()
        logger.info(f"Graph {self.name} built successfully")
        
        return self
    
    def get_compiled_graph(self):
        """
        Get the compiled graph ready for execution.
        
        Returns:
            Compiled StateGraph
            
        Raises:
            RuntimeError: If graph has not been built yet
        """
        if self.compiled_graph is None:
            raise RuntimeError(
                f"Graph {self.name} has not been built. "
                "Call build() before executing."
            )
        return self.compiled_graph
    
    async def execute(self, initial_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the graph with the given initial state.
        
        Args:
            initial_state: Initial state dictionary
            
        Returns:
            Final state after graph execution
        """
        logger.info(f"Executing graph: {self.name}")
        
        graph = self.get_compiled_graph()
        result = await graph.ainvoke(initial_state)
        
        logger.info(f"Graph {self.name} execution completed")
        return result
    
    def get_description(self) -> str:
        """
        Get a human-readable description of the graph.
        
        Returns:
            Description string
        """
        return f"Graph: {self.name}"


__all__ = [
    "BaseGraph",
]

