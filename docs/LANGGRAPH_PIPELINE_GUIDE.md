# LangGraph Pipeline Implementation Guide

## Overview

This guide explains how to implement pipelines using the new **LangGraph-based architecture** in the FinX AI Chatbot system. The LangGraph framework provides explicit state management, conditional routing, and composable workflows.

## Table of Contents

- [Architecture](#architecture)
- [Core Components](#core-components)
- [Creating a Pipeline](#creating-a-pipeline)
- [State Management](#state-management)
- [Node Functions](#node-functions)
- [Routing and Control Flow](#routing-and-control-flow)
- [Provider Injection](#provider-injection)
- [Error Handling](#error-handling)
- [Examples](#examples)
- [Migration from Hamilton](#migration-from-hamilton)

---

## Architecture

### LangGraph vs Hamilton

**Before (Hamilton)**:
```python
from hamilton.async_driver import AsyncDriver
from src.core.pipeline import BasicPipeline

class MyPipeline(BasicPipeline):
    def __init__(self, pipe: AsyncDriver):
        super().__init__(pipe)
    
    async def run(self, **kwargs):
        return await self._pipe.execute(...)
```

**After (LangGraph)**:
```python
from langgraph.graph import StateGraph, END
from src.core.pipeline import LangGraphPipeline

class MyPipeline(LangGraphPipeline[MyState]):
    def __init__(self, components: PipelineComponent):
        super().__init__(components)
        self.graph = self.create_graph()
    
    def create_graph(self) -> StateGraph:
        graph = StateGraph(MyState)
        # Define nodes and edges
        return graph.compile()
    
    async def run(self, **kwargs):
        initial_state = self.create_initial_state(...)
        return await self.graph.ainvoke(initial_state)
```

### Key Benefits

1. **Explicit State Management**: All data flows through typed state dictionaries
2. **Conditional Routing**: Dynamic workflow based on state conditions
3. **Human-in-the-Loop**: Built-in support for interrupts and approvals
4. **Checkpointing**: Save and restore pipeline state
5. **Error Recovery**: Graceful error handling with fallback paths
6. **Observability**: Complete execution traces with metadata

---

## Core Components

### 1. LangGraphPipeline Base Class

```python
from src.core.pipeline import LangGraphPipeline, PipelineComponent
from typing import Dict, Any
from langgraph.graph import StateGraph

class MyPipeline(LangGraphPipeline[MyStateSchema]):
    """
    Custom pipeline implementation.
    
    Type parameter MyStateSchema defines the state structure.
    """
    
    def __init__(self, components: PipelineComponent):
        super().__init__(components)
        self.graph = self.create_graph()
    
    def create_graph(self) -> StateGraph:
        """Define your graph structure"""
        ...
    
    async def run(self, **kwargs) -> Dict[str, Any]:
        """Execute the pipeline"""
        ...
```

### 2. PipelineComponent

Container for all provider dependencies:

```python
from src.core.pipeline import PipelineComponent
from src.core.provider import (
    LLMProvider,
    EmbedderProvider,
    DocumentStoreProvider
)
from src.core.engine import Engine

components = PipelineComponent(
    llm_provider=my_llm_provider,
    embedder_provider=my_embedder_provider,
    document_store_provider=my_doc_store_provider,
    engine=my_engine,
)

# Access providers
llm = components.llm_provider.get_model()
embedder = components.embedder_provider.get_embedder()

# Inject into state
state = components.inject_into_state(initial_state)
```

### 3. State Schemas

Define your state structure using TypedDict:

```python
from typing import TypedDict, List, Optional, Any, Dict

class MyPipelineState(TypedDict, total=False):
    """
    State schema for MyPipeline.
    
    Fields marked as total=False are optional.
    """
    # ===== INPUTS =====
    input_text: str
    parameters: Dict[str, Any]
    
    # ===== PROCESSING STAGES =====
    processed_data: Optional[Dict[str, Any]]
    intermediate_result: Optional[str]
    
    # ===== OUTPUT =====
    final_result: Optional[str]
    
    # ===== METADATA & ERROR HANDLING =====
    errors: List[str]
    warnings: List[str]
    status: str
    current_step: str
    
    # ===== PROVIDERS =====
    llm_provider: Optional[Any]
    embedder_provider: Optional[Any]
    
    # ===== OBSERVABILITY =====
    metadata: Optional[Dict[str, Any]]
```

---

## Creating a Pipeline

### Step 1: Define State Schema

Create your state schema in `src/langgraph/state/schemas.py`:

```python
from typing import TypedDict, List, Optional, Any, Dict

class TextSummarizationState(TypedDict, total=False):
    """State for text summarization pipeline."""
    
    # Inputs
    text: str
    max_length: int
    style: str  # 'concise', 'detailed', 'bullet-points'
    
    # Processing
    chunks: Optional[List[str]]
    chunk_summaries: Optional[List[str]]
    
    # Output
    final_summary: Optional[str]
    
    # Error handling
    errors: List[str]
    warnings: List[str]
    status: str
    current_step: str
    
    # Providers
    llm_provider: Optional[Any]
    
    # Metadata
    metadata: Optional[Dict[str, Any]]
```

### Step 2: Create Node Functions

Create your node functions in `src/langgraph/nodes/`:

```python
# src/langgraph/nodes/summarization_nodes.py

import logging
from typing import Dict, Any
from src.langgraph.nodes.base import node_error_handler

logger = logging.getLogger(__name__)


@node_error_handler
async def chunk_text_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Split text into manageable chunks."""
    logger.info("Chunking text")
    
    text = state.get("text", "")
    max_chunk_size = 1000
    
    # Simple chunking by sentences
    chunks = []
    current_chunk = ""
    
    for sentence in text.split(". "):
        if len(current_chunk) + len(sentence) > max_chunk_size:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence
        else:
            current_chunk += sentence + ". "
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return {
        "chunks": chunks,
        "status": "chunking",
        "current_step": "chunk_text",
    }


@node_error_handler
async def summarize_chunks_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Summarize each chunk using LLM."""
    logger.info("Summarizing chunks")
    
    llm_provider = state.get("llm_provider")
    chunks = state.get("chunks", [])
    style = state.get("style", "concise")
    
    if not llm_provider:
        raise ValueError("LLM provider is required")
    
    llm = llm_provider.get_model()
    summaries = []
    
    for chunk in chunks:
        prompt = f"Summarize this text in a {style} style:\n\n{chunk}"
        response = await llm.ainvoke(prompt)
        summaries.append(response.content)
    
    return {
        "chunk_summaries": summaries,
        "status": "summarizing",
        "current_step": "summarize_chunks",
    }


@node_error_handler
async def combine_summaries_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Combine chunk summaries into final summary."""
    logger.info("Combining summaries")
    
    llm_provider = state.get("llm_provider")
    chunk_summaries = state.get("chunk_summaries", [])
    max_length = state.get("max_length", 500)
    
    if not llm_provider:
        raise ValueError("LLM provider is required")
    
    llm = llm_provider.get_model()
    
    # Combine all summaries
    combined = "\n\n".join(chunk_summaries)
    
    # Final summarization
    prompt = f"""Combine these summaries into a single coherent summary 
    of approximately {max_length} words:
    
    {combined}"""
    
    response = await llm.ainvoke(prompt)
    
    return {
        "final_summary": response.content,
        "status": "completed",
        "current_step": "combine_summaries",
    }
```

### Step 3: Create the Graph

Create your graph in `src/langgraph/graphs/`:

```python
# src/langgraph/graphs/summarization_graph.py

import logging
from langgraph.graph import StateGraph, END

from src.langgraph.state.schemas import TextSummarizationState
from src.langgraph.nodes.summarization_nodes import (
    chunk_text_node,
    summarize_chunks_node,
    combine_summaries_node,
)
from src.langgraph.nodes.base import (
    error_handler_node,
    create_conditional_router
)

logger = logging.getLogger(__name__)


def create_summarization_graph() -> StateGraph:
    """Create text summarization graph."""
    logger.info("Creating summarization graph")
    
    graph = StateGraph(TextSummarizationState)
    
    # Add nodes
    graph.add_node("chunk_text", chunk_text_node)
    graph.add_node("summarize_chunks", summarize_chunks_node)
    graph.add_node("combine_summaries", combine_summaries_node)
    graph.add_node("error_handler", error_handler_node)
    
    # Add edges
    graph.add_edge("chunk_text", "summarize_chunks")
    
    graph.add_conditional_edges(
        "summarize_chunks",
        create_conditional_router("combine_summaries", "error_handler"),
        {
            "combine_summaries": "combine_summaries",
            "error_handler": "error_handler",
        }
    )
    
    graph.add_conditional_edges(
        "combine_summaries",
        create_conditional_router(END, "error_handler"),
        {
            END: END,
            "error_handler": "error_handler",
        }
    )
    
    graph.add_edge("error_handler", END)
    
    # Set entry point
    graph.set_entry_point("chunk_text")
    
    return graph.compile()
```

### Step 4: Create Pipeline Class

Create your pipeline in `src/langgraph/pipelines/`:

```python
# src/langgraph/pipelines/summarization_pipeline.py

import logging
from typing import Dict, Any, Optional
from langgraph.graph import StateGraph

from src.core.pipeline import LangGraphPipeline, PipelineComponent
from src.langgraph.state.schemas import TextSummarizationState
from src.langgraph.graphs.summarization_graph import create_summarization_graph

logger = logging.getLogger(__name__)


class TextSummarizationPipeline(LangGraphPipeline[TextSummarizationState]):
    """
    Text summarization pipeline using LangGraph.
    
    Example:
        ```python
        components = PipelineComponent(llm_provider=my_llm_provider)
        pipeline = TextSummarizationPipeline(components)
        
        result = await pipeline.run(
            text="Long text to summarize...",
            max_length=200,
            style="bullet-points"
        )
        
        print(result["final_summary"])
        ```
    """
    
    def __init__(self, components: PipelineComponent):
        super().__init__(components)
        self.graph = self.create_graph()
    
    def create_graph(self) -> StateGraph:
        """Create the summarization graph."""
        return create_summarization_graph()
    
    async def run(
        self,
        text: str,
        max_length: int = 500,
        style: str = "concise",
    ) -> Dict[str, Any]:
        """
        Execute text summarization.
        
        Args:
            text: Text to summarize
            max_length: Maximum length of final summary
            style: Summarization style ('concise', 'detailed', 'bullet-points')
            
        Returns:
            Result dictionary with final_summary
        """
        logger.info(f"Starting text summarization (length: {len(text)} chars)")
        
        # Create initial state
        initial_state = self.create_initial_state(
            state_class=TextSummarizationState,
            pipeline_name="text_summarization",
            text=text,
            max_length=max_length,
            style=style,
            chunks=None,
            chunk_summaries=None,
            final_summary=None,
        )
        
        try:
            # Execute graph
            result = await self.graph.ainvoke(initial_state)
            
            # Finalize result
            start_time = initial_state["metadata"]["start_time"]
            return self.finalize_result(result, start_time)
            
        except Exception as e:
            logger.error(f"Summarization failed: {e}", exc_info=True)
            
            start_time = initial_state["metadata"]["start_time"]
            error_result = {
                **initial_state,
                "status": "failed",
                "errors": [str(e)],
            }
            
            return self.finalize_result(error_result, start_time)
```

### Step 5: Use the Pipeline

```python
from src.core.pipeline import PipelineComponent
from src.core.provider import OpenAILLMProvider
from src.langgraph.pipelines.summarization_pipeline import TextSummarizationPipeline

# Create components
components = PipelineComponent(
    llm_provider=OpenAILLMProvider()
)

# Create pipeline
pipeline = TextSummarizationPipeline(components)

# Run pipeline
result = await pipeline.run(
    text="Your very long text here...",
    max_length=200,
    style="bullet-points"
)

# Check result
if result["status"] == "completed":
    print(result["final_summary"])
else:
    print(f"Error: {result['errors']}")
```

---

## State Management

### State Initialization

Use the `create_initial_state` method to properly initialize state:

```python
initial_state = self.create_initial_state(
    state_class=MyState,
    pipeline_name="my_pipeline",
    # Your custom fields
    input_data="...",
    parameters={},
)
```

This automatically adds:
- `errors: []`
- `warnings: []`
- `status: "pending"`
- `current_step: "pending"`
- `metadata: {...}` with trace_id, start_time, etc.
- All available providers from components

### State Updates

Nodes return partial state updates that get merged:

```python
@node_error_handler
async def my_node(state: Dict[str, Any]) -> Dict[str, Any]:
    # Process data
    result = process(state["input"])
    
    # Return only fields to update
    return {
        "processed_data": result,
        "status": "processing",
        "current_step": "my_node",
    }
```

### Accumulating Lists

For errors and warnings, use list concatenation:

```python
return {
    "errors": state.get("errors", []) + ["New error message"],
    "warnings": state.get("warnings", []) + ["Warning message"],
}
```

Or use the `node_error_handler` decorator which handles this automatically.

---

## Node Functions

### Node Signature

All node functions should follow this signature:

```python
async def my_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node description.
    
    Args:
        state: Current pipeline state
        
    Returns:
        Partial state updates
    """
    ...
```

### Using the Error Handler Decorator

Wrap nodes with `@node_error_handler` for automatic error handling:

```python
from src.langgraph.nodes.base import node_error_handler

@node_error_handler
async def my_node(state: Dict[str, Any]) -> Dict[str, Any]:
    # Your code here
    # Exceptions are automatically caught and added to errors
    result = risky_operation()
    
    return {
        "result": result,
        "status": "processing",
    }
```

### Accessing Providers in Nodes

```python
@node_error_handler
async def my_node(state: Dict[str, Any]) -> Dict[str, Any]:
    # Get providers from state
    llm_provider = state.get("llm_provider")
    embedder_provider = state.get("embedder_provider")
    doc_store_provider = state.get("document_store_provider")
    engine = state.get("engine")
    
    # Use providers
    if llm_provider:
        llm = llm_provider.get_model()
        response = await llm.ainvoke("Your prompt")
    
    return {
        "result": response.content,
    }
```

---

## Routing and Control Flow

### Sequential Flow

```python
graph.add_edge("node1", "node2")
graph.add_edge("node2", "node3")
graph.add_edge("node3", END)
```

### Conditional Routing

Using the helper function:

```python
from src.langgraph.nodes.base import create_conditional_router

graph.add_conditional_edges(
    "validation_node",
    create_conditional_router("success_node", "error_handler"),
    {
        "success_node": "success_node",
        "error_handler": "error_handler",
    }
)
```

Custom routing logic:

```python
def my_router(state: Dict[str, Any]) -> str:
    if state.get("score", 0) > 0.8:
        return "high_score_path"
    elif state.get("score", 0) > 0.5:
        return "medium_score_path"
    else:
        return "low_score_path"

graph.add_conditional_edges(
    "scoring_node",
    my_router,
    {
        "high_score_path": "high_score_node",
        "medium_score_path": "medium_score_node",
        "low_score_path": "low_score_node",
    }
)
```

### Loops and Iterations

```python
def should_retry(state: Dict[str, Any]) -> str:
    iterations = state.get("iterations", 0)
    max_iterations = state.get("max_iterations", 3)
    success = state.get("success", False)
    
    if success:
        return END
    elif iterations < max_iterations:
        return "retry"
    else:
        return "error_handler"

graph.add_conditional_edges(
    "validation_node",
    should_retry,
    {
        END: END,
        "retry": "processing_node",  # Loop back
        "error_handler": "error_handler",
    }
)
```

---

## Provider Injection

Providers are automatically injected into state by `create_initial_state`:

```python
# In your pipeline's run method
initial_state = self.create_initial_state(
    state_class=MyState,
    pipeline_name="my_pipeline",
    # ... your fields
)

# initial_state now contains:
# - llm_provider (if available in components)
# - embedder_provider (if available)
# - document_store_provider (if available)
# - engine (if available)
```

You can also manually inject:

```python
state = components.inject_into_state(initial_state)
```

---

## Error Handling

### Node-Level Error Handling

Use the `@node_error_handler` decorator:

```python
@node_error_handler
async def risky_node(state: Dict[str, Any]) -> Dict[str, Any]:
    # Any exception here will be caught and added to state["errors"]
    result = await risky_operation()
    
    return {
        "result": result,
        "status": "completed",
    }
```

### Graph-Level Error Handling

Add an error handler node:

```python
from src.langgraph.nodes.base import error_handler_node

graph.add_node("error_handler", error_handler_node)

# Route failed nodes to error handler
graph.add_conditional_edges(
    "risky_node",
    create_conditional_router("next_node", "error_handler"),
    {
        "next_node": "next_node",
        "error_handler": "error_handler",
    }
)

graph.add_edge("error_handler", END)
```

### Pipeline-Level Error Handling

Wrap execution in try-catch:

```python
async def run(self, **kwargs) -> Dict[str, Any]:
    initial_state = self.create_initial_state(...)
    
    try:
        result = await self.graph.ainvoke(initial_state)
        return self.finalize_result(result, start_time)
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        
        error_result = {
            **initial_state,
            "status": "failed",
            "errors": [str(e)],
        }
        
        return self.finalize_result(error_result, start_time)
```

---

## Examples

### Example 1: Simple Text Processing

```python
from langgraph.graph import StateGraph, END
from src.core.pipeline import LangGraphPipeline

class SimpleTextPipeline(LangGraphPipeline):
    def create_graph(self):
        graph = StateGraph(dict)
        
        async def process(state):
            text = state["text"]
            return {"result": text.upper()}
        
        graph.add_node("process", process)
        graph.set_entry_point("process")
        graph.add_edge("process", END)
        
        return graph.compile()
    
    async def run(self, text: str):
        state = {"text": text}
        return await self.graph.ainvoke(state)
```

### Example 2: Multi-Stage Processing with Error Handling

See `src/core/example_langgraph_pipeline.py` for a complete SQL generation example.

### Example 3: Using Existing Graphs

```python
from src.langgraph.graphs.db_schema_graph import create_db_schema_graph
from src.langgraph.state.schemas import DBSchemaIndexingState

class DBSchemaPipeline(LangGraphPipeline[DBSchemaIndexingState]):
    def create_graph(self):
        return create_db_schema_graph()
    
    async def run(self, mdl_str: str, project_id: str):
        initial_state = self.create_initial_state(
            state_class=DBSchemaIndexingState,
            pipeline_name="db_schema",
            mdl_str=mdl_str,
            project_id=project_id,
        )
        
        result = await self.graph.ainvoke(initial_state)
        return self.finalize_result(result, initial_state["metadata"]["start_time"])
```

---

## Migration from Hamilton

### Before (Hamilton)

```python
import hamilton.driver
from hamilton.async_driver import AsyncDriver

# Define functions
async def step1(input_data):
    return processed_data

async def step2(step1):
    return final_result

# Create driver
dr = AsyncDriver({}, step1, step2)

# Execute
result = await dr.execute(['final_result'], inputs={'input_data': data})
```

### After (LangGraph)

```python
from langgraph.graph import StateGraph, END
from src.core.pipeline import LangGraphPipeline

class MyPipeline(LangGraphPipeline):
    def create_graph(self):
        graph = StateGraph(dict)
        
        async def step1(state):
            return {"processed_data": process(state["input_data"])}
        
        async def step2(state):
            return {"final_result": finalize(state["processed_data"])}
        
        graph.add_node("step1", step1)
        graph.add_node("step2", step2)
        graph.add_edge("step1", "step2")
        graph.add_edge("step2", END)
        graph.set_entry_point("step1")
        
        return graph.compile()
    
    async def run(self, input_data):
        state = self.create_initial_state(
            state_class=dict,
            pipeline_name="my_pipeline",
            input_data=input_data
        )
        return await self.graph.ainvoke(state)
```

---

## Best Practices

1. **Use TypedDict for State**: Define explicit state schemas for type safety
2. **Keep Nodes Pure**: Nodes should be stateless functions that only depend on input state
3. **Use Error Decorator**: Always use `@node_error_handler` for automatic error handling
4. **Log Liberally**: Add logging at node entry/exit for observability
5. **Validate Providers**: Check provider availability before using them
6. **Handle Iterations**: Set max_iterations to prevent infinite loops
7. **Use Metadata**: Store execution metadata for debugging and monitoring
8. **Test Nodes Independently**: Unit test each node function separately
9. **Document State Flow**: Comment which state fields each node reads/writes
10. **Finalize Results**: Always call `finalize_result` to add timing metadata

---

## Troubleshooting

### Common Issues

**Issue**: `KeyError` when accessing state fields
- **Solution**: Use `.get()` with defaults: `state.get("field", default_value)`

**Issue**: Infinite loops in graph
- **Solution**: Add iteration counters and max limits

**Issue**: Providers not available in nodes
- **Solution**: Ensure providers are passed to PipelineComponent and state is initialized properly

**Issue**: Errors not being caught
- **Solution**: Use `@node_error_handler` decorator on node functions

**Issue**: Graph not executing
- **Solution**: Ensure you call `graph.compile()` before `ainvoke()`

---

## Additional Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangGraph Examples](https://github.com/langchain-ai/langgraph/tree/main/examples)
- [State Management Guide](https://langchain-ai.github.io/langgraph/concepts/low_level/#state)
- Internal: `src/core/example_langgraph_pipeline.py`
- Internal: `src/langgraph/pipelines/db_schema_pipeline.py`

---

**Last Updated**: 2025-01-26  
**Version**: 2.0.0  
**Author**: AI Team
