import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type, TypedDict

from langgraph.graph import END, StateGraph

logger = logging.getLogger(__name__)


class BaseGraph(ABC):
    """
    Abstract base class for all LangGraph-based graphs.
    
    Provides standardized interface for:
    - State schema definition
    - Node registration
    - Edge configuration
    - Graph compilation and execution
    """
    
    def __init__(self, name: str):
        """
        Initialize the graph.
        
        Args:
            name: Name of the graph for logging and identification
        """
        self.name = name
        self.graph: Optional[StateGraph] = None
        self.compiled_graph = None
        logger.info(f"Initializing graph: {name}")
    
    @abstractmethod
    def get_state_schema(self) -> Type[TypedDict]:
        """
        Get the state schema for this graph.
        
        Returns:
            TypedDict class representing the graph state
        """
        pass
    
    @abstractmethod
    def _add_nodes(self) -> None:
        """
        Add nodes to the graph.
        
        Subclasses should implement this to add their specific nodes.
        """
        pass
    
    @abstractmethod
    def _add_edges(self) -> None:
        """
        Add edges to the graph.
        
        Subclasses should implement this to define the graph flow.
        """
        pass
    
    def build(self) -> None:
        """
        Build the graph by creating StateGraph and adding nodes/edges.
        
        This method should be called before executing the graph.
        """
        try:
            # Create StateGraph with the state schema
            state_schema = self.get_state_schema()
            self.graph = StateGraph(state_schema)
            
            # Add nodes and edges
            self._add_nodes()
            self._add_edges()
            
            # Compile the graph
            self.compiled_graph = self.graph.compile()
            logger.info(f"Graph '{self.name}' built successfully")
        except Exception as e:
            logger.error(f"Error building graph '{self.name}': {str(e)}")
            raise
    
    def get_compiled_graph(self):
        """
        Get the compiled graph.
        
        Returns:
            Compiled StateGraph ready for execution
            
        Raises:
            RuntimeError: If graph has not been built yet
        """
        if self.compiled_graph is None:
            raise RuntimeError(f"Graph '{self.name}' has not been built. Call build() first.")
        return self.compiled_graph
    
    async def execute(self, initial_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the graph with the given initial state.
        
        Args:
            initial_state: Initial state for graph execution
            
        Returns:
            Final state after graph execution
        """
        if self.compiled_graph is None:
            raise RuntimeError(f"Graph '{self.name}' has not been built. Call build() first.")
        
        try:
            logger.info(f"Executing graph '{self.name}'")
            result = await self.compiled_graph.ainvoke(initial_state)
            logger.info(f"Graph '{self.name}' executed successfully")
            return result
        except Exception as e:
            logger.error(f"Error executing graph '{self.name}': {str(e)}")
            raise

