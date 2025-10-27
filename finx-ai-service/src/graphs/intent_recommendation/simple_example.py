"""
Simple Example: Testing Intent & Recommendation Graph

This is a minimal example to get started quickly with the Intent & Recommendation Graph.

Usage:
    python -m src.graphs.intent_recommendation.simple_example
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

from src.graphs.intent_recommendation import (
    IntentRecommendationGraph,
    create_initial_intent_recommendation_state,
)


# ==================== Configuration ====================

# Get Google API key from environment
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    print("\n❌ Error: GOOGLE_API_KEY not found in environment variables")
    print("   Please check your .env file")
    sys.exit(1)

print(f"✅ Using Google API Key: {GOOGLE_API_KEY[:20]}...")


# Sample database schema
SAMPLE_SCHEMA = [
    """
    CREATE TABLE customers (
        customer_id INTEGER PRIMARY KEY,
        name VARCHAR(100),
        email VARCHAR(100),
        total_spent DECIMAL(10,2)
    );
    """,
    """
    CREATE TABLE orders (
        order_id INTEGER PRIMARY KEY,
        customer_id INTEGER,
        order_date TIMESTAMP,
        total_amount DECIMAL(10,2)
    );
    """
]


# ==================== Simple Test Function ====================

async def test_query(query: str):
    """
    Test a single query with the Intent & Recommendation Graph.
    
    Args:
        query: User's question to test
    """
    print(f"\n{'='*80}")
    print(f"Testing Query: {query}")
    print(f"{'='*80}\n")
    
    # Create the graph
    print("Creating Intent & Recommendation Graph...")
    graph = IntentRecommendationGraph()
    graph.build()
    print("✅ Graph built successfully!\n")
    
    # Create initial state
    initial_state = create_initial_intent_recommendation_state(
        query=query,
        project_id="test_project",
        db_schemas=SAMPLE_SCHEMA,
        histories=[],
        configuration={"language": "en"}
    )
    
    # Run the graph
    print("Running graph...")
    result = await graph.execute(initial_state)
    
    # Print results
    print(f"\n📊 Results:")
    print(f"  Status: {result.get('status')}")
    print(f"  Intent: {result.get('intent')}")
    print(f"  Confidence: {result.get('confidence_score', 0):.2%}")
    print(f"  Rephrased: {result.get('rephrased_question')}")
    
    # Print recommendations
    if result.get('recommended_questions'):
        print(f"\n💡 Question Recommendations:")
        for i, q in enumerate(result['recommended_questions'], 1):
            print(f"  {i}. [{q.get('category')}] {q.get('question')}")
    
    if result.get('semantics_description'):
        print(f"\n📚 Semantics Description:")
        print(f"  {result.get('semantics_description')}")
    
    if result.get('recommended_relationships'):
        print(f"\n🔗 Recommended Relationships: {len(result['recommended_relationships'])}")
        for i, rel in enumerate(result['recommended_relationships'][:3], 1):
            print(f"  {i}. {rel.get('description', 'N/A')}")
    
    print(f"\n{'='*80}\n")
    
    return result


# ==================== Example Usage ====================

async def main():
    """Run example queries."""
    
    print("\n🚀 Intent & Recommendation Graph - Simple Example")
    print("="*80)
    
    # Example 1: TEXT_TO_SQL query
    await test_query("Show me the top 10 customers by spending")
    
    # Example 2: GENERAL query
    await test_query("What data do you have?")
    
    # Example 3: USER_GUIDE query
    await test_query("How do I write a SQL query?")
    
    print("\n✨ All tests completed!")


if __name__ == "__main__":
    asyncio.run(main())
