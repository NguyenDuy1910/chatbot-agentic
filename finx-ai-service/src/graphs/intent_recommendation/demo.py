"""
Demo script for testing Intent & Recommendation Graph with Google Gemini.

This demo shows how to:
1. Configure the graph with Google Gemini API
2. Create and run different types of queries (TEXT_TO_SQL, GENERAL, USER_GUIDE, MISLEADING)
3. Inspect the graph outputs and recommendations

Requirements:
- Set GOOGLE_API_KEY environment variable
- Install required packages: langgraph, google-generativeai

Usage:
    python -m src.graphs.intent_recommendation.demo
    
    # Or run specific test cases:
    python -m src.graphs.intent_recommendation.demo --test text2sql
    python -m src.graphs.intent_recommendation.demo --test general
    python -m src.graphs.intent_recommendation.demo --test all
"""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, List

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

from src.graphs.intent_recommendation import (
    IntentRecommendationGraph,
    create_initial_intent_recommendation_state,
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ==================== Sample Data ====================

SAMPLE_DB_SCHEMAS = [
    """
    CREATE TABLE customers (
        customer_id INTEGER PRIMARY KEY,
        name VARCHAR(100),
        email VARCHAR(100),
        created_at TIMESTAMP,
        country VARCHAR(50),
        total_spent DECIMAL(10,2)
    );
    """,
    """
    CREATE TABLE orders (
        order_id INTEGER PRIMARY KEY,
        customer_id INTEGER,
        order_date TIMESTAMP,
        total_amount DECIMAL(10,2),
        status VARCHAR(20),
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    );
    """,
    """
    CREATE TABLE products (
        product_id INTEGER PRIMARY KEY,
        product_name VARCHAR(200),
        category VARCHAR(50),
        price DECIMAL(10,2),
        stock_quantity INTEGER
    );
    """,
    """
    CREATE TABLE order_items (
        order_item_id INTEGER PRIMARY KEY,
        order_id INTEGER,
        product_id INTEGER,
        quantity INTEGER,
        unit_price DECIMAL(10,2),
        FOREIGN KEY (order_id) REFERENCES orders(order_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    );
    """
]

# Test cases for different intents
TEST_CASES = {
    "text2sql": {
        "query": "Show me the top 10 customers by total spending this year",
        "description": "TEXT_TO_SQL intent - specific analytical query",
        "db_schemas": SAMPLE_DB_SCHEMAS,
        "expected_intent": "TEXT_TO_SQL"
    },
    "general": {
        "query": "What data do you have?",
        "description": "GENERAL intent - exploration query",
        "db_schemas": SAMPLE_DB_SCHEMAS,
        "expected_intent": "GENERAL"
    },
    "user_guide": {
        "query": "How do I write a SQL query to join tables?",
        "description": "USER_GUIDE intent - help request",
        "db_schemas": SAMPLE_DB_SCHEMAS,
        "expected_intent": "USER_GUIDE"
    },
    "misleading": {
        "query": "What's the weather today?",
        "description": "MISLEADING_QUERY intent - off-topic question",
        "db_schemas": SAMPLE_DB_SCHEMAS,
        "expected_intent": "MISLEADING_QUERY"
    },
    "complex_text2sql": {
        "query": "Calculate the average order value for each customer segment and show trends over the last 6 months",
        "description": "Complex TEXT_TO_SQL with aggregations and time-based analysis",
        "db_schemas": SAMPLE_DB_SCHEMAS,
        "expected_intent": "TEXT_TO_SQL"
    }
}


# ==================== Helper Functions ====================

def print_section(title: str, width: int = 80):
    """Print a formatted section header."""
    print("\n" + "=" * width)
    print(f"  {title}")
    print("=" * width)


def print_state_summary(state: Dict[str, Any]):
    """Print a summary of the graph state."""
    print("\n📊 State Summary:")
    print(f"  Status: {state.get('status', 'N/A')}")
    print(f"  Current Step: {state.get('current_step', 'N/A')}")
    print(f"  Errors: {len(state.get('errors', []))}")
    print(f"  Warnings: {len(state.get('warnings', []))}")


def print_intent_results(state: Dict[str, Any]):
    """Print intent classification results."""
    print_section("Intent Classification Results")
    print(f"  Intent: {state.get('intent', 'N/A')}")
    print(f"  Confidence: {state.get('confidence_score', 0.0):.2%}")
    print(f"  Rephrased Question: {state.get('rephrased_question', 'N/A')}")
    print(f"\n  Reasoning:")
    print(f"    {state.get('intent_reasoning', 'N/A')}")


def print_question_recommendations(state: Dict[str, Any]):
    """Print question recommendations."""
    questions = state.get('recommended_questions', [])
    if not questions:
        print("\n  No question recommendations generated.")
        return
    
    print_section("Question Recommendations")
    print(f"  Total Recommendations: {len(questions)}\n")
    
    for i, q in enumerate(questions, 1):
        category = q.get('category', 'N/A')
        question = q.get('question', 'N/A')
        print(f"  {i}. [{category}] {question}")
    
    if state.get('question_recommendation_reasoning'):
        print(f"\n  Reasoning:")
        print(f"    {state.get('question_recommendation_reasoning')}")


def print_relationship_recommendations(state: Dict[str, Any]):
    """Print relationship recommendations."""
    relationships = state.get('recommended_relationships', [])
    if not relationships:
        print("\n  No relationship recommendations generated.")
        return
    
    print_section("Relationship Recommendations")
    print(f"  Total Recommendations: {len(relationships)}\n")
    
    for i, rel in enumerate(relationships, 1):
        print(f"  {i}. {rel.get('description', 'N/A')}")
        print(f"     Type: {rel.get('type', 'N/A')}")
        print(f"     Tables: {rel.get('tables', [])}")
    
    if state.get('relationship_reasoning'):
        print(f"\n  Reasoning:")
        print(f"    {state.get('relationship_reasoning')}")


def print_semantics_description(state: Dict[str, Any]):
    """Print semantics description."""
    description = state.get('semantics_description')
    if not description:
        print("\n  No semantics description generated.")
        return
    
    print_section("Semantics Description")
    print(f"  {description}")
    
    if state.get('semantics_reasoning'):
        print(f"\n  Reasoning:")
        print(f"    {state.get('semantics_reasoning')}")


def print_final_response(state: Dict[str, Any]):
    """Print final formatted response."""
    response = state.get('response')
    if not response:
        print("\n  No final response generated.")
        return
    
    print_section("Final Response")
    print(json.dumps(response, indent=2, ensure_ascii=False))


def check_google_api_key():
    """Check if Google API key is set."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        logger.error("❌ GOOGLE_API_KEY environment variable not set!")
        logger.info("Please set it using:")
        logger.info("  export GOOGLE_API_KEY='your-api-key-here'")
        return False
    
    logger.info("✅ GOOGLE_API_KEY found")
    return True


# ==================== Main Demo Functions ====================

async def run_test_case(
    graph: IntentRecommendationGraph,
    test_name: str,
    test_data: Dict[str, Any],
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Run a single test case.
    
    Args:
        graph: Compiled IntentRecommendationGraph
        test_name: Name of the test case
        test_data: Test data containing query, db_schemas, etc.
        verbose: Whether to print detailed output
        
    Returns:
        Final state after graph execution
    """
    if verbose:
        print_section(f"Test Case: {test_name.upper()}", width=80)
        print(f"  Description: {test_data['description']}")
        print(f"  Query: {test_data['query']}")
        print(f"  Expected Intent: {test_data['expected_intent']}")
    
    # Create initial state
    initial_state = create_initial_intent_recommendation_state(
        query=test_data['query'],
        project_id="demo_project",
        db_schemas=test_data.get('db_schemas', []),
        histories=[],
        configuration={"language": "en"}
    )
    
    try:
        # Run the graph
        logger.info(f"Running graph for test case: {test_name}")
        final_state = await graph.invoke(initial_state)
        
        if verbose:
            # Print results
            print_state_summary(final_state)
            print_intent_results(final_state)
            
            # Print recommendations based on intent
            intent = final_state.get('intent')
            if intent in ["TEXT_TO_SQL", "USER_GUIDE"]:
                print_question_recommendations(final_state)
            elif intent == "GENERAL":
                print_semantics_description(final_state)
                print_relationship_recommendations(final_state)
            
            print_final_response(final_state)
            
            # Check if intent matches expected
            actual_intent = final_state.get('intent')
            expected_intent = test_data['expected_intent']
            if actual_intent == expected_intent:
                print(f"\n✅ Intent classification CORRECT: {actual_intent}")
            else:
                print(f"\n⚠️  Intent classification MISMATCH:")
                print(f"    Expected: {expected_intent}")
                print(f"    Got: {actual_intent}")
        
        return final_state
        
    except Exception as e:
        logger.error(f"❌ Error running test case '{test_name}': {e}", exc_info=True)
        return {"status": "failed", "error": str(e)}


async def run_all_tests(verbose: bool = True):
    """Run all test cases."""
    print_section("Intent & Recommendation Graph Demo - Google Gemini", width=80)
    
    # Check API key
    if not check_google_api_key():
        return
    
    # Create and build the graph
    logger.info("Creating Intent & Recommendation Graph...")
    graph = IntentRecommendationGraph()
    graph.build()
    logger.info("✅ Graph built successfully")
    
    # Run all test cases
    results = {}
    for test_name, test_data in TEST_CASES.items():
        result = await run_test_case(graph, test_name, test_data, verbose=verbose)
        results[test_name] = result
        
        # Add a separator between tests
        if verbose:
            print("\n" + "-" * 80 + "\n")
    
    # Print summary
    print_section("Test Summary", width=80)
    print(f"  Total Tests: {len(results)}")
    
    passed = sum(1 for r in results.values() if r.get('status') == 'completed')
    failed = sum(1 for r in results.values() if r.get('status') == 'failed')
    
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")
    
    # Print intent accuracy
    correct_intents = sum(
        1 for test_name, state in results.items() 
        if state.get('intent') == TEST_CASES[test_name]['expected_intent']
    )
    print(f"  Intent Accuracy: {correct_intents}/{len(results)} ({correct_intents/len(results)*100:.1f}%)")


async def run_interactive_demo():
    """Run interactive demo where user can input queries."""
    print_section("Interactive Intent & Recommendation Demo", width=80)
    
    # Check API key
    if not check_google_api_key():
        return
    
    # Create and build the graph
    logger.info("Creating Intent & Recommendation Graph...")
    graph = IntentRecommendationGraph()
    graph.build()
    logger.info("✅ Graph built successfully")
    
    print("\n💡 Enter your queries to test intent classification and recommendations")
    print("   Type 'quit' or 'exit' to stop\n")
    
    while True:
        try:
            # Get user input
            query = input("\n📝 Your query: ").strip()
            
            if not query:
                continue
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            # Run the query
            test_data = {
                "query": query,
                "description": "User query",
                "db_schemas": SAMPLE_DB_SCHEMAS,
                "expected_intent": "UNKNOWN"
            }
            
            await run_test_case(graph, "user_query", test_data, verbose=True)
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)


async def run_custom_query(query: str):
    """Run a single custom query."""
    print_section("Custom Query Test", width=80)
    
    # Check API key
    if not check_google_api_key():
        return
    
    # Create and build the graph
    logger.info("Creating Intent & Recommendation Graph...")
    graph = IntentRecommendationGraph()
    graph.build()
    logger.info("✅ Graph built successfully")
    
    # Run the query
    test_data = {
        "query": query,
        "description": "Custom query",
        "db_schemas": SAMPLE_DB_SCHEMAS,
        "expected_intent": "UNKNOWN"
    }
    
    await run_test_case(graph, "custom", test_data, verbose=True)


# ==================== CLI Entry Point ====================

def main():
    """Main entry point for the demo script."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Demo for Intent & Recommendation Graph with Google Gemini"
    )
    parser.add_argument(
        "--test",
        type=str,
        choices=list(TEST_CASES.keys()) + ["all", "interactive"],
        default="all",
        help="Test case to run (default: all)"
    )
    parser.add_argument(
        "--query",
        type=str,
        help="Custom query to test"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        default=True,
        help="Verbose output (default: True)"
    )
    
    args = parser.parse_args()
    
    try:
        if args.query:
            # Run custom query
            asyncio.run(run_custom_query(args.query))
        elif args.test == "all":
            # Run all test cases
            asyncio.run(run_all_tests(verbose=args.verbose))
        elif args.test == "interactive":
            # Run interactive mode
            asyncio.run(run_interactive_demo())
        else:
            # Run specific test case
            if not check_google_api_key():
                return
            
            graph = IntentRecommendationGraph()
            graph.build()
            
            test_data = TEST_CASES[args.test]
            asyncio.run(run_test_case(graph, args.test, test_data, verbose=args.verbose))
            
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
