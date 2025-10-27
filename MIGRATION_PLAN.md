# FinX AI Service: Detailed Migration Plan

## Overview

This document provides a step-by-step migration plan from Haystack to LangGraph, with specific implementation details, code examples, and testing strategies.

---

## Part 1: State Schema Design

### 1.1 Core State Schemas

**DB Schema Indexing State:**
```python
from typing import TypedDict, List, Optional

class DBSchemaIndexingState(TypedDict):
    # Inputs
    mdl_str: str
    project_id: Optional[str]
    column_batch_size: int
    
    # Processing stages
    validated_mdl: Optional[dict]
    chunks: Optional[List[dict]]
    embeddings: Optional[List[dict]]
    
    # Output
    indexed_documents: Optional[List[dict]]
    
    # Metadata
    errors: List[str]
    status: str  # "pending", "processing", "completed", "failed"
```

**Question Recommendation State:**
```python
class QuestionRecommendationState(TypedDict):
    # Inputs
    contexts: List[str]
    previous_questions: List[str]
    categories: List[str]
    language: str
    max_questions: int
    max_categories: int
    
    # Processing
    prompt_text: Optional[str]
    raw_response: Optional[str]
    
    # Output
    questions: Optional[List[dict]]
    
    # Metadata
    errors: List[str]
    status: str
```

### 1.2 Shared State Components

```python
class SharedPipelineState(TypedDict):
    # Providers (injected at graph creation)
    llm_provider: Any
    embedder_provider: Any
    document_store_provider: Any
    engine: Any
    
    # Observability
    trace_id: str
    start_time: float
    
    # Configuration
    config: dict
```

---

## Part 2: Node Implementation Pattern

### 2.1 Base Node Template

```python
from langgraph.graph import StateGraph
from typing import Any, Dict

async def validation_node(state: DBSchemaIndexingState) -> Dict[str, Any]:
    """
    Validates MDL string and converts to structured format.
    
    Args:
        state: Current pipeline state
        
    Returns:
        Updated state with validated_mdl
    """
    try:
        validator = MDLValidator()
        result = validator.run(mdl=state["mdl_str"])
        
        return {
            "validated_mdl": result["mdl"],
            "status": "validated"
        }
    except Exception as e:
        return {
            "errors": state.get("errors", []) + [str(e)],
            "status": "failed"
        }

async def chunking_node(state: DBSchemaIndexingState) -> Dict[str, Any]:
    """Chunks validated MDL into documents."""
    if state.get("status") == "failed":
        return {"status": "skipped"}
    
    try:
        chunker = DDLChunker()
        result = await chunker.run(
            mdl=state["validated_mdl"],
            column_batch_size=state["column_batch_size"],
            project_id=state.get("project_id")
        )
        
        return {
            "chunks": result["documents"],
            "status": "chunked"
        }
    except Exception as e:
        return {
            "errors": state.get("errors", []) + [str(e)],
            "status": "failed"
        }
```

### 2.2 Conditional Routing

```python
def should_continue(state: DBSchemaIndexingState) -> str:
    """Route based on current status."""
    if state.get("status") == "failed":
        return "error_handler"
    elif state.get("status") == "chunked":
        return "embedding"
    else:
        return "end"
```

---

## Part 3: Graph Construction

### 3.1 DB Schema Indexing Graph

```python
from langgraph.graph import StateGraph, END

def create_db_schema_graph(
    embedder_provider,
    document_store_provider
) -> StateGraph:
    """Create DB schema indexing graph."""
    
    graph = StateGraph(DBSchemaIndexingState)
    
    # Add nodes
    graph.add_node("validate", validation_node)
    graph.add_node("chunk", chunking_node)
    graph.add_node("embed", embedding_node)
    graph.add_node("clean", cleaning_node)
    graph.add_node("write", writing_node)
    graph.add_node("error_handler", error_handler_node)
    
    # Add edges
    graph.add_edge("validate", "chunk")
    graph.add_conditional_edges(
        "chunk",
        should_continue,
        {
            "embedding": "embed",
            "error_handler": "error_handler",
            "end": END
        }
    )
    graph.add_edge("embed", "clean")
    graph.add_edge("clean", "write")
    graph.add_edge("write", END)
    graph.add_edge("error_handler", END)
    
    # Set entry point
    graph.set_entry_point("validate")
    
    return graph.compile()
```

### 3.2 Question Recommendation Graph

```python
def create_question_recommendation_graph(
    llm_provider
) -> StateGraph:
    """Create question recommendation graph."""
    
    graph = StateGraph(QuestionRecommendationState)
    
    # Add nodes
    graph.add_node("build_prompt", prompt_building_node)
    graph.add_node("generate", generation_node)
    graph.add_node("normalize", normalization_node)
    graph.add_node("error_handler", error_handler_node)
    
    # Add edges
    graph.add_edge("build_prompt", "generate")
    graph.add_conditional_edges(
        "generate",
        lambda s: "error_handler" if s.get("status") == "failed" else "normalize",
        {"error_handler": "error_handler", "normalize": "normalize"}
    )
    graph.add_edge("normalize", END)
    graph.add_edge("error_handler", END)
    
    graph.set_entry_point("build_prompt")
    
    return graph.compile()
```

---

## Part 4: Provider Integration

### 4.1 Updated Provider Pattern

```python
class LLMProvider(ABC):
    """Updated provider with LangGraph support."""
    
    @abstractmethod
    async def generate(self, prompt: str) -> str:
        """Generate text from prompt."""
        pass
    
    def get_model(self) -> str:
        return self._model

class EmbedderProvider(ABC):
    """Updated embedder provider."""
    
    @abstractmethod
    async def embed_documents(self, documents: List[dict]) -> List[List[float]]:
        """Embed documents."""
        pass
    
    def get_model(self) -> str:
        return self._embedding_model
```

### 4.2 Graph Execution with Providers

```python
async def run_db_schema_indexing(
    mdl_str: str,
    embedder_provider: EmbedderProvider,
    document_store_provider: DocumentStoreProvider,
    project_id: Optional[str] = None
) -> Dict[str, Any]:
    """Execute DB schema indexing pipeline."""
    
    graph = create_db_schema_graph(
        embedder_provider,
        document_store_provider
    )
    
    initial_state = DBSchemaIndexingState(
        mdl_str=mdl_str,
        project_id=project_id,
        column_batch_size=50,
        validated_mdl=None,
        chunks=None,
        embeddings=None,
        indexed_documents=None,
        errors=[],
        status="pending"
    )
    
    result = await graph.ainvoke(initial_state)
    return result
```

---

## Part 5: Testing Strategy

### 5.1 Unit Tests for Nodes

```python
import pytest

@pytest.mark.asyncio
async def test_validation_node():
    """Test MDL validation node."""
    state = DBSchemaIndexingState(
        mdl_str='{"models": [], "relationships": []}',
        # ... other fields
    )
    
    result = await validation_node(state)
    
    assert result["status"] == "validated"
    assert result["validated_mdl"] is not None

@pytest.mark.asyncio
async def test_chunking_node():
    """Test chunking node."""
    state = DBSchemaIndexingState(
        validated_mdl={"models": [], "relationships": []},
        # ... other fields
    )
    
    result = await chunking_node(state)
    
    assert result["status"] == "chunked"
    assert isinstance(result["chunks"], list)
```

### 5.2 Integration Tests

```python
@pytest.mark.asyncio
async def test_db_schema_indexing_pipeline():
    """Test complete DB schema indexing pipeline."""
    
    # Setup
    embedder_provider = MockEmbedderProvider()
    document_store_provider = MockDocumentStoreProvider()
    
    # Execute
    result = await run_db_schema_indexing(
        mdl_str='{"models": [], "relationships": []}',
        embedder_provider=embedder_provider,
        document_store_provider=document_store_provider
    )
    
    # Assert
    assert result["status"] == "completed"
    assert result["indexed_documents"] is not None
    assert len(result["errors"]) == 0
```

---

## Part 6: Migration Checklist

- [ ] Create state schemas
- [ ] Implement node functions
- [ ] Build graph structures
- [ ] Update provider interfaces
- [ ] Write unit tests
- [ ] Write integration tests
- [ ] Update FastAPI endpoints
- [ ] Performance testing
- [ ] Documentation updates
- [ ] Deprecate Haystack code
- [ ] Remove dependencies

---

## Part 7: Rollback Plan

If issues arise:
1. Keep Haystack code in separate branch
2. Maintain dual-running pipelines temporarily
3. Use feature flags for gradual rollout
4. Monitor performance metrics
5. Have rollback procedure documented


