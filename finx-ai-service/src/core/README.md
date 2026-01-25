# Workflow State Management & Reusable Nodes

Hệ thống quản lý state và các node có thể tái sử dụng cho LangGraph workflows.

## 🎯 Tổng quan

Hệ thống này cung cấp:

1. **WorkflowState** - Class quản lý state chung cho tất cả workflows
2. **Base Nodes** - Các node classes có thể tái sử dụng (LLMNode, ToolNode, ValidationNode, etc.)
3. **Decorators** - Các decorator để tạo nodes nhanh chóng và dễ dàng
4. **Utilities** - Các helper functions cho routing, state management, etc.

## 📦 Các Components

### 1. State Management (`src/core/workflow_state.py`)

```python
from src.core.workflow_state import WorkflowState, create_workflow_state

# Tạo state
state = create_workflow_state(
    query="Show me sales by region",
    project_id="project_123",
    max_retries=3,
)
```

**Specialized States:**
- `SQLWorkflowState` - Cho SQL generation workflows
- `IntentClassificationState` - Cho intent classification
- `RetrievalWorkflowState` - Cho retrieval workflows
- `AssistanceWorkflowState` - Cho user assistance

### 2. Base Nodes (`src/core/base_nodes.py`)

```python
from src.core.base_nodes import LLMNode, ToolNode, ValidationNode

# LLM Node
llm_node = LLMNode(
    name="reasoning",
    user_prompt_template="prompts/reasoning.jinja2",
    output_field="reasoning_result",
)

# Tool Node
tool_node = ToolNode(
    name="execute_sql",
    tool_func=execute_sql_function,
    output_field="results",
)

# Validation Node
validation_node = ValidationNode(
    name="validate",
    validation_func=validate_function,
)
```

### 3. Decorators (`src/core/node_utils.py`)

```python
from src.core.node_utils import node, llm_node, validation_node

# LLM Decorator
@llm_node(name="generation", output_field="sql")
async def generate_sql(state):
    return {
        "user_prompt": f"Generate SQL: {state['query']}",
    }

# Validation Decorator
@validation_node(name="validate")
async def validate_sql(state):
    sql = state.get("sql")
    if not sql:
        return False, ["Empty SQL"]
    return True, []

# Generic Node Decorator
@node(name="process")
async def process_data(state):
    # Your logic
    return state
```

### 4. Utilities

```python
from src.core.node_utils import (
    route_by_validation,  # Routing với validation logic
    route_by_field,       # Routing theo field value
    get_from_state,       # Get nested values
    should_retry,         # Check retry logic
    increment_retry,      # Increment retry counter
)
```

## 🚀 Quick Start

### Example 1: Simple Workflow với Base Nodes

```python
from langgraph.graph import END, StateGraph
from src.core.workflow_state import SQLWorkflowState
from src.core.base_nodes import LLMNode, ValidationNode

# Create nodes
reasoning = LLMNode(
    name="reasoning",
    user_prompt_text="Analyze: {query}",
    output_field="reasoning",
)

generation = LLMNode(
    name="generation",
    user_prompt_text="Generate SQL for: {query}",
    output_field="sql",
)

# Build graph
graph = StateGraph(SQLWorkflowState)
graph.add_node("reasoning", reasoning)
graph.add_node("generation", generation)

graph.set_entry_point("reasoning")
graph.add_edge("reasoning", "generation")
graph.add_edge("generation", END)

compiled = graph.compile()
```

### Example 2: Workflow với Decorators

```python
from src.core.node_utils import llm_node, validation_node

@llm_node(name="generation", output_field="sql")
async def generate(state):
    return {"user_prompt": f"Generate SQL: {state['query']}"}

@validation_node(name="validate")
async def validate(state):
    sql = state.get("sql")
    return bool(sql), [] if sql else ["Empty SQL"]

# Add to graph
graph.add_node("generation", generate)
graph.add_node("validate", validate)
```

### Example 3: Workflow với Retry Logic

```python
from src.core.node_utils import route_by_validation

# Define validation router
router = route_by_validation(
    valid_route="done",
    invalid_route="retry",
    max_retries_route="give_up",
)

# Add conditional edges
graph.add_conditional_edges("validation", router, {
    "done": END,
    "retry": "correction_node",
    "give_up": "fallback_node",
})
```

## 📚 Documentation

Xem hướng dẫn chi tiết tại: [`docs/WORKFLOW_STATE_AND_NODES_GUIDE.md`](../docs/WORKFLOW_STATE_AND_NODES_GUIDE.md)

## 🎨 Examples

Xem ví dụ đầy đủ tại: [`examples/workflow_with_reusable_nodes.py`](../examples/workflow_with_reusable_nodes.py)

```bash
# Run example
python examples/workflow_with_reusable_nodes.py
```

## 🔑 Key Features

### ✅ State Management
- **Unified state** cho tất cả workflows
- **Specialized states** cho từng loại workflow (SQL, Intent, Retrieval, etc.)
- **Automatic tracking** của LLM calls, tool executions, timings
- **Error & warning tracking** built-in

### ✅ Reusable Nodes
- **LLMNode** - Gọi LLM với prompt templates
- **ToolNode** - Thực thi tools/functions
- **ValidationNode** - Validate data với rules
- **JSONParseNode** - Parse JSON responses
- **TransformNode** - Transform data
- **ConditionalNode** - Conditional routing

### ✅ Simple Decorators
- `@node` - Tạo node từ function
- `@llm_node` - Tạo LLM node
- `@validation_node` - Tạo validation node
- `@tool_node` - Tạo tool node

### ✅ Powerful Utilities
- Conditional routing helpers
- Retry logic helpers
- State management helpers
- History tracking
- Nested state access

## 🎯 Best Practices

### 1. Chọn approach phù hợp:

**Base Node Classes** → Reusable, configurable nodes
```python
node = LLMNode(name="my_node", user_prompt_template="template.jinja2")
```

**Decorators** → Quick prototyping, simple logic
```python
@llm_node(name="my_node")
async def my_node(state): ...
```

**Custom Functions** → Complex, unique requirements
```python
async def my_custom_node(state): 
    # Complex logic
    return state
```

### 2. State Management
- Luôn dùng `create_workflow_state()` để tạo state
- Extend từ specialized states khi cần (SQLWorkflowState, etc.)
- Track errors và warnings trong state

### 3. Error Handling
- Nodes tự động catch errors nếu dùng decorators
- Store errors trong `state["errors"]`
- Log đầy đủ

### 4. Performance
- Track timing với `step_timings`
- Monitor token usage với `total_llm_tokens`
- Use `observe=True` cho Langfuse tracking

## 🔧 Architecture

```
src/core/
├── base_state.py          # BaseState class
├── workflow_state.py      # WorkflowState & specialized states
├── base_graph.py          # BaseGraph class
├── base_nodes.py          # Reusable node classes
└── node_utils.py          # Decorators & utilities
```

## 💡 Migration Guide

### Migrating existing workflows:

**Before:**
```python
async def my_node(state: Dict[str, Any]) -> Dict[str, Any]:
    state["current_step"] = "my_node"
    try:
        generator = state.get("context", {}).get("generator")
        response = await generator(prompt=...)
        state["result"] = response
    except Exception as e:
        state["errors"].append(str(e))
    return state
```

**After (với decorator):**
```python
@llm_node(name="my_node", output_field="result")
async def my_node(state: Dict[str, Any]) -> Dict:
    return {"user_prompt": "..."}
```

**After (với base class):**
```python
my_node = LLMNode(
    name="my_node",
    user_prompt_text="...",
    output_field="result",
)
```

## 🤝 Contributing

Khi thêm node mới:
1. Extend từ `BaseNode` nếu tạo class
2. Use decorators nếu tạo function
3. Luôn log đầy đủ
4. Track timing và errors
5. Add unit tests

## 📝 Files Reference

- `src/core/workflow_state.py` - State management
- `src/core/base_nodes.py` - Reusable node classes
- `src/core/node_utils.py` - Decorators & utilities
- `docs/WORKFLOW_STATE_AND_NODES_GUIDE.md` - Full documentation
- `examples/workflow_with_reusable_nodes.py` - Complete examples
