# LangGraph Pipeline Architecture Diagram

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        LANGGRAPH PIPELINE FRAMEWORK                          │
│                              (New Implementation)                            │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                           USER LAYER                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  from src.core.pipeline import LangGraphPipeline, PipelineComponent         │
│                                                                              │
│  components = PipelineComponent(                                            │
│      llm_provider=OpenAILLMProvider(),                                      │
│      embedder_provider=OpenAIEmbedderProvider(),                            │
│  )                                                                           │
│                                                                              │
│  pipeline = MyPipeline(components)                                          │
│  result = await pipeline.run(input="test")                                  │
│                                                                              │
└───────────────────────────────┬─────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      PIPELINE LAYER (Your Code)                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  class MyPipeline(LangGraphPipeline[MyState]):                              │
│                                                                              │
│      def create_graph(self) -> StateGraph:                                  │
│          graph = StateGraph(MyState)                                        │
│          graph.add_node("node1", node1_func)                                │
│          graph.add_node("node2", node2_func)                                │
│          graph.add_edge("node1", "node2")                                   │
│          return graph.compile()                                             │
│                                                                              │
│      async def run(self, **kwargs):                                         │
│          state = self.create_initial_state(...)  ◄── Automatic provider    │
│          result = await self.graph.ainvoke(state)   injection              │
│          return self.finalize_result(result)     ◄── Automatic timing       │
│                                                                              │
└───────────────────────────────┬─────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    FRAMEWORK LAYER (Base Classes)                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  LangGraphPipeline[StateT]                 PipelineComponent                │
│  ├─ create_graph()                         ├─ llm_provider                  │
│  ├─ run()                                   ├─ embedder_provider             │
│  ├─ create_initial_state()                 ├─ document_store_provider       │
│  └─ finalize_result()                      ├─ engine                        │
│                                             ├─ inject_into_state()           │
│                                             └─ validate()                    │
│                                                                              │
└───────────────────────────────┬─────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      LANGGRAPH LAYER (Execution)                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                          StateGraph[MyState]                                │
│                                  │                                           │
│                                  ▼                                           │
│                      ┌────────────────────────┐                             │
│                      │   START (Entry Point)  │                             │
│                      └──────────┬─────────────┘                             │
│                                 │                                            │
│                                 ▼                                            │
│                      ┌────────────────────────┐                             │
│                      │   Node 1 (Function)    │                             │
│                      │   @node_error_handler  │                             │
│                      └──────────┬─────────────┘                             │
│                                 │                                            │
│                          ┌──────┴──────┐                                    │
│                          │ Conditional │                                    │
│                          │   Router    │                                    │
│                          └──┬──────┬───┘                                    │
│                             │      │                                        │
│                    Success  │      │  Error                                 │
│                             ▼      ▼                                        │
│                 ┌──────────────┐ ┌──────────────┐                          │
│                 │   Node 2     │ │ Error        │                          │
│                 │              │ │ Handler      │                          │
│                 └──────┬───────┘ └──────┬───────┘                          │
│                        │                │                                   │
│                        └────────┬───────┘                                   │
│                                 │                                            │
│                                 ▼                                            │
│                      ┌────────────────────────┐                             │
│                      │   END (Exit Point)     │                             │
│                      └────────────────────────┘                             │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│                         STATE FLOW DIAGRAM                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Initial State                    Node Updates                Final State   │
│  ┌──────────────┐                ┌──────────────┐           ┌────────────┐│
│  │ input: "..."  │───────────────►│ Partial      │──────────►│ Complete   ││
│  │ errors: []    │   Node 1       │ Update       │  Node 2   │ Result     ││
│  │ status: "..."  │                │ ┌──────────┐ │           │            ││
│  │ llm_provider │                │ │result: X │ │           │ status:    ││
│  │ metadata: {} │                │ │status: Y │ │           │ "complete" ││
│  └──────────────┘                │ └──────────┘ │           │ errors: [] ││
│                                   └──────────────┘           └────────────┘│
│                                                                              │
│                     State is IMMUTABLE - nodes return updates               │
│                     Framework MERGES updates with current state             │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│                      PROVIDER INJECTION FLOW                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  PipelineComponent                create_initial_state()        Node Access│
│  ┌──────────────┐                ┌──────────────┐           ┌────────────┐│
│  │ llm_provider ├───────────────►│ Inject into  ├──────────►│ Get from   ││
│  │              │  Automatic     │ state dict   │  Pass     │ state      ││
│  │ embedder     │                │              │  state    │            ││
│  │              │                │ state[       │  to node  │ llm =      ││
│  │ doc_store    │                │  "llm_..."]  │           │ state.get( ││
│  │              │                │              │           │  "llm...")  ││
│  │ engine       │                │              │           │            ││
│  └──────────────┘                └──────────────┘           └────────────┘│
│                                                                              │
│                     No manual passing - automatic injection                 │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│                       ERROR HANDLING LAYERS                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Layer 1: Node Decorator                                                    │
│  ┌────────────────────────────────────────────┐                            │
│  │ @node_error_handler                        │                            │
│  │ async def my_node(state):                  │                            │
│  │     # Exceptions auto-caught               │                            │
│  │     risky_operation()                      │                            │
│  └────────────────────────────────────────────┘                            │
│                      │                                                       │
│                      │ Catches exceptions                                   │
│                      ▼                                                       │
│  Layer 2: Conditional Routing                                               │
│  ┌────────────────────────────────────────────┐                            │
│  │ if state["status"] == "failed":            │                            │
│  │     return "error_handler"                 │                            │
│  └────────────────────────────────────────────┘                            │
│                      │                                                       │
│                      │ Routes to error node                                 │
│                      ▼                                                       │
│  Layer 3: Error Handler Node                                                │
│  ┌────────────────────────────────────────────┐                            │
│  │ async def error_handler_node(state):       │                            │
│  │     log_errors(state["errors"])            │                            │
│  │     return {"status": "failed"}            │                            │
│  └────────────────────────────────────────────┘                            │
│                      │                                                       │
│                      │ Logs and finalizes                                   │
│                      ▼                                                       │
│  Layer 4: Pipeline Try-Catch                                                │
│  ┌────────────────────────────────────────────┐                            │
│  │ try:                                        │                            │
│  │     result = await graph.ainvoke(state)    │                            │
│  │ except Exception as e:                     │                            │
│  │     return {"status": "failed", ...}       │                            │
│  └────────────────────────────────────────────┘                            │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│                      EXAMPLE: SQL GENERATION FLOW                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  User Question: "Top 10 customers by revenue"                               │
│       │                                                                      │
│       ▼                                                                      │
│  ┌──────────────────┐                                                       │
│  │ Analyze Question │  ◄── Uses question_analysis logic                     │
│  └────────┬─────────┘                                                       │
│           │                                                                  │
│           ▼                                                                  │
│  ┌──────────────────┐                                                       │
│  │ Retrieve Schema  │  ◄── Uses embedder + document_store                   │
│  └────────┬─────────┘                                                       │
│           │                                                                  │
│           ▼                                                                  │
│  ┌──────────────────┐                                                       │
│  │ Generate SQL     │  ◄── Uses llm_provider                                │
│  └────────┬─────────┘                                                       │
│           │                                                                  │
│           ▼                                                                  │
│  ┌──────────────────┐                                                       │
│  │ Validate SQL     │  ◄── Syntax checking                                  │
│  └────────┬─────────┘                                                       │
│           │                                                                  │
│      ┌────┴────┐                                                            │
│      │         │                                                            │
│   Valid?    Invalid                                                         │
│      │         │                                                            │
│      │         ▼                                                            │
│      │    ┌──────────┐                                                      │
│      │    │ Refine   │──┐                                                   │
│      │    │ SQL      │  │                                                   │
│      │    └──────────┘  │                                                   │
│      │         ▲        │                                                   │
│      │         └────────┘ Loop back (max 3 times)                           │
│      │                                                                       │
│      ▼                                                                       │
│  ┌──────────────────┐                                                       │
│  │ Return SQL       │                                                       │
│  └──────────────────┘                                                       │
│                                                                              │
│  State throughout:                                                          │
│  {                                                                           │
│    "question": "Top 10 customers...",                                       │
│    "question_analysis": {...},                                              │
│    "relevant_schema": [...],                                                │
│    "generated_sql": "SELECT ...",                                           │
│    "sql_valid": true,                                                       │
│    "final_sql": "SELECT ...",                                               │
│    "status": "completed",                                                   │
│    "llm_provider": <provider>,  ◄── Auto-injected                           │
│    "embedder_provider": <provider>,  ◄── Auto-injected                      │
│    "metadata": {...}  ◄── Auto-added                                        │
│  }                                                                           │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│                      FILE ORGANIZATION                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  src/core/                         ◄── Core abstractions                    │
│  ├── pipeline.py                   ◄── NEW: LangGraphPipeline base          │
│  ├── example_langgraph_pipeline.py ◄── NEW: Example implementation          │
│  ├── provider.py                   ◄── Provider definitions                 │
│  └── engine.py                     ◄── SQL engine                           │
│                                                                              │
│  src/langgraph/                    ◄── LangGraph implementations            │
│  ├── state/                                                                 │
│  │   └── schemas.py               ◄── TypedDict state schemas               │
│  ├── nodes/                                                                 │
│  │   ├── base.py                  ◄── Decorators and utilities              │
│  │   ├── indexing_nodes.py        ◄── DB schema indexing nodes             │
│  │   └── generation_nodes.py      ◄── Question generation nodes            │
│  ├── graphs/                                                                │
│  │   ├── db_schema_graph.py       ◄── DB schema graph definition           │
│  │   └── question_recommendation_graph.py                                  │
│  └── pipelines/                                                             │
│      ├── db_schema_pipeline.py    ◄── Can use new base class               │
│      └── question_recommendation_pipeline.py                                │
│                                                                              │
│  docs/                             ◄── Documentation                        │
│  ├── LANGGRAPH_PIPELINE_GUIDE.md  ◄── NEW: Complete guide                  │
│  ├── LANGGRAPH_ARCHITECTURE.md    ◄── Architecture overview                │
│  └── LANGGRAPH_IMPLEMENTATION_GUIDE.md                                      │
│                                                                              │
│  Root:                                                                       │
│  ├── LANGGRAPH_PIPELINE_IMPLEMENTATION_SUMMARY.md  ◄── NEW: Summary        │
│  └── LANGGRAPH_QUICK_REFERENCE.md                  ◄── NEW: Quick ref      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│                      KEY ADVANTAGES                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Before (Hamilton)              │  After (LangGraph)                        │
│  ──────────────────────────────┼───────────────────────────────────────    │
│  ❌ Implicit state              │  ✅ Explicit state management              │
│  ❌ DAG only                    │  ✅ Conditional routing                    │
│  ❌ No human-in-the-loop        │  ✅ Built-in interrupts                   │
│  ❌ Limited error handling      │  ✅ Multi-layer error handling            │
│  ❌ Hard to debug               │  ✅ Full execution traces                 │
│  ❌ No checkpointing            │  ✅ State persistence support             │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

**Created**: 2025-01-26  
**Version**: 2.0.0  
**For**: LangGraph Pipeline Framework Implementation
