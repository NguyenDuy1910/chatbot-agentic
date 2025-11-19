# Cách Xem Graph của LangGraph Workflow

## Tóm tắt nhanh

Bạn có **3 cách** để visualize LangGraph workflow:

### 1. 🖼️ Xem dưới dạng PNG (Khuyên dùng)

```bash
cd finx-ai-service
python visualize_sql_graph.py
open sql_graph.png
```

File PNG `sql_graph.png` sẽ được tạo ra và tự động mở.

### 2. 📊 Xem trên Mermaid.live (Online)

```bash
python visualize_sql_graph.py
```

Script sẽ in ra Mermaid code. Copy code đó và paste vào https://mermaid.live để xem interactive diagram.

### 3. 📝 Xem dưới dạng text

Script cũng sẽ in ra:
- Danh sách nodes
- Danh sách edges (connections)
- Flow description

---

## Chi tiết các cách visualize

### Cách 1: Sử dụng script có sẵn

```bash
# Đã có sẵn script visualize_sql_graph.py
python visualize_sql_graph.py
```

Output:
- **Mermaid Diagram**: Copy/paste vào mermaid.live
- **PNG Image**: Saved to `sql_graph.png`
- **Text Structure**: Nodes và Edges
- **Flow Description**: Mô tả luồng

### Cách 2: Tự viết code visualize

```python
from src.workflows.sql_processing.graph import create_sql_processing_graph

# Create graph
graph = create_sql_processing_graph()

# Get Mermaid diagram
compiled = graph.compiled_graph
mermaid_code = compiled.get_graph().draw_mermaid()
print(mermaid_code)

# Save PNG
png_bytes = compiled.get_graph().draw_mermaid_png()
with open("my_graph.png", "wb") as f:
    f.write(png_bytes)
```

### Cách 3: Xem trong runtime

Khi chạy workflow, bạn có thể xem state changes:

```python
from src.workflows.sql_processing.graph import create_sql_processing_graph
from src.workflows.sql_processing.state import create_initial_sql_processing_state

# Create graph
graph = create_sql_processing_graph()

# Prepare state
state = create_initial_sql_processing_state(
    query="Show me sales data",
    db_schemas=["CREATE TABLE sales ..."]
)

# Execute with streaming
async for event in graph.compiled_graph.astream(state):
    print(f"Current node: {event}")
    print(f"State: {event}")
```

---

## SQL Processing Graph Flow

Workflow hiện tại:

```
START
  ↓
check_followup_node
  ├─ [Follow-up] → followup_sql_reasoning_node → followup_sql_generation_node
  └─ [New Query] → sql_reasoning_node → sql_generation_node
  
Both merge at:
sql_validation_node
  ├─ [Valid] → sql_tables_extraction_node → sql_question_node → sql_answer_node → format_response_node → END
  ├─ [Invalid] → sql_diagnosis_node → sql_correction_node → (loop back to validation)
  └─ [Max Retries] → sql_regeneration_node → (back to validation)
```

---

## Yêu cầu

### Để tạo PNG image:

```bash
# macOS
brew install graphviz
pip install pygraphviz

# Ubuntu/Debian
sudo apt-get install graphviz graphviz-dev
pip install pygraphviz

# Windows
# Download from: https://graphviz.org/download/
pip install pygraphviz
```

### Để xem Mermaid diagram:

Không cần cài gì, chỉ cần:
1. Copy Mermaid code
2. Mở https://mermaid.live
3. Paste và xem

---

## Troubleshooting

### Lỗi: Node name conflicts with state key

```
ValueError: 'sql_reasoning' is already being used as a state key
```

**Giải pháp**: Node names không được trùng với state keys. Đã fix bằng cách thêm `_node` suffix:
- `sql_reasoning` → `sql_reasoning_node`
- `sql_generation` → `sql_generation_node`
- etc.

### Lỗi: graphviz not installed

```
Could not generate PNG: ...
```

**Giải pháp**: Install graphviz (xem phần Yêu cầu bên trên) hoặc dùng Mermaid.live để xem online.

---

## Các workflow khác

Để visualize workflow khác (ví dụ: Intent Recommendation):

```python
# Create script tương tự
from src.workflows.intent_recommendation.graph import create_intent_recommendation_graph

graph = create_intent_recommendation_graph()
compiled = graph.compiled_graph

# Generate Mermaid
mermaid = compiled.get_graph().draw_mermaid()
print(mermaid)

# Save PNG
png_bytes = compiled.get_graph().draw_mermaid_png()
with open("intent_graph.png", "wb") as f:
    f.write(png_bytes)
```

---

## Tài liệu tham khảo

- LangGraph Docs: https://langchain-ai.github.io/langgraph/
- Mermaid Live Editor: https://mermaid.live
- Graphviz: https://graphviz.org/
