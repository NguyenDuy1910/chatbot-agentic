# Schema Builder Utility

A comprehensive Python utility for building database schemas and generating DDL statements from JSON metadata.

## Location

`finx-ai-service/src/utils/schema_builder.py`

## Features

- ✅ Parse table schemas from JSON format
- ✅ Generate DDL (Data Definition Language) statements
- ✅ Support for multiple database dialects (PostgreSQL, MySQL, SQLite)
- ✅ Handle table relationships and foreign keys
- ✅ Extract table metadata and schema information
- ✅ Generate human-readable schema documentation
- ✅ Type-safe with dataclasses and enums

## Why This Location?

The `src/utils/` folder is the ideal location because:

1. **Reusability**: Can be imported and used across different services (AI service, workflows, web API)
2. **Utility Nature**: Provides general-purpose schema manipulation functions
3. **No Dependencies**: Works independently without coupling to specific workflows or services
4. **Easy Import**: Simple import path: `from src.utils.schema_builder import SchemaBuilder`

## Installation

No additional dependencies required! Uses only Python standard library.

## Quick Start

### Basic Usage

```python
from src.utils.schema_builder import build_ddl_from_json

# Your schema definition
schema_data = {
    "models": [
        {
            "name": "customers",
            "columns": [
                {"name": "id", "type": "INTEGER"},
                {"name": "email", "type": "VARCHAR"},
                # ... more columns
            ],
            "primaryKey": "id",
            "properties": {
                "displayName": "Customers",
                "description": "Customer information"
            }
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

# Generate DDL
ddl = build_ddl_from_json(schema_data, dialect="postgresql")
print(ddl)
```

### Advanced Usage

```python
from src.utils.schema_builder import SchemaBuilder

# Initialize builder with specific dialect
builder = SchemaBuilder(dialect="postgresql")

# Parse schema
tables = builder.parse_schema(schema_data)

# Generate DDL with options
ddl = builder.build_ddl(
    tables,
    include_comments=True,
    include_if_not_exists=True
)

# Get detailed table information
table_info = builder.get_table_schema(tables["customers"])

# Generate documentation
docs = builder.build_schema_documentation(tables)
```

## Schema JSON Format

### Model Definition

```json
{
  "name": "table_name",
  "columns": [
    {
      "name": "column_name",
      "type": "DATA_TYPE",
      "nullable": true/false,
      "primary_key": true/false,
      "unique": true/false,
      "default": "default_value",
      "comment": "Column description",
      "auto_increment": true/false
    }
  ],
  "primaryKey": "column_name",
  "properties": {
    "displayName": "Display Name",
    "description": "Table description"
  }
}
```

### Relationship Definition

```json
{
  "models": ["parent_table", "child_table"],
  "condition": "parent_table.id = child_table.parent_id",
  "joinType": "ONE_TO_MANY"
}
```

### Supported Join Types

- `ONE_TO_ONE`
- `ONE_TO_MANY`
- `MANY_TO_ONE`
- `MANY_TO_MANY`

### Supported Data Types

**Numeric:**
- `INTEGER`, `BIGINT`, `SMALLINT`
- `DECIMAL`, `NUMERIC`
- `FLOAT`, `DOUBLE`, `REAL`

**String:**
- `VARCHAR`, `CHAR`, `TEXT`

**Date/Time:**
- `DATE`, `TIME`, `TIMESTAMP`, `DATETIME`

**Others:**
- `BOOLEAN`
- `BYTEA`, `BLOB`
- `JSON`, `JSONB`
- `UUID`

## Complete Example

```python
from src.utils.schema_builder import SchemaBuilder

# Complex schema with relationships
schema = {
    "models": [
        {
            "name": "customers",
            "columns": [
                {"name": "id", "type": "INTEGER", "nullable": False, "auto_increment": True},
                {"name": "email", "type": "VARCHAR", "nullable": False, "unique": True},
                {"name": "first_name", "type": "VARCHAR"},
                {"name": "last_name", "type": "VARCHAR"},
                {"name": "created_at", "type": "TIMESTAMP", "default": "CURRENT_TIMESTAMP"}
            ],
            "primaryKey": "id",
            "properties": {
                "displayName": "Customers",
                "description": "Customer information and contact details"
            }
        },
        {
            "name": "orders",
            "columns": [
                {"name": "id", "type": "INTEGER", "nullable": False, "auto_increment": True},
                {"name": "customer_id", "type": "INTEGER", "nullable": False},
                {"name": "order_date", "type": "TIMESTAMP"},
                {"name": "total_amount", "type": "DECIMAL"},
                {"name": "status", "type": "VARCHAR", "default": "pending"}
            ],
            "primaryKey": "id",
            "properties": {
                "displayName": "Orders",
                "description": "Customer orders"
            }
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

# Initialize and use
builder = SchemaBuilder(dialect="postgresql")
tables = builder.parse_schema(schema)
ddl = builder.build_ddl(tables)

print(ddl)
```

**Output:**

```sql
-- Customer information and contact details
CREATE TABLE IF NOT EXISTS customers (
  id SERIAL PRIMARY KEY,
  email VARCHAR NOT NULL UNIQUE,
  first_name VARCHAR,
  last_name VARCHAR,
  created_at TIMESTAMP DEFAULT 'CURRENT_TIMESTAMP',
  CONSTRAINT fk_orders_customer_id FOREIGN KEY (customer_id) REFERENCES customers(id)
);

-- Customer orders
CREATE TABLE IF NOT EXISTS orders (
  id SERIAL PRIMARY KEY,
  customer_id INTEGER NOT NULL,
  order_date TIMESTAMP,
  total_amount DECIMAL,
  status VARCHAR DEFAULT 'pending',
  CONSTRAINT fk_orders_customer_id FOREIGN KEY (customer_id) REFERENCES customers(id)
);
```

## API Reference

### Classes

#### `SchemaBuilder(dialect: str = "postgresql")`

Main class for schema building operations.

**Methods:**
- `parse_schema(schema_data: Dict) -> Dict[str, TableSchema]` - Parse JSON schema to table objects
- `build_ddl(tables: Dict[str, TableSchema], ...) -> str` - Generate DDL statements
- `get_table_schema(table: TableSchema) -> Dict` - Get detailed table information
- `build_schema_documentation(tables: Dict) -> str` - Generate markdown documentation

#### `ColumnSchema`

Represents a column definition.

**Attributes:**
- `name: str` - Column name
- `type: str` - Data type
- `nullable: bool` - Whether column allows NULL
- `primary_key: bool` - Whether column is primary key
- `unique: bool` - Whether column has unique constraint
- `default: Any` - Default value
- `comment: str` - Column description
- `auto_increment: bool` - Auto-increment flag
- `foreign_key: Dict` - Foreign key reference

#### `TableSchema`

Represents a table definition.

**Attributes:**
- `name: str` - Table name
- `columns: List[ColumnSchema]` - List of columns
- `primary_key: str` - Primary key column name
- `properties: Dict` - Table metadata
- `indexes: List[Dict]` - Index definitions

### Convenience Functions

```python
# Quick DDL generation
ddl = build_ddl_from_json(schema_data, dialect="postgresql")

# Parse schema
tables = parse_schema_from_json(schema_data, dialect="postgresql")

# Get table info
info = get_table_info(schema_data, table_name="customers")
```

## Database Dialect Support

The utility automatically adapts DDL generation for different databases:

### PostgreSQL
- Uses `SERIAL` for auto-increment
- Supports `BYTEA` for binary data
- Uses `TIMESTAMP` for datetime

### MySQL
- Uses `AUTO_INCREMENT` for auto-increment
- Uses `BLOB` for binary data
- Supports `DATETIME`

### SQLite
- Converts `VARCHAR` to `TEXT`
- Simplified type system
- Uses `TEXT` for timestamp storage

## Integration Examples

### With LangGraph Workflow

```python
from src.utils.schema_builder import SchemaBuilder

async def schema_extraction_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Extract and build schema for database"""
    
    # Get schema from connection metadata
    schema_data = state.get("connection_metadata", {}).get("schema")
    
    # Build DDL
    builder = SchemaBuilder(dialect="postgresql")
    tables = builder.parse_schema(schema_data)
    ddl = builder.build_ddl(tables)
    
    # Store in state
    state["db_schema_ddl"] = ddl
    state["db_tables"] = {name: table.to_dict() for name, table in tables.items()}
    
    return state
```

### With REST API

```python
from fastapi import APIRouter
from src.utils.schema_builder import build_ddl_from_json, get_table_info

router = APIRouter()

@router.post("/schema/ddl")
async def generate_ddl(schema: dict, dialect: str = "postgresql"):
    """Generate DDL from schema"""
    ddl = build_ddl_from_json(schema, dialect=dialect)
    return {"ddl": ddl}

@router.get("/schema/table/{table_name}")
async def get_table_schema(schema: dict, table_name: str):
    """Get table schema info"""
    info = get_table_info(schema, table_name)
    return info
```

### With Document Store

```python
from src.utils.schema_builder import SchemaBuilder
from src.services.document_store_service import DocumentStoreService

async def index_schema(schema_data: dict, doc_store: DocumentStoreService):
    """Index schema into document store"""
    
    builder = SchemaBuilder()
    tables = builder.parse_schema(schema_data)
    
    # Create documents for each table
    documents = []
    for table_name, table in tables.items():
        doc = {
            "content": builder.get_table_schema(table),
            "metadata": {
                "type": "table_schema",
                "table_name": table_name,
                "columns": len(table.columns)
            }
        }
        documents.append(doc)
    
    # Write to store
    await doc_store.write_documents(documents)
```

## Running Examples

```bash
# Navigate to utils directory
cd finx-ai-service/src/utils

# Run examples
python schema_builder_example.py
```

## Testing

See `schema_builder_example.py` for comprehensive examples covering:
- Simple single-table schemas
- Complex multi-table schemas with relationships
- Multiple database dialects
- Schema documentation generation
- Practical workflow scenarios

## Best Practices

1. **Always specify primary keys** - Helps with relationship mapping
2. **Use meaningful descriptions** - Stored in properties for documentation
3. **Define relationships explicitly** - Ensures foreign keys are created
4. **Validate schema before DDL generation** - Check for missing required fields
5. **Choose appropriate dialect** - Ensures compatibility with target database

## Common Use Cases

1. **Database Migration** - Generate DDL for new database setup
2. **Schema Documentation** - Auto-generate human-readable docs
3. **API Integration** - Expose schema info through REST endpoints
4. **AI/ML Workflows** - Provide schema context to LLM models
5. **Data Validation** - Verify data against schema definitions

## Troubleshooting

**Issue: Foreign keys not created**
- Ensure relationship condition follows format: `parent.col = child.col`
- Check that both tables exist in the schema

**Issue: Type conversion errors**
- Verify data type is in supported types list
- Check dialect-specific type mappings

**Issue: Import errors**
- Ensure you're running from correct directory
- Check Python path includes `finx-ai-service`

## Contributing

When adding new features:
1. Add type hints for all functions
2. Update docstrings
3. Add examples to `schema_builder_example.py`
4. Update this README

## License

Part of the FinX AI Service project.
