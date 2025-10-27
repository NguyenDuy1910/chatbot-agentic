# LangGraph Pipeline Quick Reference

## 🚀 Quick Start

```python
from src.core.pipeline import LangGraphPipeline, PipelineComponent
from langgraph.graph import StateGraph, END

# 1. Define your state
from typing import TypedDict, Optional, List, Any, Dict

class MyState(TypedDict, total=False):
    input: str
    result: Optional[str]
    errors: List[str]
    status: str

# 2. Create node functions
async def process_node(state: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "result": state["input"].upper(),
        "status": "completed"
    }

# 3. Create pipeline class
class MyPipeline(LangGraphPipeline[MyState]):
    def create_graph(self) -> StateGraph:
        graph = StateGraph(MyState)
        graph.add_node("process", process_node)
        graph.set_entry_point("process")
        graph.add_edge("process", END)
        return graph.compile()
    
    async def run(self, input_text: str) -> Dict[str, Any]:
        state = self.create_initial_state(
            state_class=MyState,
            pipeline_name="my_pipeline",
            input=input_text
        )
        return await self.graph.ainvoke(state)

# 4. Use it
components = PipelineComponent()
pipeline = MyPipeline(components)
result = await pipeline.run("hello")
print(result["result"])  # "HELLO"
```

---

## 📋 Common Patterns

### Pattern 1: Simple Sequential Pipeline

```python
graph = StateGraph(MyState)
graph.add_node("step1", step1_func)
graph.add_node("step2", step2_func)
graph.add_node("step3", step3_func)

graph.set_entry_point("step1")
graph.add_edge("step1", "step2")
graph.add_edge("step2", "step3")
graph.add_edge("step3", END)
```

### Pattern 2: Conditional Routing

```python
from src.langgraph.nodes.base import create_conditional_router

graph.add_conditional_edges(
    "validation",
    create_conditional_router("success", "error_handler"),
    {
        "success": "next_step",
        "error_handler": "error_handler"
    }
)
```

### Pattern 3: Retry Loop

```python
def should_retry(state):
    if state.get("success"):
        return END
    if state.get("iterations", 0) < 3:
        return "retry"
    return "error_handler"

graph.add_conditional_edges(
    "validate",
    should_retry,
    {
        END: END,
        "retry": "process",  # Loop back
        "error_handler": "error_handler"
    }
)
```

### Pattern 4: Using Providers

```python
from src.langgraph.nodes.base import node_error_handler

@node_error_handler
async def generate_with_llm(state):
    llm_provider = state.get("llm_provider")
    if not llm_provider:
        raise ValueError("LLM provider required")
    
    llm = llm_provider.get_model()
    response = await llm.ainvoke("Your prompt")
    
    return {
        "result": response.content,
        "status": "completed"
    }
```

---

## 🏗️ File Structure Template

```
src/
├── langgraph/
│   ├── state/
│   │   └── schemas.py          # Add your state here
│   ├── nodes/
│   │   └── my_nodes.py         # Add your nodes here
│   ├── graphs/
│   │   └── my_graph.py         # Add your graph here
│   └── pipelines/
│       └── my_pipeline.py      # Add your pipeline here
```

### schemas.py Template

```python
from typing import TypedDict, List, Optional, Any, Dict

class MyPipelineState(TypedDict, total=False):
    # Inputs
    input_data: str
    
    # Processing
    processed: Optional[Dict[str, Any]]
    
    # Output
    result: Optional[str]
    
    # Metadata
    errors: List[str]
    warnings: List[str]
    status: str
    current_step: str
    
    # Providers
    llm_provider: Optional[Any]
    embedder_provider: Optional[Any]
    
    # Observability
    metadata: Optional[Dict[str, Any]]
```

### my_nodes.py Template

```python
import logging
from typing import Dict, Any
from src.langgraph.nodes.base import node_error_handler

logger = logging.getLogger(__name__)

@node_error_handler
async def my_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Node description."""
    logger.info("Processing in my_node")
    
    # Get inputs
    input_data = state.get("input_data")
    
    # Process
    result = process(input_data)
    
    # Return updates
    return {
        "processed": result,
        "status": "processing",
        "current_step": "my_node"
    }
```

### my_graph.py Template

```python
import logging
from langgraph.graph import StateGraph, END
from src.langgraph.state.schemas import MyPipelineState
from src.langgraph.nodes.my_nodes import my_node
from src.langgraph.nodes.base import error_handler_node, create_conditional_router

logger = logging.getLogger(__name__)

def create_my_graph() -> StateGraph:
    """Create my pipeline graph."""
    logger.info("Creating my graph")
    
    graph = StateGraph(MyPipelineState)
    
    # Add nodes
    graph.add_node("my_node", my_node)
    graph.add_node("error_handler", error_handler_node)
    
    # Add edges
    graph.set_entry_point("my_node")
    graph.add_conditional_edges(
        "my_node",
        create_conditional_router(END, "error_handler"),
        {
            END: END,
            "error_handler": "error_handler"
        }
    )
    graph.add_edge("error_handler", END)
    
    return graph.compile()
```

### my_pipeline.py Template

```python
import logging
from typing import Dict, Any
from langgraph.graph import StateGraph

from src.core.pipeline import LangGraphPipeline, PipelineComponent
from src.langgraph.state.schemas import MyPipelineState
from src.langgraph.graphs.my_graph import create_my_graph

logger = logging.getLogger(__name__)

class MyPipeline(LangGraphPipeline[MyPipelineState]):
    """My custom pipeline."""
    
    def __init__(self, components: PipelineComponent):
        super().__init__(components)
        self.graph = self.create_graph()
    
    def create_graph(self) -> StateGraph:
        return create_my_graph()
    
    async def run(self, input_data: str) -> Dict[str, Any]:
        """Execute pipeline."""
        logger.info(f"Starting pipeline with: {input_data[:50]}...")
        
        initial_state = self.create_initial_state(
            state_class=MyPipelineState,
            pipeline_name="my_pipeline",
            input_data=input_data,
            processed=None,
            result=None
        )
        
        try:
            result = await self.graph.ainvoke(initial_state)
            start_time = initial_state["metadata"]["start_time"]
            return self.finalize_result(result, start_time)
        except Exception as e:
            logger.error(f"Pipeline failed: {e}", exc_info=True)
            start_time = initial_state["metadata"]["start_time"]
            error_result = {
                **initial_state,
                "status": "failed",
                "errors": [str(e)]
            }
            return self.finalize_result(error_result, start_time)
```

---

## 🔧 Common Operations

### Initialize Pipeline

```python
from src.core.pipeline import PipelineComponent
from src.core.provider import OpenAILLMProvider

components = PipelineComponent(
    llm_provider=OpenAILLMProvider(),
    # ... other providers
)

pipeline = MyPipeline(components)
```

### Run Pipeline

```python
result = await pipeline.run(input_data="test")

if result["status"] == "completed":
    print(result["result"])
else:
    print(f"Failed: {result['errors']}")
```

### Access State in Nodes

```python
@node_error_handler
async def my_node(state):
    # Input data
    data = state.get("input_data")
    
    # Providers
    llm = state.get("llm_provider")
    embedder = state.get("embedder_provider")
    
    # Previous results
    prev = state.get("previous_result")
    
    # Process and return
    return {"result": processed_data}
```

### Add Error Handling

```python
@node_error_handler  # Auto error handling
async def my_node(state):
    # This will catch exceptions and add to errors
    risky_operation()
    return {"result": data}

# Or manual
async def my_node(state):
    try:
        result = risky_operation()
        return {"result": result}
    except Exception as e:
        return {
            "errors": state.get("errors", []) + [str(e)],
            "status": "failed"
        }
```

---

## 📊 State Schema Conventions

```python
class MyState(TypedDict, total=False):
    # ===== INPUTS =====
    # User-provided inputs
    input_field: str
    
    # ===== PROCESSING STAGES =====
    # Intermediate results (one per stage)
    stage1_result: Optional[Dict]
    stage2_result: Optional[Dict]
    
    # ===== OUTPUT =====
    # Final output
    final_result: Optional[str]
    
    # ===== METADATA & ERROR HANDLING =====
    # Always include these
    errors: List[str]
    warnings: List[str]
    status: str  # "pending", "processing", "completed", "failed"
    current_step: str
    
    # ===== PROVIDERS =====
    # Injected at runtime
    llm_provider: Optional[Any]
    embedder_provider: Optional[Any]
    document_store_provider: Optional[Any]
    engine: Optional[Any]
    
    # ===== OBSERVABILITY =====
    # Added automatically
    metadata: Optional[Dict[str, Any]]
```

---

## ⚡ Best Practices

### DO ✅

- Use `@node_error_handler` decorator
- Use `.get()` with defaults: `state.get("field", default)`
- Log at node entry/exit
- Validate providers before use
- Set max iterations for loops
- Use TypedDict for states
- Return only fields to update
- Test nodes independently

### DON'T ❌

- Access state fields without `.get()`
- Mutate state directly
- Skip error handling
- Create infinite loops
- Mix business logic with routing
- Return entire state from nodes
- Forget to compile graph
- Skip provider validation

---

## 🐛 Debugging Tips

### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Print State at Each Node

```python
async def debug_node(state):
    print(f"State: {state}")
    return {}

graph.add_node("debug", debug_node)
graph.add_edge("step1", "debug")
graph.add_edge("debug", "step2")
```

### Check Execution Metadata

```python
result = await pipeline.run(input="test")
print(f"Duration: {result['metadata']['duration_seconds']}s")
print(f"Steps: {result['current_step']}")
print(f"Status: {result['status']}")
```

---

## 📚 Quick Links

- **Full Guide**: `docs/LANGGRAPH_PIPELINE_GUIDE.md`
- **Example**: `src/core/example_langgraph_pipeline.py`
- **Base Classes**: `src/core/pipeline.py`
- **Summary**: `LANGGRAPH_PIPELINE_IMPLEMENTATION_SUMMARY.md`

---

## 💡 Need Help?

1. Check `docs/LANGGRAPH_PIPELINE_GUIDE.md` for detailed explanations
2. Study `src/core/example_langgraph_pipeline.py` for a complete example
3. Look at existing graphs in `src/langgraph/graphs/`
4. Review node utilities in `src/langgraph/nodes/base.py`

---

**Last Updated**: 2025-01-26  
**Version**: 2.0.0
