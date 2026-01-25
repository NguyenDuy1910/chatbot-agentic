"""
Simple example showing how to use AskService without managing state.

Just pass params directly - no need to create initial state!
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.web.services.ask import AskService
from src.workflows import (
    create_sql_processing_graph,
    create_intent_recommendation_graph,
    create_assistance_visualization_graph,
)


async def main():
    print("=" * 80)
    print("AskService Simple Usage - No State Management Required!")
    print("=" * 80)
    
    # Step 1: Create base_workflow
    print("\n1. Creating base_workflow...")
    base_workflow = {
        "sql_processing": create_sql_processing_graph(),
        "intent_recommendation": create_intent_recommendation_graph(),
        "assistance_visualization": create_assistance_visualization_graph(),
    }
    print("✓ base_workflow created with 3 workflows")
    
    # Step 2: Initialize AskService
    print("\n2. Initializing AskService...")
    ask_service = AskService(
        base_workflow=base_workflow,
        allow_intent_classification=True,
        should_execute_by_default=False,
        max_sql_correction_retries=3,
    )
    print("✓ AskService initialized")
    
    # ========== Example 1: Intent Classification ==========
    print("\n" + "=" * 80)
    print("Example 1: Intent Classification - Just pass params!")
    print("=" * 80)
    
    result = await ask_service.execute_intent_classification(
        query="What is the total revenue for Q1 2024?",
        project_id="demo-project",
        db_schemas=["sales", "customers"],
    )
    
    print(f"\nQuery: What is the total revenue for Q1 2024?")
    print(f"Intent: {result.get('intent')}")
    print(f"Confidence: {result.get('confidence_score', 0):.2%}")
    print(f"Rephrased: {result.get('rephrased_question')}")
    print(f"Reasoning: {result.get('intent_reasoning')}")
    
    # ========== Example 2: SQL Processing ==========
    print("\n" + "=" * 80)
    print("Example 2: SQL Processing - Just pass params!")
    print("=" * 80)
    
    result = await ask_service.execute_sql_processing(
        query="Show me top 10 customers by revenue",
        project_id="demo-project",
        db_schemas=["sales", "customers"],
        should_execute=False,  # Don't execute, just generate SQL
    )
    
    print(f"\nQuery: Show me top 10 customers by revenue")
    print(f"Generated SQL:\n{result.get('generated_sql')}")
    print(f"SQL Reasoning: {result.get('sql_reasoning')}")
    print(f"Is Valid: {result.get('is_valid_sql')}")
    
    # ========== Example 3: SQL Processing with Follow-up ==========
    print("\n" + "=" * 80)
    print("Example 3: Follow-up Query - Just pass params!")
    print("=" * 80)
    
    previous_sql = "SELECT customer_id, SUM(revenue) as total FROM sales GROUP BY customer_id"
    
    result = await ask_service.execute_sql_processing(
        query="Filter only customers with revenue > 10000",
        project_id="demo-project",
        db_schemas=["sales"],
        is_followup=True,
        previous_sql=previous_sql,
        histories=[
            {
                "question": "Show me revenue by customer",
                "sql": previous_sql,
            }
        ],
    )
    
    print(f"\nPrevious SQL: {previous_sql}")
    print(f"Follow-up Query: Filter only customers with revenue > 10000")
    print(f"Generated SQL:\n{result.get('generated_sql')}")
    
    # ========== Example 4: Assistance ==========
    print("\n" + "=" * 80)
    print("Example 4: General Assistance - Just pass params!")
    print("=" * 80)
    
    result = await ask_service.execute_assistance(
        query="How do I create a new dashboard?",
        project_id="demo-project",
        intent="USER_GUIDE",
    )
    
    print(f"\nQuery: How do I create a new dashboard?")
    print(f"Response: {result.get('assistance_response')}")
    print(f"Reasoning: {result.get('assistance_reasoning')}")
    
    # ========== Example 5: Complete Workflow with Custom Context ==========
    print("\n" + "=" * 80)
    print("Example 5: With Custom Context - Just pass params!")
    print("=" * 80)
    
    custom_context = {
        "user_id": "user123",
        "session_id": "session456",
        "metadata": {"source": "web_app"},
    }
    
    result = await ask_service.execute_intent_classification(
        query="What's the average order value?",
        project_id="demo-project",
        db_schemas=["orders"],
        configuration={
            "model": "gpt-4",
            "temperature": 0.7,
        },
        context=custom_context,
    )
    
    print(f"\nQuery: What's the average order value?")
    print(f"Intent: {result.get('intent')}")
    print(f"Context passed: {custom_context}")
    
    print("\n" + "=" * 80)
    print("✅ All examples completed!")
    print("=" * 80)
    print("\nKey Takeaways:")
    print("1. No need to create initial state manually")
    print("2. Just pass params directly to execute_* methods")
    print("3. State management is handled internally")
    print("4. Clean and simple API!")


if __name__ == "__main__":
    asyncio.run(main())

