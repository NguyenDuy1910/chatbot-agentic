# Athena Test JSON Payloads

This document provides example JSON payloads for testing AWS Athena connector via the API.

## Table of Contents
1. [Create Datasource](#create-datasource)
2. [Test Connection](#test-connection)
3. [Introspection](#introspection)
4. [Configuration Examples](#configuration-examples)

---

## Create Datasource

### Endpoint
```
POST /api/datasources
```

### Example 1: Basic Athena Configuration (Using IAM Role)
```json
{
  "name": "athena-sales-data",
  "type": "athena",
  "host": "",
  "port": 443,
  "database": "sales_database",
  "username": "",
  "password": "",
  "schema": null,
  "extra_params": {
    "aws_region": "us-east-1",
    "s3_staging_dir": "s3://my-athena-query-results/staging/",
    "catalog_name": "AwsDataCatalog",
    "work_group": "primary"
  }
}
```

### Example 2: Athena with Explicit AWS Credentials
```json
{
  "name": "athena-analytics",
  "type": "athena",
  "host": "",
  "port": 443,
  "database": "analytics_db",
  "username": "",
  "password": "",
  "schema": null,
  "extra_params": {
    "aws_region": "us-west-2",
    "s3_staging_dir": "s3://athena-results-bucket/output/",
    "catalog_name": "AwsDataCatalog",
    "work_group": "analytics-workgroup",
    "aws_access_key_id": "AKIAIOSFODNN7EXAMPLE",
    "aws_secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
  }
}
```

### Example 3: Athena with Temporary Credentials (Session Token)
```json
{
  "name": "athena-temp-access",
  "type": "athena",
  "host": "",
  "port": 443,
  "database": "temp_database",
  "username": "",
  "password": "",
  "schema": null,
  "extra_params": {
    "aws_region": "eu-west-1",
    "s3_staging_dir": "s3://temp-athena-results/queries/",
    "catalog_name": "AwsDataCatalog",
    "work_group": "primary",
    "aws_access_key_id": "ASIAIOSFODNN7EXAMPLE",
    "aws_secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    "aws_session_token": "FwoGZXIvYXdzEBYaDHExNjE0MjM1NjY5OSKSAQsD..."
  }
}
```

### Example 4: Custom Glue Catalog
```json
{
  "name": "athena-custom-catalog",
  "type": "athena",
  "host": "",
  "port": 443,
  "database": "custom_db",
  "username": "",
  "password": "",
  "schema": null,
  "extra_params": {
    "aws_region": "ap-southeast-1",
    "s3_staging_dir": "s3://custom-catalog-results/output/",
    "catalog_name": "CustomGlueCatalog",
    "work_group": "custom-workgroup"
  }
}
```

### Example 5: Multi-Region Setup
```json
{
  "name": "athena-cross-region",
  "type": "athena",
  "host": "",
  "port": 443,
  "database": "global_data",
  "username": "",
  "password": "",
  "schema": null,
  "extra_params": {
    "aws_region": "us-east-1",
    "s3_staging_dir": "s3://global-athena-staging/region-us-east-1/",
    "catalog_name": "AwsDataCatalog",
    "work_group": "global-analytics"
  }
}
```

---

## Test Connection

### Endpoint
```
POST /api/datasources/{datasource_id}/test
```

### Request
No body required - just call the endpoint with the datasource ID.

### Expected Response (Success)
```json
{
  "status": "connected",
  "message": "Connection successful to Athena database 'sales_database'",
  "latency_ms": 1234.56
}
```

### Expected Response (Failure)
```json
{
  "status": "failed",
  "message": "Connection failed: s3_staging_dir is required in extra_params for Athena",
  "latency_ms": null
}
```

---

## Introspection

### Endpoint
```
POST /api/introspection/{datasource_id}
```

### Example 1: Full Introspection
```json
{
  "schema_name": null,
  "tables": null,
  "detect_relationships": true,
  "detect_primary_keys": true
}
```

### Example 2: Specific Tables Only
```json
{
  "schema_name": "sales_schema",
  "tables": ["orders", "customers", "products"],
  "detect_relationships": true,
  "detect_primary_keys": true
}
```

### Example 3: No Relationship Detection
```json
{
  "schema_name": null,
  "tables": null,
  "detect_relationships": false,
  "detect_primary_keys": false
}
```

---

## Configuration Examples

### Minimal Required Configuration
```json
{
  "name": "athena-minimal",
  "type": "athena",
  "database": "my_database",
  "extra_params": {
    "aws_region": "us-east-1",
    "s3_staging_dir": "s3://my-bucket/athena-results/"
  }
}
```

### Full Configuration with All Options
```json
{
  "name": "athena-full-config",
  "type": "athena",
  "host": "",
  "port": 443,
  "database": "production_database",
  "username": "",
  "password": "",
  "schema": "public",
  "extra_params": {
    "aws_region": "us-east-1",
    "s3_staging_dir": "s3://prod-athena-results/queries/",
    "catalog_name": "AwsDataCatalog",
    "work_group": "production-workgroup",
    "aws_access_key_id": "AKIAIOSFODNN7EXAMPLE",
    "aws_secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    "aws_session_token": "temporary-session-token-here"
  }
}
```

---

## Update Datasource

### Endpoint
```
PUT /api/datasources/{datasource_id}
```

### Example: Update S3 Staging Directory
```json
{
  "extra_params": {
    "aws_region": "us-east-1",
    "s3_staging_dir": "s3://new-athena-bucket/results/",
    "catalog_name": "AwsDataCatalog",
    "work_group": "primary"
  }
}
```

### Example: Update Workgroup
```json
{
  "extra_params": {
    "aws_region": "us-east-1",
    "s3_staging_dir": "s3://my-bucket/results/",
    "catalog_name": "AwsDataCatalog",
    "work_group": "new-workgroup"
  }
}
```

### Example: Switch to IAM Role (Remove Credentials)
```json
{
  "username": "",
  "password": "",
  "extra_params": {
    "aws_region": "us-east-1",
    "s3_staging_dir": "s3://my-bucket/results/",
    "catalog_name": "AwsDataCatalog",
    "work_group": "primary"
  }
}
```

---

## Testing with cURL

### Create Datasource
```bash
curl -X POST http://localhost:8000/api/datasources \
  -H "Content-Type: application/json" \
  -d '{
    "name": "athena-test",
    "type": "athena",
    "host": "",
    "port": 443,
    "database": "my_database",
    "username": "",
    "password": "",
    "extra_params": {
      "aws_region": "us-east-1",
      "s3_staging_dir": "s3://my-bucket/athena-results/"
    }
  }'
```

### Test Connection
```bash
curl -X POST http://localhost:8000/api/datasources/athena-test/test
```

### Run Introspection
```bash
curl -X POST http://localhost:8000/api/introspection/athena-test \
  -H "Content-Type: application/json" \
  -d '{
    "detect_relationships": true,
    "detect_primary_keys": true
  }'
```

### Get MDL
```bash
curl -X GET http://localhost:8000/api/mdl/athena-test
```

### List All Datasources
```bash
curl -X GET http://localhost:8000/api/datasources
```

---

## Testing with Python Requests

```python
import requests

BASE_URL = "http://localhost:8000/api"

# Create datasource
payload = {
    "name": "athena-python-test",
    "type": "athena",
    "host": "",
    "port": 443,
    "database": "my_database",
    "username": "",
    "password": "",
    "extra_params": {
        "aws_region": "us-east-1",
        "s3_staging_dir": "s3://my-bucket/athena-results/",
        "catalog_name": "AwsDataCatalog",
        "work_group": "primary"
    }
}

response = requests.post(f"{BASE_URL}/datasources", json=payload)
print(f"Create Response: {response.json()}")

datasource_id = response.json()["id"]

# Test connection
test_response = requests.post(f"{BASE_URL}/datasources/{datasource_id}/test")
print(f"Test Response: {test_response.json()}")

# Run introspection
introspect_payload = {
    "detect_relationships": True,
    "detect_primary_keys": True
}
introspect_response = requests.post(
    f"{BASE_URL}/introspection/{datasource_id}",
    json=introspect_payload
)
print(f"Introspection Response: {introspect_response.json()}")

# Get MDL
mdl_response = requests.get(f"{BASE_URL}/mdl/{datasource_id}")
print(f"MDL Response: {mdl_response.json()}")
```

---

## Common Issues and Solutions

### Issue 1: Missing S3 Staging Directory
**Error**: `s3_staging_dir is required in extra_params for Athena`

**Solution**: Always include `s3_staging_dir` in `extra_params`:
```json
{
  "extra_params": {
    "s3_staging_dir": "s3://your-bucket/path/"
  }
}
```

### Issue 2: Invalid AWS Credentials
**Error**: `Connection failed: Unable to locate credentials`

**Solution**: Either provide credentials in `extra_params` or ensure IAM role is attached to your EC2/ECS instance.

### Issue 3: S3 Access Denied
**Error**: `Access Denied (Service: Amazon S3; Status Code: 403)`

**Solution**: Ensure your AWS credentials/IAM role has permissions:
- `s3:PutObject` on the S3 staging directory
- `s3:GetObject` on query results
- `athena:StartQueryExecution`
- `athena:GetQueryExecution`
- `glue:GetTable`, `glue:GetDatabase` for Glue Catalog

### Issue 4: Workgroup Not Found
**Error**: `Workgroup 'my-workgroup' not found`

**Solution**: Verify workgroup exists or use `"primary"` (default):
```json
{
  "extra_params": {
    "work_group": "primary"
  }
}
```

---

## IAM Policy Example

For Athena access, your IAM role/user needs these permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "athena:StartQueryExecution",
        "athena:GetQueryExecution",
        "athena:GetQueryResults",
        "athena:StopQueryExecution",
        "athena:GetWorkGroup"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetBucketLocation",
        "s3:GetObject",
        "s3:ListBucket",
        "s3:PutObject"
      ],
      "Resource": [
        "arn:aws:s3:::your-athena-bucket",
        "arn:aws:s3:::your-athena-bucket/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "glue:GetDatabase",
        "glue:GetTable",
        "glue:GetPartitions"
      ],
      "Resource": "*"
    }
  ]
}
```

---

## Notes

1. **Host and Port**: Not required for Athena but can be set to empty string and 443 respectively
2. **Username/Password**: Not required for Athena when using IAM authentication
3. **AWS Region**: Must match the region where your Athena workgroup exists
4. **S3 Staging Directory**: Required - this is where Athena stores query results
5. **Catalog Name**: Defaults to "AwsDataCatalog" if not specified
6. **Work Group**: Defaults to "primary" if not specified
7. **Primary Keys**: Athena tables typically don't have primary keys; the connector returns partition columns as a proxy
8. **Foreign Keys**: Athena doesn't support foreign keys, so this will always return an empty list
