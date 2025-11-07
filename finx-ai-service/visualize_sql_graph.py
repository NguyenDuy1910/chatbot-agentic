from src.workflows.sql_processing.graph import create_sql_processing_graph
from src.workflows.intent_recommendation.graph import create_intent_recommendation_graph
from src.workflows.orchestrator.graph import create_orchestrator_graph

def visualize_graph(graph_name, create_graph_func, output_filename):
    """Visualize a single graph and save outputs"""
    print("\n" + "=" * 80)
    print(f"Processing: {graph_name}")
    print("=" * 80)
    
    # Create and build graph
    print(f"Creating {graph_name}...")
    graph = create_graph_func()
    print(f"Graph created!\n")

    # Get compiled graph
    compiled = graph.compiled_graph

    # Try to get Mermaid diagram
    try:
        print("=" * 80)
        print("MERMAID DIAGRAM (Copy to https://mermaid.live)")
        print("=" * 80)
        mermaid = compiled.get_graph().draw_mermaid()
        print(mermaid)
        
        # Save mermaid to file
        mermaid_file = f"{output_filename}.mmd"
        with open(mermaid_file, "w") as f:
            f.write(mermaid)
        print(f"\nMermaid diagram saved to: {mermaid_file}")
        print("Copy the above and paste to https://mermaid.live\n")
    except Exception as e:
        print(f"Error generating Mermaid: {e}\n")

    # Try to save PNG
    try:
        print("=" * 80)
        print("SAVING PNG IMAGE")
        print("=" * 80)
        png_bytes = compiled.get_graph().draw_mermaid_png()
        png_file = f"{output_filename}.png"
        with open(png_file, "wb") as f:
            f.write(png_bytes)
        print(f"Saved to: {png_file}\n")
    except Exception as e:
        print(f"Could not save PNG: {e}")
        print("   Install with: pip install pygraphviz\n")

    # Print graph structure
    try:
        print("=" * 80)
        print("GRAPH STRUCTURE")
        print("=" * 80)
        graph_def = compiled.get_graph()
        
        print("\nNODES:")
        for node in graph_def.nodes:
            print(f"   - {node}")
        
        print("\nEDGES:")
        for edge in graph_def.edges:
            print(f"   {edge.source} -> {edge.target}")
        
    except Exception as e:
        print(f"Error: {e}")

# Generate all graphs
print("=" * 80)
print("GENERATING ALL WORKFLOW GRAPHS")
print("=" * 80)

visualize_graph("SQL Processing Graph", create_sql_processing_graph, "sql_processing_graph")
visualize_graph("Intent Recommendation Graph", create_intent_recommendation_graph, "intent_recommendation_graph")
visualize_graph("Orchestrator Graph", create_orchestrator_graph, "orchestrator_graph")

print("\n" + "=" * 80)
print("GENERATION COMPLETE")
print("=" * 80)
print("\nAll graphs have been generated and saved:")
print("  - sql_processing_graph.png / .mmd")
print("  - intent_recommendation_graph.png / .mmd")
print("  - orchestrator_graph.png / .mmd")
