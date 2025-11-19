# LangGraph Architecture for FinX AI Chatbot

## 📋 Tổng quan

Tài liệu này mô tả kiến trúc áp dụng **LangGraph** cho FinX AI Chatbot - một hệ thống text-to-SQL với khả năng migration, schema analysis, và chat intelligence.

---

## 🎯 Tại sao LangGraph?

### Vấn đề hiện tại:
- ✅ Đã có multi-agent system (SchemaAnalyzer, MigrationPlanner, DataTransform, ValidationAgent)
- ✅ Đã có pipeline framework (BasicPipeline)
- ❌ Thiếu orchestration logic phức tạp giữa các agents
- ❌ Không có state management nhất quán
- ❌ Khó mở rộng workflow và conditional routing
- ❌ Thiếu human-in-the-loop capabilities

### LangGraph giải quyết:
- ✅ **State Management**: StateGraph quản lý state qua toàn bộ workflow
- ✅ **Conditional Routing**: Routing thông minh dựa trên context
- ✅ **Checkpointing**: Lưu và restore state bất kỳ lúc nào
- ✅ **Human-in-the-Loop**: Cho phép human approval tại các điểm quan trọng
- ✅ **Parallel Execution**: Chạy song song các agents độc lập
- ✅ **Subgraphs**: Tổ chức workflow phân cấp

---

## 🏗️ Kiến trúc tổng quan

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        LANGGRAPH ARCHITECTURE                            │
└─────────────────────────────────────────────────────────────────────────┘

                              ┌──────────────┐
                              │   User Input │
                              └──────┬───────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │   Router Graph        │
                         │  (Main Orchestrator)  │
                         └───────────┬───────────┘
                                     │
              ┌──────────────────────┼──────────────────────┐
              │                      │                      │
              ▼                      ▼                      ▼
    ┌─────────────────┐   ┌──────────────────┐   ┌─────────────────┐
    │  Chat Subgraph  │   │ Migration        │   │ Schema          │
    │                 │   │ Subgraph         │   │ Subgraph        │
    └─────────────────┘   └──────────────────┘   └─────────────────┘
              │                      │                      │
              └──────────────────────┼──────────────────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │   Response Formatter  │
                         └───────────────────────┘
                                     │
                                     ▼
                              ┌──────────────┐
                              │   Response   │
                              └──────────────┘
```

---

## 📊 LangGraph State Schema

```python
from typing import TypedDict, Annotated, List, Dict, Any, Optional
from operator import add
from langgraph.graph import StateGraph

class ChatbotState(TypedDict):
    """Global state cho toàn bộ chatbot system"""
    
    # User context
    user_id: str
    session_id: str
    conversation_history: Annotated[List[Dict], add]
    
    # Request info
    user_query: str
    intent: Optional[str]  # 'chat', 'migration', 'schema_analysis', 'sql_generation'
    
    # Database context
    connections: List[Dict[str, Any]]
    active_connection: Optional[Dict[str, Any]]
    schema_context: Optional[Dict[str, Any]]
    
    # Migration context
    migration_plan: Optional[Dict[str, Any]]
    migration_status: Optional[str]
    migration_results: Optional[Dict[str, Any]]
    
    # SQL context
    generated_sql: Optional[str]
    sql_results: Optional[Any]
    
    # Response
    response: Optional[str]
    metadata: Dict[str, Any]
    
    # Control flow
    needs_human_approval: bool
    approved: Optional[bool]
    errors: Annotated[List[str], add]
```

---

## 🔄 Main Router Graph

```python
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver

# Define router graph
def create_router_graph():
    """Create main routing graph"""
    
    workflow = StateGraph(ChatbotState)
    
    # Add nodes
    workflow.add_node("intent_classifier", classify_intent)
    workflow.add_node("chat_handler", handle_chat)
    workflow.add_node("migration_handler", handle_migration)
    workflow.add_node("schema_handler", handle_schema)
    workflow.add_node("sql_handler", handle_sql)
    workflow.add_node("response_formatter", format_response)
    
    # Define edges
    workflow.set_entry_point("intent_classifier")
    
    # Conditional routing based on intent
    workflow.add_conditional_edges(
        "intent_classifier",
        route_by_intent,
        {
            "chat": "chat_handler",
            "migration": "migration_handler",
            "schema": "schema_handler",
            "sql": "sql_handler"
        }
    )
    
    # All handlers route to response formatter
    workflow.add_edge("chat_handler", "response_formatter")
    workflow.add_edge("migration_handler", "response_formatter")
    workflow.add_edge("schema_handler", "response_formatter")
    workflow.add_edge("sql_handler", "response_formatter")
    workflow.add_edge("response_formatter", END)
    
    # Compile with checkpointing
    memory = SqliteSaver.from_conn_string(":memory:")
    return workflow.compile(checkpointer=memory)
```

---

## 🤖 Chat Subgraph

```
┌────────────────────────────────────────────────────────────┐
│                    CHAT SUBGRAPH                           │
└────────────────────────────────────────────────────────────┘

    START
      │
      ▼
┌─────────────────┐
│ Retrieve        │
│ Conversation    │
│ Context         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Load Prompts &  │
│ Knowledge Base  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐         ┌──────────────┐
│ Generate        │────────►│ Vector DB    │
│ Response        │         │ Search       │
└────────┬────────┘         └──────────────┘
         │
         ▼
┌─────────────────┐
│ Save to         │
│ Conversation    │
└────────┬────────┘
         │
         ▼
      END
```

### Implementation:

```python
from typing import TypedDict

class ChatState(TypedDict):
    """State for chat subgraph"""
    query: str
    conversation_history: List[Dict]
    knowledge_context: Optional[str]
    response: str
    user_id: str

def create_chat_subgraph():
    """Create chat conversation subgraph"""
    
    workflow = StateGraph(ChatState)
    
    workflow.add_node("retrieve_context", retrieve_conversation_context)
    workflow.add_node("vector_search", perform_vector_search)
    workflow.add_node("generate_response", generate_llm_response)
    workflow.add_node("save_conversation", save_to_database)
    
    workflow.set_entry_point("retrieve_context")
    workflow.add_edge("retrieve_context", "vector_search")
    workflow.add_edge("vector_search", "generate_response")
    workflow.add_edge("generate_response", "save_conversation")
    workflow.add_edge("save_conversation", END)
    
    return workflow.compile()
```

---

## 🔄 Migration Subgraph (Complex Flow)

```
┌────────────────────────────────────────────────────────────────┐
│                  MIGRATION SUBGRAPH                            │
└────────────────────────────────────────────────────────────────┘

         START
           │
           ▼
    ┌──────────────┐
    │ Validate     │
    │ Connections  │
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │ Schema       │◄────────┐
    │ Analysis     │         │ Parallel
    └──────┬───────┘         │
           │                 │
           ▼                 │
    ┌──────────────┐         │
    │ Compatibility│         │
    │ Scoring      │─────────┘
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │ Generate     │
    │ Migration    │
    │ Plan         │
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐      ┌─────────────┐
    │ Human        │─────►│ Approval    │
    │ Approval?    │      │ Required    │
    └──────┬───────┘      └─────────────┘
           │                     │
           │ Approved            │ Rejected
           ▼                     ▼
    ┌──────────────┐       ┌──────────┐
    │ Execute      │       │ Revise   │
    │ Migration    │       │ Plan     │
    └──────┬───────┘       └────┬─────┘
           │                     │
           ▼                     │
    ┌──────────────┐            │
    │ Validate     │            │
    │ Results      │            │
    └──────┬───────┘            │
           │                     │
     ┌─────┴─────┐              │
     │           │              │
     ▼           ▼              │
  Success?     Failed           │
     │           │              │
     │           ▼              │
     │     ┌──────────┐         │
     │     │ Rollback │         │
     │     └────┬─────┘         │
     │          │               │
     └──────────┴───────────────┘
                │
                ▼
             END
```

### Implementation:

```python
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver

class MigrationState(TypedDict):
    """State for migration subgraph"""
    source_connection: Dict
    target_connection: Dict
    source_schema: Optional[Dict]
    target_schema: Optional[Dict]
    compatibility_score: Optional[float]
    migration_plan: Optional[Dict]
    execution_results: Optional[Dict]
    validation_results: Optional[Dict]
    needs_approval: bool
    approved: Optional[bool]
    status: str
    errors: List[str]

def create_migration_subgraph():
    """Create migration workflow subgraph"""
    
    workflow = StateGraph(MigrationState)
    
    # Add nodes
    workflow.add_node("validate_connections", validate_connections_node)
    workflow.add_node("analyze_source_schema", analyze_source_schema_node)
    workflow.add_node("analyze_target_schema", analyze_target_schema_node)
    workflow.add_node("calculate_compatibility", calculate_compatibility_node)
    workflow.add_node("generate_migration_plan", generate_plan_node)
    workflow.add_node("human_approval", human_approval_node)
    workflow.add_node("execute_migration", execute_migration_node)
    workflow.add_node("validate_results", validate_results_node)
    workflow.add_node("rollback", rollback_node)
    workflow.add_node("revise_plan", revise_plan_node)
    
    # Entry point
    workflow.set_entry_point("validate_connections")
    
    # Parallel schema analysis
    workflow.add_edge("validate_connections", "analyze_source_schema")
    workflow.add_edge("validate_connections", "analyze_target_schema")
    
    # Join parallel branches
    workflow.add_edge("analyze_source_schema", "calculate_compatibility")
    workflow.add_edge("analyze_target_schema", "calculate_compatibility")
    
    # Plan generation
    workflow.add_edge("calculate_compatibility", "generate_migration_plan")
    
    # Conditional: check if approval needed
    workflow.add_conditional_edges(
        "generate_migration_plan",
        check_approval_needed,
        {
            "needs_approval": "human_approval",
            "auto_execute": "execute_migration"
        }
    )
    
    # Human approval routing
    workflow.add_conditional_edges(
        "human_approval",
        check_approval_status,
        {
            "approved": "execute_migration",
            "rejected": "revise_plan"
        }
    )
    
    # Revise and retry
    workflow.add_edge("revise_plan", "generate_migration_plan")
    
    # Validation routing
    workflow.add_edge("execute_migration", "validate_results")
    workflow.add_conditional_edges(
        "validate_results",
        check_validation_status,
        {
            "success": END,
            "failed": "rollback"
        }
    )
    
    workflow.add_edge("rollback", END)
    
    # Compile with persistence
    memory = SqliteSaver.from_conn_string("./migration_checkpoints.db")
    return workflow.compile(checkpointer=memory, interrupt_before=["human_approval"])
```

---

## 🔍 Schema Analysis Subgraph

```
┌────────────────────────────────────────────────────────┐
│              SCHEMA ANALYSIS SUBGRAPH                  │
└────────────────────────────────────────────────────────┘

      START
        │
        ▼
  ┌─────────────┐
  │ Connect to  │
  │ Database    │
  └──────┬──────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐ ┌────────┐
│Extract │ │Extract │  Parallel
│Tables  │ │Views   │
└───┬────┘ └───┬────┘
    │          │
    └────┬─────┘
         │
         ▼
  ┌─────────────┐
  │ Analyze     │
  │ Relationships│
  └──────┬──────┘
         │
         ▼
  ┌─────────────┐
  │ Generate    │
  │ MDL/ERD     │
  └──────┬──────┘
         │
         ▼
  ┌─────────────┐
  │ Cache       │
  │ Results     │
  └──────┬──────┘
         │
         ▼
       END
```

---

## 💡 SQL Generation Subgraph

```
┌────────────────────────────────────────────────────────┐
│              SQL GENERATION SUBGRAPH                   │
└────────────────────────────────────────────────────────┘

      START
        │
        ▼
  ┌─────────────┐
  │ Parse       │
  │ Question    │
  └──────┬──────┘
         │
         ▼
  ┌─────────────┐      ┌──────────────┐
  │ Retrieve    │─────►│ Vector Store │
  │ Schema      │      │ (MDL/Schema) │
  └──────┬──────┘      └──────────────┘
         │
         ▼
  ┌─────────────┐      ┌──────────────┐
  │ Generate    │─────►│ Few-shot     │
  │ SQL         │      │ Examples     │
  └──────┬──────┘      └──────────────┘
         │
         ▼
  ┌─────────────┐
  │ Validate    │
  │ SQL         │
  └──────┬──────┘
         │
    ┌────┴────┐
    │         │
Valid?      Invalid
    │         │
    ▼         ▼
  ┌────┐  ┌────────┐
  │ OK │  │ Refine │─┐
  └─┬──┘  └────────┘ │
    │         ▲       │
    │         └───────┘
    │
    ▼
  ┌─────────────┐
  │ Execute     │
  │ (Optional)  │
  └──────┬──────┘
         │
         ▼
       END
```

---

## 🛠️ Implementation Plan

### Phase 1: Core Infrastructure (Week 1-2)
```python
# 1. Install dependencies
pip install langgraph langchain langchain-openai langchain-google-genai

# 2. Define state schemas
# - ChatbotState
# - MigrationState
# - SchemaState
# - SQLGenerationState

# 3. Create base graph structure
# - Router graph
# - State management
# - Checkpointing setup
```

### Phase 2: Migrate Existing Agents (Week 2-3)
```python
# 1. Wrap existing agents as LangGraph nodes
# - SchemaAnalyzerAgent -> analyze_schema_node()
# - MigrationPlannerAgent -> generate_plan_node()
# - DataTransformAgent -> transform_data_node()
# - ValidationAgent -> validate_results_node()

# 2. Update agents to use state instead of direct parameters
# 3. Add error handling and retry logic
```

### Phase 3: Build Subgraphs (Week 3-4)
```python
# 1. Chat Subgraph
# 2. Migration Subgraph
# 3. Schema Analysis Subgraph
# 4. SQL Generation Subgraph
```

### Phase 4: Integration & Testing (Week 4-5)
```python
# 1. Integrate with FastAPI
# 2. Add streaming support
# 3. Human-in-the-loop interface
# 4. Testing & debugging
```

### Phase 5: Production Ready (Week 5-6)
```python
# 1. Add monitoring and logging
# 2. Performance optimization
# 3. Documentation
# 4. Deployment
```

---

## 📝 Code Structure

```
finx-ai-service/
├── src/
│   ├── langgraph/
│   │   ├── __init__.py
│   │   ├── graphs/
│   │   │   ├── __init__.py
│   │   │   ├── router.py              # Main router graph
│   │   │   ├── chat_graph.py          # Chat subgraph
│   │   │   ├── migration_graph.py     # Migration subgraph
│   │   │   ├── schema_graph.py        # Schema subgraph
│   │   │   └── sql_graph.py           # SQL generation subgraph
│   │   ├── nodes/
│   │   │   ├── __init__.py
│   │   │   ├── chat_nodes.py          # Chat-related nodes
│   │   │   ├── migration_nodes.py     # Migration nodes
│   │   │   ├── schema_nodes.py        # Schema analysis nodes
│   │   │   └── sql_nodes.py           # SQL generation nodes
│   │   ├── state/
│   │   │   ├── __init__.py
│   │   │   ├── schemas.py             # State schemas
│   │   │   └── reducers.py            # State reducers
│   │   ├── tools/
│   │   │   ├── __init__.py
│   │   │   ├── database_tools.py
│   │   │   ├── llm_tools.py
│   │   │   └── validation_tools.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── routing.py             # Routing logic
│   │       └── checkpointing.py       # Checkpoint utilities
│   ├── core/                          # Existing agents (will be wrapped)
│   │   ├── migration_agent.py
│   │   └── ...
│   └── web/
│       ├── routers/
│       │   └── langgraph_router.py    # FastAPI router for LangGraph
│       └── ...
└── tests/
    └── langgraph/
        ├── test_graphs.py
        ├── test_nodes.py
        └── test_integration.py
```

---

## 🚀 Quick Start Example

```python
from src.langgraph.graphs.router import create_router_graph
from src.langgraph.state.schemas import ChatbotState

# Initialize graph
graph = create_router_graph()

# Create initial state
initial_state = ChatbotState(
    user_id="user_123",
    session_id="session_456",
    user_query="Migrate data from MySQL to PostgreSQL",
    conversation_history=[],
    connections=[],
    needs_human_approval=False,
    metadata={}
)

# Run graph
config = {"configurable": {"thread_id": "session_456"}}
result = graph.invoke(initial_state, config)

print(result["response"])
```

---

## 🎨 Visualization Tools

LangGraph cung cấp built-in visualization:

```python
from IPython.display import Image, display

# Visualize graph structure
display(Image(graph.get_graph().draw_mermaid_png()))
```

---

## 📊 Monitoring & Observability

```python
from langchain.callbacks import LangChainTracer

# Add tracing
tracer = LangChainTracer(project_name="finx-chatbot")

result = graph.invoke(
    initial_state,
    config={
        "configurable": {"thread_id": "session_456"},
        "callbacks": [tracer]
    }
)
```

---

## 🔐 Security Considerations

1. **Checkpoint Security**: Encrypt sensitive data in checkpoints
2. **Human Approval**: Add authentication for approval endpoints
3. **Connection Credentials**: Never store in state, use secure vault
4. **Input Validation**: Validate all user inputs before processing

---

## 📚 Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangGraph Tutorials](https://github.com/langchain-ai/langgraph/tree/main/examples)
- [State Management Guide](https://langchain-ai.github.io/langgraph/concepts/low_level/#state)

---

**Last Updated**: 2025-01-26  
**Version**: 1.0.0  
**Author**: AI Team
