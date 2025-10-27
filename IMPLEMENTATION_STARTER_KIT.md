# LangGraph Implementation Starter Kit

This document provides ready-to-use code templates for starting the migration.

---

## 1. Project Structure Setup

```bash
# Create new LangGraph directory structure
mkdir -p finx-ai-service/src/langgraph/{graphs,nodes,state}

# Create __init__.py files
touch finx-ai-service/src/langgraph/__init__.py
touch finx-ai-service/src/langgraph/graphs/__init__.py
touch finx-ai-service/src/langgraph/nodes/__init__.py
touch finx-ai-service/src/langgraph/state/__init__.py
```

---

## 2. State Schemas (src/langgraph/state/schemas.py)

```python
from typing import TypedDict, List, Optional, Any

class DBSchemaIndexingState(TypedDict):
    """State for DB schema indexing pipeline."""
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

class QuestionRecommendationState(TypedDict):
    """State for question recommendation pipeline."""
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

---

## 3. Base Node Utilities (src/langgraph/nodes/base.py)

```python
import logging
from typing import Any, Dict, Callable
from functools import wraps

logger = logging.getLogger(__name__)

def node_error_handler(func: Callable) -> Callable:
    """Decorator for error handling in nodes."""
    async def wrapper(state: Dict[str, Any]) -> Dict[str, Any]:
        try:
            return await func(state)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            return {
                "errors": state.get("errors", []) + [str(e)],
                "status": "failed"
            }
    return wrapper

def should_continue(state: Dict[str, Any], success_status: str) -> str:
    """Generic conditional routing based on status."""
    if state.get("status") == "failed":
        return "error_handler"
    elif state.get("status") == success_status:
        return "continue"
    else:
        return "end"
```

---

## 4. Indexing Nodes (src/langgraph/nodes/indexing_nodes.py)

```python
import logging
from typing import Any, Dict
from src.langgraph.nodes.base import node_error_handler
from src.pipelines.indexing import MDLValidator, DDLChunker

logger = logging.getLogger(__name__)

@node_error_handler
async def validate_mdl_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Validate MDL string."""
    validator = MDLValidator()
    result = validator.run(mdl=state["mdl_str"])
    
    return {
        "validated_mdl": result["mdl"],
        "status": "validated"
    }

@node_error_handler
async def chunk_mdl_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Chunk validated MDL."""
    if state.get("status") == "failed":
        return {"status": "skipped"}
    
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

@node_error_handler
async def embed_documents_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Embed documents."""
    if state.get("status") == "failed":
        return {"status": "skipped"}
    
    # Embedder will be injected from graph context
    embeddings = await state["embedder"].run(
        documents=state["chunks"]
    )
    
    return {
        "embeddings": embeddings,
        "status": "embedded"
    }

@node_error_handler
async def write_documents_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Write documents to store."""
    if state.get("status") == "failed":
        return {"status": "skipped"}
    
    # Document store will be injected from graph context
    await state["document_store"].run(
        documents=state["chunks"]
    )
    
    return {
        "indexed_documents": state["chunks"],
        "status": "completed"
    }

async def error_handler_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Handle errors."""
    logger.error(f"Pipeline failed with errors: {state['errors']}")
    return {"status": "failed"}
```

---

## 5. Graph Construction (src/langgraph/graphs/db_schema_graph.py)

```python
from langgraph.graph import StateGraph, END
from src.langgraph.state.schemas import DBSchemaIndexingState
from src.langgraph.nodes.indexing_nodes import (
    validate_mdl_node,
    chunk_mdl_node,
    embed_documents_node,
    write_documents_node,
    error_handler_node
)

def create_db_schema_graph():
    """Create DB schema indexing graph."""
    
    graph = StateGraph(DBSchemaIndexingState)
    
    # Add nodes
    graph.add_node("validate", validate_mdl_node)
    graph.add_node("chunk", chunk_mdl_node)
    graph.add_node("embed", embed_documents_node)
    graph.add_node("write", write_documents_node)
    graph.add_node("error_handler", error_handler_node)
    
    # Add edges
    graph.add_edge("validate", "chunk")
    graph.add_conditional_edges(
        "chunk",
        lambda s: "error_handler" if s.get("status") == "failed" else "embed",
        {"error_handler": "error_handler", "embed": "embed"}
    )
    graph.add_edge("embed", "write")
    graph.add_edge("write", END)
    graph.add_edge("error_handler", END)
    
    # Set entry point
    graph.set_entry_point("validate")
    
    return graph.compile()
```

---

## 6. Pipeline Wrapper (src/langgraph/pipelines/db_schema.py)

```python
from typing import Optional, Dict, Any
from src.langgraph.graphs.db_schema_graph import create_db_schema_graph
from src.langgraph.state.schemas import DBSchemaIndexingState

class DBSchemaPipeline:
    """LangGraph-based DB Schema indexing pipeline."""
    
    def __init__(self, embedder_provider, document_store_provider):
        self.embedder_provider = embedder_provider
        self.document_store_provider = document_store_provider
        self.graph = create_db_schema_graph()
    
    async def run(
        self,
        mdl_str: str,
        project_id: Optional[str] = None,
        column_batch_size: int = 50
    ) -> Dict[str, Any]:
        """Execute DB schema indexing pipeline."""
        
        initial_state = DBSchemaIndexingState(
            mdl_str=mdl_str,
            project_id=project_id,
            column_batch_size=column_batch_size,
            validated_mdl=None,
            chunks=None,
            embeddings=None,
            indexed_documents=None,
            errors=[],
            status="pending"
        )
        
        # Inject providers into state
        initial_state["embedder"] = self.embedder_provider
        initial_state["document_store"] = self.document_store_provider
        
        result = await self.graph.ainvoke(initial_state)
        return result
```

---

## 7. FastAPI Integration (src/web/routers/langgraph_pipelines.py)

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.langgraph.pipelines.db_schema import DBSchemaPipeline
from src.providers.google_genai import GoogleGenAIEmbedderProvider
from src.providers.qdrant import QdrantDocumentStoreProvider

router = APIRouter()

class DBSchemaIndexRequest(BaseModel):
    mdl_str: str
    project_id: Optional[str] = None
    column_batch_size: int = 50

@router.post("/db-schema-indexing")
async def index_db_schema(request: DBSchemaIndexRequest):
    """Index database schema using LangGraph pipeline."""
    try:
        embedder = GoogleGenAIEmbedderProvider()
        doc_store = QdrantDocumentStoreProvider()
        
        pipeline = DBSchemaPipeline(embedder, doc_store)
        result = await pipeline.run(
            mdl_str=request.mdl_str,
            project_id=request.project_id,
            column_batch_size=request.column_batch_size
        )
        
        return {
            "success": result["status"] == "completed",
            "data": result,
            "errors": result.get("errors", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## 8. Unit Test Template (tests/test_langgraph_nodes.py)

```python
import pytest
from src.langgraph.nodes.indexing_nodes import validate_mdl_node
from src.langgraph.state.schemas import DBSchemaIndexingState

@pytest.mark.asyncio
async def test_validate_mdl_node():
    """Test MDL validation node."""
    state = DBSchemaIndexingState(
        mdl_str='{"models": [], "relationships": []}',
        project_id=None,
        column_batch_size=50,
        validated_mdl=None,
        chunks=None,
        embeddings=None,
        indexed_documents=None,
        errors=[],
        status="pending"
    )
    
    result = await validate_mdl_node(state)
    
    assert result["status"] == "validated"
    assert result["validated_mdl"] is not None
```

---

## 9. Dependencies to Add

```bash
# Add to requirements.txt
langgraph==0.0.x
langchain-core>=0.1.0
```

---

## 10. Quick Start Checklist

- [ ] Create directory structure
- [ ] Copy state schemas
- [ ] Copy base utilities
- [ ] Copy node implementations
- [ ] Copy graph construction
- [ ] Copy pipeline wrapper
- [ ] Update FastAPI routes
- [ ] Write tests
- [ ] Run tests
- [ ] Performance test

---

## Next: Begin Implementation

Ready to start? Follow these steps:

1. Create the directory structure
2. Copy the state schemas
3. Implement the nodes
4. Build the graph
5. Test each component
6. Integrate with FastAPI
7. Run full pipeline tests


