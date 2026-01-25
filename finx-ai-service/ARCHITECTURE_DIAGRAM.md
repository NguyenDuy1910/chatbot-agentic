# Workflow Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          WORKFLOW STATE MANAGEMENT                          │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ BaseState (src/core/base_state.py)                                          │
│ ┌──────────────────────────────────────────────────────────────────────────┐ │
│ │ • errors: List[str]                                                      │ │
│ │ • warnings: List[str]                                                    │ │
│ │ • status: str                                                            │ │
│ │ • current_step: str                                                      │ │
│ │ • metadata: Dict                                                         │ │
│ │ • context: Dict                                                          │ │
│ └──────────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────────┘
                                       ▲
                                       │ extends
                                       │
┌──────────────────────────────────────────────────────────────────────────────┐
│ WorkflowState (src/core/workflow_state.py)                                  │
│ ┌──────────────────────────────────────────────────────────────────────────┐ │
│ │ INPUT & QUERY                                                            │ │
│ │ • query, project_id, session_id, user_id                                │ │
│ │                                                                          │ │
│ │ LLM INTERACTION                                                          │ │
│ │ • llm_executions: List[LLMExecutionInfo]                                │ │
│ │ • llm_response, llm_reasoning                                           │ │
│ │                                                                          │ │
│ │ TOOL EXECUTION                                                           │ │
│ │ • tool_executions: List[ToolExecutionInfo]                              │ │
│ │ • tool_results: Dict                                                    │ │
│ │                                                                          │ │
│ │ VALIDATION & QUALITY                                                     │ │
│ │ • validation_info: ValidationInfo                                       │ │
│ │ • quality_score: float                                                  │ │
│ │                                                                          │ │
│ │ RETRY & CORRECTION                                                       │ │
│ │ • retry_count, max_retries                                              │ │
│ │ • correction_history: List                                              │ │
│ │                                                                          │ │
│ │ OUTPUT & PERFORMANCE                                                     │ │
│ │ • response, formatted_output                                            │ │
│ │ • step_timings, total_llm_tokens                                        │ │
│ └──────────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────────┘
                    │
                    ├─────────────────┬─────────────────┬──────────────────┐
                    ▼                 ▼                 ▼                  ▼
        ┌───────────────────┐ ┌──────────────┐ ┌──────────────┐ ┌────────────┐
        │ SQLWorkflowState  │ │IntentClassif-│ │ Retrieval-   │ │Assistance- │
        │                   │ │icationState  │ │WorkflowState │ │WorkflowState│
        │ + sql fields      │ │ + intent     │ │ + documents  │ │ + docs     │
        │ + validation      │ │   fields     │ │ + embeddings │ │ + answer   │
        │ + execution       │ │ + confidence │ │ + filters    │ │   fields   │
        └───────────────────┘ └──────────────┘ └──────────────┘ └────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│                            REUSABLE BASE NODES                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ BaseNode (src/core/base_nodes.py)                                           │
│ ┌──────────────────────────────────────────────────────────────────────────┐ │
│ │ abstract execute(state) -> state                                         │ │
│ │ + Automatic timing tracking                                              │ │
│ │ + Automatic error handling                                               │ │
│ │ + Logging integration                                                    │ │
│ └──────────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────────┘
                                       ▲
                                       │ extends
        ┌──────────────────────────────┼──────────────────────────────┐
        │                              │                              │
        ▼                              ▼                              ▼
┌───────────────┐            ┌────────────────┐            ┌──────────────┐
│   LLMNode     │            │   ToolNode     │            │ValidationNode│
│               │            │                │            │              │
│ • Render      │            │ • Execute tool │            │ • Validate   │
│   prompts     │            │ • Build input  │            │   data       │
│ • Call LLM    │            │ • Track exec   │            │ • Return     │
│ • Parse       │            │ • Handle error │            │   errors     │
│   response    │            │                │            │              │
│ • Track exec  │            │                │            │              │
└───────────────┘            └────────────────┘            └──────────────┘
        │                              │                              │
        │                              │                              │
        ▼                              ▼                              ▼
┌───────────────┐            ┌────────────────┐            ┌──────────────┐
│ JSONParseNode │            │ConditionalNode │            │TransformNode │
│               │            │                │            │              │
│ • Parse JSON  │            │ • Evaluate     │            │ • Transform  │
│ • Validate    │            │   condition    │            │   data       │
│   fields      │            │ • Route to     │            │ • Map input  │
│               │            │   next step    │            │   to output  │
└───────────────┘            └────────────────┘            └──────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│                          NODE DECORATORS & UTILITIES                        │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ Decorators (src/core/node_utils.py)                                         │
│                                                                              │
│  @node                    @llm_node                 @validation_node         │
│  ┌──────────────┐        ┌──────────────┐         ┌──────────────┐         │
│  │ • Set step   │        │ • Get gen    │         │ • Validate   │         │
│  │ • Track time │        │ • Render     │         │ • Store      │         │
│  │ • Handle err │        │   prompts    │         │   results    │         │
│  │ • Log        │        │ • Call LLM   │         │ • Track info │         │
│  └──────────────┘        │ • Track exec │         └──────────────┘         │
│                          └──────────────┘                                   │
│                                                                              │
│  @tool_node                                                                  │
│  ┌──────────────┐                                                           │
│  │ • Execute    │                                                           │
│  │   tool       │                                                           │
│  │ • Track exec │                                                           │
│  │ • Handle err │                                                           │
│  └──────────────┘                                                           │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ Routing Utilities                                                            │
│                                                                              │
│  route_by_validation()    route_by_field()      create_conditional_router() │
│  ┌──────────────┐        ┌──────────────┐      ┌──────────────┐            │
│  │ • Check      │        │ • Read field │      │ • Custom     │            │
│  │   is_valid   │        │ • Map value  │      │   conditions │            │
│  │ • Check      │        │   to route   │      │ • Multiple   │            │
│  │   retries    │        │              │      │   routes     │            │
│  │ • Route      │        │              │      │              │            │
│  └──────────────┘        └──────────────┘      └──────────────┘            │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ State Utilities                                                              │
│                                                                              │
│  get_from_state()    set_in_state()    merge_states()    extract_field()    │
│  should_retry()      increment_retry()  reset_retry()    add_to_history()   │
└──────────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│                              WORKFLOW FLOW                                  │
└─────────────────────────────────────────────────────────────────────────────┘

                        ┌─────────────────────┐
                        │ Create Initial      │
                        │ State               │
                        │ (create_workflow_   │
                        │  state)             │
                        └──────────┬──────────┘
                                   │
                                   ▼
                        ┌─────────────────────┐
                        │ Add Context         │
                        │ (generator,         │
                        │  retriever, etc.)   │
                        └──────────┬──────────┘
                                   │
                                   ▼
                        ┌─────────────────────┐
                        │ Node 1: LLMNode     │
                        │ • Render prompts    │
                        │ • Call LLM          │
                        │ • Store response    │
                        └──────────┬──────────┘
                                   │
                                   ▼
                        ┌─────────────────────┐
                        │ Node 2: Transform   │
                        │ • Clean data        │
                        │ • Format output     │
                        └──────────┬──────────┘
                                   │
                                   ▼
                        ┌─────────────────────┐
                        │ Node 3: Validation  │
                        │ • Validate data     │
                        │ • Check rules       │
                        └──────────┬──────────┘
                                   │
                                   ▼
                        ┌─────────────────────┐
                        │ Conditional Router  │
                        │ • route_by_         │
                        │   validation()      │
                        └──────────┬──────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    ▼              ▼              ▼
            ┌────────────┐  ┌────────────┐  ┌────────────┐
            │   Valid    │  │  Invalid   │  │Max Retries │
            │   Route    │  │  Retry     │  │ Give Up    │
            │            │  │  Correct   │  │            │
            └────────────┘  └────────────┘  └────────────┘
                    │              │              │
                    │              │ (loop back)  │
                    │              ▼              │
                    │       ┌────────────┐        │
                    │       │ Correction │        │
                    │       │ Node       │        │
                    │       └────────────┘        │
                    │              │              │
                    │              │              │
                    └──────────────┴──────────────┘
                                   │
                                   ▼
                        ┌─────────────────────┐
                        │ Format Response     │
                        │ • Build response    │
                        │ • Set status        │
                        └──────────┬──────────┘
                                   │
                                   ▼
                        ┌─────────────────────┐
                        │ Final State         │
                        │ • response          │
                        │ • status            │
                        │ • step_timings      │
                        │ • errors/warnings   │
                        └─────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│                          3 APPROACHES TO CREATE NODES                       │
└─────────────────────────────────────────────────────────────────────────────┘

  1. BASE CLASSES          2. DECORATORS           3. CUSTOM FUNCTIONS
  (Reusable)              (Quick)                 (Flexible)

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ node = LLMNode( │    │ @llm_node(...)  │    │ @node(...)      │
│   name="gen",   │    │ async def gen(  │    │ async def my(   │
│   prompt="...", │    │   state):       │    │   state):       │
│   output="sql"  │    │   return {...}  │    │   # logic       │
│ )               │    │                 │    │   return state  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                      │                      │
        ├──────────────────────┼──────────────────────┤
        │         All produce workflow nodes          │
        └────────────────────┬─────────────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Add to Graph    │
                    │ graph.add_node( │
                    │   "name", node) │
                    └─────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│                                BENEFITS                                     │
└─────────────────────────────────────────────────────────────────────────────┘

  Consistency          Reusability         Maintainability      DX
  ┌─────────┐         ┌─────────┐         ┌─────────┐        ┌─────────┐
  │ Same    │         │ Reuse   │         │ Less    │        │ Quick   │
  │ pattern │         │ across  │         │ code    │        │ proto-  │
  │ for all │         │ work-   │         │ Clear   │        │ typing  │
  │ nodes   │         │ flows   │         │ separa- │        │ Easy    │
  │         │         │         │         │ tion    │        │ to use  │
  └─────────┘         └─────────┘         └─────────┘        └─────────┘


  Features                               Tracking
  ┌─────────────────────────┐           ┌─────────────────────────┐
  │ • Auto timing           │           │ • LLM executions        │
  │ • Auto error handling   │           │ • Tool executions       │
  │ • Validation + retry    │           │ • Step timings          │
  │ • Conditional routing   │           │ • Token usage           │
  │ • State management      │           │ • Errors & warnings     │
  │ • Langfuse integration  │           │ • History tracking      │
  └─────────────────────────┘           └─────────────────────────┘
