# Summary: Workflow State Management & Reusable Nodes

## 📦 Đã tạo

### 1. **WorkflowState Management** (`src/core/workflow_state.py`)
- ✅ `WorkflowState` - Base state với tất cả fields common
- ✅ `SQLWorkflowState` - Specialized state cho SQL workflows
- ✅ `IntentClassificationState` - Specialized state cho intent classification
- ✅ `RetrievalWorkflowState` - Specialized state cho retrieval
- ✅ `AssistanceWorkflowState` - Specialized state cho user assistance
- ✅ `create_workflow_state()` - Factory function để tạo state

### 2. **Reusable Base Nodes** (`src/core/base_nodes.py`)
- ✅ `BaseNode` - Abstract base class cho tất cả nodes
- ✅ `LLMNode` - Node để gọi LLM với prompt templates
- ✅ `JSONParseNode` - Node để parse JSON responses
- ✅ `ToolNode` - Node để execute tools/functions
- ✅ `ValidationNode` - Node để validate data
- ✅ `ConditionalNode` - Node cho conditional routing
- ✅ `TransformNode` - Node để transform data
- ✅ Helper functions: `create_llm_node()`, `create_tool_node()`, `create_validation_node()`

### 3. **Node Decorators & Utilities** (`src/core/node_utils.py`)
- ✅ `@node` - Decorator để convert function thành node
- ✅ `@llm_node` - Decorator để tạo LLM node
- ✅ `@validation_node` - Decorator để tạo validation node
- ✅ `@tool_node` - Decorator để tạo tool node
- ✅ State utilities: `get_from_state()`, `set_in_state()`, `merge_states()`
- ✅ Retry utilities: `should_retry()`, `increment_retry()`, `reset_retry()`
- ✅ Routing helpers: `create_conditional_router()`, `route_by_field()`, `route_by_validation()`
- ✅ History management: `add_to_history()`
- ✅ Response extraction: `extract_field()`

### 4. **Documentation**
- ✅ `docs/WORKFLOW_STATE_AND_NODES_GUIDE.md` - Hướng dẫn chi tiết đầy đủ
- ✅ `src/core/README.md` - Quick start guide
- ✅ `examples/workflow_with_reusable_nodes.py` - Example workflows

### 5. **Core Module Export** (`src/core/__init__.py`)
- ✅ Đã update để export tất cả classes và functions mới

## 🎯 3 Cách tạo Nodes

### 1️⃣ **Base Node Classes** (Reusable, Configurable)
```python
from src.core import LLMNode, ValidationNode

node = LLMNode(
    name="generation",
    user_prompt_template="prompts/generation.jinja2",
    output_field="sql",
)
```

**Khi nào dùng:**
- Cần reuse logic giống nhau nhiều lần
- Cần configure node với nhiều options
- Node có logic phức tạp cần structure tốt

### 2️⃣ **Decorators** (Quick, Simple)
```python
from src.core import llm_node, validation_node

@llm_node(name="generation", output_field="sql")
async def generate_sql(state):
    return {"user_prompt": f"Generate SQL: {state['query']}"}

@validation_node(name="validate")
async def validate(state):
    return bool(state.get("sql")), []
```

**Khi nào dùng:**
- Prototyping nhanh
- Logic đơn giản, specific cho một workflow
- Muốn code ngắn gọn, dễ đọc

### 3️⃣ **Custom Functions** (Complex, Unique)
```python
@node(name="complex_processing")
async def complex_node(state):
    # Complex, unique logic
    result = await do_something_complex(state)
    state["result"] = result
    return state
```

**Khi nào dùng:**
- Logic rất phức tạp, không fit vào base classes
- Cần control hoàn toàn flow
- Unique requirements không reuse được

## 📊 So sánh

| Approach | Pros | Cons | Use Case |
|----------|------|------|----------|
| **Base Classes** | ✅ Reusable<br>✅ Configurable<br>✅ Type-safe | ❌ Verbose<br>❌ Learning curve | Production, reusable nodes |
| **Decorators** | ✅ Quick<br>✅ Clean code<br>✅ Easy to read | ❌ Less flexible | Prototyping, simple logic |
| **Custom Functions** | ✅ Full control<br>✅ No constraints | ❌ Less structure<br>❌ Harder to reuse | Complex, unique logic |

## 🔄 Migration Path

### Cũ (Trước đây):
```python
async def my_node(state: Dict[str, Any]) -> Dict[str, Any]:
    state["current_step"] = "my_node"
    start_time = time.time()
    
    try:
        generator = state.get("context", {}).get("generator")
        if not generator:
            state["errors"].append("No generator")
            return state
        
        response = await generator(prompt="...", system_prompt="...")
        
        if isinstance(response, dict):
            result = response.get("replies", [""])[0]
        else:
            result = str(response)
        
        state["result"] = result
        
        if "llm_executions" not in state:
            state["llm_executions"] = []
        state["llm_executions"].append({...})
        
        duration = (time.time() - start_time) * 1000
        if "step_timings" not in state:
            state["step_timings"] = {}
        state["step_timings"]["my_node"] = duration
        
    except Exception as e:
        state["errors"].append(str(e))
        logger.error(f"Error: {e}")
    
    return state
```

### Mới (Với decorator):
```python
from src.core import llm_node

@llm_node(name="my_node", output_field="result")
async def my_node(state: Dict[str, Any]) -> Dict:
    return {
        "user_prompt": "...",
        "system_prompt": "...",
    }
```

### Mới (Với base class):
```python
from src.core import LLMNode

my_node = LLMNode(
    name="my_node",
    user_prompt_text="...",
    system_prompt_text="...",
    output_field="result",
)
```

**Giảm code từ ~40 lines → 5 lines! 🎉**

## 💡 Key Benefits

### 1. **Consistency**
- Tất cả nodes follow same pattern
- Automatic tracking of LLM calls, tool executions, timings
- Consistent error handling

### 2. **Reusability**
- Base classes có thể reuse across workflows
- Common patterns extracted thành utilities
- Specialized states cho từng workflow type

### 3. **Maintainability**
- Less boilerplate code
- Clear separation of concerns
- Easy to understand and modify

### 4. **Developer Experience**
- 3 approaches cho different use cases
- Quick prototyping với decorators
- Production-ready với base classes
- Full flexibility với custom functions

### 5. **Features**
- ✅ Automatic timing tracking
- ✅ Automatic error handling
- ✅ LLM execution tracking
- ✅ Tool execution tracking
- ✅ Validation with retry logic
- ✅ Conditional routing helpers
- ✅ State management utilities
- ✅ Langfuse integration

## 📈 Usage Examples

### Example 1: Simple Workflow
```python
from src.core import create_workflow_state, llm_node

@llm_node(name="generation", output_field="sql")
async def generate(state):
    return {"user_prompt": f"Generate SQL: {state['query']}"}

# Use in graph
graph.add_node("generation", generate)
```

### Example 2: Workflow with Validation & Retry
```python
from src.core import llm_node, validation_node, route_by_validation

@llm_node(name="generation", output_field="sql")
async def generate(state):
    return {"user_prompt": f"Generate SQL: {state['query']}"}

@validation_node(name="validate")
async def validate(state):
    sql = state.get("sql")
    return bool(sql), [] if sql else ["Empty SQL"]

@llm_node(name="correction", output_field="sql")
async def correct(state):
    errors = state.get("validation_errors", [])
    return {"user_prompt": f"Fix SQL. Errors: {errors}"}

# Routing
router = route_by_validation()
graph.add_conditional_edges("validate", router, {
    "valid": END,
    "invalid": "correction",
    "max_retries": END,
})
```

### Example 3: Complex Workflow with Multiple Node Types
```python
from src.core import (
    LLMNode,
    ValidationNode,
    ToolNode,
    route_by_validation,
)

# LLM nodes
reasoning = LLMNode(name="reasoning", ...)
generation = LLMNode(name="generation", ...)

# Validation
validation = ValidationNode(name="validation", ...)

# Tool execution
execution = ToolNode(name="execution", tool_func=execute_sql)

# Build graph
graph.add_node("reasoning", reasoning)
graph.add_node("generation", generation)
graph.add_node("validation", validation)
graph.add_node("execution", execution)

# Add edges with routing
graph.add_edge("reasoning", "generation")
graph.add_edge("generation", "validation")

router = route_by_validation()
graph.add_conditional_edges("validation", router, {
    "valid": "execution",
    "invalid": "generation",
    "max_retries": END,
})
```

## 🎓 Next Steps

1. **Try the examples:**
   ```bash
   python examples/workflow_with_reusable_nodes.py
   ```

2. **Read the full guide:**
   - `docs/WORKFLOW_STATE_AND_NODES_GUIDE.md`

3. **Start migrating existing workflows:**
   - Identify reusable patterns
   - Convert to base classes or decorators
   - Use specialized states

4. **Create new workflows:**
   - Start with `create_workflow_state()`
   - Use base nodes for common operations
   - Use decorators for quick prototyping

## 🤝 Contributing

When adding new nodes or utilities:
1. Follow the same patterns
2. Add documentation
3. Add examples
4. Add unit tests
5. Update `__init__.py` exports

## 📚 References

- `src/core/workflow_state.py` - State management
- `src/core/base_nodes.py` - Base node classes
- `src/core/node_utils.py` - Decorators & utilities
- `src/core/README.md` - Quick start
- `docs/WORKFLOW_STATE_AND_NODES_GUIDE.md` - Full guide
- `examples/workflow_with_reusable_nodes.py` - Examples
