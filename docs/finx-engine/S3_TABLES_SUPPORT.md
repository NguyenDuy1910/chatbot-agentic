# AWS S3 Tables Catalog Support

FinX Engine now supports AWS S3 Tables catalog in addition to the standard AWS Glue Data Catalog.

## What is S3 Tables?

AWS S3 Tables is a new storage option optimized for analytics workloads. It provides:
- Apache Iceberg table format support
- Automatic compaction and optimization
- ACID transactions
- Time travel queries
- Schema evolution

## How to Use S3 Tables with FinX Engine

### 1. Prerequisites

- AWS account with S3 Tables enabled
- S3 Tables catalog created
- Athena workgroup configured to use S3 Tables
- Appropriate IAM permissions

### 2. Required IAM Permissions

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3tables:GetTable",
        "s3tables:GetTableBucket",
        "s3tables:GetTableMetadata",
        "s3tables:ListTables",
        "s3tables:ListNamespaces",
        "athena:StartQueryExecution",
        "athena:GetQueryExecution",
        "athena:GetQueryResults",
        "s3:GetObject",
        "s3:PutObject",
        "s3:ListBucket"
      ],
      "Resource": "*"
    }
  ]
}
```

### 3. Connection Configuration

#### Via API

```json
{
  "datasource_id": "my_s3tables",
  "datasource_type": "athena",
  "connection_params": {
    "region_name": "us-east-1",
    "database": "my_namespace",
    "s3_output_location": "s3://my-athena-results/",
    "catalog": "my-s3tables-catalog",
    "workgroup": "primary",
    "aws_access_key_id": "AKIAIOSFODNN7EXAMPLE",
    "aws_secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
  }
}
```

#### Via Web UI

1. Click "Add Data Source"
2. Select "AWS Athena"
3. Fill in the form:
   - **Data Source ID**: `my_s3tables`
   - **Region**: `us-east-1`
   - **Database**: Your S3 Tables namespace (e.g., `my_namespace`)
   - **S3 Output Location**: S3 bucket for query results (e.g., `s3://my-athena-results/`)
   - **Catalog**: Your S3 Tables catalog name (e.g., `my-s3tables-catalog`)
   - **Workgroup**: Athena workgroup (default: `primary`)
   - **AWS Access Key ID**: (Optional) Your AWS access key
   - **AWS Secret Access Key**: (Optional) Your AWS secret key

4. Click "Add Data Source"

### 4. Catalog Detection

FinX Engine automatically detects S3 Tables catalogs based on the catalog name:
- Catalog name contains "s3tables" (case-insensitive)
- Catalog name starts with "s3t_"

Examples of detected S3 Tables catalogs:
- `my-s3tables-catalog`
- `s3tables_production`
- `s3t_analytics`
- `S3TablesDataCatalog`

### 5. Differences from Glue Data Catalog

When using S3 Tables, FinX Engine uses different methods to retrieve metadata:

| Operation | Glue Data Catalog | S3 Tables Catalog |
|-----------|-------------------|-------------------|
| List Schemas | `glue.get_databases()` | `SHOW DATABASES IN catalog` |
| List Tables | `glue.get_tables()` | `SHOW TABLES IN catalog.database` |
| Get Columns | `glue.get_table()` | `DESCRIBE catalog.database.table` |
| Test Connection | `glue.get_database()` | `SHOW DATABASES IN catalog` |

### 6. Example: Complete Workflow

```python
import requests

api_url = "http://localhost:8000"

data_source = {
    "datasource_id": "sales_s3tables",
    "datasource_type": "athena",
    "connection_params": {
        "region_name": "us-west-2",
        "database": "sales_namespace",
        "s3_output_location": "s3://my-query-results/",
        "catalog": "sales-s3tables-catalog",
        "workgroup": "analytics"
    }
}

response = requests.post(f"{api_url}/datasources", json=data_source)
print(f"Data source created: {response.json()}")

introspection_request = {
    "schema": "sales_namespace",
    "detect_relationships": True,
    "detect_primary_keys": True
}

response = requests.post(
    f"{api_url}/datasources/sales_s3tables/introspect",
    json=introspection_request
)
print(f"Introspection complete: {response.json()}")

response = requests.get(f"{api_url}/mdl/sales_s3tables")
mdl = response.json()
print(f"MDL generated with {len(mdl['mdl']['models'])} models")
```

### 7. Limitations

- S3 Tables does not support all Glue Data Catalog features
- Partition information may be limited
- Some metadata fields may not be available
- Foreign key detection is heuristic-based (same as Glue)

### 8. Troubleshooting

#### Connection Fails

**Problem**: Cannot connect to S3 Tables catalog

**Solutions**:
1. Verify catalog name is correct
2. Check IAM permissions include `s3tables:*` actions
3. Ensure Athena workgroup has access to the catalog
4. Verify S3 output location is accessible

#### No Tables Found

**Problem**: `SHOW TABLES` returns empty result

**Solutions**:
1. Verify namespace (database) name is correct
2. Check that tables exist in the namespace
3. Ensure IAM permissions include `s3tables:ListTables`
4. Try listing namespaces first: `SHOW DATABASES IN catalog`

#### Query Execution Errors

**Problem**: Athena queries fail with permission errors

**Solutions**:
1. Add S3 permissions for query results bucket
2. Verify Athena workgroup configuration
3. Check catalog permissions in Athena settings
4. Ensure S3 Tables bucket has correct permissions

### 9. Best Practices

1. **Use Workgroups**: Create dedicated Athena workgroups for S3 Tables
2. **Separate Catalogs**: Keep S3 Tables and Glue catalogs separate
3. **IAM Roles**: Use IAM roles instead of access keys when possible
4. **Query Results**: Use separate S3 buckets for query results
5. **Naming Convention**: Use clear catalog names (e.g., `prod-s3tables`, `analytics-s3t`)

### 10. Resources

- [AWS S3 Tables Documentation](https://docs.aws.amazon.com/s3/latest/userguide/s3-tables.html)
- [Athena S3 Tables Integration](https://docs.aws.amazon.com/athena/latest/ug/s3-tables.html)
- [Apache Iceberg Format](https://iceberg.apache.org/)

