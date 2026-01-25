# Workflow Examples

This directory contains examples demonstrating how to use the workflow system.

## Quick Start

### Simple Demo (Recommended)

The simplest way to understand base_workflow, compilation, and execution:

```bash
python examples/simple_workflow_demo.py
```

This demonstrates:
- Creating the `base_workflow` dictionary
- Graph compilation (automatic)
- Running graphs with different methods
- Visualizing graph structure

### Complete Examples

For more advanced usage patterns:

```bash
python examples/workflow_usage_example.py
```

This demonstrates:
- Manual graph creation and building
- Synchronous vs asynchronous execution
- Streaming execution
- Complete workflow orchestration
- Direct compiled graph usage

## Key Concepts

### 1. base_workflow Dictionary

The `base_workflow` is a dictionary containing all compiled workflow graphs:

```python
base_workflow = {
    "sql_processing": SQLProcessingGraph (compiled),
    "intent_recommendation": IntentRecommendationGraph (compiled),
    "assistance_visualization": AssistanceVisualizationGraph (compiled),
}
```

### 2. Graph Compilation

Graphs are automatically compiled when using factory functions:

```python
# Automatic compilation (recommended)
graph = create_intent_recommendation_graph()  # Already compiled!

# Manual compilation
graph = IntentRecommendationGraph()
graph.build()  # Now compiled
```

### 3. Running Graphs

**Async Execution** (recommended):
```python
result = await graph.execute(initial_state)
```

**Streaming Execution**:
```python
async for chunk in graph.stream(initial_state):
    print(chunk)
```

**Direct Compiled Graph**:
```python
compiled = graph.get_compiled_graph()
result = await compiled.ainvoke(initial_state)
```

## Examples Overview

### simple_workflow_demo.py

**Purpose**: Quick introduction to workflow basics

**What it shows**:
- Creating base_workflow dictionary
- Verifying compilation
- Running graphs (async)
- Streaming execution
- Graph visualization

**Run time**: ~5 seconds

**Output**: 
- Console output showing execution flow
- `intent_graph_demo.mmd` - Mermaid diagram

### workflow_usage_example.py

**Purpose**: Comprehensive workflow patterns

**What it shows**:
- Manual vs automatic graph creation
- Different execution methods
- Complete workflow orchestration
- State management
- Error handling

**Run time**: ~10 seconds

**Output**: Console output with detailed examples

## Common Patterns

### Pattern 1: Simple Query Processing

```python
import asyncio
from src.workflows import (
    create_intent_recommendation_graph,
    create_initial_intent_recommendation_state,
)

async def process_query(query: str):
    # Create graph
    graph = create_intent_recommendation_graph()
    
    # Create state
    state = create_initial_intent_recommendation_state(
        query=query,
        project_id="my-project",
    )
    
    # Execute
    result = await graph.execute(state)
    return result['intent']

# Run
intent = asyncio.run(process_query("What is the total revenue?"))
print(f"Intent: {intent}")
```

### Pattern 2: Workflow Orchestration

```python
async def orchestrate_workflows(query: str):
    # Create all workflows
    base_workflow = {
        "intent": create_intent_recommendation_graph(),
        "sql": create_sql_processing_graph(),
        "assistance": create_assistance_visualization_graph(),
    }
    
    # Step 1: Classify intent
    intent_state = create_initial_intent_recommendation_state(query=query)
    intent_result = await base_workflow["intent"].execute(intent_state)
    
    # Step 2: Route to appropriate workflow
    if intent_result['intent'] == "TEXT_TO_SQL":
        sql_state = create_initial_sql_processing_state(query=query)
        return await base_workflow["sql"].execute(sql_state)
    else:
        assist_state = create_initial_assistance_visualization_state(query=query)
        return await base_workflow["assistance"].execute(assist_state)
```

### Pattern 3: Streaming with Progress Updates

```python
async def process_with_progress(query: str):
    graph = create_intent_recommendation_graph()
    state = create_initial_intent_recommendation_state(query=query)
    
    async for chunk in graph.stream(state):
        node_name = list(chunk.keys())[0]
        print(f"Processing: {node_name}")
        
        # Update UI or progress bar here
```

## Troubleshooting

### Import Errors

If you get `ModuleNotFoundError: No module named 'src'`:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
```

### Async Errors

All workflow nodes are async. Always use:
- `await graph.execute(state)` 
- `await compiled.ainvoke(state)`
- `async for chunk in graph.stream(state)`

Do NOT use synchronous methods like `graph.invoke()`.

## See Also

- [Base Workflow Guide](../docs/BASE_WORKFLOW_GUIDE.md)
- [Ask Service Integration](../docs/ASK_SERVICE_INTEGRATION.md)
- [Ask API Documentation](../docs/ASK_API.md)

