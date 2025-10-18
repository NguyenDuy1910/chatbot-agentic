# FinX Engine API Documentation

Complete REST API reference for FinX Engine.

Base URL: `http://localhost:8000/api/v1`

## Authentication

Currently, the API does not require authentication. This will be added in future versions.

## Data Source Management

### List All Data Sources

```http
GET /datasources
```

**Response:**
```json
[
  {
    "datasource_id": "my_postgres",
    "datasource_type": "postgresql",
    "connection_params": {
      "host": "localhost",
      "port": 5432,
      "database": "mydb",
      "user": "postgres",
      "schema": "public"
    }
  }
]
```

### Create Data Source

```http
POST /datasources
```

**Request Body:**
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

**Response:**
```json
{
  "datasource_id": "my_postgres",
  "datasource_type": "postgresql",
  "connection_params": {
    "host": "localhost",
    "port": 5432,
    "database": "mydb",
    "user": "postgres",
    "schema": "public"
  },
  "status": "connected"
}
```

**Status Codes:**
- `200 OK` - Data source created successfully
- `400 Bad Request` - Invalid request body
- `500 Internal Server Error` - Connection test failed

### Get Data Source

```http
GET /datasources/{datasource_id}
```

**Response:**
```json
{
  "datasource_id": "my_postgres",
  "datasource_type": "postgresql",
  "connection_params": {
    "host": "localhost",
    "port": 5432,
    "database": "mydb",
    "user": "postgres",
    "schema": "public"
  }
}
```

**Status Codes:**
- `200 OK` - Success
- `404 Not Found` - Data source not found

### Delete Data Source

```http
DELETE /datasources/{datasource_id}
```

**Status Codes:**
- `204 No Content` - Successfully deleted
- `404 Not Found` - Data source not found

### Test Connection

```http
GET /datasources/{datasource_id}/test
```

**Response:**
```json
{
  "status": "success",
  "message": "Connection successful"
}
```

**Status Codes:**
- `200 OK` - Connection successful
- `500 Internal Server Error` - Connection failed

## Schema Exploration

### List Schemas

```http
GET /datasources/{datasource_id}/schemas
```

**Response:**
```json
{
  "schemas": ["public", "analytics", "staging"]
}
```

### List Tables

```http
GET /datasources/{datasource_id}/schemas/{schema_name}/tables
```

**Response:**
```json
{
  "tables": ["customers", "orders", "products"]
}
```

### Get Table Details

```http
GET /datasources/{datasource_id}/schemas/{schema_name}/tables/{table_name}
```

**Response:**
```json
{
  "name": "customers",
  "schema": "public",
  "columns": [
    {
      "name": "customer_id",
      "type": "INTEGER",
      "nullable": false,
      "default": null,
      "comment": "Unique customer identifier"
    },
    {
      "name": "email",
      "type": "VARCHAR",
      "nullable": false,
      "default": null,
      "comment": null
    }
  ],
  "primary_keys": ["customer_id"],
  "foreign_keys": [],
  "metadata": {}
}
```

## Introspection

### Run Schema Introspection

```http
POST /datasources/{datasource_id}/introspect
```

**Request Body:**
```json
{
  "schema": "public",
  "tables": ["customers", "orders"],
  "detect_relationships": true,
  "detect_primary_keys": true
}
```

**Parameters:**
- `schema` (optional): Specific schema to introspect. If not provided, introspects all schemas.
- `tables` (optional): Specific tables to introspect. If not provided, introspects all tables.
- `detect_relationships` (default: true): Whether to detect foreign key relationships
- `detect_primary_keys` (default: true): Whether to detect primary keys

**Response:**
```json
{
  "datasource_id": "my_postgres",
  "status": "success",
  "tables_count": 4,
  "relationships_count": 3,
  "mdl_generated": true
}
```

**Status Codes:**
- `200 OK` - Introspection successful
- `404 Not Found` - Data source not found
- `500 Internal Server Error` - Introspection failed

## MDL Operations

### Get MDL

```http
GET /mdl/{datasource_id}
```

**Response:**
```json
{
  "datasource_id": "my_postgres",
  "mdl": {
    "models": [
      {
        "name": "customers",
        "properties": {
          "displayName": "Customers",
          "description": "Table customers"
        },
        "columns": [
          {
            "name": "customer_id",
            "type": "INTEGER",
            "isHidden": false,
            "properties": {
              "description": ""
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
}
```

**Status Codes:**
- `200 OK` - Success
- `404 Not Found` - Data source or MDL not found

### Download MDL

```http
GET /mdl/{datasource_id}/download
```

Downloads the MDL as a JSON file.

**Response:**
- Content-Type: `application/json`
- Content-Disposition: `attachment; filename={datasource_id}_mdl.json`

### Delete MDL

```http
DELETE /mdl/{datasource_id}
```

**Status Codes:**
- `204 No Content` - Successfully deleted
- `404 Not Found` - MDL not found

## Connection Parameters

### PostgreSQL

```json
{
  "host": "localhost",
  "port": 5432,
  "database": "mydb",
  "user": "postgres",
  "password": "password",
  "schema": "public"
}
```

### DuckDB

```json
{
  "database_path": "/path/to/database.db",
  "read_only": false
}
```

Use `:memory:` for in-memory database.

### AWS Athena

```json
{
  "region_name": "us-east-1",
  "database": "my_database",
  "s3_output_location": "s3://my-bucket/athena-results/",
  "catalog": "AwsDataCatalog",
  "workgroup": "primary",
  "aws_access_key_id": "optional",
  "aws_secret_access_key": "optional"
}
```

If AWS credentials are not provided, the connector will use the default credential chain.

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

Common error codes:
- `400 Bad Request` - Invalid request parameters
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error or operation failed

## Examples

### Python

```python
import requests

base_url = "http://localhost:8000/api/v1"

datasource = {
    "datasource_id": "my_db",
    "datasource_type": "postgresql",
    "connection_params": {
        "host": "localhost",
        "port": 5432,
        "database": "mydb",
        "user": "postgres",
        "password": "password"
    }
}

response = requests.post(f"{base_url}/datasources", json=datasource)
print(response.json())

response = requests.post(f"{base_url}/datasources/my_db/introspect", json={
    "detect_relationships": True,
    "detect_primary_keys": True
})
print(response.json())

response = requests.get(f"{base_url}/mdl/my_db")
mdl = response.json()["mdl"]
print(f"Models: {len(mdl['models'])}")
print(f"Relationships: {len(mdl['relationships'])}")
```

### cURL

```bash
curl -X POST http://localhost:8000/api/v1/datasources \
  -H "Content-Type: application/json" \
  -d '{
    "datasource_id": "my_db",
    "datasource_type": "duckdb",
    "connection_params": {
      "database_path": ":memory:"
    }
  }'

curl http://localhost:8000/api/v1/datasources

curl -X POST http://localhost:8000/api/v1/datasources/my_db/introspect \
  -H "Content-Type: application/json" \
  -d '{
    "detect_relationships": true,
    "detect_primary_keys": true
  }'

curl http://localhost:8000/api/v1/mdl/my_db

curl -O -J http://localhost:8000/api/v1/mdl/my_db/download
```

### JavaScript

```javascript
const baseUrl = 'http://localhost:8000/api/v1';

const datasource = {
  datasource_id: 'my_db',
  datasource_type: 'postgresql',
  connection_params: {
    host: 'localhost',
    port: 5432,
    database: 'mydb',
    user: 'postgres',
    password: 'password'
  }
};

const response = await fetch(`${baseUrl}/datasources`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(datasource)
});

const data = await response.json();
console.log(data);

const introspectResponse = await fetch(
  `${baseUrl}/datasources/my_db/introspect`,
  {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      detect_relationships: true,
      detect_primary_keys: true
    })
  }
);

const introspectData = await introspectResponse.json();
console.log(introspectData);
```

