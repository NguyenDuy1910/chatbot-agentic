# 📖 Workflow State Management & Reusable Nodes - Documentation Index

## 🎯 Overview

Hệ thống quản lý state và các node có thể tái sử dụng cho LangGraph workflows, giúp xây dựng workflows nhanh hơn, dễ maintain hơn, và có thể tái sử dụng code.

---

## 📚 Documentation Files

### 1. **Quick Start** 
📄 [`src/core/README.md`](src/core/README.md)
- Quick start guide
- Basic usage examples
- Core concepts overview
- **Đọc đầu tiên nếu bạn là người mới**

### 2. **Complete Guide**
📄 [`docs/WORKFLOW_STATE_AND_NODES_GUIDE.md`](docs/WORKFLOW_STATE_AND_NODES_GUIDE.md)
- Hướng dẫn chi tiết đầy đủ
- Giải thích tất cả components
- Multiple examples
- Best practices
- **Đọc để hiểu sâu về hệ thống**

### 3. **Quick Reference**
📄 [`QUICK_REFERENCE.md`](QUICK_REFERENCE.md)
- Cheat sheet
- Common patterns
- Copy-paste examples
- Tips & tricks
- **Dùng khi code để reference nhanh**

### 4. **Summary**
📄 [`WORKFLOW_STATE_NODES_SUMMARY.md`](WORKFLOW_STATE_NODES_SUMMARY.md)
- Tổng quan những gì đã tạo
- So sánh các approaches
- Migration guide
- Key benefits
- **Đọc để hiểu tổng quan**

### 5. **Architecture Diagram**
📄 [`ARCHITECTURE_DIAGRAM.md`](ARCHITECTURE_DIAGRAM.md)
- Visual diagrams
- Architecture overview
- Flow diagrams
- Component relationships
- **Đọc để hiểu cấu trúc**

### 6. **Examples**
📄 [`examples/workflow_with_reusable_nodes.py`](examples/workflow_with_reusable_nodes.py)
- Complete working examples
- 3 different approaches
- Demo workflows
- **Chạy để xem thực tế**

---

## 🗂️ Source Code Structure

```
src/core/
├── base_state.py          # BaseState class
├── base_graph.py          # BaseGraph class
├── workflow_state.py      # WorkflowState & specialized states ⭐
├── base_nodes.py          # Reusable node classes ⭐
├── node_utils.py          # Decorators & utilities ⭐
├── node_registry.py       # Node registry
└── README.md              # Quick start guide

docs/
└── WORKFLOW_STATE_AND_NODES_GUIDE.md  # Complete guide ⭐

examples/
└── workflow_with_reusable_nodes.py    # Working examples ⭐

Root:
├── WORKFLOW_STATE_NODES_SUMMARY.md    # Summary ⭐
├── QUICK_REFERENCE.md                 # Quick reference ⭐
├── ARCHITECTURE_DIAGRAM.md            # Diagrams ⭐
└── DOCUMENTATION_INDEX.md             # This file
```

**⭐ = Newly created files**

---

## 🚀 Getting Started Path

### For Beginners:
1. 📖 Read [`src/core/README.md`](src/core/README.md) - Quick start
2. 🏃 Run [`examples/workflow_with_reusable_nodes.py`](examples/workflow_with_reusable_nodes.py) - See it work
3. 📚 Read [`docs/WORKFLOW_STATE_AND_NODES_GUIDE.md`](docs/WORKFLOW_STATE_AND_NODES_GUIDE.md) - Learn details
4. 💻 Start building your own workflow

### For Experienced Developers:
1. 📊 Read [`ARCHITECTURE_DIAGRAM.md`](ARCHITECTURE_DIAGRAM.md) - Understand structure
2. 📝 Check [`QUICK_REFERENCE.md`](QUICK_REFERENCE.md) - Copy patterns
3. 🏃 Run examples and start coding

### For Migrating Existing Code:
1. 📄 Read [`WORKFLOW_STATE_NODES_SUMMARY.md`](WORKFLOW_STATE_NODES_SUMMARY.md) - See migration path
2. 📚 Check [`docs/WORKFLOW_STATE_AND_NODES_GUIDE.md`](docs/WORKFLOW_STATE_AND_NODES_GUIDE.md) - Migration section
3. 💻 Gradually refactor your code

---

## 🎓 Learning by Topic

### State Management
- **Quick:** [`src/core/README.md`](src/core/README.md) → "State Management" section
- **Detailed:** [`docs/WORKFLOW_STATE_AND_NODES_GUIDE.md`](docs/WORKFLOW_STATE_AND_NODES_GUIDE.md) → "WorkflowState - State Management"
- **Code:** `src/core/workflow_state.py`

### Base Nodes
- **Quick:** [`QUICK_REFERENCE.md`](QUICK_REFERENCE.md) → "Quick Patterns"
- **Detailed:** [`docs/WORKFLOW_STATE_AND_NODES_GUIDE.md`](docs/WORKFLOW_STATE_AND_NODES_GUIDE.md) → "Base Nodes"
- **Code:** `src/core/base_nodes.py`

### Decorators
- **Quick:** [`QUICK_REFERENCE.md`](QUICK_REFERENCE.md) → "Pattern 2"
- **Detailed:** [`docs/WORKFLOW_STATE_AND_NODES_GUIDE.md`](docs/WORKFLOW_STATE_AND_NODES_GUIDE.md) → "Node Decorators"
- **Code:** `src/core/node_utils.py`

### Routing & Utilities
- **Quick:** [`QUICK_REFERENCE.md`](QUICK_REFERENCE.md) → "Common Routers"
- **Detailed:** [`docs/WORKFLOW_STATE_AND_NODES_GUIDE.md`](docs/WORKFLOW_STATE_AND_NODES_GUIDE.md) → "Utilities & Helpers"
- **Code:** `src/core/node_utils.py`

### Complete Examples
- **File:** [`examples/workflow_with_reusable_nodes.py`](examples/workflow_with_reusable_nodes.py)
- **Run:** `python examples/workflow_with_reusable_nodes.py`

---

## 💡 Use Cases

### Building a New Workflow
1. Read [`src/core/README.md`](src/core/README.md)
2. Check [`QUICK_REFERENCE.md`](QUICK_REFERENCE.md) for patterns
3. Use [`examples/workflow_with_reusable_nodes.py`](examples/workflow_with_reusable_nodes.py) as template

### Debugging a Workflow
1. Check [`QUICK_REFERENCE.md`](QUICK_REFERENCE.md) → "State Fields"
2. Review [`docs/WORKFLOW_STATE_AND_NODES_GUIDE.md`](docs/WORKFLOW_STATE_AND_NODES_GUIDE.md) → "Best Practices"

### Understanding Architecture
1. Read [`ARCHITECTURE_DIAGRAM.md`](ARCHITECTURE_DIAGRAM.md)
2. Read [`WORKFLOW_STATE_NODES_SUMMARY.md`](WORKFLOW_STATE_NODES_SUMMARY.md)

### Refactoring Existing Code
1. Read [`WORKFLOW_STATE_NODES_SUMMARY.md`](WORKFLOW_STATE_NODES_SUMMARY.md) → "Migration Path"
2. Follow patterns in [`docs/WORKFLOW_STATE_AND_NODES_GUIDE.md`](docs/WORKFLOW_STATE_AND_NODES_GUIDE.md)

---

## 🔍 Quick Find

### "How do I...?"

**Create a new workflow?**
→ [`src/core/README.md`](src/core/README.md) → Example 1

**Use LLM in a node?**
→ [`QUICK_REFERENCE.md`](QUICK_REFERENCE.md) → Pattern 1 & 2

**Validate data?**
→ [`QUICK_REFERENCE.md`](QUICK_REFERENCE.md) → Pattern 3

**Add retry logic?**
→ [`QUICK_REFERENCE.md`](QUICK_REFERENCE.md) → Pattern 3
→ [`docs/WORKFLOW_STATE_AND_NODES_GUIDE.md`](docs/WORKFLOW_STATE_AND_NODES_GUIDE.md) → Example 3

**Execute tools?**
→ [`QUICK_REFERENCE.md`](QUICK_REFERENCE.md) → Pattern 4

**Route conditionally?**
→ [`QUICK_REFERENCE.md`](QUICK_REFERENCE.md) → Pattern 5

**Manage state?**
→ [`QUICK_REFERENCE.md`](QUICK_REFERENCE.md) → Pattern 6
→ [`docs/WORKFLOW_STATE_AND_NODES_GUIDE.md`](docs/WORKFLOW_STATE_AND_NODES_GUIDE.md) → "WorkflowState"

**Transform data?**
→ [`QUICK_REFERENCE.md`](QUICK_REFERENCE.md) → Pattern 7

**Parse JSON?**
→ [`QUICK_REFERENCE.md`](QUICK_REFERENCE.md) → Pattern 8

**Create simple nodes?**
→ [`QUICK_REFERENCE.md`](QUICK_REFERENCE.md) → Pattern 9

**See a complete example?**
→ [`QUICK_REFERENCE.md`](QUICK_REFERENCE.md) → Pattern 10
→ [`examples/workflow_with_reusable_nodes.py`](examples/workflow_with_reusable_nodes.py)

---

## 📊 Comparison Table

| Need | Use This | Read This |
|------|----------|-----------|
| Quick start | Base classes or decorators | [`src/core/README.md`](src/core/README.md) |
| Detailed guide | Full documentation | [`docs/WORKFLOW_STATE_AND_NODES_GUIDE.md`](docs/WORKFLOW_STATE_AND_NODES_GUIDE.md) |
| Quick reference | Cheat sheet | [`QUICK_REFERENCE.md`](QUICK_REFERENCE.md) |
| Understanding | Architecture & summary | [`ARCHITECTURE_DIAGRAM.md`](ARCHITECTURE_DIAGRAM.md), [`WORKFLOW_STATE_NODES_SUMMARY.md`](WORKFLOW_STATE_NODES_SUMMARY.md) |
| Practical examples | Working code | [`examples/workflow_with_reusable_nodes.py`](examples/workflow_with_reusable_nodes.py) |

---

## 🎯 Next Steps

1. ✅ **Start with Quick Start**: Read [`src/core/README.md`](src/core/README.md)
2. ✅ **Run Examples**: Execute [`examples/workflow_with_reusable_nodes.py`](examples/workflow_with_reusable_nodes.py)
3. ✅ **Build Your First Workflow**: Use patterns from [`QUICK_REFERENCE.md`](QUICK_REFERENCE.md)
4. ✅ **Deep Dive**: Read [`docs/WORKFLOW_STATE_AND_NODES_GUIDE.md`](docs/WORKFLOW_STATE_AND_NODES_GUIDE.md)
5. ✅ **Refactor Existing Code**: Follow migration guide in [`WORKFLOW_STATE_NODES_SUMMARY.md`](WORKFLOW_STATE_NODES_SUMMARY.md)

---

## 🤝 Contributing

When contributing:
1. Follow existing patterns
2. Update relevant documentation
3. Add examples if needed
4. Update this index if adding new files

---

## 📞 Need Help?

1. Check [`QUICK_REFERENCE.md`](QUICK_REFERENCE.md) first
2. Search in [`docs/WORKFLOW_STATE_AND_NODES_GUIDE.md`](docs/WORKFLOW_STATE_AND_NODES_GUIDE.md)
3. Look at examples in [`examples/workflow_with_reusable_nodes.py`](examples/workflow_with_reusable_nodes.py)
4. Ask your team!

---

**Happy coding! 🚀**
