# FinX Engine

Multi-Source Data Introspection and MDL Generation Engine with REST API and Web UI

## Overview

FinX Engine is a comprehensive data introspection system similar to Wren Engine's architecture that connects to multiple data sources (AWS Athena, PostgreSQL, DuckDB) and generates structured metadata in MDL (Modeling Definition Language) format. It provides a REST API and modern web interface for managing data sources, exploring schemas, and visualizing relationships.

### Key Features

- **Multi-Source Support**: Connect to AWS Athena (including S3 Tables), PostgreSQL, and DuckDB databases
- **S3 Tables Support**: Full support for AWS S3 Tables catalog with Apache Iceberg format
- **REST API**: FastAPI-based API for programmatic access
- **Web UI**: Modern React interface for schema browsing and visualization
- **Intelligent Relationship Detection**: Automatically detect foreign key relationships
- **Primary Key Detection**: Heuristic-based and constraint-based detection
- **MDL Generation**: Generate Wren-compatible MDL JSON format
- **Schema Visualization**: Interactive relationship diagrams using React Flow
- **Docker Support**: Complete Docker Compose setup for easy deployment
- **FinX AI Service Integration**: Seamless integration with existing indexing pipeline

## Architecture

```
finx-engine/
├── src/
│   ├── connectors/          # Data source connectors
│   │   ├── base.py          # Abstract base connector
│   │   ├── athena.py        # AWS Athena connector
│   │   ├── postgresql.py    # PostgreSQL connector
│   │   ├── duckdb_connector.py  # DuckDB connector
│   │   └── factory.py       # Connector factory and registry
│   ├── introspection/       # Schema introspection logic
│   │   ├── models.py        # Data models for schema metadata
│   │   └── athena_introspector.py  # Introspection engine
│   ├── mdl/                 # MDL generation
│   │   └── generator.py     # MDL JSON generator
│   └── integration/         # FinX AI Service integration
│       └── finx_ai_integration.py
├── api/                     # REST API
│   ├── main.py              # FastAPI application
│   ├── config.py            # API configuration
│   ├── models.py            # Pydantic models
│   ├── storage.py           # Data persistence
│   └── routers/             # API endpoints
│       ├── datasources.py   # Data source management
│       ├── introspection.py # Schema introspection
│       └── mdl.py           # MDL operations
├── web-ui/                  # React Web UI
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── services/        # API client
│   │   └── App.jsx          # Main application
│   ├── package.json
│   └── vite.config.js
├── docker/                  # Docker configuration
│   ├── Dockerfile.api       # API container
│   ├── Dockerfile.ui        # UI container
│   ├── nginx.conf           # Nginx configuration
│   └── init-postgres.sql    # Sample database
├── examples/                # Usage examples
├── docs/                    # Documentation
├── tests/                   # Unit tests
├── docker-compose.yml       # Docker Compose setup
└── requirements.txt         # Python dependencies
```

## Quick Start with Docker

The fastest way to get started is using Docker Compose:

```bash
cd finx-engine
docker-compose up -d
```

This will start:
- **API Server**: http://localhost:8000
- **Web UI**: http://localhost:3000
- **PostgreSQL Sample Database**: localhost:5432

Access the Web UI at http://localhost:3000 to:
1. Add data sources (PostgreSQL, DuckDB, AWS Athena)
2. Browse schemas and tables
3. Run introspection to generate MDL
4. Visualize relationships
5. Download MDL JSON

API documentation available at: http://localhost:8000/docs

## Manual Installation

### Prerequisites

- Python 3.11+
- Node.js 18+ (for Web UI)
- PostgreSQL (optional, for testing)

### Backend Setup

```bash
cd finx-engine
pip install -r requirements.txt

python api/main.py
```

### Frontend Setup

```bash
cd web-ui
npm install
npm run dev
```

## Usage

### 1. Using the Web UI

1. **Add a Data Source**:
   - Click "Add Data Source"
   - Select type (PostgreSQL, DuckDB, or Athena)
   - Enter connection details
   - Test connection

2. **Explore Schema**:
   - Click "Explore" on a data source
   - Browse schemas and tables
   - View column details and relationships

3. **Generate MDL**:
   - Click the "Play" button on a data source
   - Wait for introspection to complete
   - View and download the generated MDL

4. **Visualize Relationships**:
   - Go to "Schema Explorer"
   - Select a data source and schema
   - View interactive relationship diagram

### 2. Using the REST API

```python
import requests

api_url = "http://localhost:8000/api/v1"

datasource = {
    "datasource_id": "my_postgres",
    "datasource_type": "postgresql",
    "connection_params": {
        "host": "localhost",
        "port": 5432,
        "database": "sample_db",
        "user": "finx_user",
        "password": "finx_password",
        "schema": "public"
    }
}

response = requests.post(f"{api_url}/datasources", json=datasource)
print(response.json())

introspection = {
    "detect_relationships": True,
    "detect_primary_keys": True
}

response = requests.post(
    f"{api_url}/datasources/my_postgres/introspect",
    json=introspection
)
print(response.json())

response = requests.get(f"{api_url}/mdl/my_postgres")
mdl = response.json()["mdl"]
print(f"Found {len(mdl['models'])} tables")
```

### 3. Using Python SDK

```python
from src.connectors import ConnectorFactory, DataSourceConfig
from src.mdl.generator import MDLGenerator

config = DataSourceConfig(
    datasource_id="my_db",
    datasource_type="postgresql",
    connection_params={
        "host": "localhost",
        "port": 5432,
        "database": "sample_db",
        "user": "finx_user",
        "password": "finx_password"
    }
)

connector = ConnectorFactory.create_connector(config)
connector.connect()

tables = connector.get_tables()
print(f"Found {len(tables)} tables")

connector.disconnect()
```

## API Endpoints

### Data Sources

- `GET /api/v1/datasources` - List all data sources
- `POST /api/v1/datasources` - Create new data source
- `GET /api/v1/datasources/{id}` - Get data source details
- `DELETE /api/v1/datasources/{id}` - Delete data source
- `GET /api/v1/datasources/{id}/test` - Test connection
- `GET /api/v1/datasources/{id}/schemas` - List schemas
- `GET /api/v1/datasources/{id}/schemas/{schema}/tables` - List tables
- `GET /api/v1/datasources/{id}/schemas/{schema}/tables/{table}` - Get table details

### Introspection

- `POST /api/v1/datasources/{id}/introspect` - Run schema introspection

### MDL

- `GET /api/v1/mdl/{id}` - Get generated MDL
- `GET /api/v1/mdl/{id}/download` - Download MDL as JSON file
- `DELETE /api/v1/mdl/{id}` - Delete MDL

Full API documentation: http://localhost:8000/docs

## Supported Data Sources

### PostgreSQL

```json
{
  "datasource_id": "my_postgres",
  "datasource_type": "postgresql",
  "connection_params": {
    "host": "localhost",
    "port": 5432,
    "database": "mydb",
    "user": "postgres",
    "password": "password",
    "schema": "public"
  }
}
```

### DuckDB

```json
{
  "datasource_id": "my_duckdb",
  "datasource_type": "duckdb",
  "connection_params": {
    "database_path": "/path/to/database.db",
    "read_only": false
  }
}
```

### AWS Athena (Glue Data Catalog)

```json
{
  "datasource_id": "my_athena",
  "datasource_type": "athena",
  "connection_params": {
    "region_name": "us-east-1",
    "database": "my_database",
    "s3_output_location": "s3://bucket/path/",
    "catalog": "AwsDataCatalog",
    "workgroup": "primary",
    "aws_access_key_id": "AKIAIOSFODNN7EXAMPLE",
    "aws_secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
  }
}
```

### AWS Athena (S3 Tables Catalog)

```json
{
  "datasource_id": "my_s3tables",
  "datasource_type": "athena",
  "connection_params": {
    "region_name": "us-east-1",
    "database": "my_namespace",
    "s3_output_location": "s3://bucket/path/",
    "catalog": "my-s3tables-catalog",
    "workgroup": "primary"
  }
}
```

**Note**: S3 Tables support is automatically detected based on catalog name. See [S3 Tables Documentation](docs/S3_TABLES_SUPPORT.md) for details.

## Examples

The `examples/` directory contains comprehensive examples:

- **`athena_introspection.py`**: Basic Athena introspection examples
- **`finx_ai_integration.py`**: Integration with FinX AI Service
- **`end_to_end_example.py`**: Complete end-to-end workflow

Run examples:

```bash
cd examples
python athena_introspection.py
python end_to_end_example.py
```

## Documentation

- **[AWS Setup Guide](docs/AWS_SETUP.md)**: Detailed AWS configuration instructions
  - Athena setup
  - S3 configuration
  - IAM permissions
  - Credentials management

- **[Integration Guide](docs/INTEGRATION.md)**: FinX AI Service integration
  - Architecture overview
  - Setup instructions
  - API reference
  - Advanced usage

## Testing

Run tests:

```bash
cd tests
pytest test_basic.py -v
```

## MDL Format

FinX Engine generates MDL JSON compatible with Wren Engine format:

```json
{
  "models": [
    {
      "name": "customers",
      "properties": {
        "displayName": "Customers",
        "description": "Customer information"
      },
      "columns": [
        {
          "name": "customer_id",
          "type": "INTEGER",
          "isHidden": false,
          "properties": {
            "description": "Unique customer identifier"
          }
        }
      ],
      "primaryKey": "customer_id"
    }
  ],
  "relationships": [
    {
      "name": "orders_customers",
      "models": ["orders", "customers"],
      "joinType": "MANY_TO_ONE",
      "condition": "orders.customer_id = customers.customer_id"
    }
  ],
  "views": [],
  "metrics": []
}
```

## How It Works

### 1. Schema Introspection

FinX Engine connects to AWS Athena using boto3 and PyAthena to extract:
- Table names and descriptions
- Column names, types, and comments
- Primary keys (heuristic-based detection)
- Foreign key relationships (naming convention-based)

### 2. Relationship Detection

Automatically detects relationships using heuristics:
- **Primary Keys**: Columns named `id` or `{table}_id`
- **Foreign Keys**: Columns ending with `_id` that match other table names

### 3. MDL Generation

Converts extracted metadata into Wren-compatible MDL JSON format with:
- Models (tables with columns and properties)
- Relationships (foreign key constraints)
- Views (custom SQL views)
- Metrics (aggregations and calculations)

### 4. Integration

Integrates with FinX AI Service indexing pipeline:
- Validates MDL structure
- Chunks schema into documents
- Generates embeddings
- Stores in vector database

## License

MIT

