"""
Example: How to use base_workflow, compile graph, and run workflows

This script demonstrates:
1. Creating workflow graphs
2. Building/compiling graphs
3. Running graphs with different methods (sync, async, stream)
4. Visualizing graphs
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Dict, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import workflows
from src.workflows import (
    create_sql_processing_graph,
    create_intent_recommendation_graph,
    create_assistance_visualization_graph,
    create_initial_sql_processing_state,
    create_initial_intent_recommendation_state,
    create_initial_assistance_visualization_state,
)


def example_1_create_and_build_graph():
    """Example 1: Create and build a graph"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Create and Build Graph")
    print("="*60)
    
    # Method 1: Using the factory function (recommended)
    # This automatically builds the graph
    intent_graph = create_intent_recommendation_graph()
    print(f"✓ Intent graph created and built: {intent_graph.name}")
    print(f"✓ Graph is compiled: {intent_graph.compiled_graph is not None}")
    
    # Method 2: Manual creation and building
    from src.workflows.generation.sql_processing import SQLProcessingGraph
    
    sql_graph = SQLProcessingGraph()
    print(f"✓ SQL graph created: {sql_graph.name}")
    print(f"✓ Graph is compiled: {sql_graph.compiled_graph is not None}")
    
    # Build the graph manually
    sql_graph.build()
    print(f"✓ SQL graph built manually")
    print(f"✓ Graph is now compiled: {sql_graph.compiled_graph is not None}")
    
    return intent_graph, sql_graph


def example_2_visualize_graph():
    """Example 2: Visualize graph structure"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Visualize Graph")
    print("="*60)
    
    # Create and build graph
    graph = create_intent_recommendation_graph()
    
    # Get Mermaid visualization
    mermaid = graph.get_graph_visualization()
    print("✓ Mermaid diagram generated:")
    print(mermaid[:200] + "...")
    
    # Save to file
    output_path = "intent_recommendation_graph.mmd"
    graph.save_graph_visualization(output_path)
    print(f"✓ Graph visualization saved to {output_path}")
    
    return graph


async def example_3_run_intent_classification():
    """Example 3: Run intent classification workflow"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Run Intent Classification")
    print("="*60)
    
    # Create graph
    graph = create_intent_recommendation_graph()
    
    # Create initial state
    initial_state = create_initial_intent_recommendation_state(
        query="What is the total revenue for Q1 2024?",
        project_id="project-123",
        db_schemas=["sales", "customers"],
    )
    
    print(f"✓ Initial state created")
    print(f"  Query: {initial_state['query']}")
    
    # Execute graph (async)
    result = await graph.execute(initial_state)
    
    print(f"✓ Graph executed successfully")
    print(f"  Intent: {result.get('intent')}")
    print(f"  Confidence: {result.get('confidence_score')}")
    print(f"  Rephrased: {result.get('rephrased_question')}")
    print(f"  Status: {result.get('status')}")
    
    return result


def example_4_run_sync():
    """Example 4: Run graph synchronously"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Run Graph Synchronously")
    print("="*60)
    
    # Create graph
    graph = create_intent_recommendation_graph()
    
    # Create initial state
    initial_state = create_initial_intent_recommendation_state(
        query="How do I create a new report?",
        project_id="project-123",
    )
    
    # Execute synchronously
    result = graph.invoke(initial_state)
    
    print(f"✓ Graph executed synchronously")
    print(f"  Intent: {result.get('intent')}")
    print(f"  Status: {result.get('status')}")
    
    return result


async def example_5_stream_execution():
    """Example 5: Stream graph execution"""
    print("\n" + "="*60)
    print("EXAMPLE 5: Stream Graph Execution")
    print("="*60)
    
    # Create graph
    graph = create_intent_recommendation_graph()
    
    # Create initial state
    initial_state = create_initial_intent_recommendation_state(
        query="Show me sales data",
        project_id="project-123",
    )
    
    print("✓ Streaming graph execution...")
    
    # Stream execution
    async for chunk in graph.stream(initial_state):
        print(f"  Chunk received: {list(chunk.keys())}")
    
    print("✓ Streaming completed")


async def example_6_complete_workflow():
    """Example 6: Complete workflow with base_workflow dictionary"""
    print("\n" + "="*60)
    print("EXAMPLE 6: Complete Workflow (Like AskService)")
    print("="*60)

    # Create all workflow graphs (this is what happens in main.py)
    sql_processing_graph = create_sql_processing_graph()
    intent_recommendation_graph = create_intent_recommendation_graph()
    assistance_visualization_graph = create_assistance_visualization_graph()

    # Create base_workflow dictionary
    base_workflow = {
        "sql_processing": sql_processing_graph,
        "intent_recommendation": intent_recommendation_graph,
        "assistance_visualization": assistance_visualization_graph,
    }

    print("✓ All workflows created and compiled:")
    for name, graph in base_workflow.items():
        print(f"  - {name}: {graph.compiled_graph is not None}")

    # Step 1: Classify intent
    print("\n1. Classifying intent...")
    intent_state = create_initial_intent_recommendation_state(
        query="What is the total revenue for Q1 2024?",
        project_id="project-123",
        db_schemas=["sales", "revenue"],
    )

    intent_result = await base_workflow["intent_recommendation"].execute(intent_state)
    intent = intent_result.get("intent")
    print(f"   Intent: {intent}")

    # Step 2: Route to appropriate workflow
    if intent == "TEXT_TO_SQL":
        print("\n2. Routing to SQL Processing workflow...")

        sql_state = create_initial_sql_processing_state(
            query=intent_result.get("rephrased_question") or intent_result.get("query"),
            project_id="project-123",
            db_schemas=["sales", "revenue"],
            is_followup=False,
        )

        # Note: This would normally execute, but requires actual DB connection
        print("   SQL workflow ready to execute")
        print(f"   State prepared with query: {sql_state['query']}")

    elif intent in ["GENERAL", "USER_GUIDE", "MISLEADING_QUERY"]:
        print(f"\n2. Routing to Assistance & Visualization workflow...")

        assistance_state = create_initial_assistance_visualization_state(
            query=intent_result.get("rephrased_question") or intent_result.get("query"),
            project_id="project-123",
            intent=intent,
        )

        # Execute assistance workflow
        assistance_result = await base_workflow["assistance_visualization"].execute(assistance_state)
        print(f"   Assistance type: {assistance_result.get('assistance_type')}")
        print(f"   Status: {assistance_result.get('status')}")

    print("\n✓ Complete workflow executed successfully")


def example_7_get_compiled_graph():
    """Example 7: Get compiled graph for direct use"""
    print("\n" + "="*60)
    print("EXAMPLE 7: Get Compiled Graph")
    print("="*60)

    # Create graph
    graph = create_intent_recommendation_graph()

    # Get compiled graph
    compiled = graph.get_compiled_graph()
    print(f"✓ Compiled graph retrieved: {type(compiled)}")

    # You can use the compiled graph directly
    initial_state = create_initial_intent_recommendation_state(
        query="Test query",
        project_id="test",
    )

    # Direct invocation
    result = compiled.invoke(initial_state)
    print(f"✓ Direct invocation successful")
    print(f"  Status: {result.get('status')}")

    return compiled


async def main():
    """Run all examples"""
    print("\n" + "="*80)
    print("WORKFLOW USAGE EXAMPLES")
    print("="*80)

    # Example 1: Create and build
    example_1_create_and_build_graph()

    # Example 2: Visualize
    example_2_visualize_graph()

    # Example 3: Run async
    await example_3_run_intent_classification()

    # Example 4: Run sync
    example_4_run_sync()

    # Example 5: Stream
    await example_5_stream_execution()

    # Example 6: Complete workflow
    await example_6_complete_workflow()

    # Example 7: Get compiled graph
    example_7_get_compiled_graph()

    print("\n" + "="*80)
    print("ALL EXAMPLES COMPLETED SUCCESSFULLY!")
    print("="*80)


if __name__ == "__main__":
    # Run all examples
    asyncio.run(main())

