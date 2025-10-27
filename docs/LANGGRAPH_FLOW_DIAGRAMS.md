# LangGraph Flow Diagrams

## 📊 Visualizations cho LangGraph Architecture

Tài liệu này chứa các biểu đồ Mermaid để visualize LangGraph flows.

---

## 🎯 1. Router Graph - Main Orchestrator

```mermaid
graph TD
    Start([User Input]) --> IntentClassifier[Intent Classifier]
    
    IntentClassifier --> CheckIntent{Classify Intent}
    
    CheckIntent -->|chat| ChatSubgraph[Chat Subgraph]
    CheckIntent -->|sql| SQLSubgraph[SQL Generation Subgraph]
    CheckIntent -->|schema| SchemaSubgraph[Schema Analysis Subgraph]
    CheckIntent -->|migration| MigrationSubgraph[Migration Subgraph]
    CheckIntent -->|connection| ConnectionHandler[Connection Handler]
    CheckIntent -->|unknown| ErrorHandler[Error Handler]
    
    ChatSubgraph --> ResponseFormatter[Response Formatter]
    SQLSubgraph --> ResponseFormatter
    SchemaSubgraph --> ResponseFormatter
    MigrationSubgraph --> ResponseFormatter
    ConnectionHandler --> ResponseFormatter
    ErrorHandler --> ResponseFormatter
    
    ResponseFormatter --> End([Return Response])
    
    style Start fill:#4CAF50
    style End fill:#2196F3
    style IntentClassifier fill:#FF9800
    style CheckIntent fill:#FFC107
    style ResponseFormatter fill:#9C27B0
```

---

## 💬 2. Chat Subgraph

```mermaid
graph TD
    Start([Chat Request]) --> RetrieveContext[Retrieve Conversation Context]
    
    RetrieveContext --> VectorSearch[Vector Search]
    VectorSearch --> LoadPrompts[Load Relevant Prompts]
    
    LoadPrompts --> GenerateResponse[Generate LLM Response]
    
    GenerateResponse --> CheckQuality{Response Quality Check}
    
    CheckQuality -->|Good| SaveConversation[Save to Database]
    CheckQuality -->|Needs Refinement| RefineResponse[Refine Response]
    
    RefineResponse --> GenerateResponse
    
    SaveConversation --> UpdateContext[Update Conversation Context]
    UpdateContext --> End([Return Response])
    
    style Start fill:#4CAF50
    style End fill:#2196F3
    style GenerateResponse fill:#FF5722
    style CheckQuality fill:#FFC107
```

---

## 🔄 3. Migration Subgraph (Detailed)

```mermaid
graph TD
    Start([Migration Request]) --> ValidateConnections[Validate Connections]
    
    ValidateConnections --> CheckValid{Connections Valid?}
    CheckValid -->|No| ErrorEnd([Return Error])
    CheckValid -->|Yes| ParallelAnalysis{Parallel Analysis}
    
    ParallelAnalysis --> AnalyzeSource[Analyze Source Schema]
    ParallelAnalysis --> AnalyzeTarget[Analyze Target Schema]
    
    AnalyzeSource --> WaitForBoth{Wait for Both}
    AnalyzeTarget --> WaitForBoth
    
    WaitForBoth --> CalculateCompatibility[Calculate Compatibility Score]
    
    CalculateCompatibility --> CheckCompatibility{Compatibility >= 0.9?}
    
    CheckCompatibility -->|Yes| GeneratePlan[Generate Migration Plan]
    CheckCompatibility -->|No| NeedsApproval[Mark Needs Approval]
    
    NeedsApproval --> GeneratePlan
    
    GeneratePlan --> CheckApprovalNeeded{Needs Human Approval?}
    
    CheckApprovalNeeded -->|No| ExecuteMigration[Execute Migration]
    CheckApprovalNeeded -->|Yes| HumanApproval[⏸️ Human Approval]
    
    HumanApproval --> CheckApproved{Approved?}
    
    CheckApproved -->|Yes| ExecuteMigration
    CheckApproved -->|No| RevisePlan[Revise Plan]
    
    RevisePlan --> GeneratePlan
    
    ExecuteMigration --> ValidateResults[Validate Results]
    
    ValidateResults --> CheckValidation{Validation Passed?}
    
    CheckValidation -->|Yes| SuccessEnd([Migration Completed])
    CheckValidation -->|No| Rollback[Rollback Migration]
    
    Rollback --> RollbackEnd([Migration Rolled Back])
    
    style Start fill:#4CAF50
    style SuccessEnd fill:#2196F3
    style RollbackEnd fill:#F44336
    style ErrorEnd fill:#F44336
    style HumanApproval fill:#FFC107
    style ExecuteMigration fill:#FF5722
    style CheckApprovalNeeded fill:#9C27B0
    style CheckValidation fill:#9C27B0
```

---

## 🔍 4. Schema Analysis Subgraph

```mermaid
graph TD
    Start([Schema Analysis Request]) --> ConnectDB[Connect to Database]
    
    ConnectDB --> CheckConnection{Connection OK?}
    CheckConnection -->|No| ErrorEnd([Return Error])
    CheckConnection -->|Yes| CheckCache{Schema Cached?}
    
    CheckCache -->|Yes| ReturnCached[Return Cached Schema]
    CheckCache -->|No| ParallelExtract{Parallel Extraction}
    
    ParallelExtract --> ExtractTables[Extract Tables]
    ParallelExtract --> ExtractViews[Extract Views]
    ParallelExtract --> ExtractConstraints[Extract Constraints]
    
    ExtractTables --> WaitForAll{Wait for All}
    ExtractViews --> WaitForAll
    ExtractConstraints --> WaitForAll
    
    WaitForAll --> AnalyzeRelationships[Analyze Relationships]
    
    AnalyzeRelationships --> GenerateMDL[Generate MDL]
    GenerateMDL --> GenerateERD[Generate ERD Diagram]
    
    GenerateERD --> CacheResults[Cache Results]
    CacheResults --> ReturnResults[Return Schema]
    
    ReturnCached --> End([Return Response])
    ReturnResults --> End
    
    style Start fill:#4CAF50
    style End fill:#2196F3
    style ErrorEnd fill:#F44336
    style CheckCache fill:#FFC107
    style ParallelExtract fill:#9C27B0
```

---

## 💡 5. SQL Generation Subgraph

```mermaid
graph TD
    Start([SQL Generation Request]) --> ParseQuestion[Parse Natural Language Question]
    
    ParseQuestion --> RetrieveSchema[Retrieve Schema Context]
    RetrieveSchema --> LoadExamples[Load Few-Shot Examples]
    
    LoadExamples --> GenerateSQL[Generate SQL with LLM]
    
    GenerateSQL --> ValidateSQL[Validate SQL Syntax]
    
    ValidateSQL --> CheckValid{SQL Valid?}
    
    CheckValid -->|Yes| CheckExecute{Execute Query?}
    CheckValid -->|No| CheckIterations{Iterations < Max?}
    
    CheckIterations -->|Yes| RefineSQL[Refine SQL]
    CheckIterations -->|No| ReturnError([Return Invalid SQL Error])
    
    RefineSQL --> GenerateSQL
    
    CheckExecute -->|Yes| ExecuteQuery[Execute Query]
    CheckExecute -->|No| ReturnSQL[Return SQL Only]
    
    ExecuteQuery --> CheckResults{Results OK?}
    
    CheckResults -->|Yes| ReturnResults[Return SQL + Results]
    CheckResults -->|Error| HandleError[Handle Error]
    
    HandleError --> ReturnSQLWithError[Return SQL + Error]
    
    ReturnSQL --> End([Return Response])
    ReturnResults --> End
    ReturnSQLWithError --> End
    
    style Start fill:#4CAF50
    style End fill:#2196F3
    style ReturnError fill:#F44336
    style GenerateSQL fill:#FF5722
    style ValidateSQL fill:#9C27B0
    style ExecuteQuery fill:#FF9800
```

---

## 🏗️ 6. Complete System Architecture with LangGraph

```mermaid
graph TB
    subgraph "Frontend Layer"
        UI[React UI]
    end
    
    subgraph "API Layer"
        FastAPI[FastAPI Router]
        WSS[WebSocket Server]
    end
    
    subgraph "LangGraph Layer"
        Router[Router Graph]
        
        subgraph "Subgraphs"
            ChatGraph[Chat Subgraph]
            SQLGraph[SQL Subgraph]
            SchemaGraph[Schema Subgraph]
            MigrationGraph[Migration Subgraph]
        end
        
        Router --> ChatGraph
        Router --> SQLGraph
        Router --> SchemaGraph
        Router --> MigrationGraph
    end
    
    subgraph "Agent Layer"
        SchemaAgent[Schema Analyzer Agent]
        PlannerAgent[Migration Planner Agent]
        TransformAgent[Data Transform Agent]
        ValidationAgent[Validation Agent]
        
        MigrationGraph --> SchemaAgent
        MigrationGraph --> PlannerAgent
        MigrationGraph --> TransformAgent
        MigrationGraph --> ValidationAgent
    end
    
    subgraph "Data Layer"
        PrimaryDB[(Primary Database)]
        VectorDB[(Vector Store)]
        CacheDB[(Redis Cache)]
        CheckpointDB[(Checkpoint DB)]
        
        Router --> CheckpointDB
        ChatGraph --> PrimaryDB
        ChatGraph --> VectorDB
        SchemaGraph --> CacheDB
    end
    
    subgraph "External Services"
        OpenAI[OpenAI API]
        Gemini[Google Gemini]
        SourceDB[(Source Databases)]
        TargetDB[(Target Databases)]
    end
    
    UI <--> FastAPI
    UI <--> WSS
    FastAPI --> Router
    WSS --> Router
    
    ChatGraph --> OpenAI
    ChatGraph --> Gemini
    SQLGraph --> OpenAI
    SchemaAgent --> SourceDB
    SchemaAgent --> TargetDB
    TransformAgent --> SourceDB
    TransformAgent --> TargetDB
    
    style Router fill:#FF9800
    style ChatGraph fill:#4CAF50
    style SQLGraph fill:#2196F3
    style SchemaGraph fill:#9C27B0
    style MigrationGraph fill:#F44336
```

---

## 🔄 7. State Flow Through System

```mermaid
sequenceDiagram
    participant User
    participant FastAPI
    participant Router as Router Graph
    participant Subgraph as Subgraph
    participant Agent as AI Agent
    participant LLM as LLM Provider
    participant DB as Database
    
    User->>FastAPI: POST /api/chat
    FastAPI->>Router: invoke(initial_state)
    
    Router->>Router: classify_intent()
    Note over Router: Intent: "migration"
    
    Router->>Subgraph: Migration Subgraph
    Subgraph->>Agent: SchemaAnalyzerAgent
    Agent->>DB: Query Schema
    DB-->>Agent: Schema Data
    Agent-->>Subgraph: Schema Analysis
    
    Subgraph->>Agent: MigrationPlannerAgent
    Agent->>LLM: Generate Plan
    LLM-->>Agent: Migration Plan
    Agent-->>Subgraph: Plan
    
    Note over Subgraph: needs_approval = True
    Subgraph-->>Router: Interrupt (Approval Needed)
    Router-->>FastAPI: State Checkpoint Saved
    FastAPI-->>User: Approval Required
    
    User->>FastAPI: POST /api/approve
    FastAPI->>Router: invoke(state, approval=True)
    Router->>Subgraph: Resume from Checkpoint
    
    Subgraph->>Agent: MigrationExecutorAgent
    Agent->>DB: Execute Migration
    DB-->>Agent: Results
    Agent-->>Subgraph: Execution Results
    
    Subgraph->>Agent: ValidationAgent
    Agent->>DB: Validate Data
    DB-->>Agent: Validation Results
    Agent-->>Subgraph: Validation Passed
    
    Subgraph-->>Router: Final State
    Router-->>FastAPI: Response
    FastAPI-->>User: Migration Complete
```

---

## 📦 8. State Management Flow

```mermaid
stateDiagram-v2
    [*] --> InitialState: User Request
    
    InitialState --> IntentClassified: classify_intent()
    
    IntentClassified --> ChatState: intent = "chat"
    IntentClassified --> SQLState: intent = "sql"
    IntentClassified --> SchemaState: intent = "schema"
    IntentClassified --> MigrationState: intent = "migration"
    
    state MigrationState {
        [*] --> Validating
        Validating --> Analyzing
        Analyzing --> Planning
        Planning --> AwaitingApproval: needs_approval = True
        Planning --> Executing: needs_approval = False
        AwaitingApproval --> Executing: approved = True
        AwaitingApproval --> Planning: approved = False
        Executing --> Validating
        Validating --> Completed: validation_passed = True
        Validating --> RollingBack: validation_passed = False
        RollingBack --> Failed
        Completed --> [*]
        Failed --> [*]
    }
    
    ChatState --> ResponseFormatted
    SQLState --> ResponseFormatted
    SchemaState --> ResponseFormatted
    MigrationState --> ResponseFormatted
    
    ResponseFormatted --> [*]: Return to User
```

---

## 🔧 9. Error Handling & Retry Flow

```mermaid
graph TD
    Start([Node Execution]) --> TryExecute{Try Execute}
    
    TryExecute -->|Success| LogSuccess[Log Success]
    TryExecute -->|Error| CatchError[Catch Error]
    
    CatchError --> CheckRetryable{Error Retryable?}
    
    CheckRetryable -->|Yes| CheckRetries{Retries < Max?}
    CheckRetryable -->|No| LogError[Log Fatal Error]
    
    CheckRetries -->|Yes| Delay[Exponential Backoff]
    CheckRetries -->|No| LogError
    
    Delay --> TryExecute
    
    LogError --> UpdateState[Update State with Error]
    UpdateState --> CheckFallback{Fallback Available?}
    
    CheckFallback -->|Yes| ExecuteFallback[Execute Fallback]
    CheckFallback -->|No| FailNode[Node Failed]
    
    ExecuteFallback --> LogSuccess
    
    LogSuccess --> NextNode[Continue to Next Node]
    FailNode --> ErrorEnd([Error Handling])
    
    NextNode --> End([Node Complete])
    
    style Start fill:#4CAF50
    style End fill:#2196F3
    style ErrorEnd fill:#F44336
    style LogError fill:#FF9800
    style CheckRetryable fill:#FFC107
```

---

## 📊 10. Checkpoint & Recovery Flow

```mermaid
graph TD
    Start([Graph Execution]) --> SaveCheckpoint{After Each Node}
    
    SaveCheckpoint --> CheckpointDB[(Checkpoint Database)]
    CheckpointDB --> ContinueExec[Continue Execution]
    
    ContinueExec --> CheckInterrupt{Interrupt Point?}
    
    CheckInterrupt -->|No| NextNode[Execute Next Node]
    CheckInterrupt -->|Yes| SaveState[Save State]
    
    SaveState --> WaitForInput[⏸️ Wait for User Input]
    
    WaitForInput --> UserInput[User Provides Input]
    UserInput --> LoadCheckpoint[Load from Checkpoint]
    
    LoadCheckpoint --> RestoreState[Restore State]
    RestoreState --> NextNode
    
    NextNode --> SaveCheckpoint
    
    NextNode --> CheckEnd{End of Graph?}
    CheckEnd -->|No| SaveCheckpoint
    CheckEnd -->|Yes| CleanupCheckpoint[Cleanup Checkpoint]
    
    CleanupCheckpoint --> End([Execution Complete])
    
    style Start fill:#4CAF50
    style End fill:#2196F3
    style WaitForInput fill:#FFC107
    style CheckpointDB fill:#9C27B0
    style RestoreState fill:#FF9800
```

---

## 🎨 Visual Representation Guide

### Cách đọc các biểu đồ:

#### Màu sắc:
- 🟢 **Green** (#4CAF50): Entry points / Start nodes
- 🔵 **Blue** (#2196F3): Exit points / End nodes
- 🔴 **Red** (#F44336): Error states / Rollback
- 🟠 **Orange** (#FF9800): Processing nodes / Important logic
- 🟡 **Yellow** (#FFC107): Decision points / Conditions
- 🟣 **Purple** (#9C27B0): Special operations / Parallel execution

#### Hình dạng:
- **Rectangle**: Processing node
- **Diamond**: Decision/Conditional
- **Rounded Rectangle**: Start/End
- **Cylinder**: Database
- **Parallelogram**: Input/Output

#### Mũi tên:
- **Solid**: Normal flow
- **Dashed**: Optional/Conditional flow
- **Bold**: Main path

---

## 📖 Sử dụng diagrams

### 1. Trong VS Code:
- Cài extension: "Markdown Preview Mermaid Support"
- Mở file này và preview

### 2. Trong Documentation:
- Copy vào MkDocs/Docusaurus
- Sử dụng mermaid plugin

### 3. Export hình ảnh:
```bash
# Sử dụng mermaid-cli
npm install -g @mermaid-js/mermaid-cli
mmdc -i LANGGRAPH_FLOW_DIAGRAMS.md -o output.png
```

---

**Last Updated**: 2025-01-26  
**Version**: 1.0.0
