# FinX AI Service: Haystack to LangGraph Migration Summary

## Quick Overview

**Current State:** Haystack 2.7.0 + Hamilton orchestration  
**Target State:** LangGraph with explicit state graphs  
**Complexity:** Medium  
**Estimated Timeline:** 4 weeks  
**Risk Level:** Low-Medium

---

## Key Findings

### Architecture Analysis

The finx-ai-service uses a **layered architecture**:

1. **Framework Layer:** Haystack + Hamilton
   - Haystack for components (Document, PromptBuilder, DocumentWriter)
   - Hamilton for pipeline orchestration and dependency injection
   - Langfuse for observability

2. **Pipeline Layer:** Two main pipeline types
   - **Indexing:** DB Schema → Validation → Chunking → Embedding → Storage
   - **Generation:** Context → Prompt Building → LLM Generation → Normalization

3. **Provider Layer:** Abstract interfaces
   - LLMProvider (Google Gemini)
   - EmbedderProvider (Google text-embedding-004)
   - DocumentStoreProvider (Qdrant)
   - Engine (SQL execution)

4. **Web Layer:** FastAPI endpoints
   - RESTful API for pipeline execution
   - Database models for persistence

### Haystack Components Used

**Direct Dependencies:**
- `haystack.Document` - Data structure
- `haystack.component` - Decorator
- `haystack.components.builders.PromptBuilder` - Prompt templating
- `haystack.components.writers.DocumentWriter` - Document persistence
- `haystack.document_stores.types` - Abstract interfaces

**Custom Components:**
- `AsyncDocumentWriter` - Async wrapper
- `DocumentCleaner` - Document cleanup
- `DDLChunker` - DDL chunking logic
- `MDLValidator` - Schema validation

### Current Orchestration Pattern

**Hamilton-based Approach:**
```
Function Dependencies → Hamilton AsyncDriver → Execution
```

**Issues:**
- Implicit state management
- Difficult to trace data flow
- Limited error handling
- No built-in state persistence

---

## Migration Strategy

### Phase 1: Foundation (Week 1)
**Deliverables:**
- LangGraph state schemas
- Base node utilities
- Graph infrastructure
- Testing framework

**Key Files:**
- `src/langgraph/state/schemas.py` (NEW)
- `src/langgraph/nodes/base.py` (NEW)
- `src/langgraph/graphs/base.py` (NEW)

### Phase 2: Core Pipelines (Week 2)
**Deliverables:**
- DB Schema indexing graph
- Question recommendation graph
- Provider adapters
- Node implementations

**Key Files:**
- `src/langgraph/graphs/db_schema_graph.py` (NEW)
- `src/langgraph/graphs/question_recommendation_graph.py` (NEW)
- `src/langgraph/nodes/indexing_nodes.py` (NEW)
- `src/langgraph/nodes/generation_nodes.py` (NEW)

### Phase 3: Integration (Week 3)
**Deliverables:**
- Updated FastAPI endpoints
- Migrated tests
- Performance validation
- Documentation

**Key Files:**
- `src/web/routers/pipelines.py` (UPDATED)
- `tests/test_langgraph_pipelines.py` (NEW)

### Phase 4: Cleanup (Week 4)
**Deliverables:**
- Removed Haystack code
- Updated dependencies
- Final testing
- Production deployment

---

## Component Mapping

| Haystack | LangGraph | Notes |
|----------|-----------|-------|
| `@component` | Node function | Pure async functions |
| `AsyncDriver` | `StateGraph` | Explicit graph structure |
| Function params | State TypedDict | Explicit state schema |
| `Document` | `dict` | Keep structure, wrap if needed |
| `PromptBuilder` | Prompt node | Custom implementation |
| `DocumentWriter` | Write node | Custom implementation |
| Implicit routing | Conditional edges | Explicit routing logic |

---

## Key Advantages of LangGraph

1. **Explicit State Management**
   - Clear state schema with TypedDict
   - Easier debugging and tracing
   - Built-in state persistence

2. **Better Error Handling**
   - Conditional edges for error paths
   - Retry mechanisms
   - Detailed error tracking

3. **Improved Observability**
   - Graph visualization
   - Step-by-step execution tracking
   - Integration with LangSmith

4. **Scalability**
   - Subgraphs for modularity
   - Parallel node execution
   - Checkpointing support

5. **Developer Experience**
   - Clearer data flow
   - Easier testing
   - Better IDE support

---

## Potential Challenges

| Challenge | Severity | Mitigation |
|-----------|----------|-----------|
| Learning curve | Low | Documentation + examples |
| State complexity | Medium | TypedDict validation |
| Provider integration | Low | Adapter pattern |
| Performance | Low | Benchmarking |
| Async handling | Medium | Proper async/await usage |

---

## Success Metrics

- ✅ All pipelines functional
- ✅ No performance degradation (< 5% variance)
- ✅ 100% test coverage
- ✅ Observability maintained/improved
- ✅ Documentation complete
- ✅ Team trained on LangGraph

---

## Recommended Next Steps

1. **Review & Approve**
   - Team review of analysis
   - Stakeholder approval
   - Timeline confirmation

2. **Setup Infrastructure**
   - Create LangGraph directory structure
   - Set up testing framework
   - Configure development environment

3. **Begin Implementation**
   - Start with state schemas
   - Implement base nodes
   - Build first graph (DB Schema)

4. **Iterate & Validate**
   - Test each component
   - Performance benchmarking
   - Integration testing

5. **Deploy & Monitor**
   - Gradual rollout
   - Performance monitoring
   - User feedback collection

---

## Resources

- **LangGraph Documentation:** https://langchain-ai.github.io/langgraph/
- **State Management Guide:** See MIGRATION_PLAN.md
- **Implementation Examples:** See MIGRATION_PLAN.md
- **Testing Strategy:** See MIGRATION_PLAN.md

---

## Questions & Decisions Needed

1. **Timeline:** Is 4 weeks acceptable?
2. **Rollout:** Gradual or big-bang migration?
3. **Backward Compatibility:** Maintain dual-running pipelines?
4. **Testing:** What's the acceptable test coverage?
5. **Monitoring:** What metrics should we track?


