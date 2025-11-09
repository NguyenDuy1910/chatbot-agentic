# Schema Builder - Quick Reference Card

## 🚀 Installation
No installation needed! Already in your project at:
```
finx-ai-service/src/utils/schema_builder.py
```

## 📦 Import

```python
# Quick functions
from src.utils import build_ddl_from_json, get_table_info

# Full builder
from src.utils import SchemaBuilder

# Everything
from src.utils import (
    SchemaBuilder,
    ColumnSchema,
    TableSchema,
    build_ddl_from_json,
    parse_schema_from_json,
    get_table_info
)
```

## 🎯 Basic Usage (3 Lines!)

```python
from src.utils import build_ddl_from_json

ddl = build_ddl_from_json(your_schema_json, dialect="postgresql")
print(ddl)
```

## 📝 JSON Schema Format

```json
{
  "models": [
    {
      "name": "table_name",
      "columns": [
        {
          "name": "column_name",
          "type": "DATA_TYPE",
          "nullable": true,
          "primary_key": false,
          "unique": false,
          "default": null,
          "auto_increment": false
        }
      ],
      "primaryKey": "id",
      "properties": {
        "displayName": "Display Name",
        "description": "Description"
      }
    }
  ],
  "relationships": [
    {
      "models": ["parent", "child"],
      "condition": "parent.id = child.parent_id",
      "joinType": "ONE_TO_MANY"
    }
  ]
}
```

## 🔧 Common Operations

### Generate DDL
```python
from src.utils import build_ddl_from_json

ddl = build_ddl_from_json(schema, dialect="postgresql")
```

### Parse Schema
```python
from src.utils import SchemaBuilder

builder = SchemaBuilder(dialect="postgresql")
tables = builder.parse_schema(schema_data)
```

### Get Table Info
```python
from src.utils import get_table_info

info = get_table_info(schema, "table_name")
print(info["columns"])
print(info["foreignKeys"])
```

### Generate Documentation
```python
from src.utils import SchemaBuilder

builder = SchemaBuilder()
tables = builder.parse_schema(schema)
docs = builder.build_schema_documentation(tables)
print(docs)  # Markdown format
```

## 💾 Supported Data Types

| Type | Example |
|------|---------|
| Numeric | INTEGER, BIGINT, DECIMAL, FLOAT, DOUBLE |
| String | VARCHAR, CHAR, TEXT |
| Date/Time | DATE, TIME, TIMESTAMP, DATETIME |
| Boolean | BOOLEAN |
| Binary | BYTEA, BLOB |
| Special | JSON, JSONB, UUID |

## 🔗 Supported Dialects

- `postgresql` (default)
- `mysql`
- `sqlite`

## 🎨 Full Example

```python
from src.utils import SchemaBuilder

# Your schema
schema = {
    "models": [
        {
            "name": "customers",
            "columns": [
                {"name": "id", "type": "INTEGER", "auto_increment": True},
                {"name": "email", "type": "VARCHAR", "unique": True, "nullable": False},
                {"name": "name", "type": "VARCHAR"},
                {"name": "created_at", "type": "TIMESTAMP", "default": "CURRENT_TIMESTAMP"}
            ],
            "primaryKey": "id",
            "properties": {
                "displayName": "Customers",
                "description": "Customer information"
            }
        },
        {
            "name": "orders",
            "columns": [
                {"name": "id", "type": "INTEGER", "auto_increment": True},
                {"name": "customer_id", "type": "INTEGER", "nullable": False},
                {"name": "total", "type": "DECIMAL"}
            ],
            "primaryKey": "id"
        }
    ],
    "relationships": [
        {
            "models": ["customers", "orders"],
            "condition": "customers.id = orders.customer_id",
            "joinType": "ONE_TO_MANY"
        }
    ]
}

# Use it
builder = SchemaBuilder(dialect="postgresql")
tables = builder.parse_schema(schema)
ddl = builder.build_ddl(tables, include_comments=True)

print(ddl)
```

## 🏃 Run Examples

```bash
cd finx-ai-service/src/utils
python schema_builder_example.py
```

## 🧪 Run Tests

```bash
cd finx-ai-service/src/utils
python test_schema_builder.py
```

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| `SCHEMA_BUILDER_README.md` | Complete documentation |
| `INTEGRATION_GUIDE.md` | Integration examples |
| `SUMMARY.md` | Implementation summary |
| `QUICK_REFERENCE.md` | This file |
| `schema_builder_example.py` | Working examples |
| `test_schema_builder.py` | Unit tests |

## 🆘 Quick Help

### Problem: Can't import module
```python
# Use correct import path
from src.utils.schema_builder import SchemaBuilder
# OR
from src.utils import SchemaBuilder
```

### Problem: Schema parsing fails
```python
# Check schema has required fields
assert "models" in schema_data
assert len(schema_data["models"]) > 0
```

### Problem: Wrong DDL output
```python
# Specify correct dialect
builder = SchemaBuilder(dialect="postgresql")  # or mysql, sqlite
```

## 🎯 Common Patterns

### Pattern 1: Quick DDL
```python
from src.utils import build_ddl_from_json
ddl = build_ddl_from_json(schema, "postgresql")
```

### Pattern 2: Detailed Processing
```python
from src.utils import SchemaBuilder

builder = SchemaBuilder()
tables = builder.parse_schema(schema)
for name, table in tables.items():
    info = builder.get_table_schema(table)
    print(f"{name}: {len(info['columns'])} columns")
```

### Pattern 3: Multiple Outputs
```python
from src.utils import SchemaBuilder

builder = SchemaBuilder()
tables = builder.parse_schema(schema)

# Get DDL
ddl = builder.build_ddl(tables)

# Get docs
docs = builder.build_schema_documentation(tables)

# Get metadata
metadata = {
    name: builder.get_table_schema(table)
    for name, table in tables.items()
}
```

## ⚡ Performance Tips

1. Parse schema once, reuse tables object
2. Cache DDL output if schema doesn't change
3. Use appropriate dialect for your database

## 🔐 Best Practices

1. ✅ Always specify primary keys
2. ✅ Use meaningful table/column descriptions
3. ✅ Define relationships explicitly
4. ✅ Validate schema before processing
5. ✅ Handle errors gracefully
6. ✅ Log operations for debugging

## 📞 Need More Help?

- 📖 Full docs: `SCHEMA_BUILDER_README.md`
- 🔗 Integration: `INTEGRATION_GUIDE.md`
- 📝 Summary: `SUMMARY.md`
- 💻 Examples: `schema_builder_example.py`
- 🧪 Tests: `test_schema_builder.py`

## 🎉 Quick Win

```python
# Just 3 lines to get started!
from src.utils import build_ddl_from_json

ddl = build_ddl_from_json(your_schema, "postgresql")
print(ddl)  # Done! 🎉
```

---

**Location:** `finx-ai-service/src/utils/`

**Created:** November 2025

**Status:** ✅ Production Ready
