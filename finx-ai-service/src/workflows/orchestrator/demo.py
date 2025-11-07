"""
Demo script for Master Orchestrator Graph.

Shows how to use the complete workflow for user-friendly chatbot interactions.
"""

import asyncio
import logging
from typing import Dict, Any

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Mock components for demo (replace with real implementations)
class MockEmbedder:
    async def run(self, text: str):
        return {"embedding": [0.1] * 768}


class MockRetriever:
    async def run(self, query_embedding, filters):
        return {"documents": []}


class MockGenerator:
    async def __call__(self, prompt: str):
        return {"replies": ['{"intent": "TEXT_TO_SQL", "rephrased_question": "query", "reasoning": "test"}']}


async def demo_orchestrator():
    """
    Demonstrate complete orchestrator workflow with different scenarios.
    """
    print("=" * 80)
    print("🤖 CHATBOT ORCHESTRATOR DEMO")
    print("=" * 80)
    
    # Note: Import here to show the pattern
    # from src.workflows.orchestrator import create_orchestrator_graph
    
    # For demo, we'll show the input/output structure
    
    # ==================== Scenario 1: New TEXT_TO_SQL Query ====================
    print("\n" + "=" * 80)
    print("📊 SCENARIO 1: TEXT_TO_SQL Query")
    print("=" * 80)
    
    scenario_1_input = {
        "session_id": "demo_session_001",
        "query": "What is the total revenue for last quarter?",
        "project_id": "project_123",
        "user_preferences": {
            "language": "English",
            "enable_streaming": True,
            "max_recommendations": 5,
        },
        "context": {
            "embedder": MockEmbedder(),
            "table_retriever": MockRetriever(),
            "dbschema_retriever": MockRetriever(),
            "generator": MockGenerator(),
        },
    }
    
    print("\n📥 INPUT:")
    print(f"  Query: {scenario_1_input['query']}")
    print(f"  Session: {scenario_1_input['session_id']}")
    
    print("\n🔄 WORKFLOW:")
    print("  1. ✅ Initialize Session")
    print("  2. ✅ Intent Classification → TEXT_TO_SQL")
    print("  3. ✅ Route to SQL Processing")
    print("  4. ✅ Generate SQL")
    print("  5. ✅ Validate & Execute")
    print("  6. ✅ Check Visualization → Not needed")
    print("  7. ✅ Format Response")
    print("  8. ✅ Save History")
    
    scenario_1_expected_output = {
        "session_id": "demo_session_001",
        "query": "What is the total revenue for last quarter?",
        "intent": "TEXT_TO_SQL",
        "confidence": 0.95,
        "sql": {
            "query": "SELECT SUM(revenue) FROM sales WHERE date >= '2024-07-01' AND date < '2024-10-01'",
            "reasoning": "Query aggregates revenue from sales table for Q3 2024",
            "answer": "The total revenue for last quarter is $1,234,567.89",
            "tables_used": ["sales"],
            "is_valid": True,
        },
        "recommendations": {
            "questions": [
                "What was the revenue for the same quarter last year?",
                "Show me the revenue breakdown by product category",
                "What is the average order value?",
            ]
        },
        "metadata": {
            "processing_time": 1.23,
            "correction_attempts": 0,
            "streaming_enabled": False,
        }
    }
    
    print("\n📤 EXPECTED OUTPUT:")
    print(f"  Intent: {scenario_1_expected_output['intent']}")
    print(f"  SQL: {scenario_1_expected_output['sql']['query']}")
    print(f"  Answer: {scenario_1_expected_output['sql']['answer']}")
    print(f"  Recommendations: {len(scenario_1_expected_output['recommendations']['questions'])} questions")
    
    
    # ==================== Scenario 2: Follow-up Query ====================
    print("\n" + "=" * 80)
    print("🔁 SCENARIO 2: Follow-up Query")
    print("=" * 80)
    
    scenario_2_input = {
        "session_id": "demo_session_001",
        "query": "What about this quarter?",
        "project_id": "project_123",
        "conversation_history": [
            {
                "query": "What is the total revenue for last quarter?",
                "intent": "TEXT_TO_SQL",
                "sql": "SELECT SUM(revenue) FROM sales WHERE date >= '2024-07-01' AND date < '2024-10-01'",
                "answer": "The total revenue for last quarter is $1,234,567.89",
            }
        ],
        "user_preferences": {
            "language": "English",
            "enable_streaming": False,
        },
        "context": {
            "embedder": MockEmbedder(),
            "generator": MockGenerator(),
        },
    }
    
    print("\n📥 INPUT:")
    print(f"  Query: {scenario_2_input['query']}")
    print(f"  History: {len(scenario_2_input['conversation_history'])} previous queries")
    
    print("\n🔄 WORKFLOW:")
    print("  1. ✅ Initialize Session → Load history")
    print("  2. ✅ Intent Classification → TEXT_TO_SQL")
    print("  3. ✅ Detect Follow-up → YES (keyword: 'what about')")
    print("  4. ✅ Follow-up SQL Generation → Use previous context")
    print("  5. ✅ Generate modified SQL")
    print("  6. ✅ Format Response")
    print("  7. ✅ Save History")
    
    scenario_2_expected_output = {
        "session_id": "demo_session_001",
        "query": "What about this quarter?",
        "intent": "TEXT_TO_SQL",
        "is_followup": True,
        "sql": {
            "query": "SELECT SUM(revenue) FROM sales WHERE date >= '2024-10-01' AND date < '2025-01-01'",
            "reasoning": "Modified previous query for current quarter (Q4 2024)",
            "answer": "The total revenue for this quarter is $1,456,789.12",
        }
    }
    
    print("\n📤 EXPECTED OUTPUT:")
    print(f"  Follow-up: {scenario_2_expected_output['is_followup']}")
    print(f"  SQL: {scenario_2_expected_output['sql']['query']}")
    print(f"  Answer: {scenario_2_expected_output['sql']['answer']}")
    
    
    # ==================== Scenario 3: GENERAL Query with Streaming ====================
    print("\n" + "=" * 80)
    print("💬 SCENARIO 3: GENERAL Query (Streaming)")
    print("=" * 80)
    
    scenario_3_input = {
        "session_id": "demo_session_002",
        "query": "What data do I have in this database?",
        "project_id": "project_123",
        "user_preferences": {
            "language": "English",
            "enable_streaming": True,
        },
        "context": {
            "embedder": MockEmbedder(),
            "generator": MockGenerator(),
        },
    }
    
    print("\n📥 INPUT:")
    print(f"  Query: {scenario_3_input['query']}")
    
    print("\n🔄 WORKFLOW:")
    print("  1. ✅ Initialize Session")
    print("  2. ✅ Intent Classification → GENERAL")
    print("  3. ✅ Route to Assistance & Visualization")
    print("  4. ✅ Generate Data Assistance (with streaming)")
    print("  5. ✅ Stream Response to User")
    print("  6. ✅ Format Final Response")
    print("  7. ✅ Save History")
    
    print("\n🌊 STREAMING OUTPUT:")
    streaming_chunks = [
        "Your database contains information about sales, customers, and products. ",
        "The sales table has 10,000 records tracking transactions from 2023-2024. ",
        "The customers table includes 2,500 unique customers with contact information. ",
        "The products table catalogs 500 items across 10 categories. ",
        "Key relationships: customers have many orders, orders contain many products."
    ]
    
    for i, chunk in enumerate(streaming_chunks, 1):
        print(f"  Chunk {i}: {chunk}")
        await asyncio.sleep(0.2)  # Simulate streaming delay
    
    scenario_3_expected_output = {
        "session_id": "demo_session_002",
        "query": "What data do I have in this database?",
        "intent": "GENERAL",
        "assistance": {
            "response": "".join(streaming_chunks),
            "reasoning": "Analyzed database schema and provided overview",
        },
        "recommendations": {
            "relationships": [
                {"from": "customers", "to": "orders", "type": "one_to_many"},
                {"from": "orders", "to": "products", "type": "many_to_many"},
            ],
            "questions": [
                "Show me the top 10 customers by revenue",
                "What are the best-selling products?",
                "What is the average order value?",
            ]
        },
        "metadata": {
            "streaming_enabled": True,
        }
    }
    
    print("\n📤 FINAL OUTPUT:")
    print(f"  Intent: {scenario_3_expected_output['intent']}")
    print(f"  Streaming: {scenario_3_expected_output['metadata']['streaming_enabled']}")
    print(f"  Recommendations: {len(scenario_3_expected_output['recommendations']['questions'])} questions")
    
    
    # ==================== Scenario 4: Visualization Query ====================
    print("\n" + "=" * 80)
    print("📊 SCENARIO 4: Query with Visualization")
    print("=" * 80)
    
    scenario_4_input = {
        "session_id": "demo_session_003",
        "query": "Show me the revenue trend over the last 6 months",
        "project_id": "project_123",
        "user_preferences": {
            "language": "English",
        },
        "context": {
            "embedder": MockEmbedder(),
            "generator": MockGenerator(),
        },
    }
    
    print("\n📥 INPUT:")
    print(f"  Query: {scenario_4_input['query']}")
    
    print("\n🔄 WORKFLOW:")
    print("  1. ✅ Initialize Session")
    print("  2. ✅ Intent Classification → TEXT_TO_SQL")
    print("  3. ✅ Generate SQL")
    print("  4. ✅ Execute SQL")
    print("  5. ✅ Detect Visualization Need → YES (keyword: 'trend')")
    print("  6. ✅ Route to Chart Generation")
    print("  7. ✅ Generate Line Chart")
    print("  8. ✅ Format Response with Chart")
    print("  9. ✅ Save History")
    
    scenario_4_expected_output = {
        "session_id": "demo_session_003",
        "query": "Show me the revenue trend over the last 6 months",
        "intent": "TEXT_TO_SQL",
        "sql": {
            "query": "SELECT DATE_TRUNC('month', date) as month, SUM(revenue) as total_revenue FROM sales WHERE date >= CURRENT_DATE - INTERVAL '6 months' GROUP BY month ORDER BY month",
            "answer": "Revenue has been trending upward over the last 6 months",
        },
        "visualization": {
            "type": "line_chart",
            "schema": {
                "title": "Revenue Trend - Last 6 Months",
                "x_axis": "month",
                "y_axis": "total_revenue",
                "data": [
                    {"month": "2024-05", "total_revenue": 150000},
                    {"month": "2024-06", "total_revenue": 175000},
                    {"month": "2024-07", "total_revenue": 190000},
                    {"month": "2024-08", "total_revenue": 210000},
                    {"month": "2024-09", "total_revenue": 235000},
                    {"month": "2024-10", "total_revenue": 260000},
                ]
            }
        },
        "recommendations": {
            "questions": [
                "What factors contributed to the revenue increase?",
                "Show me the breakdown by product category",
                "Compare this to the same period last year",
            ]
        }
    }
    
    print("\n📤 EXPECTED OUTPUT:")
    print(f"  Intent: {scenario_4_expected_output['intent']}")
    print(f"  Chart Type: {scenario_4_expected_output['visualization']['type']}")
    print(f"  Data Points: {len(scenario_4_expected_output['visualization']['schema']['data'])}")
    print(f"  Recommendations: {len(scenario_4_expected_output['recommendations']['questions'])} questions")
    
    
    # ==================== Scenario 5: Error Handling ====================
    print("\n" + "=" * 80)
    print("⚠️ SCENARIO 5: Error Handling")
    print("=" * 80)
    
    scenario_5_input = {
        "session_id": "demo_session_004",
        "query": "Show me sales for product ABC123XYZ999 with filter criteria from the previous discussion that we never had",
        "project_id": "project_123",
        "user_preferences": {
            "language": "English",
        },
        "context": {
            "embedder": MockEmbedder(),
            "generator": MockGenerator(),
        },
    }
    
    print("\n📥 INPUT:")
    print(f"  Query: {scenario_5_input['query']}")
    
    print("\n🔄 WORKFLOW:")
    print("  1. ✅ Initialize Session")
    print("  2. ✅ Intent Classification → TEXT_TO_SQL")
    print("  3. ✅ Generate SQL")
    print("  4. ❌ SQL Validation → FAILED (missing criteria)")
    print("  5. ✅ SQL Diagnosis → 'Incomplete filter criteria'")
    print("  6. ✅ SQL Correction Attempt 1 → FAILED")
    print("  7. ✅ SQL Correction Attempt 2 → FAILED")
    print("  8. ✅ SQL Correction Attempt 3 → FAILED")
    print("  9. ✅ Max Retries Reached → Fallback to helpful message")
    print("  10. ✅ Format Error Response with Recommendations")
    
    scenario_5_expected_output = {
        "session_id": "demo_session_004",
        "query": scenario_5_input["query"],
        "intent": "TEXT_TO_SQL",
        "status": "error",
        "message": "I couldn't generate a valid SQL query. Could you provide more details about the filter criteria?",
        "details": {
            "issue": "Missing or ambiguous filter criteria",
            "correction_attempts": 3,
        },
        "recommendations": {
            "questions": [
                "Show me all sales for product ABC123XYZ999",
                "What products are available?",
                "Show me sales filtered by date range",
            ]
        }
    }
    
    print("\n📤 EXPECTED OUTPUT:")
    print(f"  Status: {scenario_5_expected_output['status']}")
    print(f"  Message: {scenario_5_expected_output['message']}")
    print(f"  Correction Attempts: {scenario_5_expected_output['details']['correction_attempts']}")
    print(f"  Still Helpful: {len(scenario_5_expected_output['recommendations']['questions'])} recommendations")
    
    
    # ==================== Scenario 6: MISLEADING_QUERY ====================
    print("\n" + "=" * 80)
    print("🎭 SCENARIO 6: Misleading Query (Graceful Handling)")
    print("=" * 80)
    
    scenario_6_input = {
        "session_id": "demo_session_005",
        "query": "What's the weather like today?",
        "project_id": "project_123",
        "user_preferences": {
            "language": "English",
        },
        "context": {
            "embedder": MockEmbedder(),
            "generator": MockGenerator(),
        },
    }
    
    print("\n📥 INPUT:")
    print(f"  Query: {scenario_6_input['query']}")
    
    print("\n🔄 WORKFLOW:")
    print("  1. ✅ Initialize Session")
    print("  2. ✅ Intent Classification → MISLEADING_QUERY")
    print("  3. ✅ Route to Assistance & Visualization")
    print("  4. ✅ Generate Helpful Redirect Message")
    print("  5. ✅ Provide Sample Queries")
    print("  6. ✅ Format Response")
    
    scenario_6_expected_output = {
        "session_id": "demo_session_005",
        "query": "What's the weather like today?",
        "intent": "MISLEADING_QUERY",
        "message": "I'm here to help you analyze your data, not weather information. Here are some things I can help you with:",
        "recommendations": {
            "questions": [
                "What data is available in this database?",
                "Show me the total revenue",
                "List the top 10 customers",
                "What are the best-selling products?",
                "Show me sales trends",
            ]
        }
    }
    
    print("\n📤 EXPECTED OUTPUT:")
    print(f"  Intent: {scenario_6_expected_output['intent']}")
    print(f"  Message: {scenario_6_expected_output['message']}")
    print(f"  Helpful Suggestions: {len(scenario_6_expected_output['recommendations']['questions'])} sample queries")
    
    
    # ==================== Summary ====================
    print("\n" + "=" * 80)
    print("📋 DEMO SUMMARY")
    print("=" * 80)
    print("\n✅ Demonstrated Features:")
    print("  1. TEXT_TO_SQL query processing")
    print("  2. Follow-up query detection and handling")
    print("  3. GENERAL query with streaming response")
    print("  4. Automatic visualization generation")
    print("  5. Graceful error handling with retry loop")
    print("  6. Misleading query redirect with helpful suggestions")
    print("\n🎯 Key User-Friendly Aspects:")
    print("  • Multi-turn conversation support")
    print("  • Smart intent detection and routing")
    print("  • Automatic visualization for trends")
    print("  • Streaming for better UX")
    print("  • Always provide recommendations")
    print("  • Graceful error handling")
    print("  • Helpful redirects for off-topic queries")
    print("\n" + "=" * 80)
    print("✨ DEMO COMPLETE!")
    print("=" * 80)


async def demo_api_usage():
    """
    Show how to use the orchestrator in an API endpoint.
    """
    print("\n" + "=" * 80)
    print("🌐 API USAGE EXAMPLE")
    print("=" * 80)
    
    print("""
# FastAPI endpoint example

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from src.workflows.orchestrator import create_orchestrator_graph

app = FastAPI()
orchestrator = create_orchestrator_graph()

@app.post("/chat")
async def chat(request: ChatRequest):
    '''Handle chat request with orchestrator'''
    
    try:
        # Prepare input
        input_state = {
            "session_id": request.session_id,
            "query": request.query,
            "project_id": request.project_id,
            "conversation_history": await load_history(request.session_id),
            "user_preferences": await load_preferences(request.user_id),
            "context": {
                "embedder": embedder,
                "generator": generator,
                # ... other components
            },
        }
        
        # Execute workflow
        result = await orchestrator.app.ainvoke(input_state)
        
        # Check if streaming
        if result.get("streaming_enabled"):
            return StreamingResponse(
                stream_chunks(result["stream_chunks"]),
                media_type="text/event-stream"
            )
        
        # Return normal response
        return {
            "status": "success",
            "data": result["final_response"]
        }
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def stream_chunks(chunks):
    '''Stream response chunks'''
    for chunk in chunks:
        yield f"data: {chunk}\\n\\n"
        await asyncio.sleep(0.1)
    """)
    print("=" * 80)


if __name__ == "__main__":
    print("\n🚀 Starting Orchestrator Demo...\n")
    
    # Run demo
    asyncio.run(demo_orchestrator())
    
    # Show API usage
    asyncio.run(demo_api_usage())
    
    print("\n✅ Demo completed successfully!\n")
