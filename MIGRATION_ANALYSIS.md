# FinX AI Service: Haystack to LangGraph Migration Analysis

## Executive Summary

This document provides a comprehensive analysis of migrating the finx-ai-service project from the Haystack framework to LangGraph. The project currently uses Haystack 2.7.0 with Hamilton for pipeline orchestration and needs to transition to LangGraph for improved workflow management and state handling.

---

## Phase 1: Analysis Results

### 1.1 Current Architecture Overview

**Project Structure:**
```
finx-ai-service/
├── src/
│   ├── core/
│   │   ├── pipeline.py          # BasicPipeline base class (uses Hamilton AsyncDriver)
│   │   ├── provider.py          # Abstract providers (LLM, Embedder, DocumentStore)
│   │   ├── engine.py            # SQL execution engine
│   │   └── migration_agent.py    # AI-powered migration orchestrator
│   ├── pipelines/
│   │   ├── indexing/
│   │   │   └── db_schema.py      # DB schema indexing pipeline
│   │   ├── generation/
│   │   │   └── question_recommendation.py  # Question generation pipeline
│   │   └── retrieval/            # (Placeholder for retrieval pipelines)
│   ├── providers/                # (Empty - providers defined elsewhere)
│   └── web/                      # FastAPI web layer
├── config.example.yaml           # Pipeline configuration
└── requirements.txt              # Dependencies
```

### 1.2 Haystack Components Currently Used

**Direct Haystack Imports:**
- `haystack.Document` - Document data structure
- `haystack.component` - Component decorator
- `haystack.components.builders.PromptBuilder` - Prompt template builder
- `haystack.components.writers.DocumentWriter` - Document persistence
- `haystack.document_stores.types.DocumentStore` - Abstract document store
- `haystack.document_stores.types.DuplicatePolicy` - Duplicate handling policy

**Custom Haystack-based Components:**
- `AsyncDocumentWriter` - Custom async wrapper for DocumentWriter
- `DocumentCleaner` - Custom component for cleaning documents
- `DDLChunker` - Custom component for chunking DDL commands
- `MDLValidator` - Custom component for validating MDL schemas

**Haystack Integration Points:**
- Document store providers (Qdrant integration)
- Embedder providers (Google GenAI embeddings)
- LLM providers (Google Gemini models)

### 1.3 Pipeline Orchestration: Hamilton Framework

**Current Approach:**
- Uses `hamilton.async_driver.AsyncDriver` for pipeline execution
- Pipelines defined as module-level functions with dependencies
- Function modifiers: `@extract_fields`, `@observe` (Langfuse)
- Result builder: `base.DictResult()`

**Pipeline Functions:**
1. **DB Schema Indexing Pipeline:**
   - `validate_mdl()` → `chunk()` → `embedding()` → `clean()` → `write()`
   
2. **Question Recommendation Pipeline:**
   - `prompt()` → `generate()` → `normalized()`

### 1.4 Core Functionality Patterns

**Pattern 1: Indexing Pipelines**
- Input: Raw data (MDL strings, documents)
- Processing: Validation → Chunking → Embedding → Cleaning → Writing
- Output: Indexed documents in vector store

**Pattern 2: Generation Pipelines**
- Input: Context documents, user parameters
- Processing: Prompt building → LLM generation → Response normalization
- Output: Generated content (questions, SQL, etc.)

**Pattern 3: Retrieval Pipelines** (Placeholder)
- Input: Query text
- Processing: Embedding → Vector search
- Output: Retrieved documents

### 1.5 State Management

**Current State Handling:**
- Implicit state through function parameters
- Hamilton manages dependency injection
- No explicit state graph
- State passed as dictionaries between functions

**Data Structures:**
- `PipelineComponent` - Dataclass for component configuration
- `Document` - Haystack document with metadata
- Custom Pydantic models for validation

### 1.6 Key Dependencies

**Framework Dependencies:**
- `haystack-ai==2.7.0` - Core framework
- `farm-haystack` - Legacy Haystack
- `google-ai-haystack` - Google integration
- `sf-hamilton==1.69.0` - Pipeline orchestration
- `langfuse==2.43.3` - Observability

**Supporting Libraries:**
- `langchain==0.3.27` - LLM utilities
- `pydantic==2.11.7` - Data validation
- `fastapi==0.116.1` - Web framework
- `sqlalchemy==2.0.32` - ORM

---

## Phase 2: Migration Planning

### 2.1 Haystack → LangGraph Component Mapping

| Haystack Component | LangGraph Equivalent | Migration Strategy |
|-------------------|---------------------|-------------------|
| `Document` | `dict` or custom `DocumentNode` | Keep as-is, wrap if needed |
| `@component` decorator | `@node` or function | Convert to node functions |
| `PromptBuilder` | `PromptTemplate` + node | Create prompt node |
| `DocumentWriter` | Custom write node | Create write node |
| `DocumentStore` | State field | Store in graph state |
| `AsyncDriver` | `StateGraph` | Replace orchestration |
| Function dependencies | State graph edges | Define explicit edges |

### 2.2 LangGraph Architecture Design

**State Schema:**
```python
class PipelineState(TypedDict):
    # Input
    mdl_str: str
    documents: List[dict]
    
    # Processing
    validated_mdl: dict
    chunks: List[dict]
    embeddings: List[List[float]]
    
    # Output
    indexed_documents: List[dict]
    errors: List[str]
```

**Graph Structure:**
- Nodes: Pure functions that process state
- Edges: Conditional routing based on state
- Subgraphs: Modular pipeline components
- Checkpointing: Built-in state persistence

### 2.3 Migration Strategy

**Phase 1: Core Infrastructure**
1. Create LangGraph state schemas
2. Implement base node functions
3. Build state graph structure
4. Add error handling and logging

**Phase 2: Pipeline Migration**
1. Migrate DB Schema indexing pipeline
2. Migrate Question Recommendation pipeline
3. Migrate retrieval pipelines
4. Update provider interfaces

**Phase 3: Integration & Testing**
1. Update FastAPI endpoints
2. Migrate tests
3. Performance validation
4. Deprecate Haystack code

### 2.4 Identified Challenges & Solutions

| Challenge | Impact | Solution |
|-----------|--------|----------|
| Hamilton → LangGraph transition | High | Gradual migration with adapter layer |
| Document structure changes | Medium | Create wrapper classes |
| Async handling differences | Medium | Use LangGraph's async support |
| Provider abstraction | Low | Keep provider interfaces unchanged |
| Observability (Langfuse) | Low | Integrate with LangGraph hooks |
| State management complexity | Medium | Use TypedDict for clarity |

### 2.5 Breaking Changes & Deprecations

**Breaking Changes:**
- Pipeline execution API changes
- State structure modifications
- Component initialization patterns

**Deprecations:**
- Hamilton AsyncDriver usage
- Haystack component decorators
- Function-based pipeline definitions

---

## Phase 3: Implementation Roadmap

### 3.1 Recommended Implementation Order

1. **Week 1: Foundation**
   - Create LangGraph state schemas
   - Implement base node utilities
   - Set up graph infrastructure

2. **Week 2: Core Pipelines**
   - Migrate DB Schema indexing
   - Migrate Question Recommendation
   - Create adapter layer for providers

3. **Week 3: Integration**
   - Update FastAPI endpoints
   - Migrate tests
   - Performance optimization

4. **Week 4: Cleanup**
   - Remove Haystack dependencies
   - Documentation updates
   - Final testing

### 3.2 Success Criteria

- ✅ All pipelines functional with LangGraph
- ✅ No performance degradation
- ✅ All tests passing
- ✅ Observability maintained
- ✅ Backward compatibility (if needed)

---

## Next Steps

1. **Review this analysis** with the team
2. **Approve migration strategy** and timeline
3. **Begin Phase 3 implementation** with core infrastructure
4. **Create detailed implementation guide** for each pipeline
5. **Set up testing framework** for LangGraph pipelines

---

## Appendix: Key Files to Migrate

- `src/core/pipeline.py` - Replace with LangGraph graphs
- `src/pipelines/indexing/db_schema.py` - Convert to LangGraph nodes
- `src/pipelines/generation/question_recommendation.py` - Convert to LangGraph nodes
- `src/core/provider.py` - Keep interface, update implementations
- `src/core/engine.py` - Keep as-is, integrate with nodes
- `src/core/migration_agent.py` - Refactor for LangGraph


