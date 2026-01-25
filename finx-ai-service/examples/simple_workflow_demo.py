"""
Simple Workflow Demo: base_workflow, compile, and run

This demonstrates the 3 key steps:
1. Create base_workflow dictionary
2. Compile graphs (done automatically)
3. Run graphs
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from src.workflows import (
    create_sql_processing_graph,
    create_intent_recommendation_graph,
    create_assistance_visualization_graph,
    create_initial_intent_recommendation_state,
)


async def main():
    print("\n" + "="*60)
    print("SIMPLE WORKFLOW DEMO")
    print("="*60)
    
    # ========================================
    # STEP 1: Create base_workflow dictionary
    # ========================================
    print("\n[STEP 1] Creating base_workflow dictionary...")
    
    # Create individual graphs (these are automatically compiled)
    sql_processing_graph = create_sql_processing_graph()
    intent_recommendation_graph = create_intent_recommendation_graph()
    assistance_visualization_graph = create_assistance_visualization_graph()
    
    # Create base_workflow dictionary (like in AskService)
    base_workflow = {
        "sql_processing": sql_processing_graph,
        "intent_recommendation": intent_recommendation_graph,
        "assistance_visualization": assistance_visualization_graph,
    }
    
    print("✓ base_workflow created with 3 graphs:")
    for name, graph in base_workflow.items():
        is_compiled = graph.compiled_graph is not None
        print(f"  - {name}: compiled={is_compiled}")
    
    # ========================================
    # STEP 2: Graphs are already compiled!
    # ========================================
    print("\n[STEP 2] Graphs are already compiled!")
    print("The create_*_graph() functions call .build() internally")
    print("which compiles the graph automatically.")
    
    # You can verify compilation
    for name, graph in base_workflow.items():
        compiled = graph.get_compiled_graph()
        print(f"✓ {name} compiled graph: {type(compiled).__name__}")
    
    # ========================================
    # STEP 3: Run graphs
    # ========================================
    print("\n[STEP 3] Running a graph...")
    
    # Create initial state
    initial_state = create_initial_intent_recommendation_state(
        query="What is the total revenue for Q1 2024?",
        project_id="demo-project",
        db_schemas=["sales", "revenue"],
    )
    
    print(f"Initial state created:")
    print(f"  - query: {initial_state['query']}")
    print(f"  - project_id: {initial_state['project_id']}")
    
    # Method 1: Using the graph's execute method (async)
    print("\nMethod 1: Using graph.execute() [async]")
    result = await base_workflow["intent_recommendation"].execute(initial_state)
    
    print(f"✓ Execution completed!")
    print(f"  - intent: {result.get('intent')}")
    print(f"  - confidence: {result.get('confidence_score')}")
    print(f"  - rephrased: {result.get('rephrased_question')}")
    print(f"  - status: {result.get('status')}")
    
    # Method 2: Using the compiled graph directly (async)
    print("\nMethod 2: Using compiled_graph.ainvoke() [direct async]")
    compiled = base_workflow["intent_recommendation"].get_compiled_graph()
    result2 = await compiled.ainvoke(initial_state)

    print(f"✓ Execution completed!")
    print(f"  - intent: {result2.get('intent')}")
    print(f"  - status: {result2.get('status')}")
    
    # Method 3: Streaming execution
    print("\nMethod 3: Using graph.stream() [streaming]")
    chunk_count = 0
    async for chunk in base_workflow["intent_recommendation"].stream(initial_state):
        chunk_count += 1
        node_name = list(chunk.keys())[0] if chunk else "unknown"
        print(f"  Chunk {chunk_count}: {node_name}")

    print(f"✓ Streaming completed with {chunk_count} chunks!")
    
    # ========================================
    # BONUS: Visualize graph
    # ========================================
    print("\n[BONUS] Visualizing graph structure...")
    
    mermaid = base_workflow["intent_recommendation"].get_graph_visualization()
    print(f"✓ Mermaid diagram generated ({len(mermaid)} chars)")
    
    # Save to file
    output_file = "intent_graph_demo.mmd"
    base_workflow["intent_recommendation"].save_graph_visualization(output_file)
    print(f"✓ Saved to {output_file}")
    
    print("\n" + "="*60)
    print("DEMO COMPLETED SUCCESSFULLY!")
    print("="*60)
    
    print("\nKey Takeaways:")
    print("1. base_workflow is a dict of compiled graph objects")
    print("2. Graphs are compiled when you call create_*_graph()")
    print("3. Run graphs with: execute() (async) or stream() (async)")
    print("4. Access compiled graph with: get_compiled_graph()")
    print("5. Use ainvoke() or astream() on compiled graphs (nodes are async)")


if __name__ == "__main__":
    asyncio.run(main())

