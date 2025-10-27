# 🤖 Hướng Dẫn Thiết Kế Workflow Thân Thiện với Người Dùng

## 📖 Tổng Quan

Tài liệu này giải thích cách thiết kế 3 graph chính và Master Orchestrator để tạo trải nghiệm chatbot thân thiện với người dùng.

---

## 🎯 Kiến Trúc Tổng Thể

```
┌─────────────────────────────────────────────────────────────┐
│                    MASTER ORCHESTRATOR                       │
│                    (graph.py)                                │
│                                                              │
│  ┌────────────┐    ┌────────────┐    ┌──────────────┐      │
│  │  Session   │ -> │   Intent   │ -> │   Routing    │      │
│  │    Init    │    │ & Recommend│    │   Logic      │      │
│  └────────────┘    └────────────┘    └──────────────┘      │
│         │                                    │               │
│         v                                    v               │
│  ┌─────────────────────────────────────────────────┐       │
│  │              Sub-Graph Invocation                │       │
│  └─────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
         │                │                    │
         v                v                    v
┌─────────────┐  ┌──────────────┐   ┌─────────────────┐
│   Graph 1   │  │   Graph 2    │   │    Graph 3      │
│   Intent &  │  │     SQL      │   │  Assistance &   │
│Recommendation│  │  Processing  │   │ Visualization   │
└─────────────┘  └──────────────┘   └─────────────────┘
```

---

## 🔧 3 Graph Chính

### 1️⃣ **Intent & Recommendation Graph**

**Mục đích:** Phân loại ý định và đề xuất câu hỏi/mối quan hệ

**Workflow:**
```
START
  ↓
[Intent Classification]
  ├─ TEXT_TO_SQL → [Question Recommendation] → END
  ├─ GENERAL → [Semantics Description] → [Relationship Recommendation] → END
  ├─ USER_GUIDE → [Question Recommendation] → END
  └─ MISLEADING_QUERY → END
```

**User-Friendly Features:**
- ✅ Phân loại ý định chính xác
- ✅ Đề xuất câu hỏi tiếp theo thông minh
- ✅ Gợi ý mối quan hệ dữ liệu
- ✅ Xử lý graceful với câu hỏi không liên quan

**Khi nào sử dụng:**
- User bắt đầu conversation mới
- Cần recommendations cho bước tiếp theo
- Khám phá khả năng của database

---

### 2️⃣ **SQL Processing Graph**

**Mục đích:** Sinh SQL, validate, correct và trả về kết quả

**Workflow:**
```
START
  ↓
[Check Follow-up]
  ├─ New Query → [SQL Reasoning] → [SQL Generation]
  └─ Follow-up → [Follow-up Reasoning] → [Follow-up Generation]
  ↓
[SQL Validation]
  ├─ Valid → [Extract Tables] → [Generate Question] → [Format Answer] → END
  └─ Invalid → [Diagnosis] → [Correction] → [Validation] (retry loop)
                                               ↓
                                          (Max retries) → [Regeneration]
```

**User-Friendly Features:**
- ✅ Tự động sửa lỗi SQL (retry loop)
- ✅ Hỗ trợ câu hỏi follow-up
- ✅ Giải thích SQL bằng ngôn ngữ tự nhiên
- ✅ Validation trước khi execute
- ✅ Fallback khi correction fails

**Khi nào sử dụng:**
- Intent = TEXT_TO_SQL
- User muốn query data
- Follow-up questions về data

---

### 3️⃣ **Assistance & Visualization Graph**

**Mục đích:** Hỗ trợ user và tạo visualization

**Workflow:**
```
START
  ↓
[Route by Intent]
  ├─ GENERAL → [Data Assistance] (streaming) → END
  ├─ USER_GUIDE → [User Guide Assistance] (streaming) → END
  ├─ MISLEADING → [Misleading Assistance] → END
  └─ TEXT_TO_SQL + visualization → [Chart Generation]
                                        ↓
                                   [Check Adjustment]
                                        ├─ Yes → [Chart Adjustment]
                                        └─ No → END
```

**User-Friendly Features:**
- ✅ Streaming responses (GENERAL, USER_GUIDE)
- ✅ Tự động tạo chart phù hợp
- ✅ Điều chỉnh chart theo yêu cầu
- ✅ Gợi ý thân thiện với misleading queries

**Khi nào sử dụng:**
- Intent = GENERAL, USER_GUIDE, MISLEADING_QUERY
- Cần visualization cho SQL results
- User cần trợ giúp sử dụng hệ thống

---

## 🎭 Master Orchestrator Graph

**Mục đích:** Điều phối toàn bộ workflow và tạo trải nghiệm liền mạch

### **Complete Workflow:**

```
START
  ↓
┌──────────────────────┐
│ Initialize Session    │ ← Load history, user preferences
└──────────────────────┘
  ↓
┌──────────────────────┐
│ Intent & Recommend   │ ← Classify + Generate recommendations
└──────────────────────┘
  ↓
┌──────────────────────┐
│   Route by Intent    │
└──────────────────────┘
  ├─ TEXT_TO_SQL ────────────────┐
  │                               v
  │                      ┌─────────────────┐
  │                      │ SQL Processing  │
  │                      └─────────────────┘
  │                               │
  │                               v
  │                      ┌─────────────────┐
  │                      │ Visualization?  │
  │                      └─────────────────┘
  │                          │         │
  │                     Yes  │         │ No
  │                          v         v
  ├─ GENERAL ────────> ┌──────────────────┐
  ├─ USER_GUIDE ────> │   Assistance &    │
  └─ MISLEADING ────> │  Visualization    │
                       └──────────────────┘
                               │
                               v
                      ┌─────────────────┐
                      │  Streaming?     │
                      └─────────────────┘
                          │         │
                     Yes  │         │ No
                          v         v
                      ┌──────────────────┐
                      │ Format Response  │
                      └──────────────────┘
                               │
                               v
                      ┌──────────────────┐
                      │  Save History    │ ← Multi-turn support
                      └──────────────────┘
                               │
                               v
                             END
```

### **Key Features:**

#### 1. **Session Management**
```python
# Initialize session with context
{
    "session_id": "unique_id",
    "conversation_history": [...],  # Multi-turn support
    "user_preferences": {
        "language": "English",
        "enable_streaming": True,
        "max_recommendations": 5
    }
}
```

#### 2. **Intent-Based Routing**
```python
def _route_by_intent(state):
    intent = state["intent"]
    
    if intent == "TEXT_TO_SQL":
        return "sql_processing"
    elif intent in ["GENERAL", "USER_GUIDE", "MISLEADING_QUERY"]:
        return "assistance"
    else:
        return "error"
```

#### 3. **Smart Follow-up Detection**
```python
def _is_followup_question(state):
    history = state["conversation_history"]
    query = state["query"]
    
    # Detect keywords: "also", "what about", "that", etc.
    followup_keywords = ["also", "and", "what about", "previous"]
    has_history = len(history) > 0
    has_keywords = any(kw in query.lower() for kw in followup_keywords)
    
    return has_history and has_keywords
```

#### 4. **Automatic Visualization Detection**
```python
def _should_visualize(state):
    query = state["query"].lower()
    
    # Check keywords
    viz_keywords = ["chart", "graph", "plot", "visualize", "trend"]
    has_viz_keywords = any(kw in query for kw in viz_keywords)
    
    # Check data suitability
    has_numeric_data = state.get("sql_answer") is not None
    
    return has_viz_keywords or has_numeric_data
```

#### 5. **Streaming for Better UX**
```python
def _check_streaming(state):
    intent = state["intent"]
    enable_streaming = state["user_preferences"]["enable_streaming"]
    
    # Stream for GENERAL and USER_GUIDE
    should_stream = enable_streaming and intent in ["GENERAL", "USER_GUIDE"]
    
    return "stream" if should_stream else "no_stream"
```

#### 6. **Graceful Error Handling**
```python
async def _handle_error_node(state):
    errors = state["errors"]
    
    # User-friendly messages
    if "classification" in errors:
        message = "Could you rephrase your question?"
    elif "sql" in errors:
        message = "I couldn't generate SQL. Could you provide more details?"
    else:
        message = "Please try again or contact support."
    
    return {
        "status": "error",
        "message": message,
        "recommendations": state["recommended_questions"]  # Still helpful!
    }
```

---

## 💡 User-Friendly Design Patterns

### 1. **Contextual Conversations**
```python
# Luôn load history
state["conversation_history"] = await load_history(session_id)

# Sử dụng history cho follow-up
if is_followup:
    previous_context = conversation_history[-1]
    # Use previous SQL, tables, etc.
```

### 2. **Progressive Disclosure**
```python
# Không overwhelm user với quá nhiều thông tin
response = {
    "answer": "...",  # Main answer first
    "sql": "...",      # Then SQL (nếu requested)
    "reasoning": "...", # Explanation (expandable)
}
```

### 3. **Smart Recommendations**
```python
# Luôn đề xuất next steps
if intent == "TEXT_TO_SQL":
    recommend_related_questions()
elif intent == "GENERAL":
    recommend_tables_and_relationships()
elif intent == "MISLEADING_QUERY":
    recommend_sample_queries()  # Helpful redirection!
```

### 4. **Streaming Responses**
```python
# Cho GENERAL và USER_GUIDE
async def stream_response():
    chunks = chunk_text(response_text, chunk_size=50)
    for chunk in chunks:
        yield chunk
        await asyncio.sleep(0.1)  # Smooth streaming
```

### 5. **Validation Before Execution**
```python
# Validate SQL trước khi execute
is_valid = validate_sql(generated_sql)

if not is_valid:
    # Tự động correct với retry loop
    for attempt in range(max_attempts):
        diagnosis = diagnose_sql_error()
        corrected_sql = correct_sql(diagnosis)
        if validate_sql(corrected_sql):
            break
    else:
        # Regenerate nếu correction fails
        regenerate_sql()
```

### 6. **Multi-language Support**
```python
# Sử dụng ngôn ngữ từ preferences
language = state["user_preferences"]["language"]

# Pass to LLM prompts
prompt = f"Answer in {language}: {query}"
```

---

## 🚀 Cách Sử Dụng

### **1. Tạo Orchestrator Graph:**
```python
from src.graphs.orchestrator import create_orchestrator_graph

# Create master graph
orchestrator = create_orchestrator_graph()
```

### **2. Run Workflow:**
```python
# Prepare input
user_input = {
    "session_id": "user_123",
    "query": "What is the total revenue last quarter?",
    "project_id": "project_456",
    "context": {
        "embedder": embedder,
        "generator": generator,
        # ... other components
    },
}

# Execute workflow
result = await orchestrator.app.ainvoke(user_input)

# Get response
final_response = result["final_response"]
```

### **3. Handle Different Intents:**

**TEXT_TO_SQL:**
```python
{
    "intent": "TEXT_TO_SQL",
    "sql": {
        "query": "SELECT SUM(revenue) FROM sales WHERE date >= ...",
        "answer": "Total revenue is $1.2M",
        "reasoning": "Calculated sum of revenue from sales table"
    },
    "visualization": {
        "type": "bar_chart",
        "schema": {...}
    },
    "recommendations": {
        "questions": [
            "What about this quarter?",
            "How does it compare to last year?"
        ]
    }
}
```

**GENERAL:**
```python
{
    "intent": "GENERAL",
    "assistance": {
        "response": "This database contains sales, customers, and products...",
        "reasoning": "Analyzed database schema"
    },
    "recommendations": {
        "relationships": [
            {"from": "customers", "to": "orders", "type": "one_to_many"},
            {"from": "orders", "to": "products", "type": "many_to_many"}
        ]
    }
}
```

**MISLEADING_QUERY:**
```python
{
    "intent": "MISLEADING_QUERY",
    "message": "I'm here to help with data analysis. Could you ask about your data?",
    "recommendations": {
        "questions": [
            "What data do I have?",
            "Show me total sales",
            "List top customers"
        ]
    }
}
```

---

## 🎨 Best Practices

### ✅ **DO:**
1. **Luôn load conversation history** cho multi-turn support
2. **Validate inputs** trước khi processing
3. **Provide recommendations** cho mọi intent
4. **Stream responses** cho GENERAL/USER_GUIDE
5. **Handle errors gracefully** với helpful messages
6. **Save history** sau mỗi interaction
7. **Use retry loops** cho SQL correction
8. **Detect follow-ups** tự động

### ❌ **DON'T:**
1. ❌ Không bỏ qua errors - luôn handle gracefully
2. ❌ Không overwhelm user với quá nhiều thông tin
3. ❌ Không execute SQL mà không validate
4. ❌ Không ignore user preferences
5. ❌ Không quên save history
6. ❌ Không hard-code messages - use dynamic responses

---

## 📊 Flow Diagrams

### **Happy Path - TEXT_TO_SQL:**
```
User: "Show me revenue last quarter"
  ↓
[Initialize Session] → Load history ✓
  ↓
[Intent Classification] → TEXT_TO_SQL (95% confidence) ✓
  ↓
[SQL Processing] → Generate SQL → Validate ✓ → Execute ✓
  ↓
[Check Visualization] → Detect "show" keyword → Need viz ✓
  ↓
[Chart Generation] → Bar chart ✓
  ↓
[Format Response] → SQL + Answer + Chart ✓
  ↓
[Save History] → For follow-ups ✓
  ↓
User sees: Answer, Chart, Recommendations
```

### **Recovery Path - SQL Error:**
```
User: "Complex query"
  ↓
[SQL Generation] → Invalid SQL ✗
  ↓
[SQL Diagnosis] → "Missing JOIN clause"
  ↓
[SQL Correction] → Add JOIN → Validate ✓
  ↓
Success! (with 1 correction attempt)
```

### **Follow-up Path:**
```
User 1: "Show sales"
  ↓
[Response] → Sales data + Chart
  ↓
User 2: "What about last year?"  ← Follow-up detected!
  ↓
[Follow-up Detection] → Use previous SQL context ✓
  ↓
[Follow-up SQL Generation] → Modify previous SQL ✓
  ↓
[Response] → Comparison chart
```

---

## 🔍 Testing

### **Test Scenarios:**

```python
# 1. Simple Query
test_input = {"query": "What data do I have?"}
# Expected: GENERAL → Data assistance + Recommendations

# 2. SQL Query
test_input = {"query": "Show me top 10 customers"}
# Expected: TEXT_TO_SQL → SQL + Answer + Recommendations

# 3. Follow-up
test_input = {
    "query": "What about last year?",
    "conversation_history": [...]
}
# Expected: Follow-up SQL generation

# 4. Visualization
test_input = {"query": "Show revenue trend over time"}
# Expected: SQL + Chart

# 5. Misleading
test_input = {"query": "What's the weather?"}
# Expected: MISLEADING → Helpful redirect + Recommendations

# 6. Error Recovery
test_input = {"query": "Very complex ambiguous query"}
# Expected: Error → Helpful message + Recommendations
```

---

## 📚 Related Documentation

- **Intent Graph:** `src/graphs/intent_recommendation/graph.py`
- **SQL Graph:** `src/graphs/sql_processing/graph.py`
- **Assistance Graph:** `src/graphs/assistance_visualization/graph.py`
- **Orchestrator:** `src/graphs/orchestrator/graph.py`
- **States:** `src/graphs/*/state.py`

---

## 🎯 Summary

**3 Graph Chính:**
1. **Intent & Recommendation** - Phân loại + Đề xuất
2. **SQL Processing** - Sinh SQL + Validate + Answer
3. **Assistance & Visualization** - Hỗ trợ + Chart

**Master Orchestrator:**
- Điều phối 3 graphs
- Session management
- Multi-turn support
- Streaming responses
- Error handling
- Smart routing

**Key to User-Friendly:**
- ✅ Contextual conversations (history)
- ✅ Smart recommendations (always helpful)
- ✅ Graceful error handling
- ✅ Streaming for better UX
- ✅ Follow-up detection
- ✅ Auto visualization

---

**Happy Coding! 🚀**
