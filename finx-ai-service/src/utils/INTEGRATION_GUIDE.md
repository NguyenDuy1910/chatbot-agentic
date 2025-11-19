# Schema Builder - Integration Guide

## Overview

This guide shows you how to integrate the Schema Builder utility into your existing FinX AI Service workflows.

## File Structure

```
finx-ai-service/src/utils/
├── __init__.py                      # Package initialization
├── schema_builder.py                # Main schema builder module
├── schema_builder_example.py        # Usage examples
├── test_schema_builder.py           # Unit tests
├── SCHEMA_BUILDER_README.md         # Complete documentation
└── INTEGRATION_GUIDE.md             # This file
```

## Quick Integration Steps

### 1. Import the Module

```python
# Option 1: Import specific functions
from src.utils.schema_builder import build_ddl_from_json, get_table_info

# Option 2: Import the main class
from src.utils.schema_builder import SchemaBuilder

# Option 3: Import from package
from src.utils import SchemaBuilder, build_ddl_from_json
```

### 2. Use in Your Workflows

#### Integration with LangGraph Workflow

```python
# File: src/workflows/intent_recommendation/nodes/schema_node.py

from typing import Any, Dict
import logging
from src.utils.schema_builder import SchemaBuilder

logger = logging.getLogger(__name__)

async def schema_processing_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process database schema and generate DDL.
    
    This node extracts schema from connection metadata,
    parses it, and generates DDL statements.
    """
    logger.info("Processing schema...")
    
    try:
        # Get schema data from state
        schema_data = state.get("schema_metadata", {})
        
        # Initialize builder
        builder = SchemaBuilder(dialect="postgresql")
        
        # Parse schema
        tables = builder.parse_schema(schema_data)
        logger.info(f"Parsed {len(tables)} tables")
        
        # Generate DDL
        ddl = builder.build_ddl(tables, include_comments=True)
        
        # Generate documentation
        docs = builder.build_schema_documentation(tables)
        
        # Update state
        state["db_schema_ddl"] = ddl
        state["db_schema_docs"] = docs
        state["db_tables"] = {
            name: builder.get_table_schema(table)
            for name, table in tables.items()
        }
        
        logger.info("Schema processing complete")
        return state
        
    except Exception as e:
        logger.error(f"Error processing schema: {str(e)}")
        state["error"] = str(e)
        return state
```

#### Integration with REST API

```python
# File: src/web/routers/schema.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from src.utils.schema_builder import (
    build_ddl_from_json,
    get_table_info,
    SchemaBuilder
)

router = APIRouter(prefix="/api/schema", tags=["schema"])

class SchemaRequest(BaseModel):
    schema: Dict[str, Any]
    dialect: str = "postgresql"

class DDLResponse(BaseModel):
    ddl: str
    tables: int
    dialect: str

@router.post("/generate-ddl", response_model=DDLResponse)
async def generate_ddl(request: SchemaRequest):
    """Generate DDL from schema definition"""
    try:
        builder = SchemaBuilder(dialect=request.dialect)
        tables = builder.parse_schema(request.schema)
        ddl = builder.build_ddl(tables)
        
        return DDLResponse(
            ddl=ddl,
            tables=len(tables),
            dialect=request.dialect
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/table-info/{table_name}")
async def get_table_information(table_name: str, schema: Dict[str, Any]):
    """Get detailed information about a specific table"""
    try:
        info = get_table_info(schema, table_name)
        if not info:
            raise HTTPException(status_code=404, detail=f"Table {table_name} not found")
        return info
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/documentation")
async def generate_documentation(request: SchemaRequest):
    """Generate markdown documentation for schema"""
    try:
        builder = SchemaBuilder(dialect=request.dialect)
        tables = builder.parse_schema(request.schema)
        docs = builder.build_schema_documentation(tables)
        
        return {"documentation": docs}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

#### Integration with Connection Service

```python
# File: src/services/connection_schema_service.py

import logging
from typing import Dict, Any, Optional
from src.utils.schema_builder import SchemaBuilder
from src.web.models.connections import ConnectionsTable

logger = logging.getLogger(__name__)

class ConnectionSchemaService:
    """Service for managing connection schemas"""
    
    def __init__(self, connections_table: ConnectionsTable):
        self.connections = connections_table
        self.builder = SchemaBuilder()
    
    async def extract_and_store_schema(
        self,
        connection_id: str,
        schema_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract schema from database and store in connection metadata.
        
        Args:
            connection_id: Connection identifier
            schema_data: Raw schema data from database
            
        Returns:
            Processed schema information
        """
        try:
            # Parse schema
            tables = self.builder.parse_schema(schema_data)
            
            # Generate DDL
            ddl = self.builder.build_ddl(tables)
            
            # Prepare metadata
            metadata = {
                "tables": [
                    self.builder.get_table_schema(table)
                    for table in tables.values()
                ],
                "ddl": ddl,
                "table_count": len(tables),
                "column_count": sum(len(t.columns) for t in tables.values())
            }
            
            # Update connection metadata
            connection = self.connections.get_connection_by_id(connection_id)
            if connection:
                connection_metadata = connection.connection_metadata or {}
                connection_metadata["schema"] = metadata
                self.connections.update_connection(
                    connection_id,
                    {"connection_metadata": connection_metadata}
                )
            
            logger.info(f"Schema extracted and stored for connection {connection_id}")
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting schema: {str(e)}")
            raise
    
    def get_table_ddl(
        self,
        connection_id: str,
        table_name: str
    ) -> Optional[str]:
        """Get DDL for specific table"""
        try:
            connection = self.connections.get_connection_by_id(connection_id)
            if not connection:
                return None
            
            schema_data = connection.connection_metadata.get("schema", {})
            tables = self.builder.parse_schema(schema_data)
            
            if table_name in tables:
                return self.builder._build_table_ddl(tables[table_name])
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting table DDL: {str(e)}")
            return None
```

#### Integration with Document Store

```python
# File: src/services/schema_indexing_service.py

import logging
from typing import Dict, Any, List
from src.utils.schema_builder import SchemaBuilder
from src.services.document_store_service import DocumentStoreService

logger = logging.getLogger(__name__)

class SchemaIndexingService:
    """Service for indexing database schemas into document store"""
    
    def __init__(self, doc_store: DocumentStoreService):
        self.doc_store = doc_store
        self.builder = SchemaBuilder()
    
    async def index_schema(
        self,
        connection_id: str,
        schema_data: Dict[str, Any]
    ) -> int:
        """
        Index schema into document store for retrieval.
        
        Args:
            connection_id: Connection identifier
            schema_data: Schema definition
            
        Returns:
            Number of documents indexed
        """
        try:
            # Parse schema
            tables = self.builder.parse_schema(schema_data)
            
            # Create documents for each table
            documents = []
            
            for table_name, table in tables.items():
                # Get detailed table info
                table_info = self.builder.get_table_schema(table)
                
                # Generate DDL for this table
                table_ddl = self.builder._build_table_ddl(table)
                
                # Create document
                doc = {
                    "content": f"""
                    Table: {table_name}
                    Description: {table_info.get('description', '')}
                    
                    DDL:
                    {table_ddl}
                    
                    Columns: {', '.join([col['name'] for col in table_info['columns']])}
                    """,
                    "metadata": {
                        "type": "table_schema",
                        "connection_id": connection_id,
                        "table_name": table_name,
                        "column_count": len(table.columns),
                        "has_foreign_keys": len(table_info.get('foreignKeys', [])) > 0,
                        "table_info": table_info
                    }
                }
                documents.append(doc)
            
            # Index documents
            count = await self.doc_store.write_documents(documents)
            logger.info(f"Indexed {count} table schemas")
            
            return count
            
        except Exception as e:
            logger.error(f"Error indexing schema: {str(e)}")
            raise
    
    async def search_schema(
        self,
        query: str,
        connection_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for tables matching query.
        
        Args:
            query: Search query
            connection_id: Optional connection filter
            
        Returns:
            List of matching table schemas
        """
        filters = {"type": "table_schema"}
        if connection_id:
            filters["connection_id"] = connection_id
        
        results = await self.doc_store.retrieve_documents(
            query=query,
            filters=filters
        )
        
        return results
```

### 3. Usage Examples

#### Example 1: Simple DDL Generation

```python
from src.utils import build_ddl_from_json

# Your schema
schema = {
    "models": [
        {
            "name": "customers",
            "columns": [
                {"name": "id", "type": "INTEGER"},
                {"name": "email", "type": "VARCHAR"}
            ],
            "primaryKey": "id"
        }
    ]
}

# Generate DDL
ddl = build_ddl_from_json(schema, dialect="postgresql")
print(ddl)
```

#### Example 2: Complex Schema with Relationships

```python
from src.utils import SchemaBuilder

schema = {
    "models": [
        {
            "name": "customers",
            "columns": [
                {"name": "id", "type": "INTEGER"},
                {"name": "email", "type": "VARCHAR"}
            ],
            "primaryKey": "id"
        },
        {
            "name": "orders",
            "columns": [
                {"name": "id", "type": "INTEGER"},
                {"name": "customer_id", "type": "INTEGER"}
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

builder = SchemaBuilder(dialect="postgresql")
tables = builder.parse_schema(schema)
ddl = builder.build_ddl(tables)
print(ddl)
```

#### Example 3: Get Table Metadata

```python
from src.utils import get_table_info

info = get_table_info(schema, "customers")
print(f"Table: {info['name']}")
print(f"Columns: {len(info['columns'])}")
print(f"Foreign Keys: {len(info['foreignKeys'])}")
```

## Testing

Run the tests to ensure everything works:

```bash
cd finx-ai-service/src/utils
python test_schema_builder.py
```

Run examples:

```bash
python schema_builder_example.py
```

## Common Patterns

### Pattern 1: Schema Extraction from Database

```python
async def extract_schema_from_db(connection_string: str) -> Dict[str, Any]:
    """Extract schema from actual database"""
    # Use your database connector
    # This is a placeholder example
    
    # Extract tables
    tables_query = "SELECT * FROM information_schema.tables"
    columns_query = "SELECT * FROM information_schema.columns"
    
    # Build schema data structure
    schema_data = {
        "models": [],
        "relationships": []
    }
    
    # ... populate schema_data from database queries ...
    
    return schema_data
```

### Pattern 2: Schema Validation

```python
def validate_schema(schema_data: Dict[str, Any]) -> bool:
    """Validate schema before processing"""
    try:
        builder = SchemaBuilder()
        tables = builder.parse_schema(schema_data)
        
        # Validation checks
        if not tables:
            return False
        
        for table in tables.values():
            if not table.columns:
                return False
            if not table.primary_key:
                logger.warning(f"Table {table.name} has no primary key")
        
        return True
    except Exception as e:
        logger.error(f"Schema validation failed: {str(e)}")
        return False
```

### Pattern 3: Schema Migration

```python
async def migrate_schema(
    old_schema: Dict[str, Any],
    new_schema: Dict[str, Any]
) -> List[str]:
    """Generate migration SQL"""
    builder = SchemaBuilder()
    
    old_tables = builder.parse_schema(old_schema)
    new_tables = builder.parse_schema(new_schema)
    
    migrations = []
    
    # Detect new tables
    for table_name in new_tables:
        if table_name not in old_tables:
            ddl = builder._build_table_ddl(new_tables[table_name])
            migrations.append(ddl)
    
    # Detect dropped tables
    for table_name in old_tables:
        if table_name not in new_tables:
            migrations.append(f"DROP TABLE IF EXISTS {table_name};")
    
    return migrations
```

## Best Practices

1. **Always validate schema data** before processing
2. **Use appropriate dialect** for your target database
3. **Handle errors gracefully** with try-except blocks
4. **Log operations** for debugging
5. **Cache parsed schemas** when possible
6. **Use type hints** for better IDE support

## Troubleshooting

### Issue: Import Error

```python
# Make sure you're importing from the correct path
from src.utils.schema_builder import SchemaBuilder
# OR
from src.utils import SchemaBuilder
```

### Issue: Schema Parsing Fails

```python
# Add validation before parsing
if not schema_data.get("models"):
    logger.error("Schema has no models")
    return None

builder = SchemaBuilder()
tables = builder.parse_schema(schema_data)
```

### Issue: DDL Generation Issues

```python
# Check dialect
builder = SchemaBuilder(dialect="postgresql")  # or mysql, sqlite

# Enable verbose logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Next Steps

1. Review the complete documentation: `SCHEMA_BUILDER_README.md`
2. Run the examples: `schema_builder_example.py`
3. Run the tests: `test_schema_builder.py`
4. Integrate into your workflows
5. Add your own use cases

## Support

For questions or issues:
1. Check the README: `SCHEMA_BUILDER_README.md`
2. Review examples: `schema_builder_example.py`
3. Run tests to verify functionality
4. Check logs for error details
