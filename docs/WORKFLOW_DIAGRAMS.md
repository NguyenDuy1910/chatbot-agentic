# User-Friendly Workflow Architecture

## Complete System Diagram

```mermaid
graph TB
    subgraph "User Interface"
        USER[👤 User]
        CHAT[💬 Chat Interface]
    end
    
    subgraph "Master Orchestrator"
        INIT[🚀 Initialize Session<br/>Load History & Preferences]
        
        subgraph "Graph 1: Intent & Recommendation"
            IC[🎯 Intent Classification<br/>TEXT_TO_SQL | GENERAL | USER_GUIDE | MISLEADING]
            QR[💡 Question Recommendation]
            SD[📖 Semantics Description]
            RR[🔗 Relationship Recommendation]
        end
        
        ROUTE{🔀 Route by Intent}
        
        subgraph "Graph 2: SQL Processing"
            CF[🔁 Check Follow-up]
            SR[🧠 SQL Reasoning]
            SG[⚙️ SQL Generation]
            FSR[🧠 Follow-up SQL Reasoning]
            FSG[⚙️ Follow-up SQL Generation]
            VAL{✅ Validate SQL}
            DIAG[🔍 SQL Diagnosis]
            CORR[🔧 SQL Correction]
            REGEN[🔄 SQL Regeneration]
            EXT[📊 Extract Tables]
            QUEST[❓ SQL Question]
            ANS[💬 SQL Answer]
        end
        
        subgraph "Graph 3: Assistance & Visualization"
            DA[📚 Data Assistance<br/>Streaming]
            UG[📖 User Guide<br/>Streaming]
            MIS[⚠️ Misleading Assistance]
            CG[📊 Chart Generation]
            CA[🎨 Chart Adjustment]
        end
        
        VIZ{📊 Need Visualization?}
        STREAM{🌊 Enable Streaming?}
        SR_NODE[🌊 Stream Response]
        FORMAT[📦 Format Final Response]
        SAVE[💾 Save History]
        ERR[⚠️ Handle Error]
    end
    
    subgraph "Data Layer"
        DB[(🗄️ Database)]
        CACHE[(⚡ Cache)]
        HISTORY[(📚 History Store)]
    end
    
    %% User Flow
    USER --> CHAT
    CHAT --> INIT
    
    %% Session Init
    INIT --> IC
    HISTORY -.Load History.-> INIT
    CACHE -.Load Preferences.-> INIT
    
    %% Intent & Recommendation Flow
    IC --> QR
    IC --> SD
    SD --> RR
    QR --> ROUTE
    RR --> ROUTE
    
    %% Intent Routing
    ROUTE -->|TEXT_TO_SQL| CF
    ROUTE -->|GENERAL| DA
    ROUTE -->|USER_GUIDE| UG
    ROUTE -->|MISLEADING| MIS
    ROUTE -->|ERROR| ERR
    
    %% SQL Processing Flow
    CF -->|New Query| SR
    CF -->|Follow-up| FSR
    SR --> SG
    FSR --> FSG
    SG --> VAL
    FSG --> VAL
    
    VAL -->|Valid| EXT
    VAL -->|Invalid| DIAG
    DIAG --> CORR
    CORR --> VAL
    VAL -->|Max Retries| REGEN
    REGEN --> VAL
    
    EXT --> QUEST
    QUEST --> ANS
    ANS --> VIZ
    
    DB -.Execute SQL.-> ANS
    
    %% Visualization Check
    VIZ -->|Yes| CG
    VIZ -->|No| FORMAT
    
    %% Assistance Flow
    DA --> STREAM
    UG --> STREAM
    MIS --> FORMAT
    
    %% Chart Flow
    CG --> CA
    CA --> FORMAT
    
    %% Streaming Check
    STREAM -->|Yes| SR_NODE
    STREAM -->|No| FORMAT
    SR_NODE --> FORMAT
    
    %% Final Steps
    FORMAT --> SAVE
    ERR --> SAVE
    SAVE --> CHAT
    SAVE -.Save.-> HISTORY
    SAVE -.Update.-> CACHE
    
    CHAT --> USER
    
    %% Styling
    classDef userClass fill:#e1f5ff,stroke:#01579b,stroke-width:2px
    classDef graphClass fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef sqlClass fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef assistClass fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px
    classDef dataClass fill:#fce4ec,stroke:#880e4f,stroke-width:2px
    
    class USER,CHAT userClass
    class IC,QR,SD,RR graphClass
    class CF,SR,SG,FSR,FSG,VAL,DIAG,CORR,REGEN,EXT,QUEST,ANS sqlClass
    class DA,UG,MIS,CG,CA assistClass
    class DB,CACHE,HISTORY dataClass
```

## Intent-Based Routing Flow

```mermaid
flowchart LR
    subgraph "Intent Classification"
        Q[User Query]
        IC{🎯 Classify Intent}
    end
    
    subgraph "TEXT_TO_SQL Path"
        SQL1[SQL Processing]
        SQL2[Validation & Correction]
        SQL3[Answer Generation]
        VIZ[Visualization?]
    end
    
    subgraph "GENERAL Path"
        GEN1[Data Assistance]
        GEN2[Streaming Response]
        GEN3[Recommendations]
    end
    
    subgraph "USER_GUIDE Path"
        UG1[User Guide Assistance]
        UG2[Streaming Response]
        UG3[Help Content]
    end
    
    subgraph "MISLEADING Path"
        MIS1[Friendly Redirect]
        MIS2[Sample Queries]
    end
    
    Q --> IC
    IC -->|TEXT_TO_SQL| SQL1
    IC -->|GENERAL| GEN1
    IC -->|USER_GUIDE| UG1
    IC -->|MISLEADING| MIS1
    
    SQL1 --> SQL2 --> SQL3 --> VIZ
    GEN1 --> GEN2 --> GEN3
    UG1 --> UG2 --> UG3
    MIS1 --> MIS2
    
    VIZ --> FINAL[Final Response]
    GEN3 --> FINAL
    UG3 --> FINAL
    MIS2 --> FINAL
    
    style IC fill:#ffd54f
    style SQL1 fill:#81c784
    style GEN1 fill:#64b5f6
    style UG1 fill:#ba68c8
    style MIS1 fill:#ff8a65
    style FINAL fill:#4db6ac
```

## Multi-Turn Conversation Flow

```mermaid
sequenceDiagram
    participant U as 👤 User
    participant O as Orchestrator
    participant H as History Store
    participant I as Intent Graph
    participant S as SQL Graph
    participant A as Assistance Graph
    
    Note over U,A: Turn 1: Initial Query
    U->>O: "What is total revenue?"
    O->>H: Load history (empty)
    O->>I: Classify intent
    I-->>O: TEXT_TO_SQL
    O->>S: Generate SQL
    S-->>O: SQL + Answer
    O->>H: Save turn 1
    O-->>U: Answer + Recommendations
    
    Note over U,A: Turn 2: Follow-up Query
    U->>O: "What about last year?"
    O->>H: Load history (1 entry)
    O->>I: Classify intent
    I-->>O: TEXT_TO_SQL (follow-up)
    Note over O,S: Detect follow-up keyword
    O->>S: Generate follow-up SQL<br/>(use previous context)
    S-->>O: Modified SQL + Answer
    O->>H: Save turn 2
    O-->>U: Comparison Answer
    
    Note over U,A: Turn 3: Visualization Request
    U->>O: "Show me a trend chart"
    O->>H: Load history (2 entries)
    O->>I: Classify intent
    I-->>O: TEXT_TO_SQL (viz needed)
    O->>S: Use previous SQL
    S-->>O: SQL results
    O->>A: Generate chart
    A-->>O: Chart schema
    O->>H: Save turn 3
    O-->>U: Chart + Data
```

## Error Recovery Flow

```mermaid
flowchart TD
    START[Generate SQL]
    VAL{Validate}
    
    VAL -->|Valid ✅| SUCCESS[Execute & Return]
    VAL -->|Invalid ❌| DIAG[Diagnose Error]
    
    DIAG --> CHECK{Attempts < Max?}
    CHECK -->|Yes| CORR[Correct SQL]
    CHECK -->|No| REGEN[Regenerate SQL]
    
    CORR --> VAL
    REGEN --> VAL2{Validate}
    
    VAL2 -->|Valid ✅| SUCCESS
    VAL2 -->|Invalid ❌| ERROR[Format Error Response<br/>+ Recommendations]
    
    ERROR --> HELP[Still Helpful!<br/>Suggest alternatives]
    
    style SUCCESS fill:#4caf50
    style ERROR fill:#f44336
    style HELP fill:#2196f3
```

## State Management

```mermaid
graph LR
    subgraph "Orchestrator State"
        S1[Session Info<br/>session_id<br/>history<br/>preferences]
        S2[Query Info<br/>query<br/>intent<br/>confidence]
        S3[SQL Info<br/>generated_sql<br/>answer<br/>is_valid]
        S4[Assistance Info<br/>response<br/>chart_schema]
        S5[Response Info<br/>final_response<br/>status]
    end
    
    subgraph "Sub-Graph States"
        SG1[Intent State]
        SG2[SQL State]
        SG3[Assistance State]
    end
    
    S1 --> SG1
    SG1 -.Merge.-> S2
    
    S2 --> SG2
    SG2 -.Merge.-> S3
    
    S3 --> SG3
    SG3 -.Merge.-> S4
    
    S4 --> S5
    
    style S1 fill:#e3f2fd
    style S2 fill:#fff3e0
    style S3 fill:#f3e5f5
    style S4 fill:#e8f5e9
    style S5 fill:#fce4ec
```

## User Experience Flow

```mermaid
journey
    title Chatbot User Experience Journey
    section New Session
      User asks question: 5: User
      Intent classified: 5: System
      Recommendations shown: 4: User
    section SQL Query
      SQL generated: 5: System
      Answer provided: 5: User
      Chart shown: 5: User
    section Follow-up
      Context maintained: 5: System
      Quick response: 5: User
      More recommendations: 4: User
    section Error Case
      SQL fails: 2: System
      Auto-correction: 4: System
      Helpful message: 4: User
      Alternative suggested: 5: User
```

## Key User-Friendly Features

```mermaid
mindmap
  root((User-Friendly<br/>Chatbot))
    Contextual
      Multi-turn conversations
      History tracking
      Follow-up detection
      Context reuse
    Smart
      Intent classification
      Auto recommendations
      Relationship suggestions
      Sample queries
    Responsive
      Streaming responses
      Real-time updates
      Progress indicators
      Fast routing
    Helpful
      Error recovery
      Retry loops
      Friendly messages
      Always suggest
    Visual
      Auto chart detection
      Chart generation
      Chart adjustment
      Data visualization
    Reliable
      SQL validation
      Auto correction
      Fallback handling
      Error logging
```
