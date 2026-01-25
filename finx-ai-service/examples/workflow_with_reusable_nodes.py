"""
Example: Simple Workflow Using New State Management and Reusable Nodes

This example demonstrates how to build a workflow using:
1. WorkflowState for state management
2. Base node classes (LLMNode, ValidationNode, etc.)
3. Node decorators for quick node creation
4. Utility functions for routing and state management
"""

import asyncio
import logging
from typing import Any, Dict, List

from langgraph.graph import END, StateGraph

from src.core.workflow_state import SQLWorkflowState, create_workflow_state
from src.core.base_nodes import LLMNode, ValidationNode, TransformNode
from src.core.node_utils import (
    node,
    llm_node,
    validation_node,
    route_by_validation,
    increment_retry,
    should_retry,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# APPROACH 1: Using Base Node Classes
# ============================================================================

def create_workflow_with_base_nodes():
    """
    Create a workflow using base node classes.
    This approach is good for reusable, configurable nodes.
    """
    
    # Define context builder for prompts
    def build_sql_context(state: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "query": state.get("query", ""),
            "db_schemas": state.get("db_schemas", []),
            "sql_samples": state.get("sql_samples", []),
            "reasoning": state.get("sql_reasoning", ""),
        }
    
    # 1. SQL Reasoning Node
    reasoning_node = LLMNode(
        name="sql_reasoning",
        system_prompt_text="You are a SQL expert. Analyze the user's question and explain how to construct the SQL query.",
        user_prompt_text="User question: {query}\n\nProvide step-by-step reasoning for creating the SQL query.",
        output_field="sql_reasoning",
        context_builder=lambda s: {"query": s.get("query", "")},
    )
    
    # 2. SQL Generation Node
    generation_node = LLMNode(
        name="sql_generation",
        system_prompt_text="You are a SQL expert. Generate a SQL query based on the reasoning provided.",
        user_prompt_text="""
User question: {query}
Reasoning: {reasoning}
Database schemas: {db_schemas}

Generate a valid SQL query.
""",
        output_field="generated_sql",
        context_builder=build_sql_context,
    )
    
    # 3. SQL Cleaning Node
    def clean_sql(sql: str) -> str:
        """Clean SQL by removing markdown and extra whitespace."""
        if not sql:
            return ""
        return (
            sql.strip()
            .replace("```sql", "")
            .replace("```", "")
            .replace(";", "")
            .strip()
        )
    
    cleaning_node = TransformNode(
        name="sql_cleaning",
        transform_func=clean_sql,
        input_field="generated_sql",
        output_field="cleaned_sql",
    )
    
    # 4. SQL Validation Node
    def validate_sql(data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate SQL query."""
        sql = data.get("cleaned_sql", "")
        errors = []
        
        if not sql or not sql.strip():
            errors.append("Empty SQL query")
            return False, errors
        
        # Basic validation
        if sql.count('(') != sql.count(')'):
            errors.append("Unmatched parentheses")
        
        if "SELECT" not in sql.upper():
            errors.append("Not a SELECT query")
        
        return len(errors) == 0, errors
    
    validation_node = ValidationNode(
        name="sql_validation",
        validation_func=validate_sql,
        output_field="is_valid_sql",
        errors_field="validation_errors",
    )
    
    # 5. Format Response Node
    @node(name="format_response")
    async def format_response(state: Dict[str, Any]) -> Dict[str, Any]:
        """Format final response."""
        state["response"] = {
            "sql": state.get("cleaned_sql", ""),
            "reasoning": state.get("sql_reasoning", ""),
            "is_valid": state.get("is_valid_sql", False),
            "validation_errors": state.get("validation_errors", []),
        }
        state["status"] = "completed"
        return state
    
    # Build the graph
    graph = StateGraph(SQLWorkflowState)
    
    graph.add_node("reasoning", reasoning_node)
    graph.add_node("generation", generation_node)
    graph.add_node("cleaning", cleaning_node)
    graph.add_node("validation", validation_node)
    graph.add_node("format", format_response)
    
    # Define flow
    graph.set_entry_point("reasoning")
    graph.add_edge("reasoning", "generation")
    graph.add_edge("generation", "cleaning")
    graph.add_edge("cleaning", "validation")
    graph.add_edge("validation", "format")
    graph.add_edge("format", END)
    
    return graph.compile()


# ============================================================================
# APPROACH 2: Using Decorators
# ============================================================================

def create_workflow_with_decorators():
    """
    Create a workflow using node decorators.
    This approach is good for quick prototyping and simple logic.
    """
    
    # 1. SQL Reasoning Node (using decorator)
    @llm_node(name="sql_reasoning", output_field="sql_reasoning")
    async def reasoning_node(state: Dict[str, Any]) -> Dict:
        return {
            "system_prompt": "You are a SQL expert. Analyze the user's question.",
            "user_prompt": f"User question: {state['query']}\n\nProvide reasoning for the SQL query.",
        }
    
    # 2. SQL Generation Node (using decorator)
    @llm_node(name="sql_generation", output_field="generated_sql")
    async def generation_node(state: Dict[str, Any]) -> Dict:
        return {
            "system_prompt": "You are a SQL expert. Generate SQL based on reasoning.",
            "user_prompt": f"""
Question: {state['query']}
Reasoning: {state.get('sql_reasoning', '')}
Schemas: {state.get('db_schemas', [])}

Generate a valid SQL query.
""",
        }
    
    # 3. SQL Cleaning Node (using decorator)
    @node(name="sql_cleaning")
    async def cleaning_node(state: Dict[str, Any]) -> Dict[str, Any]:
        sql = state.get("generated_sql", "")
        cleaned = (
            sql.strip()
            .replace("```sql", "")
            .replace("```", "")
            .replace(";", "")
            .strip()
        )
        state["cleaned_sql"] = cleaned
        return state
    
    # 4. SQL Validation Node (using decorator)
    @validation_node(name="sql_validation", output_field="is_valid_sql")
    async def validation_node_func(state: Dict[str, Any]) -> tuple[bool, List[str]]:
        sql = state.get("cleaned_sql", "")
        errors = []
        
        if not sql:
            errors.append("Empty SQL")
        elif sql.count('(') != sql.count(')'):
            errors.append("Unmatched parentheses")
        
        return len(errors) == 0, errors
    
    # 5. Format Response
    @node(name="format_response")
    async def format_response(state: Dict[str, Any]) -> Dict[str, Any]:
        state["response"] = {
            "sql": state.get("cleaned_sql", ""),
            "reasoning": state.get("sql_reasoning", ""),
            "is_valid": state.get("is_valid_sql", False),
        }
        state["status"] = "completed"
        return state
    
    # Build the graph
    graph = StateGraph(SQLWorkflowState)
    
    graph.add_node("reasoning", reasoning_node)
    graph.add_node("generation", generation_node)
    graph.add_node("cleaning", cleaning_node)
    graph.add_node("validation", validation_node_func)
    graph.add_node("format", format_response)
    
    graph.set_entry_point("reasoning")
    graph.add_edge("reasoning", "generation")
    graph.add_edge("generation", "cleaning")
    graph.add_edge("cleaning", "validation")
    graph.add_edge("validation", "format")
    graph.add_edge("format", END)
    
    return graph.compile()


# ============================================================================
# APPROACH 3: With Retry Logic
# ============================================================================

def create_workflow_with_retry():
    """
    Create a workflow with retry logic for validation failures.
    This demonstrates conditional routing and retry mechanisms.
    """
    
    @llm_node(name="sql_generation", output_field="generated_sql")
    async def generation_node(state: Dict[str, Any]) -> Dict:
        return {
            "user_prompt": f"Generate SQL for: {state['query']}",
        }
    
    @node(name="sql_cleaning")
    async def cleaning_node(state: Dict[str, Any]) -> Dict[str, Any]:
        sql = state.get("generated_sql", "")
        state["cleaned_sql"] = sql.strip().replace("```sql", "").replace("```", "")
        return state
    
    @validation_node(name="sql_validation", output_field="is_valid_sql")
    async def validation_node_func(state: Dict[str, Any]) -> tuple[bool, List[str]]:
        sql = state.get("cleaned_sql", "")
        if not sql:
            return False, ["Empty SQL"]
        return True, []
    
    @node(name="increment_retry_counter")
    async def increment_retry_node(state: Dict[str, Any]) -> Dict[str, Any]:
        increment_retry(state)
        logger.info(f"Retry attempt {state['retry_count']}/{state['max_retries']}")
        return state
    
    @llm_node(name="sql_correction", output_field="generated_sql")
    async def correction_node(state: Dict[str, Any]) -> Dict:
        errors = state.get("validation_errors", [])
        return {
            "user_prompt": f"""
The SQL query has errors: {errors}
Previous SQL: {state.get('cleaned_sql', '')}
Please correct it.
""",
        }
    
    @llm_node(name="sql_regeneration", output_field="generated_sql")
    async def regeneration_node(state: Dict[str, Any]) -> Dict:
        return {
            "user_prompt": f"Regenerate SQL from scratch for: {state['query']}",
        }
    
    @node(name="format_response")
    async def format_response(state: Dict[str, Any]) -> Dict[str, Any]:
        state["response"] = {
            "sql": state.get("cleaned_sql", ""),
            "is_valid": state.get("is_valid_sql", False),
            "retry_count": state.get("retry_count", 0),
        }
        state["status"] = "completed"
        return state
    
    # Build graph
    graph = StateGraph(SQLWorkflowState)
    
    graph.add_node("generation", generation_node)
    graph.add_node("cleaning", cleaning_node)
    graph.add_node("validation", validation_node_func)
    graph.add_node("increment_retry", increment_retry_node)
    graph.add_node("correction", correction_node)
    graph.add_node("regeneration", regeneration_node)
    graph.add_node("format", format_response)
    
    graph.set_entry_point("generation")
    graph.add_edge("generation", "cleaning")
    graph.add_edge("cleaning", "validation")
    
    # Conditional routing after validation
    router = route_by_validation(
        valid_route="done",
        invalid_route="retry",
        max_retries_route="regenerate",
    )
    
    graph.add_conditional_edges("validation", router, {
        "done": "format",
        "retry": "increment_retry",
        "regenerate": "regeneration",
    })
    
    graph.add_edge("increment_retry", "correction")
    graph.add_edge("correction", "cleaning")  # Loop back
    graph.add_edge("regeneration", "cleaning")  # Try again
    graph.add_edge("format", END)
    
    return graph.compile()


# ============================================================================
# MOCK LLM GENERATOR (for testing without real LLM)
# ============================================================================

class MockLLMGenerator:
    """Mock LLM generator for testing."""
    
    async def __call__(self, prompt: str, system_prompt: str = None, **kwargs):
        """Mock LLM call."""
        logger.info(f"Mock LLM called with prompt: {prompt[:100]}...")
        
        # Return mock responses based on prompt content
        if "reasoning" in prompt.lower():
            return {
                "replies": [
                    "To answer this question, we need to: 1) Query the sales table, 2) Group by region, 3) Sum the amounts"
                ]
            }
        elif "generate" in prompt.lower() or "correct" in prompt.lower():
            return {
                "replies": [
                    "SELECT region, SUM(amount) as total_sales FROM sales GROUP BY region"
                ]
            }
        else:
            return {"replies": ["Mock response"]}


# ============================================================================
# DEMO EXECUTION
# ============================================================================

async def demo_approach_1():
    """Demo using base node classes."""
    print("\n" + "="*80)
    print("DEMO 1: Using Base Node Classes")
    print("="*80 + "\n")
    
    # Create workflow
    compiled_graph = create_workflow_with_base_nodes()
    
    # Create initial state
    initial_state = create_workflow_state(
        query="Show me total sales by region",
        project_id="demo_project",
        db_schemas=["CREATE TABLE sales (id INT, region VARCHAR, amount DECIMAL)"],
        max_retries=3,
    )
    
    # Add mock generator to context
    initial_state["context"]["generator"] = MockLLMGenerator()
    
    # Execute workflow
    final_state = await compiled_graph.ainvoke(initial_state)
    
    # Print results
    print("\n--- Final Response ---")
    print(final_state.get("response"))
    print("\n--- Step Timings ---")
    for step, timing in final_state.get("step_timings", {}).items():
        print(f"{step}: {timing:.2f}ms")
    print("\n--- Errors ---")
    print(final_state.get("errors", []))


async def demo_approach_2():
    """Demo using decorators."""
    print("\n" + "="*80)
    print("DEMO 2: Using Decorators")
    print("="*80 + "\n")
    
    compiled_graph = create_workflow_with_decorators()
    
    initial_state = create_workflow_state(
        query="Get customer orders from last month",
        db_schemas=["CREATE TABLE orders (id INT, customer_id INT, order_date DATE)"],
    )
    initial_state["context"]["generator"] = MockLLMGenerator()
    
    final_state = await compiled_graph.ainvoke(initial_state)
    
    print("\n--- Final Response ---")
    print(final_state.get("response"))


async def demo_approach_3():
    """Demo with retry logic."""
    print("\n" + "="*80)
    print("DEMO 3: With Retry Logic")
    print("="*80 + "\n")
    
    compiled_graph = create_workflow_with_retry()
    
    initial_state = create_workflow_state(
        query="List all products with price > 100",
        max_retries=2,
    )
    initial_state["context"]["generator"] = MockLLMGenerator()
    
    final_state = await compiled_graph.ainvoke(initial_state)
    
    print("\n--- Final Response ---")
    print(final_state.get("response"))
    print("\n--- Retry Count ---")
    print(f"Total retries: {final_state.get('retry_count', 0)}")


async def main():
    """Run all demos."""
    await demo_approach_1()
    await demo_approach_2()
    await demo_approach_3()


if __name__ == "__main__":
    asyncio.run(main())
