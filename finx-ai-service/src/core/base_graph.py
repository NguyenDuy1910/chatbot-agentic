import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type, TypedDict

from langgraph.graph import END, StateGraph

logger = logging.getLogger(__name__)


class BaseGraph(ABC):
    
    def __init__(self, name: str):
        self.name = name
        self.graph: Optional[StateGraph] = None
        self.compiled_graph = None
        logger.info(f"Initializing graph: {name}")
    
    @abstractmethod
    def get_state_schema(self) -> Type[TypedDict]:
        pass
    
    @abstractmethod
    def _add_nodes(self) -> None:
        pass
    
    @abstractmethod
    def _add_edges(self) -> None:
        pass
    
    def build(self) -> None:
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
            logger.warning(f"Graph '{self.name}' not built. Auto-building now...")
            self.build()

        try:
            logger.info(f"Executing graph '{self.name}'")
            result = await self.compiled_graph.ainvoke(initial_state)
            logger.info(f"Graph '{self.name}' executed successfully")
            return result
        except Exception as e:
            logger.error(f"Error executing graph '{self.name}': {str(e)}")
            raise



    async def stream(self, initial_state: Dict[str, Any]):
        """
        Stream the graph execution with the given initial state.

        Args:
            initial_state: Initial state for graph execution

        Yields:
            State updates during graph execution
        """
        if self.compiled_graph is None:
            logger.warning(f"Graph '{self.name}' not built. Auto-building now...")
            self.build()

        try:
            logger.info(f"Streaming graph '{self.name}'")
            async for chunk in self.compiled_graph.astream(initial_state):
                yield chunk
            logger.info(f"Graph '{self.name}' streaming completed")
        except Exception as e:
            logger.error(f"Error streaming graph '{self.name}': {str(e)}")
            raise

    def get_graph_visualization(self) -> str:
        """
        Get a Mermaid diagram representation of the graph.

        Returns:
            Mermaid diagram string

        Raises:
            RuntimeError: If graph has not been built yet
        """
        if self.compiled_graph is None:
            raise RuntimeError(f"Graph '{self.name}' has not been built. Call build() first.")

        try:
            # Get the mermaid representation
            mermaid = self.compiled_graph.get_graph().draw_mermaid()
            return mermaid
        except Exception as e:
            logger.error(f"Error generating graph visualization: {str(e)}")
            raise

    def save_graph_visualization(self, output_path: str) -> None:
        """
        Save the graph visualization to a file.

        Args:
            output_path: Path to save the Mermaid diagram
        """
        mermaid = self.get_graph_visualization()
        with open(output_path, 'w') as f:
            f.write(mermaid)
        logger.info(f"Graph visualization saved to {output_path}")

