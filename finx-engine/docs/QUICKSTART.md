# Quick Start Guide

This guide will help you get FinX Engine up and running in minutes.

## Option 1: Docker Compose (Recommended)

The easiest way to get started with all components running together.

### Prerequisites

- Docker Desktop or Docker Engine with Docker Compose
- 4GB RAM minimum
- 10GB disk space

### Steps

1. **Clone and navigate to the project**:
```bash
cd finx-engine
```

2. **Start all services**:
```bash
docker-compose up -d
```

This starts:
- PostgreSQL database with sample data (port 5432)
- FinX Engine API (port 8000)
- Web UI (port 3000)

3. **Access the Web UI**:
Open http://localhost:3000 in your browser

4. **Try the sample database**:
The PostgreSQL database is pre-configured with sample data:
- Database: `sample_db`
- User: `finx_user`
- Password: `finx_password`
- Tables: `customers`, `products`, `orders`, `order_items`

In the Web UI:
- Click "Add Data Source"
- Select "PostgreSQL"
- Enter ID: `sample_postgres`
- Host: `postgres` (or `localhost` if connecting from outside Docker)
- Port: `5432`
- Database: `sample_db`
- User: `finx_user`
- Password: `finx_password`
- Schema: `public`
- Click "Add Data Source"

5. **Run introspection**:
- Click the "Play" button on the `sample_postgres` data source
- Wait for introspection to complete
- View the generated MDL

6. **Explore the schema**:
- Click "Explore" to browse tables and columns
- Go to "Schema Explorer" to see the relationship diagram

### Stopping Services

```bash
docker-compose down
```

To remove all data:
```bash
docker-compose down -v
```

## Option 2: Manual Setup

For development or customization.

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL (optional, for testing)

### Backend Setup

1. **Install Python dependencies**:
```bash
cd finx-engine
pip install -r requirements.txt
```

2. **Start the API server**:
```bash
python api/main.py
```

The API will be available at http://localhost:8000

### Frontend Setup

1. **Install Node.js dependencies**:
```bash
cd web-ui
npm install
```

2. **Start the development server**:
```bash
npm run dev
```

The UI will be available at http://localhost:3000

### Testing with DuckDB

DuckDB is perfect for quick testing without external databases:

```python
from src.connectors import ConnectorFactory, DataSourceConfig

config = DataSourceConfig(
    datasource_id="test_duckdb",
    datasource_type="duckdb",
    connection_params={
        "database_path": ":memory:"
    }
)

connector = ConnectorFactory.create_connector(config)
connector.connect()

connector.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name VARCHAR)")
connector.execute("INSERT INTO users VALUES (1, 'Alice'), (2, 'Bob')")

tables = connector.get_tables()
print(tables)

connector.disconnect()
```

## Option 3: API Only

If you only need the REST API without the UI.

### Using Docker

```bash
docker build -f docker/Dockerfile.api -t finx-engine-api .
docker run -p 8000:8000 finx-engine-api
```

### Using Python

```bash
pip install -r requirements.txt
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

### Test the API

```bash
curl http://localhost:8000/health

curl -X POST http://localhost:8000/api/v1/datasources \
  -H "Content-Type: application/json" \
  -d '{
    "datasource_id": "test_duckdb",
    "datasource_type": "duckdb",
    "connection_params": {
      "database_path": ":memory:"
    }
  }'

curl http://localhost:8000/api/v1/datasources
```

## Next Steps

### Connect to AWS Athena

See [AWS Setup Guide](AWS_SETUP.md) for detailed instructions on:
- Configuring AWS credentials
- Setting up Athena
- Configuring S3 buckets
- IAM permissions

### Integrate with FinX AI Service

See [Integration Guide](INTEGRATION.md) for:
- Setting up the indexing pipeline
- Configuring vector database
- Running end-to-end workflows

### Explore the API

Visit http://localhost:8000/docs for interactive API documentation with:
- All available endpoints
- Request/response schemas
- Try-it-out functionality

### Customize Connectors

Create custom connectors by extending `BaseConnector`:

```python
from src.connectors.base import BaseConnector, DataSourceConfig

class MyCustomConnector(BaseConnector):
    def connect(self):
        pass
    
    def get_schemas(self):
        pass
    
    def get_tables(self, schema=None):
        pass
    
    def get_columns(self, table_name, schema=None):
        pass
    
    def get_primary_keys(self, table_name, schema=None):
        pass
    
    def get_foreign_keys(self, table_name, schema=None):
        pass
    
    def disconnect(self):
        pass
```

Register your connector:

```python
from src.connectors.factory import ConnectorRegistry

ConnectorRegistry.register("mycustom", MyCustomConnector)
```

## Troubleshooting

### Port Already in Use

If ports 3000, 5432, or 8000 are already in use, modify `docker-compose.yml`:

```yaml
services:
  api:
    ports:
      - "8001:8000"
  ui:
    ports:
      - "3001:80"
  postgres:
    ports:
      - "5433:5432"
```

### Connection Refused

If the UI can't connect to the API:
1. Check that the API is running: `curl http://localhost:8000/health`
2. Check CORS settings in `api/config.py`
3. Check browser console for errors

### Database Connection Failed

For PostgreSQL:
1. Verify the database is running
2. Check credentials
3. Ensure the database exists
4. Check firewall rules

For Athena:
1. Verify AWS credentials
2. Check IAM permissions
3. Verify S3 bucket access
4. Check Athena workgroup settings

## Getting Help

- API Documentation: http://localhost:8000/docs
- Project Documentation: See `docs/` directory
- Issues: Create an issue on GitHub

