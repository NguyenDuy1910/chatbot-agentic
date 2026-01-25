# AskService Simple API - No State Management Required!

## Overview

The AskService now provides a **simple, clean API** where you just pass parameters directly - no need to manage state manually!

## Quick Start

```python
from src.web.services.ask import AskService
from src.workflows import (
    create_sql_processing_graph,
    create_intent_recommendation_graph,
    create_assistance_visualization_graph,
)

# 1. Create base_workflow
base_workflow = {
    "sql_processing": create_sql_processing_graph(),
    "intent_recommendation": create_intent_recommendation_graph(),
    "assistance_visualization": create_assistance_visualization_graph(),
}

# 2. Initialize AskService
ask_service = AskService(base_workflow=base_workflow)

# 3. Execute directly - just pass params!
result = await ask_service.execute_intent_classification(
    query="What is the total revenue?",
    project_id="my-project",
)
```

## Available Methods

### 1. Intent Classification

Classify user intent without managing state:

```python
result = await ask_service.execute_intent_classification(
    query="What is the total revenue for Q1 2024?",
    project_id="demo-project",
    db_schemas=["sales", "customers"],  # Optional
    histories=[],  # Optional
    configuration={},  # Optional
    context={},  # Optional
)

# Result contains:
# - intent: TEXT_TO_SQL | GENERAL | USER_GUIDE | MISLEADING_QUERY
# - rephrased_question: Rephrased query
# - intent_reasoning: Why this intent was chosen
# - confidence_score: Confidence (0-1)
```

### 2. SQL Processing

Generate SQL without managing state:

```python
result = await ask_service.execute_sql_processing(
    query="Show me top 10 customers by revenue",
    project_id="demo-project",
    db_schemas=["sales", "customers"],  # Optional
    should_execute=False,  # Optional - default from service config
    is_followup=False,  # Optional
    previous_sql=None,  # Optional - for follow-up queries
    histories=[],  # Optional
    configuration={},  # Optional
    context={},  # Optional
)

# Result contains:
# - generated_sql: Generated SQL query
# - sql_reasoning: Why this SQL was generated
# - is_valid_sql: Whether SQL is valid
# - corrected_sql: Corrected SQL (if validation failed)
# - execution_results: Query results (if executed)
# - formatted_answer: Natural language answer
```

### 3. Assistance & Visualization

Get assistance without managing state:

```python
result = await ask_service.execute_assistance(
    query="How do I create a new dashboard?",
    project_id="demo-project",
    intent="USER_GUIDE",  # Optional - GENERAL or USER_GUIDE
    db_schemas=[],  # Optional
    histories=[],  # Optional
    configuration={},  # Optional
    context={},  # Optional
)

# Result contains:
# - assistance_response: Natural language response
# - assistance_reasoning: Why this response was generated
# - chart_schema: Chart configuration (if visualization)
# - vega_schema: Vega-Lite spec (if visualization)
```

## Common Patterns

### Pattern 1: Simple Query

```python
# Just pass the query and project_id - that's it!
result = await ask_service.execute_intent_classification(
    query="What is the total revenue?",
    project_id="my-project",
)
```

### Pattern 2: With Database Schemas

```python
# Add db_schemas for better SQL generation
result = await ask_service.execute_sql_processing(
    query="Show me top customers",
    project_id="my-project",
    db_schemas=["sales", "customers", "products"],
)
```

### Pattern 3: Follow-up Query

```python
# First query
result1 = await ask_service.execute_sql_processing(
    query="Show me revenue by customer",
    project_id="my-project",
)

# Follow-up query - just pass previous SQL and histories
result2 = await ask_service.execute_sql_processing(
    query="Filter only customers with revenue > 10000",
    project_id="my-project",
    is_followup=True,
    previous_sql=result1["generated_sql"],
    histories=[
        {
            "question": "Show me revenue by customer",
            "sql": result1["generated_sql"],
        }
    ],
)
```

### Pattern 4: With Custom Context

```python
# Pass custom context for tracking, metadata, etc.
result = await ask_service.execute_intent_classification(
    query="What's the average order value?",
    project_id="my-project",
    context={
        "user_id": "user123",
        "session_id": "session456",
        "metadata": {"source": "web_app"},
    },
)
```

### Pattern 5: With Configuration

```python
# Pass configuration for model settings
result = await ask_service.execute_sql_processing(
    query="Show me sales trends",
    project_id="my-project",
    configuration={
        "model": "gpt-4",
        "temperature": 0.7,
        "max_tokens": 2000,
    },
)
```

## Comparison: Old vs New

### ❌ Old Way (Complex)

```python
# Had to create initial state manually
from src.workflows.generation import create_initial_intent_recommendation_state

state = create_initial_intent_recommendation_state(
    query="What is the total revenue?",
    project_id="my-project",
    histories=[],
    configuration={},
    db_schemas=[],
)

# Then execute
result = await workflow.execute(state)
```

### ✅ New Way (Simple)

```python
# Just pass params directly!
result = await ask_service.execute_intent_classification(
    query="What is the total revenue?",
    project_id="my-project",
)
```

## Benefits

1. **No State Management**: Don't worry about creating initial state
2. **Clean API**: Just pass the params you need
3. **Type Safety**: All params are typed and documented
4. **Flexible**: All params are optional except query and project_id
5. **Consistent**: Same pattern for all workflows

## See Also

- [Ask Service Integration](./ASK_SERVICE_INTEGRATION.md)
- [Ask API Documentation](./ASK_API.md)
- [Examples](../examples/ask_service_simple_usage.py)

