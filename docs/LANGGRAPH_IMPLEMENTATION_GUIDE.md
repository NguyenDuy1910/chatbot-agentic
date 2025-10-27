# LangGraph Implementation Guide

## 🚀 Hướng dẫn triển khai LangGraph cho FinX AI Chatbot

Tài liệu này cung cấp hướng dẫn chi tiết từng bước để áp dụng LangGraph vào project.

---

## 📦 Step 1: Cài đặt Dependencies

### requirements.txt
```txt
# LangGraph & LangChain
langgraph>=0.2.0
langchain>=0.2.0
langchain-openai>=0.1.0
langchain-google-genai>=1.0.0
langchain-anthropic>=0.1.0
langchain-community>=0.2.0

# Checkpointing
aiosqlite>=0.19.0

# Existing dependencies
fastapi>=0.110.0
pydantic>=2.5.0
uvicorn>=0.27.0
sqlalchemy>=2.0.0
# ... (giữ nguyên các dependencies hiện tại)
```

### Cài đặt
```bash
cd finx-ai-service
pip install langgraph langchain langchain-openai langchain-google-genai aiosqlite
```

---

## 🏗️ Step 2: Định nghĩa State Schemas

### File: `src/langgraph/state/schemas.py`

```python
"""
State schemas for LangGraph workflows
"""

from typing import TypedDict, Annotated, List, Dict, Any, Optional, Literal
from operator import add
from datetime import datetime
from enum import Enum


# ====================
# Enums
# ====================

class IntentType(str, Enum):
    """User intent types"""
    CHAT = "chat"
    SQL_GENERATION = "sql_generation"
    SCHEMA_ANALYSIS = "schema_analysis"
    MIGRATION = "migration"
    CONNECTION_MANAGEMENT = "connection_management"
    UNKNOWN = "unknown"


class MigrationStatus(str, Enum):
    """Migration workflow status"""
    PENDING = "pending"
    ANALYZING = "analyzing"
    PLANNING = "planning"
    AWAITING_APPROVAL = "awaiting_approval"
    EXECUTING = "executing"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


# ====================
# State Schemas
# ====================

class BaseState(TypedDict):
    """Base state with common fields"""
    timestamp: str
    user_id: str
    session_id: str
    errors: Annotated[List[str], add]
    metadata: Dict[str, Any]


class ChatbotState(BaseState):
    """
    Main state for the entire chatbot system.
    This is the top-level state that flows through the router graph.
    """
    # User input
    user_query: str
    intent: Optional[IntentType]
    
    # Conversation context
    conversation_history: Annotated[List[Dict[str, str]], add]
    
    # Database context
    connections: List[Dict[str, Any]]
    active_connection_id: Optional[str]
    schema_context: Optional[Dict[str, Any]]
    
    # Subgraph states (populated by subgraphs)
    chat_result: Optional[Dict[str, Any]]
    migration_result: Optional[Dict[str, Any]]
    schema_result: Optional[Dict[str, Any]]
    sql_result: Optional[Dict[str, Any]]
    
    # Final response
    response: Optional[str]
    response_type: Optional[str]  # 'text', 'sql', 'schema', 'migration_plan'
    
    # Control flow
    needs_human_approval: bool
    approved: Optional[bool]
    should_continue: bool


class ChatState(TypedDict):
    """State for chat conversation subgraph"""
    query: str
    conversation_history: List[Dict[str, str]]
    user_id: str
    session_id: str
    
    # Retrieved context
    knowledge_context: Optional[str]
    relevant_prompts: List[Dict[str, Any]]
    
    # LLM generation
    response: str
    response_metadata: Dict[str, Any]
    
    # Errors
    errors: Annotated[List[str], add]


class SchemaAnalysisState(TypedDict):
    """State for schema analysis subgraph"""
    connection_id: str
    connection_info: Dict[str, Any]
    
    # Schema extraction
    tables: List[Dict[str, Any]]
    views: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]
    
    # Analysis results
    schema_summary: Optional[Dict[str, Any]]
    mdl_output: Optional[str]
    erd_diagram: Optional[str]
    
    # Caching
    cache_key: Optional[str]
    cached: bool
    
    # Errors
    errors: Annotated[List[str], add]


class MigrationState(TypedDict):
    """State for migration workflow subgraph"""
    # Input
    source_connection_id: str
    target_connection_id: str
    migration_config: Dict[str, Any]
    
    # Connections
    source_connection: Dict[str, Any]
    target_connection: Dict[str, Any]
    
    # Schema analysis
    source_schema: Optional[Dict[str, Any]]
    target_schema: Optional[Dict[str, Any]]
    
    # Compatibility analysis
    compatibility_score: Optional[float]
    compatibility_issues: List[Dict[str, Any]]
    
    # Migration plan
    migration_plan: Optional[Dict[str, Any]]
    migration_strategy: Optional[str]  # 'full_copy', 'incremental', 'streaming'
    
    # Execution
    execution_status: MigrationStatus
    execution_progress: float
    execution_results: Optional[Dict[str, Any]]
    
    # Validation
    validation_results: Optional[Dict[str, Any]]
    validation_passed: bool
    
    # Human approval
    needs_approval: bool
    approved: Optional[bool]
    approval_notes: Optional[str]
    
    # Rollback
    rollback_available: bool
    rollback_executed: bool
    
    # Errors
    errors: Annotated[List[str], add]


class SQLGenerationState(TypedDict):
    """State for SQL generation subgraph"""
    # Input
    question: str
    connection_id: str
    
    # Context
    schema_context: Dict[str, Any]
    relevant_examples: List[Dict[str, str]]
    
    # Generation
    generated_sql: Optional[str]
    sql_explanation: Optional[str]
    
    # Validation
    sql_valid: bool
    validation_errors: List[str]
    
    # Refinement
    refinement_iterations: int
    max_iterations: int
    
    # Execution (optional)
    should_execute: bool
    execution_results: Optional[Any]
    
    # Errors
    errors: Annotated[List[str], add]


# ====================
# Helper Functions
# ====================

def create_initial_chatbot_state(
    user_id: str,
    session_id: str,
    user_query: str,
    connections: List[Dict[str, Any]] = None
) -> ChatbotState:
    """Create initial chatbot state"""
    return ChatbotState(
        timestamp=datetime.utcnow().isoformat(),
        user_id=user_id,
        session_id=session_id,
        user_query=user_query,
        intent=None,
        conversation_history=[],
        connections=connections or [],
        active_connection_id=None,
        schema_context=None,
        chat_result=None,
        migration_result=None,
        schema_result=None,
        sql_result=None,
        response=None,
        response_type=None,
        needs_human_approval=False,
        approved=None,
        should_continue=True,
        errors=[],
        metadata={}
    )


def merge_state(base_state: Dict, updates: Dict) -> Dict:
    """Merge state updates with base state"""
    merged = base_state.copy()
    for key, value in updates.items():
        if key in merged and isinstance(merged[key], list) and isinstance(value, list):
            # Append to list (for annotated fields with add operator)
            merged[key] = merged[key] + value
        else:
            # Replace value
            merged[key] = value
    return merged
```

---

## 🔧 Step 3: Tạo Nodes cho LangGraph

### File: `src/langgraph/nodes/chat_nodes.py`

```python
"""
Nodes for chat conversation workflow
"""

import logging
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, AIMessage, SystemMessage

from src.langgraph.state.schemas import ChatState
from src.web.constants.config import AI_CONFIG

logger = logging.getLogger(__name__)


async def retrieve_conversation_context(state: ChatState) -> Dict[str, Any]:
    """
    Retrieve conversation history and context from database
    """
    logger.info(f"Retrieving conversation context for user {state['user_id']}")
    
    try:
        # TODO: Query database for conversation history
        # For now, use existing conversation_history from state
        
        return {
            "conversation_history": state.get("conversation_history", [])
        }
    except Exception as e:
        logger.error(f"Error retrieving context: {e}")
        return {
            "errors": [f"Context retrieval error: {str(e)}"]
        }


async def perform_vector_search(state: ChatState) -> Dict[str, Any]:
    """
    Perform vector search on knowledge base for relevant context
    """
    logger.info(f"Performing vector search for query: {state['query'][:50]}...")
    
    try:
        # TODO: Implement vector search
        # For now, return empty context
        
        return {
            "knowledge_context": None,
            "relevant_prompts": []
        }
    except Exception as e:
        logger.error(f"Error in vector search: {e}")
        return {
            "errors": [f"Vector search error: {str(e)}"]
        }


async def generate_llm_response(state: ChatState) -> Dict[str, Any]:
    """
    Generate response using LLM
    """
    logger.info("Generating LLM response")
    
    try:
        # Initialize LLM based on config
        provider = AI_CONFIG.get("DEFAULT_PROVIDER", "openai")
        
        if provider == "openai":
            llm = ChatOpenAI(
                model=AI_CONFIG.get("OPENAI_MODEL", "gpt-4"),
                temperature=0.7
            )
        elif provider == "google":
            llm = ChatGoogleGenerativeAI(
                model=AI_CONFIG.get("GOOGLE_MODEL", "gemini-pro"),
                temperature=0.7
            )
        else:
            raise ValueError(f"Unknown provider: {provider}")
        
        # Build conversation messages
        messages = []
        
        # System message
        system_prompt = """You are a helpful AI assistant for FinX, a financial data platform.
        You help users with:
        - Natural language questions about their data
        - SQL query generation
        - Schema analysis
        - Data migration
        
        Be concise, accurate, and helpful."""
        messages.append(SystemMessage(content=system_prompt))
        
        # Add conversation history
        for msg in state.get("conversation_history", []):
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))
        
        # Add current query
        messages.append(HumanMessage(content=state["query"]))
        
        # Generate response
        response = await llm.ainvoke(messages)
        
        return {
            "response": response.content,
            "response_metadata": {
                "model": provider,
                "tokens": response.response_metadata.get("token_usage", {})
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        return {
            "response": "I apologize, but I encountered an error generating a response.",
            "errors": [f"LLM generation error: {str(e)}"]
        }


async def save_to_database(state: ChatState) -> Dict[str, Any]:
    """
    Save conversation to database
    """
    logger.info(f"Saving conversation for user {state['user_id']}")
    
    try:
        # TODO: Save to database
        # For now, just return success
        
        return {
            "metadata": {
                "saved": True
            }
        }
    except Exception as e:
        logger.error(f"Error saving to database: {e}")
        return {
            "errors": [f"Database save error: {str(e)}"]
        }
```

### File: `src/langgraph/nodes/migration_nodes.py`

```python
"""
Nodes for migration workflow
"""

import logging
from typing import Dict, Any
from datetime import datetime

from src.langgraph.state.schemas import MigrationState, MigrationStatus
from src.core.migration_agent import (
    SchemaAnalyzerAgent,
    MigrationPlannerAgent,
    MigrationExecutorAgent,
    ValidationAgent
)

logger = logging.getLogger(__name__)


async def validate_connections_node(state: MigrationState) -> Dict[str, Any]:
    """Validate source and target connections"""
    logger.info("Validating migration connections")
    
    try:
        # TODO: Validate connections using existing connection manager
        # For now, assume valid
        
        return {
            "execution_status": MigrationStatus.ANALYZING
        }
    except Exception as e:
        logger.error(f"Connection validation error: {e}")
        return {
            "execution_status": MigrationStatus.FAILED,
            "errors": [f"Connection validation failed: {str(e)}"]
        }


async def analyze_source_schema_node(state: MigrationState) -> Dict[str, Any]:
    """Analyze source database schema"""
    logger.info("Analyzing source schema")
    
    try:
        # Use existing SchemaAnalyzerAgent
        analyzer = SchemaAnalyzerAgent()
        
        # TODO: Properly initialize and call analyzer
        # For now, return mock data
        source_schema = {
            "tables": [],
            "analyzed_at": datetime.utcnow().isoformat()
        }
        
        return {
            "source_schema": source_schema
        }
    except Exception as e:
        logger.error(f"Source schema analysis error: {e}")
        return {
            "errors": [f"Source schema analysis failed: {str(e)}"]
        }


async def analyze_target_schema_node(state: MigrationState) -> Dict[str, Any]:
    """Analyze target database schema"""
    logger.info("Analyzing target schema")
    
    try:
        analyzer = SchemaAnalyzerAgent()
        
        # TODO: Properly initialize and call analyzer
        target_schema = {
            "tables": [],
            "analyzed_at": datetime.utcnow().isoformat()
        }
        
        return {
            "target_schema": target_schema
        }
    except Exception as e:
        logger.error(f"Target schema analysis error: {e}")
        return {
            "errors": [f"Target schema analysis failed: {str(e)}"]
        }


async def calculate_compatibility_node(state: MigrationState) -> Dict[str, Any]:
    """Calculate compatibility score between schemas"""
    logger.info("Calculating schema compatibility")
    
    try:
        source_schema = state.get("source_schema")
        target_schema = state.get("target_schema")
        
        if not source_schema or not target_schema:
            raise ValueError("Missing schema information")
        
        # TODO: Implement actual compatibility calculation
        compatibility_score = 0.85
        compatibility_issues = []
        
        return {
            "compatibility_score": compatibility_score,
            "compatibility_issues": compatibility_issues,
            "needs_approval": compatibility_score < 0.9
        }
    except Exception as e:
        logger.error(f"Compatibility calculation error: {e}")
        return {
            "errors": [f"Compatibility calculation failed: {str(e)}"]
        }


async def generate_plan_node(state: MigrationState) -> Dict[str, Any]:
    """Generate migration plan"""
    logger.info("Generating migration plan")
    
    try:
        planner = MigrationPlannerAgent()
        
        # TODO: Use actual planner logic
        migration_plan = {
            "strategy": "batch",
            "steps": [],
            "estimated_duration": "2 hours",
            "created_at": datetime.utcnow().isoformat()
        }
        
        return {
            "migration_plan": migration_plan,
            "migration_strategy": "batch",
            "execution_status": MigrationStatus.PLANNING
        }
    except Exception as e:
        logger.error(f"Plan generation error: {e}")
        return {
            "errors": [f"Plan generation failed: {str(e)}"]
        }


async def human_approval_node(state: MigrationState) -> Dict[str, Any]:
    """
    Wait for human approval.
    This node triggers an interrupt in the graph.
    """
    logger.info("Awaiting human approval for migration")
    
    return {
        "execution_status": MigrationStatus.AWAITING_APPROVAL,
        "needs_approval": True
    }


async def execute_migration_node(state: MigrationState) -> Dict[str, Any]:
    """Execute migration plan"""
    logger.info("Executing migration")
    
    try:
        executor = MigrationExecutorAgent()
        
        # TODO: Execute actual migration
        execution_results = {
            "started_at": datetime.utcnow().isoformat(),
            "rows_migrated": 0,
            "status": "in_progress"
        }
        
        return {
            "execution_results": execution_results,
            "execution_status": MigrationStatus.EXECUTING,
            "execution_progress": 0.5
        }
    except Exception as e:
        logger.error(f"Migration execution error: {e}")
        return {
            "execution_status": MigrationStatus.FAILED,
            "errors": [f"Migration execution failed: {str(e)}"]
        }


async def validate_results_node(state: MigrationState) -> Dict[str, Any]:
    """Validate migration results"""
    logger.info("Validating migration results")
    
    try:
        validator = ValidationAgent()
        
        # TODO: Actual validation
        validation_results = {
            "validated_at": datetime.utcnow().isoformat(),
            "checks_passed": 10,
            "checks_failed": 0
        }
        
        validation_passed = validation_results["checks_failed"] == 0
        
        return {
            "validation_results": validation_results,
            "validation_passed": validation_passed,
            "execution_status": MigrationStatus.COMPLETED if validation_passed else MigrationStatus.FAILED
        }
    except Exception as e:
        logger.error(f"Validation error: {e}")
        return {
            "validation_passed": False,
            "errors": [f"Validation failed: {str(e)}"]
        }


async def rollback_node(state: MigrationState) -> Dict[str, Any]:
    """Rollback migration"""
    logger.info("Rolling back migration")
    
    try:
        # TODO: Implement rollback logic
        
        return {
            "rollback_executed": True,
            "execution_status": MigrationStatus.ROLLED_BACK
        }
    except Exception as e:
        logger.error(f"Rollback error: {e}")
        return {
            "errors": [f"Rollback failed: {str(e)}"]
        }


async def revise_plan_node(state: MigrationState) -> Dict[str, Any]:
    """Revise migration plan based on feedback"""
    logger.info("Revising migration plan")
    
    try:
        # TODO: Implement plan revision logic
        
        return {
            "execution_status": MigrationStatus.PLANNING
        }
    except Exception as e:
        logger.error(f"Plan revision error: {e}")
        return {
            "errors": [f"Plan revision failed: {str(e)}"]
        }
```

---

## 🔄 Step 4: Tạo Graphs

### File: `src/langgraph/graphs/chat_graph.py`

```python
"""
Chat conversation subgraph
"""

import logging
from langgraph.graph import StateGraph, END

from src.langgraph.state.schemas import ChatState
from src.langgraph.nodes.chat_nodes import (
    retrieve_conversation_context,
    perform_vector_search,
    generate_llm_response,
    save_to_database
)

logger = logging.getLogger(__name__)


def create_chat_subgraph():
    """Create chat conversation subgraph"""
    logger.info("Creating chat subgraph")
    
    workflow = StateGraph(ChatState)
    
    # Add nodes
    workflow.add_node("retrieve_context", retrieve_conversation_context)
    workflow.add_node("vector_search", perform_vector_search)
    workflow.add_node("generate_response", generate_llm_response)
    workflow.add_node("save_conversation", save_to_database)
    
    # Define edges
    workflow.set_entry_point("retrieve_context")
    workflow.add_edge("retrieve_context", "vector_search")
    workflow.add_edge("vector_search", "generate_response")
    workflow.add_edge("generate_response", "save_conversation")
    workflow.add_edge("save_conversation", END)
    
    return workflow.compile()
```

### File: `src/langgraph/graphs/migration_graph.py`

```python
"""
Migration workflow subgraph
"""

import logging
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.aiosqlite import AsyncSqliteSaver

from src.langgraph.state.schemas import MigrationState, MigrationStatus
from src.langgraph.nodes.migration_nodes import (
    validate_connections_node,
    analyze_source_schema_node,
    analyze_target_schema_node,
    calculate_compatibility_node,
    generate_plan_node,
    human_approval_node,
    execute_migration_node,
    validate_results_node,
    rollback_node,
    revise_plan_node
)

logger = logging.getLogger(__name__)


def check_approval_needed(state: MigrationState) -> str:
    """Check if human approval is needed"""
    if state.get("needs_approval", False):
        return "needs_approval"
    return "auto_execute"


def check_approval_status(state: MigrationState) -> str:
    """Check approval status"""
    if state.get("approved", False):
        return "approved"
    return "rejected"


def check_validation_status(state: MigrationState) -> str:
    """Check validation results"""
    if state.get("validation_passed", False):
        return "success"
    return "failed"


async def create_migration_subgraph():
    """Create migration workflow subgraph"""
    logger.info("Creating migration subgraph")
    
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
    
    # Sequential flow for schema analysis
    workflow.add_edge("validate_connections", "analyze_source_schema")
    workflow.add_edge("analyze_source_schema", "analyze_target_schema")
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
    
    # Compile with persistence and interrupts
    memory = AsyncSqliteSaver.from_conn_string("./data/migration_checkpoints.db")
    return workflow.compile(
        checkpointer=memory,
        interrupt_before=["human_approval"]  # Wait for approval
    )
```

---

**Tiếp tục trong phần 2...**

Tôi đã tạo phần 1 của implementation guide. Bạn có muốn tôi tiếp tục với:
1. Router graph implementation
2. FastAPI integration
3. Testing examples
4. Deployment guide

không?
