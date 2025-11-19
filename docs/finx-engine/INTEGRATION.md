# FinX AI Service Integration Guide

This guide explains how to integrate FinX Engine with FinX AI Service for automated schema indexing.

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Setup](#setup)
4. [Basic Integration](#basic-integration)
5. [Advanced Usage](#advanced-usage)
6. [API Reference](#api-reference)

---

## Overview

FinX Engine extracts schema metadata from AWS Athena and generates MDL (Modeling Definition Language) JSON. This MDL is then indexed into FinX AI Service's vector database for AI-powered query generation and analysis.

### Integration Flow

```
AWS Athena → FinX Engine → MDL JSON → FinX AI Service → Vector DB
```

**Steps:**
1. FinX Engine introspects Athena database
2. Generates MDL JSON with tables, columns, relationships
3. FinX AI Service validates and processes MDL
4. Chunks schema into documents
5. Generates embeddings
6. Stores in vector database for AI retrieval

---

## Architecture

### Components

```
┌─────────────────────────────────────────────────────────────┐
│                      FinX Engine                             │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  AthenaIntrospector                                    │ │
│  │  - Connects to AWS Athena                              │ │
│  │  - Extracts table/column metadata                      │ │
│  │  - Detects relationships                               │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  MDLGenerator                                          │ │
│  │  - Converts metadata to MDL JSON                       │ │
│  │  - Supports enrichments (views, metrics)               │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼ MDL JSON
┌─────────────────────────────────────────────────────────────┐
│                   FinX AI Service                            │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  DBSchema Pipeline                                     │ │
│  │  1. MDLValidator - Validates MDL structure             │ │
│  │  2. DDLChunker - Chunks into documents                 │ │
│  │  3. Embedder - Generates vector embeddings             │ │
│  │  4. DocumentWriter - Stores in vector DB               │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## Setup

### 1. Install Dependencies

```bash
# Install FinX Engine
cd finx-engine
pip install -r requirements.txt

# Install FinX AI Service
cd ../finx-ai-service
pip install -r requirements.txt
```

### 2. Configure FinX AI Service

Ensure `finx-ai-service/config.yaml` is properly configured:

```yaml
# Embedder configuration
type: embedder
embedders:
  - provider: google_genai
    name: default
    api_key: ${GOOGLE_API_KEY}
    model: models/embedding-001

---
# Document store configuration
type: document_store
document_stores:
  - provider: qdrant
    name: default
    url: http://localhost:6333
    collection_name: db_schema

---
# Pipeline configuration
type: pipeline
pipes:
  - name: db_schema_indexing
    embedder: google_genai_embedder.default
    document_store: qdrant
```

### 3. Start Required Services

```bash
# Start Qdrant (vector database)
docker run -p 6333:6333 qdrant/qdrant

# Or use docker-compose if available
cd finx-ai-service
docker-compose up -d
```

---

## Basic Integration

### Example 1: Simple Integration

```python
import asyncio
from pathlib import Path

# FinX Engine imports
from finx_engine import AWSConfig, AthenaIntrospector, MDLGenerator

# FinX AI Service imports
import sys
sys.path.insert(0, str(Path(__file__).parent / "finx-ai-service"))

from src.pipelines.indexing.db_schema import DBSchema
from src.providers.google_genai import GoogleGenAIEmbedderProvider
from src.providers.qdrant import QdrantDocumentStoreProvider


async def index_athena_schema():
    # Step 1: Configure AWS
    aws_config = AWSConfig(
        region_name="us-east-1",
        database="my_database",
        s3_output_location="s3://my-bucket/athena-results/"
    )
    
    # Step 2: Introspect Athena
    introspector = AthenaIntrospector(aws_config)
    schema_metadata = introspector.introspect()
    
    # Step 3: Generate MDL
    generator = MDLGenerator()
    mdl = generator.generate(schema_metadata)
    mdl_json = generator.generate_json(schema_metadata)
    
    # Step 4: Configure FinX AI Service pipeline
    embedder_provider = GoogleGenAIEmbedderProvider(
        api_key="your-google-api-key",
        model="models/embedding-001"
    )
    
    document_store_provider = QdrantDocumentStoreProvider(
        url="http://localhost:6333",
        collection_name="db_schema"
    )
    
    db_schema_pipeline = DBSchema(
        embedder_provider=embedder_provider,
        document_store_provider=document_store_provider
    )
    
    # Step 5: Index schema
    result = await db_schema_pipeline.run(
        mdl_str=mdl_json,
        project_id="athena_project_001"
    )
    
    print(f"Indexed {len(mdl['models'])} tables successfully!")
    return result


# Run
asyncio.run(index_athena_schema())
```

### Example 2: Using Integration Helper

```python
import asyncio
from finx_engine.integration import FinxAIIntegration

async def main():
    # Configure integration
    integration = FinxAIIntegration(
        finx_ai_service_path="../finx-ai-service"
    )
    
    # Generate MDL (from previous example)
    # mdl = ...
    
    # Index with pre-configured pipeline
    result = await integration.index_schema_async(
        mdl=mdl,
        db_schema_pipeline=db_schema_pipeline,
        project_id="my_project"
    )
    
    print(f"Indexing complete: {result}")

asyncio.run(main())
```

---

## Advanced Usage

### 1. Enriching MDL Before Indexing

```python
# Generate base MDL
mdl = generator.generate(schema_metadata)

# Define enrichments
enrichments = {
    "models": [
        {
            "name": "customers",
            "properties": {
                "displayName": "Customer Master Data",
                "description": "Complete customer information"
            },
            "columns": [
                {
                    "name": "customer_id",
                    "properties": {
                        "description": "Unique customer identifier"
                    }
                }
            ]
        }
    ],
    "views": [
        {
            "name": "customer_summary",
            "properties": {"description": "Customer summary view"},
            "statement": "SELECT customer_id, COUNT(*) FROM orders GROUP BY customer_id"
        }
    ],
    "metrics": [
        {
            "name": "total_revenue",
            "baseObject": "orders",
            "dimension": [{"name": "customer_id", "type": "INTEGER"}],
            "measure": [{
                "name": "revenue",
                "type": "DECIMAL",
                "expression": "SUM(total_amount)"
            }]
        }
    ]
}

# Enrich MDL
enriched_mdl = generator.enrich_mdl(mdl, enrichments)

# Index enriched MDL
mdl_json = json.dumps(enriched_mdl)
result = await db_schema_pipeline.run(mdl_str=mdl_json, project_id="my_project")
```

### 2. Batch Processing Multiple Databases

```python
async def index_multiple_databases():
    databases = ["sales_db", "analytics_db", "customer_db"]
    
    for db_name in databases:
        # Configure for this database
        config = AWSConfig(
            database=db_name,
            s3_output_location="s3://my-bucket/athena-results/"
        )
        
        # Introspect and generate MDL
        introspector = AthenaIntrospector(config)
        schema = introspector.introspect()
        
        generator = MDLGenerator()
        mdl_json = generator.generate_json(schema)
        
        # Index with database-specific project ID
        await db_schema_pipeline.run(
            mdl_str=mdl_json,
            project_id=f"athena_{db_name}"
        )
        
        print(f"Indexed {db_name}")
```

### 3. Incremental Updates

```python
async def update_schema():
    # Clean existing documents for project
    await db_schema_pipeline.clean(project_id="my_project")
    
    # Re-introspect and index
    schema = introspector.introspect()
    mdl_json = generator.generate_json(schema)
    
    await db_schema_pipeline.run(
        mdl_str=mdl_json,
        project_id="my_project"
    )
```

---

## API Reference

### FinxAIIntegration

```python
class FinxAIIntegration:
    def __init__(self, finx_ai_service_path: Optional[str] = None)
    
    async def index_schema_async(
        self,
        mdl: Dict[str, Any],
        db_schema_pipeline,
        project_id: Optional[str] = None
    ) -> Dict[str, Any]
    
    def save_mdl(self, mdl: Dict[str, Any], output_path: str) -> None
    
    def load_mdl(self, input_path: str) -> Dict[str, Any]
```

### Convenience Function

```python
async def index_athena_schema(
    aws_config: Dict[str, Any],
    db_schema_pipeline,
    project_id: Optional[str] = None,
    tables: Optional[list] = None,
    enrichments: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]
```

---

## Troubleshooting

### Issue: Import Error from finx-ai-service

**Solution:** Ensure the path to finx-ai-service is correct:

```python
integration = FinxAIIntegration(
    finx_ai_service_path="/absolute/path/to/finx-ai-service"
)
```

### Issue: MDL Validation Failed

**Solution:** Check MDL structure matches expected format:

```python
# Required MDL structure
{
    "models": [...],      # Required
    "relationships": [...],  # Required
    "views": [...],       # Required (can be empty)
    "metrics": [...]      # Required (can be empty)
}
```

### Issue: Vector DB Connection Failed

**Solution:** Verify Qdrant is running:

```bash
docker ps | grep qdrant
curl http://localhost:6333/collections
```

---

## Next Steps

- See [AWS_SETUP.md](AWS_SETUP.md) for AWS configuration
- Check [examples/](../examples/) for more examples
- Review FinX AI Service documentation for advanced pipeline configuration

