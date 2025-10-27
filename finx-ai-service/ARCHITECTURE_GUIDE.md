# LangGraph Architecture Guide

## Overview

This guide explains the refactored LangGraph-based architecture for finx-ai-service. The new structure improves scalability and maintainability for implementing multiple agents.

## Directory Structure

```
finx-ai-service/src/
├── core/                          # Core abstractions
│   ├── __init__.py
│   ├── base_graph.py              # Abstract BaseGraph class
│   ├── base_state.py              # Base state definition
│   ├── node_registry.py           # Node registration utilities
│   ├── provider.py                # Provider interfaces
│   ├── engine.py                  # Existing engine
│   ├── pipeline.py                # Existing pipeline
│   └── ...
│
├── graphs/                        # Graph implementations
│   ├── __init__.py
│   ├── question_recommend/        # Question Recommendation Agent
│   │   ├── __init__.py
│   │   ├── graph.py               # Graph class
│   │   ├── state.py               # State definition
│   │   └── nodes/
│   │       ├── __init__.py
│   │       ├── build_prompt_node.py
│   │       ├── generate_questions_node.py
│   │       └── normalize_response_node.py
│   │
│   └── question_answer/           # Question Answer Agent
│       ├── __init__.py
│       ├── graph.py               # Graph class
│       ├── state.py               # State definition
│       └── nodes/
│           ├── __init__.py
│           ├── validate_mdl_node.py
│           ├── chunk_mdl_node.py
│           ├── embed_documents_node.py
│           ├── clean_documents_node.py
│           └── write_documents_node.py
│
├── services/                      # Shared services
│   ├── __init__.py
│   ├── llm_service.py             # LLM service
│   ├── vector_store_service.py    # Vector store service
│   └── document_store_service.py  # Document store service
│
└── ...                            # Other modules
```

## Core Components

### 1. BaseGraph (src/core/base_graph.py)

Abstract base class for all graphs. Provides:
- State schema definition
- Node and edge management
- Graph compilation and execution

**Usage:**
```python
from src.core import BaseGraph
from langgraph.graph import END

class MyGraph(BaseGraph):
    def get_state_schema(self):
        return MyState
    
    def _add_nodes(self):
        self.graph.add_node("step1", step1_func)
    
    def _add_edges(self):
        self.graph.add_edge("step1", END)
        self.graph.set_entry_point("step1")

# Build and execute
graph = MyGraph()
graph.build()
result = await graph.execute(initial_state)
```

### 2. BaseState (src/core/base_state.py)

Base TypedDict for all states. Provides common fields:
- `errors`: List of error messages
- `warnings`: List of warning messages
- `status`: Current status (pending, processing, completed, failed)
- `metadata`: Execution metadata

**Usage:**
```python
from src.core import BaseState
from typing import TypedDict

class MyState(BaseState):
    input_data: str
    output_data: Optional[str]
```

### 3. NodeRegistry (src/core/node_registry.py)

Centralized registry for managing nodes. Supports:
- Node registration with metadata
- Node discovery by name or graph
- Node reuse across graphs

**Usage:**
```python
from src.core import register_node

@register_node("my_node", graph_name="my_graph")
async def my_node(state):
    return state
```

### 4. Services

High-level service wrappers for external integrations:

#### LLMService
```python
from src.services import LLMService

service = LLMService(llm_provider)
response = await service.generate(prompt)
```

#### VectorStoreService
```python
from src.services import VectorStoreService

service = VectorStoreService(embedder_provider)
embeddings = await service.embed_documents(documents)
```

#### DocumentStoreService
```python
from src.services import DocumentStoreService

service = DocumentStoreService(document_store_provider)
count = await service.write_documents(documents)
```

## Graph Implementations

### QuestionRecommendGraph

Generates recommended questions based on database schema.

**Flow:**
1. Build Prompt - Create prompt from schema
2. Generate Questions - Use LLM to generate
3. Normalize Response - Parse and normalize

**Usage:**
```python
from src.graphs import QuestionRecommendGraph

graph = QuestionRecommendGraph()
graph.build()

state = {
    "database_schema": "...",
    "table_names": ["table1", "table2"],
    "errors": [],
    "warnings": [],
}

result = await graph.execute(state)
print(result["recommended_questions"])
```

### QuestionAnswerGraph

Indexes database schemas into vector store.

**Flow:**
1. Validate MDL - Validate content
2. Chunk MDL - Split into chunks
3. Embed Documents - Generate embeddings
4. Clean Documents - Normalize
5. Write Documents - Store in vector DB

**Usage:**
```python
from src.graphs import QuestionAnswerGraph

graph = QuestionAnswerGraph()
graph.build()

state = {
    "mdl_content": "...",
    "database_schema": "...",
    "errors": [],
    "warnings": [],
}

result = await graph.execute(state)
print(f"Indexed {result['document_count']} documents")
```

## Creating New Graphs

To create a new graph:

1. Create directory: `src/graphs/my_graph/`
2. Create `state.py` extending BaseState
3. Create `nodes/` directory with node files
4. Create `graph.py` with class extending BaseGraph
5. Create `__init__.py` with exports
6. Update `src/graphs/__init__.py`

**Example:**
```python
# src/graphs/my_graph/state.py
from src.core import BaseState

class MyGraphState(BaseState):
    input: str
    output: Optional[str] = None

# src/graphs/my_graph/nodes/process_node.py
async def process_node(state):
    state["output"] = state["input"].upper()
    return state

# src/graphs/my_graph/graph.py
from src.core import BaseGraph
from langgraph.graph import END

class MyGraph(BaseGraph):
    def get_state_schema(self):
        return MyGraphState
    
    def _add_nodes(self):
        self.graph.add_node("process", process_node)
    
    def _add_edges(self):
        self.graph.set_entry_point("process")
        self.graph.add_edge("process", END)
```

## Best Practices

1. **State Management**: Keep state clean and minimal
2. **Error Handling**: Always append errors to state["errors"]
3. **Logging**: Use logging for debugging
4. **Async**: Use async/await for all node functions
5. **Testing**: Test nodes independently
6. **Documentation**: Document node purposes and inputs/outputs

## Testing

```python
import pytest
from src.graphs import QuestionRecommendGraph

@pytest.mark.asyncio
async def test_question_recommend_graph():
    graph = QuestionRecommendGraph()
    graph.build()
    
    state = {
        "database_schema": "CREATE TABLE users (id INT, name VARCHAR)",
        "table_names": ["users"],
        "errors": [],
        "warnings": [],
    }
    
    result = await graph.execute(state)
    assert result["status"] == "completed"
    assert len(result["recommended_questions"]) > 0
```

## Migration from Old Structure

If migrating from old structure:
1. Update imports to use new modules
2. Gradually migrate pipelines to new graphs
3. Keep backward compatibility where needed
4. Update tests to use new structure

## Troubleshooting

**Import Errors**: Ensure all `__init__.py` files exist
**Missing Dependencies**: Install required packages
**State Errors**: Check state schema matches TypedDict definition
**Node Errors**: Ensure nodes are async and return state

## References

- LangGraph Documentation: https://langchain-ai.github.io/langgraph/
- Python TypedDict: https://docs.python.org/3/library/typing.html#typing.TypedDict

