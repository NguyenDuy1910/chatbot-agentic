# Base Workflow Guide

## Overview

The `base_workflow` is a dictionary that contains compiled LangGraph workflow instances. It's the foundation of the Ask Service and enables intelligent routing between different processing workflows.

## Architecture

```
base_workflow (dict)
├── "sql_processing" → SQLProcessingGraph (compiled)
├── "intent_recommendation" → IntentRecommendationGraph (compiled)
└── "assistance_visualization" → AssistanceVisualizationGraph (compiled)
```

## Key Concepts

### 1. BaseGraph Class

All workflows inherit from `BaseGraph` which provides:

- **State Schema**: Type-safe state management
- **Node Management**: Add processing nodes
- **Edge Configuration**: Define workflow flow
- **Compilation**: Build executable graph
- **Execution**: Run with sync/async/streaming

<augment_code_snippet path="finx-ai-service/src/core/base_graph.py" mode="EXCERPT">
````python
class BaseGraph(ABC):
    def __init__(self, name: str):
        self.name = name
        self.graph: Optional[StateGraph] = None
        self.compiled_graph = None
    
    def build(self) -> None:
        """Build and compile the graph"""
        state_schema = self.get_state_schema()
        self.graph = StateGraph(state_schema)
        self._add_nodes()
        self._add_edges()
        self.compiled_graph = self.graph.compile()
````
</augment_code_snippet>

### 2. Creating Workflows

Each workflow has a factory function that creates and compiles the graph:

```python
from src.workflows import (
    create_sql_processing_graph,
    create_intent_recommendation_graph,
    create_assistance_visualization_graph,
)

# These functions automatically call .build() internally
sql_graph = create_sql_processing_graph()
intent_graph = create_intent_recommendation_graph()
assistance_graph = create_assistance_visualization_graph()
```

### 3. The base_workflow Dictionary

Combine all workflows into a single dictionary:

```python
base_workflow = {
    "sql_processing": sql_graph,
    "intent_recommendation": intent_graph,
    "assistance_visualization": assistance_graph,
}
```

This is exactly what happens in `main.py` during application startup.

## Compilation Process

### Automatic Compilation

When you call `create_*_graph()`, the graph is automatically compiled:

```python
def create_intent_recommendation_graph() -> IntentRecommendationGraph:
    graph = IntentRecommendationGraph()
    graph.build()  # ← Compilation happens here
    return graph
```

### Manual Compilation

You can also compile manually:

```python
from src.workflows.generation.sql_processing import SQLProcessingGraph

graph = SQLProcessingGraph()  # Not compiled yet
graph.build()                  # Now compiled
```

### What Happens During Compilation?

1. **Create StateGraph**: Initialize with state schema
2. **Add Nodes**: Register all processing nodes
3. **Add Edges**: Define workflow flow and routing
4. **Compile**: Generate executable graph

```python
def build(self) -> None:
    # 1. Create StateGraph
    state_schema = self.get_state_schema()
    self.graph = StateGraph(state_schema)
    
    # 2. Add nodes
    self._add_nodes()
    
    # 3. Add edges
    self._add_edges()
    
    # 4. Compile
    self.compiled_graph = self.graph.compile()
```

## Running Workflows

### Method 1: Async Execution

```python
result = await graph.execute(initial_state)
```

### Method 2: Sync Execution

```python
result = graph.invoke(initial_state)
```

### Method 3: Streaming Execution

```python
async for chunk in graph.stream(initial_state):
    print(chunk)
```

### Method 4: Direct Compiled Graph

```python
compiled = graph.get_compiled_graph()
result = compiled.invoke(initial_state)
```

## Complete Example

```python
import asyncio
from src.workflows import (
    create_intent_recommendation_graph,
    create_initial_intent_recommendation_state,
)

async def main():
    # 1. Create and compile graph
    graph = create_intent_recommendation_graph()
    
    # 2. Create initial state
    initial_state = create_initial_intent_recommendation_state(
        query="What is the total revenue?",
        project_id="project-123",
        db_schemas=["sales"],
    )
    
    # 3. Execute
    result = await graph.execute(initial_state)
    
    # 4. Use results
    print(f"Intent: {result['intent']}")
    print(f"Confidence: {result['confidence_score']}")

asyncio.run(main())
```

## Workflow Types

### 1. Intent Recommendation Workflow

**Purpose**: Classify user queries into intents

**Intents**:
- `TEXT_TO_SQL`: Database queries
- `GENERAL`: General assistance
- `USER_GUIDE`: Help documentation
- `MISLEADING_QUERY`: Unclear queries

**Usage**:
```python
graph = create_intent_recommendation_graph()
state = create_initial_intent_recommendation_state(
    query="Show me sales data",
    project_id="proj-1",
)
result = await graph.execute(state)
intent = result['intent']
```

### 2. SQL Processing Workflow

**Purpose**: Generate and execute SQL queries

**Features**:
- SQL generation from natural language
- Validation and correction
- Query execution
- Result formatting

**Usage**:
```python
graph = create_sql_processing_graph()
state = create_initial_sql_processing_state(
    query="Total revenue for Q1",
    db_schemas=["sales"],
    is_followup=False,
)
result = await graph.execute(state)
sql = result['generated_sql']
```

### 3. Assistance & Visualization Workflow

**Purpose**: Provide assistance and generate visualizations

**Features**:
- Data assistance
- User guide help
- Chart generation
- Chart adjustment

**Usage**:
```python
graph = create_assistance_visualization_graph()
state = create_initial_assistance_visualization_state(
    query="How do I create a report?",
    intent="USER_GUIDE",
)
result = await graph.execute(state)
response = result['assistance_response']
```

## See Also

- [Simple Workflow Demo](../examples/simple_workflow_demo.py)
- [Complete Workflow Examples](../examples/workflow_usage_example.py)
- [Ask Service Integration](./ASK_SERVICE_INTEGRATION.md)

