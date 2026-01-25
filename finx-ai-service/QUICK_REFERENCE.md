# Quick Reference: Workflow State & Reusable Nodes

## 📦 Import

```python
# State Management
from src.core import (
    WorkflowState,
    SQLWorkflowState,
    IntentClassificationState,
    create_workflow_state,
)

# Base Nodes
from src.core import (
    LLMNode,
    ToolNode,
    ValidationNode,
    JSONParseNode,
    TransformNode,
)

# Decorators
from src.core import (
    node,
    llm_node,
    validation_node,
    tool_node,
)

# Utilities
from src.core import (
    route_by_validation,
    route_by_field,
    get_from_state,
    should_retry,
    increment_retry,
)
```

## 🚀 Quick Patterns

### Pattern 1: LLM Node với Template
```python
from src.core import LLMNode

node = LLMNode(
    name="generation",
    user_prompt_template="prompts/generation.jinja2",
    system_prompt_template="prompts/system.jinja2",
    output_field="result",
)
```

### Pattern 2: LLM Node với Decorator
```python
from src.core import llm_node

@llm_node(name="generation", output_field="result")
async def generate(state):
    return {
        "system_prompt": "You are an expert",
        "user_prompt": f"Process: {state['query']}",
    }
```

### Pattern 3: Validation với Retry
```python
from src.core import validation_node, route_by_validation

@validation_node(name="validate")
async def validate(state):
    data = state.get("data")
    if not data:
        return False, ["Empty data"]
    return True, []

# Routing
router = route_by_validation(
    valid_route="next_step",
    invalid_route="retry",
    max_retries_route="give_up",
)

graph.add_conditional_edges("validate", router, {
    "next_step": "process",
    "retry": "correction",
    "give_up": END,
})
```

### Pattern 4: Tool Execution
```python
from src.core import ToolNode

async def my_tool(data: str, config: dict):
    # Tool logic
    return result

tool_node = ToolNode(
    name="execute",
    tool_func=my_tool,
    input_builder=lambda s: {
        "data": s.get("data"),
        "config": s.get("config"),
    },
    output_field="result",
)
```

### Pattern 5: Conditional Routing
```python
from src.core import route_by_field

# Route by intent
router = route_by_field("intent", {
    "TEXT_TO_SQL": "sql_generation",
    "GENERAL": "general_response",
    "USER_GUIDE": "user_guide",
})

graph.add_conditional_edges("classify", router, {
    "sql_generation": "sql_node",
    "general_response": "general_node",
    "user_guide": "guide_node",
})
```

### Pattern 6: Create Initial State
```python
from src.core import create_workflow_state

state = create_workflow_state(
    query="Show sales by region",
    project_id="proj_123",
    session_id="sess_456",
    language="Vietnamese",
    max_retries=3,
)

# Add generator to context
state["context"]["generator"] = llm_generator
```

### Pattern 7: Transform Data
```python
from src.core import TransformNode

def clean_sql(sql: str) -> str:
    return sql.strip().replace("```sql", "").replace("```", "")

cleaner = TransformNode(
    name="clean",
    transform_func=clean_sql,
    input_field="raw_sql",
    output_field="clean_sql",
)
```

### Pattern 8: Parse JSON Response
```python
from src.core import JSONParseNode

parser = JSONParseNode(
    name="parse",
    input_field="llm_response",
    output_field="parsed_data",
    required_fields=["intent", "reasoning"],
    default_value={},
)
```

### Pattern 9: Simple Node with Decorator
```python
from src.core import node

@node(name="process")
async def process(state):
    # Your logic
    result = do_something(state["data"])
    state["result"] = result
    return state
```

### Pattern 10: Complete Workflow
```python
from langgraph.graph import END, StateGraph
from src.core import (
    SQLWorkflowState,
    create_workflow_state,
    llm_node,
    validation_node,
    route_by_validation,
)

# Define nodes
@llm_node(name="generation", output_field="sql")
async def generate(state):
    return {"user_prompt": f"Generate SQL: {state['query']}"}

@validation_node(name="validate")
async def validate(state):
    sql = state.get("sql")
    return bool(sql), [] if sql else ["Empty SQL"]

@llm_node(name="correction", output_field="sql")
async def correct(state):
    return {"user_prompt": f"Fix SQL: {state.get('validation_errors')}"}

# Build graph
graph = StateGraph(SQLWorkflowState)
graph.add_node("generation", generate)
graph.add_node("validation", validate)
graph.add_node("correction", correct)

graph.set_entry_point("generation")
graph.add_edge("generation", "validation")

router = route_by_validation()
graph.add_conditional_edges("validation", router, {
    "valid": END,
    "invalid": "correction",
    "max_retries": END,
})

graph.add_edge("correction", "validation")

compiled = graph.compile()

# Execute
initial_state = create_workflow_state(
    query="Show sales",
    max_retries=3,
)
initial_state["context"]["generator"] = llm_generator

result = await compiled.ainvoke(initial_state)
print(result["response"])
```

## 🎯 Cheat Sheet

### State Fields
```python
state = {
    # Core
    "query": str,
    "project_id": str,
    "session_id": str,
    
    # LLM
    "llm_executions": List[dict],
    "llm_response": str,
    "llm_reasoning": str,
    
    # Tools
    "tool_executions": List[dict],
    "tool_results": dict,
    
    # Validation
    "validation_info": dict,
    "is_valid": bool,
    "validation_errors": List[str],
    
    # Retry
    "retry_count": int,
    "max_retries": int,
    
    # Output
    "response": dict,
    "status": str,
    
    # Tracking
    "step_timings": dict,
    "errors": List[str],
    "warnings": List[str],
    "current_step": str,
    
    # Context
    "context": {
        "generator": callable,
        "retriever": callable,
        # ...
    }
}
```

### Common Routers
```python
# By validation
route_by_validation(valid_route, invalid_route, max_retries_route)

# By field value
route_by_field(field_name, value_map, default)

# Custom router
create_conditional_router({
    "route1": lambda s: s.get("field") == "value1",
    "route2": lambda s: s.get("field") == "value2",
})
```

### State Utilities
```python
# Get nested value
value = get_from_state(state, "context", "generator", default=None)

# Set nested value
set_in_state(state, value, "nested", "key")

# Merge states
merged = merge_states(base_state, update_state)

# Extract LLM response
text = extract_field(response, "replies", 0, default="")

# Add to history
add_to_history(state, "user", "Hello", metadata={})
```

### Retry Logic
```python
# Check if should retry
if should_retry(state):
    increment_retry(state)
    # Retry logic
else:
    reset_retry(state)
    # Give up
```

## 📝 Tips

1. **Use specialized states** for specific workflows
2. **Track everything** in state (LLM calls, tools, timings)
3. **Handle errors** gracefully with try-except
4. **Log extensively** for debugging
5. **Use decorators** for quick prototyping
6. **Use base classes** for production code
7. **Test nodes** independently
8. **Keep nodes small** and focused

## 📚 Full Documentation

- `src/core/README.md` - Quick start
- `docs/WORKFLOW_STATE_AND_NODES_GUIDE.md` - Complete guide
- `examples/workflow_with_reusable_nodes.py` - Examples
