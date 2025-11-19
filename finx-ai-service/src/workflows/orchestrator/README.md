# 🤖 Orchestrator - Master Workflow Coordinator

> **Điều phối 3 graphs chính để tạo trải nghiệm chatbot thân thiện với người dùng**

---

## 📋 Mục Lục

- [Giới Thiệu](#-giới-thiệu)
- [Kiến Trúc](#-kiến-trúc)
- [3 Graph Chính](#-3-graph-chính)
- [Cách Sử Dụng](#-cách-sử-dụng)
- [Tính Năng User-Friendly](#-tính-năng-user-friendly)
- [Demo](#-demo)
- [Tài Liệu](#-tài-liệu)

---

## 🎯 Giới Thiệu

**Master Orchestrator** là graph chính điều phối toàn bộ workflow chatbot, kết hợp 3 sub-graphs:

1. **Intent & Recommendation Graph** - Phân loại ý định + Đề xuất
2. **SQL Processing Graph** - Sinh SQL + Validate + Answer
3. **Assistance & Visualization Graph** - Hỗ trợ + Chart

### Tại Sao Cần Orchestrator?

✅ **Trải nghiệm liền mạch** - Tự động route giữa các graphs  
✅ **Multi-turn conversations** - Nhớ context qua nhiều lượt hội thoại  
✅ **Smart routing** - Chọn đúng graph dựa trên intent  
✅ **Error recovery** - Xử lý lỗi gracefully  
✅ **Always helpful** - Luôn đề xuất next steps  

---

## 🏗️ Kiến Trúc

```
┌─────────────────────────────────────────────────┐
│          MASTER ORCHESTRATOR                     │
│                                                  │
│  Session Init → Intent → Routing → Processing   │
│                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │ Graph 1  │  │ Graph 2  │  │ Graph 3  │      │
│  │ Intent & │  │   SQL    │  │Assistance│      │
│  │ Recommend│  │Processing│  │   & Viz  │      │
│  └──────────┘  └──────────┘  └──────────┘      │
│                                                  │
│  Format Response → Save History → END           │
└─────────────────────────────────────────────────┘
```

### Complete Workflow:

```
USER QUERY
    ↓
1. Initialize Session (load history + preferences)
    ↓
2. Intent & Recommendation (classify + recommend)
    ↓
3. Route by Intent
    ├─ TEXT_TO_SQL → SQL Processing → (Visualization?)
    ├─ GENERAL → Data Assistance (streaming)
    ├─ USER_GUIDE → User Guide (streaming)
    └─ MISLEADING → Helpful redirect
    ↓
4. Format Response (với recommendations)
    ↓
5. Save History (for multi-turn)
    ↓
RESPONSE TO USER
```

---

## 🔧 3 Graph Chính

### 1️⃣ Intent & Recommendation Graph

**Path:** `src/graphs/intent_recommendation/graph.py`

**Workflow:**
```
Intent Classification
  ├─ TEXT_TO_SQL → Question Recommendation
  ├─ GENERAL → Semantics Description → Relationship Recommendation
  ├─ USER_GUIDE → Question Recommendation
  └─ MISLEADING → End (no recommendations)
```

**Đầu vào:**
- User query
- Conversation history
- Database schemas
- User instructions

**Đầu ra:**
- Intent classification
- Rephrased question
- Recommended questions
- Recommended relationships
- Confidence score

---

### 2️⃣ SQL Processing Graph

**Path:** `src/graphs/sql_processing/graph.py`

**Workflow:**
```
Check Follow-up
  ├─ New → SQL Reasoning → SQL Generation
  └─ Follow-up → Follow-up Reasoning → Follow-up Generation
      ↓
  Validation
      ├─ Valid → Extract Tables → Answer
      └─ Invalid → Diagnosis → Correction → Retry
                                     ↓
                              (Max retries) → Regeneration
```

**Đầu vào:**
- Query (rephrased)
- Database schemas
- Is follow-up?
- Previous SQL (if follow-up)

**Đầu ra:**
- Generated SQL
- SQL reasoning
- Formatted answer
- Validation status
- Correction attempts

---

### 3️⃣ Assistance & Visualization Graph

**Path:** `src/graphs/assistance_visualization/graph.py`

**Workflow:**
```
Route by Intent
  ├─ GENERAL → Data Assistance (streaming)
  ├─ USER_GUIDE → User Guide (streaming)
  ├─ MISLEADING → Misleading Assistance
  └─ TEXT_TO_SQL + viz → Chart Generation → Adjustment?
```

**Đầu vào:**
- Intent
- Query
- SQL results (if applicable)
- Adjustment instructions

**Đầu ra:**
- Assistance response
- Chart schema (if needed)
- Streaming chunks
- Reasoning

---

## 🚀 Cách Sử Dụng

### Quick Start

```python
from src.graphs.orchestrator import create_orchestrator_graph

# 1. Create orchestrator
orchestrator = create_orchestrator_graph()

# 2. Prepare input
user_input = {
    "session_id": "user_123",
    "query": "What is the total revenue last quarter?",
    "project_id": "project_456",
    "user_preferences": {
        "language": "English",
        "enable_streaming": True,
    },
    "context": {
        "embedder": embedder,
        "generator": generator,
        # ... other components
    },
}

# 3. Run workflow
result = await orchestrator.app.ainvoke(user_input)

# 4. Get response
response = result["final_response"]
print(response)
```

### Output Structure

```python
{
    "session_id": "user_123",
    "query": "What is the total revenue last quarter?",
    "intent": "TEXT_TO_SQL",
    "confidence": 0.95,
    
    # For TEXT_TO_SQL
    "sql": {
        "query": "SELECT SUM(revenue) FROM sales WHERE ...",
        "reasoning": "Query aggregates revenue...",
        "answer": "Total revenue is $1.2M",
        "tables_used": ["sales"],
        "is_valid": True
    },
    
    # For visualization
    "visualization": {
        "type": "bar_chart",
        "schema": {...}
    },
    
    # Always included
    "recommendations": {
        "questions": [
            "What about this quarter?",
            "Show me by category",
        ]
    },
    
    "metadata": {
        "processing_time": 1.23,
        "correction_attempts": 0,
        "streaming_enabled": False
    }
}
```

---

## 💡 Tính Năng User-Friendly

### 1. **Contextual Conversations (Multi-turn)**

```python
# Turn 1
User: "What is total revenue?"
Bot: "$1.2M" + recommendations

# Turn 2 (follow-up detected!)
User: "What about last year?"
Bot: "$980K" + comparison
```

**Cơ chế:**
- Load conversation history
- Detect follow-up keywords: "also", "what about", "that", etc.
- Reuse previous SQL context
- Modify SQL for new criteria

---

### 2. **Smart Recommendations**

**Luôn đề xuất next steps:**

```python
# For TEXT_TO_SQL
recommendations = [
    "What about this quarter?",
    "Show me breakdown by category",
    "Compare to last year"
]

# For GENERAL
recommendations = {
    "questions": [...],
    "relationships": [...]
}

# For MISLEADING
recommendations = [
    "What data do I have?",
    "Show me total sales",
    "List top customers"
]
```

---

### 3. **Streaming Responses**

**Cho GENERAL và USER_GUIDE intents:**

```python
# User sees response progressively
"Your database contains..."  # Chunk 1
"The sales table has..."      # Chunk 2
"Key relationships are..."    # Chunk 3
```

**Benefits:**
- Faster perceived response time
- Better UX for long responses
- User can start reading immediately

---

### 4. **Automatic Visualization**

**Tự động detect khi cần chart:**

```python
# Keywords detected
queries_needing_viz = [
    "show me trend",
    "compare over time",
    "distribution of",
    "breakdown by"
]

# Auto-generate appropriate chart
- Trend → Line chart
- Comparison → Bar chart
- Distribution → Pie chart
```

---

### 5. **Error Recovery with Retry Loop**

```python
# SQL generation fails
1. Diagnose error
2. Attempt correction (max 3 times)
3. If still fails → Regenerate
4. If regeneration fails → Helpful error message + recommendations
```

**User never sees technical errors!**

---

### 6. **Graceful Handling of All Intents**

```python
# MISLEADING_QUERY
Input: "What's the weather?"
Output: "I help with data analysis. Try these: [sample queries]"

# GENERAL
Input: "What data do I have?"
Output: Streaming data overview + relationships + questions

# USER_GUIDE
Input: "How do I create a chart?"
Output: Streaming help content + examples
```

---

## 🎬 Demo

### Run Demo Script:

```bash
cd finx-ai-service
python -m src.graphs.orchestrator.demo
```

**Demo scenarios:**

1. ✅ TEXT_TO_SQL query
2. ✅ Follow-up query
3. ✅ GENERAL query with streaming
4. ✅ Visualization query
5. ✅ Error handling
6. ✅ Misleading query

### Expected Output:

```
🤖 CHATBOT ORCHESTRATOR DEMO
===============================================

📊 SCENARIO 1: TEXT_TO_SQL Query
  Query: What is the total revenue for last quarter?
  
  Workflow:
    1. ✅ Initialize Session
    2. ✅ Intent Classification → TEXT_TO_SQL
    3. ✅ Route to SQL Processing
    4. ✅ Generate SQL
    5. ✅ Validate & Execute
    6. ✅ Format Response
    7. ✅ Save History
  
  Output:
    Intent: TEXT_TO_SQL
    SQL: SELECT SUM(revenue) FROM sales WHERE...
    Answer: Total revenue is $1,234,567.89
    Recommendations: 3 questions

...
```

---

## 📚 Tài Liệu

### Files Created:

```
src/graphs/orchestrator/
├── __init__.py          # Package exports
├── graph.py             # Master Orchestrator implementation
├── state.py             # State schema
└── demo.py              # Demo script

docs/
├── USER_FRIENDLY_WORKFLOW_GUIDE.md  # Complete guide
└── WORKFLOW_DIAGRAMS.md              # Mermaid diagrams
```

### Detailed Guides:

1. **Complete Guide:** [`docs/USER_FRIENDLY_WORKFLOW_GUIDE.md`](../../docs/USER_FRIENDLY_WORKFLOW_GUIDE.md)
   - Kiến trúc chi tiết
   - Workflow diagrams
   - Best practices
   - Examples

2. **Flow Diagrams:** [`docs/WORKFLOW_DIAGRAMS.md`](../../docs/WORKFLOW_DIAGRAMS.md)
   - System architecture
   - Intent routing flow
   - Multi-turn conversation
   - Error recovery
   - State management

3. **Demo Script:** [`demo.py`](./demo.py)
   - 6 scenarios
   - Expected outputs
   - API usage example

---

## 🎯 Key Takeaways

### Orchestrator làm gì?

1. **Điều phối** 3 graphs dựa trên intent
2. **Quản lý** session và conversation history
3. **Route** tới đúng graph cho từng intent
4. **Detect** follow-up questions
5. **Auto-generate** visualizations
6. **Stream** responses khi cần
7. **Handle** errors gracefully
8. **Always** provide recommendations

### User Benefits:

✅ Trải nghiệm liền mạch qua nhiều lượt hội thoại  
✅ Context được nhớ và sử dụng  
✅ Luôn nhận được gợi ý hữu ích  
✅ Streaming cho responses dài  
✅ Tự động tạo chart khi cần  
✅ Lỗi được xử lý thân thiện  
✅ Redirect hữu ích cho off-topic queries  

---

## 🔗 Related Graphs

- [Intent & Recommendation Graph](../intent_recommendation/README.md)
- [SQL Processing Graph](../sql_processing/README.md)
- [Assistance & Visualization Graph](../assistance_visualization/README.md)

---

## 📞 Support

Nếu có câu hỏi hoặc cần hỗ trợ, vui lòng:

1. Xem [Complete Guide](../../docs/USER_FRIENDLY_WORKFLOW_GUIDE.md)
2. Chạy [Demo](./demo.py)
3. Xem [Diagrams](../../docs/WORKFLOW_DIAGRAMS.md)

---

**Happy Coding! 🚀**
