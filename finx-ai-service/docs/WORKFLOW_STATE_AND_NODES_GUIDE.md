# Workflow State Management & Reusable Nodes Guide

Hệ thống quản lý state và các node có thể tái sử dụng cho LangGraph workflows.

## 📋 Mục lục

- [Giới thiệu](#giới-thiệu)
- [WorkflowState - State Management](#workflowstate---state-management)
- [Base Nodes - Các node có thể tái sử dụng](#base-nodes---các-node-có-thể-tái-sử-dụng)
- [Node Decorators - Tạo nodes đơn giản hơn](#node-decorators---tạo-nodes-đơn-giản-hơn)
- [Utilities & Helpers](#utilities--helpers)
- [Ví dụ thực tế](#ví-dụ-thực-tế)

---

## Giới thiệu

Hệ thống này cung cấp:

1. **WorkflowState**: Class quản lý state chung cho tất cả workflows
2. **Base Nodes**: Các node classes có thể tái sử dụng (LLMNode, ToolNode, ValidationNode, etc.)
3. **Decorators**: Các decorator để tạo nodes nhanh chóng
4. **Utilities**: Các helper functions cho routing, state management, etc.

---

## WorkflowState - State Management

### 1. Base WorkflowState

`WorkflowState` kế thừa từ `BaseState` và bao gồm các field common:

```python
from src.core.workflow_state import WorkflowState, create_workflow_state

# Tạo state
state = create_workflow_state(
    query="Show me sales by region",
    project_id="project_123",
    session_id="session_456",
    language="Vietnamese",
    db_schemas=["schema1", "schema2"],
    max_retries=3,
)
```

### 2. Specialized States

Có các specialized states cho từng loại workflow:

#### SQLWorkflowState
```python
from src.core.workflow_state import SQLWorkflowState

# Bao gồm thêm các fields cho SQL generation:
# - sql_reasoning, generated_sql, sql_generation_prompt
# - followup_sql_reasoning, followup_generated_sql
# - is_valid_sql, validation_errors, diagnosed_issues
# - execution_results, extracted_tables
# - etc.
```

#### IntentClassificationState
```python
from src.core.workflow_state import IntentClassificationState

# Bao gồm thêm các fields cho intent classification:
# - intent, intent_reasoning, confidence_score
# - rephrased_question, classification_prompt
```

#### RetrievalWorkflowState
```python
from src.core.workflow_state import RetrievalWorkflowState

# Bao gồm thêm các fields cho retrieval:
# - processed_query, query_embedding
# - documents, similarity_scores
# - filters, top_k, similarity_threshold
```

### 3. Các field quan trọng trong WorkflowState

```python
{
    # INPUT & QUERY
    "query": str,                    # User query
    "project_id": str,               # Project ID
    "session_id": str,               # Session ID
    
    # LLM INTERACTION
    "llm_executions": List[dict],    # Track tất cả LLM calls
    "llm_response": str,             # Latest LLM response
    "llm_reasoning": str,            # LLM reasoning
    
    # TOOL EXECUTION
    "tool_executions": List[dict],   # Track tất cả tool calls
    "tool_results": dict,            # Tool results
    
    # VALIDATION
    "validation_info": dict,         # Validation results
    "quality_score": float,          # Quality score (0-1)
    
    # RETRY & CORRECTION
    "retry_count": int,              # Current retry count
    "max_retries": int,              # Max allowed retries
    "correction_history": List,      # History of corrections
    
    # OUTPUT
    "response": dict,                # Final response
    "formatted_output": str,         # Formatted output
    
    # PERFORMANCE
    "step_timings": dict,            # Timing for each step
    "total_llm_tokens": int,         # Total tokens used
    
    # BASE STATE FIELDS
    "errors": List[str],             # Error messages
    "warnings": List[str],           # Warning messages
    "status": str,                   # Status (pending/processing/completed/failed)
    "current_step": str,             # Current step name
    "metadata": dict,                # Metadata
    "context": dict,                 # Context (chứa generator, retriever, etc.)
}
```

---

## Base Nodes - Các node có thể tái sử dụng

### 1. LLMNode - Gọi LLM với prompt templates

```python
from src.core.base_nodes import LLMNode

# Cách 1: Sử dụng prompt templates
reasoning_node = LLMNode(
    name="sql_reasoning",
    system_prompt_template="sql_processing/reasoning_system.jinja2",
    user_prompt_template="sql_processing/reasoning_user.jinja2",
    output_field="sql_reasoning",
)

# Cách 2: Sử dụng prompt text trực tiếp
simple_node = LLMNode(
    name="simple_llm",
    system_prompt_text="You are a helpful assistant",
    user_prompt_text="Answer: {query}",
    output_field="answer",
)

# Cách 3: Với context builder tùy chỉnh
def build_context(state):
    return {
        "query": state["query"],
        "schemas": state["db_schemas"],
        "samples": state.get("sql_samples", []),
    }

generation_node = LLMNode(
    name="sql_generation",
    user_prompt_template="sql_processing/generation_user.jinja2",
    output_field="generated_sql",
    context_builder=build_context,
    response_format={"type": "json_object"},  # Optional: JSON response
)

# Sử dụng trong graph
graph.add_node("reasoning", reasoning_node)
```

### 2. ToolNode - Thực thi tools/functions

```python
from src.core.base_nodes import ToolNode

# Define tool function
async def execute_sql_tool(sql: str, project_id: str):
    # Execute SQL logic
    return results

# Cách 1: Tool node với input builder
def build_tool_input(state):
    return {
        "sql": state.get("generated_sql"),
        "project_id": state.get("project_id"),
    }

sql_execution_node = ToolNode(
    name="sql_execution",
    tool_func=execute_sql_tool,
    input_builder=build_tool_input,
    output_field="execution_results",
)

# Cách 2: Simple tool node
async def simple_tool(**kwargs):
    return "result"

tool_node = ToolNode(
    name="my_tool",
    tool_func=simple_tool,
    output_field="tool_output",
)

# Sử dụng
graph.add_node("execute_sql", sql_execution_node)
```

### 3. ValidationNode - Validate data

```python
from src.core.base_nodes import ValidationNode

# Define validation function
def validate_sql(sql: str) -> tuple[bool, List[str]]:
    errors = []
    
    if not sql or not sql.strip():
        errors.append("Empty SQL query")
    
    if sql.count('(') != sql.count(')'):
        errors.append("Unmatched parentheses")
    
    return len(errors) == 0, errors

# Create validation node
sql_validation_node = ValidationNode(
    name="sql_validation",
    validation_func=lambda state: validate_sql(state.get("generated_sql", "")),
    output_field="is_valid_sql",
    errors_field="validation_errors",
)

# Sử dụng
graph.add_node("validate", sql_validation_node)
```

### 4. JSONParseNode - Parse JSON responses

```python
from src.core.base_nodes import JSONParseNode

# Parse LLM JSON response
parse_node = JSONParseNode(
    name="parse_intent",
    input_field="llm_response",
    output_field="parsed_intent",
    required_fields=["intent", "reasoning", "confidence"],
    default_value={"intent": "UNKNOWN"},
)

graph.add_node("parse_json", parse_node)
```

### 5. TransformNode - Transform data

```python
from src.core.base_nodes import TransformNode

# Transform SQL by cleaning it
def clean_sql(sql: str) -> str:
    return sql.strip().replace("```sql", "").replace("```", "")

clean_node = TransformNode(
    name="clean_sql",
    transform_func=clean_sql,
    input_field="raw_sql",
    output_field="cleaned_sql",
)

graph.add_node("clean", clean_node)
```

### 6. ConditionalNode - Routing logic

```python
from src.core.base_nodes import ConditionalNode

# Define routing condition
def determine_next_step(state):
    if state.get("is_valid_sql"):
        return "execute"
    elif state.get("retry_count", 0) >= 3:
        return "give_up"
    else:
        return "retry"

router_node = ConditionalNode(
    name="router",
    condition_func=determine_next_step,
    output_field="next_action",
)
```

---

## Node Decorators - Tạo nodes đơn giản hơn

### 1. @node - Decorator cơ bản

```python
from src.core.node_utils import node

@node(name="my_processing_node", track_timing=True, observe=True)
async def process_data(state: Dict[str, Any]) -> Dict[str, Any]:
    # Your logic here
    result = do_something(state["query"])
    state["result"] = result
    return state

# Decorator tự động:
# - Set current_step
# - Track execution time
# - Handle errors
# - Integrate with Langfuse
```

### 2. @llm_node - LLM decorator

```python
from src.core.node_utils import llm_node

@llm_node(
    name="reasoning",
    output_field="reasoning_result",
    response_format={"type": "json_object"}
)
async def reasoning_node(state: Dict[str, Any]) -> Dict:
    # Chỉ cần return prompts
    return {
        "system_prompt": "You are a SQL expert",
        "user_prompt": f"Analyze this query: {state['query']}",
    }

# Hoặc với templates
@llm_node(
    name="generation",
    user_prompt_template="sql_processing/generation_user.jinja2",
    system_prompt_template="sql_processing/generation_system.jinja2",
    output_field="generated_sql"
)
async def generation_node(state: Dict[str, Any]) -> Dict:
    # Return context for template
    return {
        "context": {
            "query": state["query"],
            "schemas": state["db_schemas"],
        }
    }
```

### 3. @validation_node - Validation decorator

```python
from src.core.node_utils import validation_node

@validation_node(name="validate_sql", output_field="is_valid")
async def validate_sql_node(state: Dict[str, Any]) -> tuple[bool, List[str]]:
    sql = state.get("generated_sql", "")
    errors = []
    
    if not sql:
        errors.append("No SQL generated")
    
    if "DROP TABLE" in sql.upper():
        errors.append("Dangerous SQL detected")
    
    return len(errors) == 0, errors
```

### 4. @tool_node - Tool decorator

```python
from src.core.node_utils import tool_node

@tool_node(name="execute_sql", output_field="results")
async def execute_sql_node(state: Dict[str, Any]) -> Any:
    sql = state["generated_sql"]
    project_id = state["project_id"]
    
    # Execute SQL
    results = await db_executor.execute(sql, project_id)
    return results
```

---

## Utilities & Helpers

### 1. State utilities

```python
from src.core.node_utils import (
    get_from_state,
    set_in_state,
    merge_states,
)

# Safely get nested values
generator = get_from_state(state, "context", "generator", default=None)

# Set nested values
set_in_state(state, "my_value", "nested", "key", "path")

# Merge states
merged = merge_states(base_state, update_state)
```

### 2. Retry utilities

```python
from src.core.node_utils import (
    should_retry,
    increment_retry,
    reset_retry,
)

if should_retry(state):
    increment_retry(state)
    # Retry logic
else:
    reset_retry(state)
```

### 3. History management

```python
from src.core.node_utils import add_to_history

add_to_history(
    state,
    role="user",
    content="What are the sales?",
    metadata={"timestamp": "2024-01-01"}
)
```

### 4. Conditional routing helpers

```python
from src.core.node_utils import (
    create_conditional_router,
    route_by_field,
    route_by_validation,
)

# Cách 1: Conditional router
router = create_conditional_router({
    "valid": lambda s: s.get("is_valid", False),
    "invalid": lambda s: not s.get("is_valid", False),
    "max_retries": lambda s: s.get("retry_count", 0) >= 3,
})

graph.add_conditional_edges("validation", router, {
    "valid": "execute",
    "invalid": "correct",
    "max_retries": "give_up",
})

# Cách 2: Route by field
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

# Cách 3: Validation router (with retry logic)
router = route_by_validation(
    valid_route="execute",
    invalid_route="correct",
    max_retries_route="regenerate",
)

graph.add_conditional_edges("validate", router, {
    "execute": "execution_node",
    "correct": "correction_node",
    "regenerate": "regeneration_node",
})
```

---

## Ví dụ thực tế

### Example 1: Simple SQL Processing Workflow

```python
from langgraph.graph import END, StateGraph
from src.core.workflow_state import SQLWorkflowState, create_workflow_state
from src.core.base_nodes import LLMNode, ValidationNode, ToolNode
from src.core.node_utils import route_by_validation

# Define nodes using base classes
reasoning_node = LLMNode(
    name="reasoning",
    user_prompt_template="sql/reasoning.jinja2",
    output_field="sql_reasoning",
)

generation_node = LLMNode(
    name="generation",
    user_prompt_template="sql/generation.jinja2",
    output_field="generated_sql",
)

def validate_sql_func(data):
    sql = data.get("generated_sql", "")
    if not sql:
        return False, ["No SQL generated"]
    return True, []

validation_node = ValidationNode(
    name="validation",
    validation_func=validate_sql_func,
    output_field="is_valid_sql",
)

# Build graph
graph = StateGraph(SQLWorkflowState)

graph.add_node("reasoning", reasoning_node)
graph.add_node("generation", generation_node)
graph.add_node("validation", validation_node)

graph.set_entry_point("reasoning")
graph.add_edge("reasoning", "generation")
graph.add_edge("generation", "validation")

# Add conditional routing
router = route_by_validation()
graph.add_conditional_edges("validation", router, {
    "valid": END,
    "invalid": "generation",  # Retry
    "max_retries": END,
})

compiled = graph.compile()
```

### Example 2: Using Decorators

```python
from src.core.node_utils import node, llm_node, validation_node
from src.core.workflow_state import SQLWorkflowState

@llm_node(name="reasoning", output_field="sql_reasoning")
async def reasoning(state):
    return {
        "system_prompt": "You are a SQL expert",
        "user_prompt": f"Analyze: {state['query']}",
    }

@llm_node(name="generation", output_field="generated_sql")
async def generation(state):
    return {
        "user_prompt": f"Generate SQL for: {state['query']}\nReasoning: {state['sql_reasoning']}",
    }

@validation_node(name="validation")
async def validate(state):
    sql = state.get("generated_sql", "")
    if not sql:
        return False, ["No SQL"]
    return True, []

@node(name="format_response")
async def format_response(state):
    state["response"] = {
        "sql": state["generated_sql"],
        "reasoning": state["sql_reasoning"],
    }
    return state

# Build graph
graph = StateGraph(SQLWorkflowState)
graph.add_node("reasoning", reasoning)
graph.add_node("generation", generation)
graph.add_node("validation", validate)
graph.add_node("format", format_response)

graph.set_entry_point("reasoning")
graph.add_edge("reasoning", "generation")
graph.add_edge("generation", "validation")
graph.add_edge("validation", "format")
graph.add_edge("format", END)

compiled = graph.compile()
```

### Example 3: Complex Workflow với Retry Logic

```python
from src.core.workflow_state import SQLWorkflowState
from src.core.base_nodes import LLMNode, ValidationNode
from src.core.node_utils import route_by_validation, node, increment_retry

# LLM Nodes
generation_node = LLMNode(
    name="generation",
    user_prompt_template="sql/generation.jinja2",
    output_field="generated_sql",
)

correction_node = LLMNode(
    name="correction",
    user_prompt_template="sql/correction.jinja2",
    output_field="corrected_sql",
)

regeneration_node = LLMNode(
    name="regeneration",
    user_prompt_template="sql/regeneration.jinja2",
    output_field="regenerated_sql",
)

# Validation
validation_node = ValidationNode(
    name="validation",
    validation_func=lambda s: validate_sql(s.get("generated_sql", "")),
)

# Increment retry on correction
@node(name="increment_retry")
async def increment_retry_node(state):
    increment_retry(state)
    return state

# Build graph
graph = StateGraph(SQLWorkflowState)
graph.add_node("generation", generation_node)
graph.add_node("validation", validation_node)
graph.add_node("increment_retry", increment_retry_node)
graph.add_node("correction", correction_node)
graph.add_node("regeneration", regeneration_node)

graph.set_entry_point("generation")
graph.add_edge("generation", "validation")

# Routing logic
router = route_by_validation(
    valid_route="done",
    invalid_route="retry",
    max_retries_route="regenerate"
)

graph.add_conditional_edges("validation", router, {
    "done": END,
    "retry": "increment_retry",
    "regenerate": "regeneration",
})

graph.add_edge("increment_retry", "correction")
graph.add_edge("correction", "validation")  # Loop back
graph.add_edge("regeneration", "validation")

compiled = graph.compile()
```

---

## Best Practices

### 1. State Management
- Sử dụng `create_workflow_state()` để tạo state với defaults
- Extend từ `SQLWorkflowState`, `IntentClassificationState`, etc. cho specialized workflows
- Luôn track errors và warnings trong state

### 2. Node Design
- Sử dụng **base node classes** cho reusable logic
- Sử dụng **decorators** cho quick node creation
- Mỗi node chỉ làm một việc (single responsibility)
- Log đầy đủ với `logger.info()`, `logger.warning()`, `logger.error()`

### 3. Error Handling
- Nodes tự động catch errors nếu dùng decorators
- Store errors trong `state["errors"]`
- Use try-except trong custom nodes

### 4. Performance
- Track timing với `step_timings`
- Monitor LLM token usage với `total_llm_tokens`
- Use `observe=True` cho Langfuse tracking

### 5. Testing
- Test mỗi node independently
- Mock LLM responses cho unit tests
- Test routing logic với different states

---

## Tóm tắt

**3 cách chính để tạo nodes:**

1. **Base Node Classes**: Cho reusable, configurable nodes
   ```python
   node = LLMNode(name="my_node", user_prompt_template="template.jinja2")
   ```

2. **Decorators**: Cho quick, simple nodes
   ```python
   @llm_node(name="my_node")
   async def my_node(state): ...
   ```

3. **Custom Functions**: Cho complex, custom logic
   ```python
   async def my_custom_node(state: Dict[str, Any]) -> Dict[str, Any]:
       # Custom logic
       return state
   ```

**Chọn approach nào:**
- Base Classes → Reusable, standard operations
- Decorators → Quick prototyping, simple logic
- Custom Functions → Complex, unique requirements

---

## Files Reference

- `src/core/workflow_state.py` - WorkflowState và specialized states
- `src/core/base_nodes.py` - Base node classes
- `src/core/node_utils.py` - Decorators và utilities
- `src/core/base_graph.py` - BaseGraph class
- `src/core/base_state.py` - BaseState class
