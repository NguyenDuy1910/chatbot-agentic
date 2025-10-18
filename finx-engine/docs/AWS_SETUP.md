# AWS Setup Guide for FinX Engine

This guide provides step-by-step instructions for setting up AWS services required by FinX Engine.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [AWS Athena Setup](#aws-athena-setup)
3. [S3 Configuration](#s3-configuration)
4. [IAM Permissions](#iam-permissions)
5. [AWS Credentials Configuration](#aws-credentials-configuration)
6. [Testing the Setup](#testing-the-setup)

---

## Prerequisites

- AWS Account with appropriate permissions
- AWS CLI installed and configured (optional but recommended)
- Python 3.8+ installed
- FinX Engine installed (`pip install -r requirements.txt`)

---

## AWS Athena Setup

### 1. Create an Athena Database

**Using AWS Console:**

1. Navigate to AWS Athena console
2. Click "Query editor"
3. Run the following SQL to create a database:

```sql
CREATE DATABASE IF NOT EXISTS my_database
COMMENT 'Database for FinX Engine introspection';
```

**Using AWS CLI:**

```bash
aws athena start-query-execution \
  --query-string "CREATE DATABASE IF NOT EXISTS my_database" \
  --result-configuration "OutputLocation=s3://my-bucket/athena-results/" \
  --region us-east-1
```

### 2. Create Sample Tables (Optional)

Create sample tables for testing:

```sql
-- Customers table
CREATE EXTERNAL TABLE IF NOT EXISTS my_database.customers (
  customer_id INT,
  name STRING,
  email STRING,
  country STRING,
  created_at TIMESTAMP
)
STORED AS PARQUET
LOCATION 's3://my-bucket/data/customers/';

-- Orders table
CREATE EXTERNAL TABLE IF NOT EXISTS my_database.orders (
  order_id INT,
  customer_id INT,
  order_date TIMESTAMP,
  total_amount DECIMAL(10,2),
  status STRING
)
STORED AS PARQUET
LOCATION 's3://my-bucket/data/orders/';
```

### 3. Configure Athena Workgroup

**Using AWS Console:**

1. Go to Athena → Workgroups
2. Create a new workgroup or use "primary"
3. Configure query result location: `s3://my-bucket/athena-results/`
4. Enable query result encryption (optional but recommended)

**Using AWS CLI:**

```bash
aws athena create-work-group \
  --name finx-engine-workgroup \
  --configuration "ResultConfigurationUpdates={OutputLocation=s3://my-bucket/athena-results/}" \
  --region us-east-1
```

---

## S3 Configuration

### 1. Create S3 Bucket for Athena Results

```bash
# Create bucket
aws s3 mb s3://my-bucket --region us-east-1

# Create folder for Athena results
aws s3api put-object \
  --bucket my-bucket \
  --key athena-results/
```

### 2. Configure S3 Bucket Policy (Optional)

If you need to restrict access, create a bucket policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AthenaQueryResults",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::YOUR_ACCOUNT_ID:user/YOUR_USER"
      },
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::my-bucket/athena-results/*"
    }
  ]
}
```

### 3. S3 Tables Setup

For S3 Tables (AWS Lake Formation):

1. Navigate to AWS Lake Formation console
2. Register your S3 location
3. Grant permissions to your IAM user/role
4. Create tables using Glue Crawler or manually

---

## IAM Permissions

### Required IAM Policy

Create an IAM policy with the following permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AthenaAccess",
      "Effect": "Allow",
      "Action": [
        "athena:StartQueryExecution",
        "athena:GetQueryExecution",
        "athena:GetQueryResults",
        "athena:StopQueryExecution",
        "athena:GetWorkGroup",
        "athena:ListWorkGroups"
      ],
      "Resource": [
        "arn:aws:athena:*:*:workgroup/*"
      ]
    },
    {
      "Sid": "GlueAccess",
      "Effect": "Allow",
      "Action": [
        "glue:GetDatabase",
        "glue:GetDatabases",
        "glue:GetTable",
        "glue:GetTables",
        "glue:GetPartition",
        "glue:GetPartitions",
        "glue:BatchGetPartition"
      ],
      "Resource": [
        "arn:aws:glue:*:*:catalog",
        "arn:aws:glue:*:*:database/*",
        "arn:aws:glue:*:*:table/*/*"
      ]
    },
    {
      "Sid": "S3Access",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:ListBucket",
        "s3:GetBucketLocation"
      ],
      "Resource": [
        "arn:aws:s3:::my-bucket",
        "arn:aws:s3:::my-bucket/*"
      ]
    },
    {
      "Sid": "LakeFormationAccess",
      "Effect": "Allow",
      "Action": [
        "lakeformation:GetDataAccess"
      ],
      "Resource": "*"
    }
  ]
}
```

### Attach Policy to User/Role

**Using AWS Console:**

1. Go to IAM → Policies
2. Create policy with the JSON above
3. Attach to your IAM user or role

**Using AWS CLI:**

```bash
# Create policy
aws iam create-policy \
  --policy-name FinxEngineAthenaPolicy \
  --policy-document file://policy.json

# Attach to user
aws iam attach-user-policy \
  --user-name YOUR_USER \
  --policy-arn arn:aws:iam::YOUR_ACCOUNT_ID:policy/FinxEngineAthenaPolicy
```

---

## AWS Credentials Configuration

### Option 1: Environment Variables

```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_REGION="us-east-1"
export ATHENA_DATABASE="my_database"
export ATHENA_S3_OUTPUT="s3://my-bucket/athena-results/"
```

### Option 2: .env File

Create a `.env` file in your project root:

```env
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
ATHENA_DATABASE=my_database
ATHENA_S3_OUTPUT=s3://my-bucket/athena-results/
```

### Option 3: AWS CLI Configuration

```bash
aws configure
# Follow prompts to enter:
# - AWS Access Key ID
# - AWS Secret Access Key
# - Default region name
# - Default output format
```

### Option 4: IAM Role (for EC2/ECS)

If running on AWS infrastructure, use IAM roles:

1. Create IAM role with the policy above
2. Attach role to EC2 instance or ECS task
3. No credentials needed in code

---

## Testing the Setup

### 1. Test AWS Credentials

```python
import boto3

# Test credentials
session = boto3.Session(region_name='us-east-1')
glue_client = session.client('glue')

# List databases
response = glue_client.get_databases()
print("Databases:", [db['Name'] for db in response['DatabaseList']])
```

### 2. Test Athena Connection

```python
from pyathena import connect

conn = connect(
    region_name='us-east-1',
    schema_name='my_database',
    s3_staging_dir='s3://my-bucket/athena-results/'
)

cursor = conn.cursor()
cursor.execute("SHOW TABLES")
print("Tables:", cursor.fetchall())
```

### 3. Test FinX Engine

```python
from finx_engine import AWSConfig, AthenaIntrospector

config = AWSConfig(
    region_name="us-east-1",
    database="my_database",
    s3_output_location="s3://my-bucket/athena-results/"
)

introspector = AthenaIntrospector(config)
schema = introspector.introspect()

print(f"Found {len(schema.tables)} tables")
```

---

## Troubleshooting

### Common Issues

**1. Access Denied Errors**
- Verify IAM permissions are correctly configured
- Check S3 bucket policies
- Ensure Lake Formation permissions if using S3 Tables

**2. Query Execution Timeout**
- Increase timeout in PyAthena configuration
- Check Athena query history for errors
- Verify S3 output location is accessible

**3. Table Not Found**
- Verify database name is correct
- Check Glue Data Catalog for table definitions
- Run `SHOW TABLES` in Athena console

**4. Invalid S3 Location**
- Ensure S3 output location starts with `s3://`
- Verify bucket exists and is in the same region
- Check bucket permissions

---

## Next Steps

- See [INTEGRATION.md](INTEGRATION.md) for integrating with FinX AI Service
- Check [examples/](../examples/) for usage examples
- Review [README.md](../README.md) for API documentation

