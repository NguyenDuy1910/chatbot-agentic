# AWS Athena Workgroup Setup Guide

## Problem

You're getting this error:
```
botocore.errorfactory.InvalidRequestException: An error occurred (InvalidRequestException) 
when calling the StartQueryExecution operation: WorkGroup is not found.
```

This means the Athena workgroup specified in your configuration doesn't exist in your AWS account/region.

## Solution

You need to either:
1. Create a new Athena workgroup, OR
2. Use an existing workgroup name

## Option 1: Create a New Athena Workgroup

### Via AWS Console

1. **Go to AWS Athena Console**
   - Navigate to: https://console.aws.amazon.com/athena/
   - Make sure you're in the correct region: **ap-southeast-5** (Jakarta)

2. **Create Workgroup**
   - Click **"Workgroups"** in the left navigation menu
   - Click **"Create workgroup"** button

3. **Configure Workgroup**
   - **Workgroup name**: `s3tables-workgroup` (or any name you prefer)
   - **Description**: "Workgroup for S3 Tables queries"
   - **Query result location**: `s3://s3-bucket-apse5-dev-olap-athena-output/`
   - **Engine version**: Athena engine version 3 (recommended for S3 Tables)
   - Click **"Create workgroup"**

4. **Verify Workgroup**
   - The workgroup should appear in the list with state "ENABLED"

### Via AWS CLI

```bash
aws athena create-work-group \
  --name s3tables-workgroup \
  --configuration "ResultConfigurationUpdates={OutputLocation=s3://s3-bucket-apse5-dev-olap-athena-output/},EngineVersion={SelectedEngineVersion=Athena engine version 3}" \
  --description "Workgroup for S3 Tables queries" \
  --region ap-southeast-5
```

## Option 2: Find Existing Workgroup

### Via AWS Console

1. Go to AWS Athena Console
2. Click "Workgroups" in the left menu
3. Look for any ENABLED workgroups
4. Note the workgroup name

### Via AWS CLI

```bash
aws athena list-work-groups --region ap-southeast-5
```

### Via Python Script

Run the checker script:
```bash
cd finx-engine
python examples/check_athena_workgroups.py
```

This will list all available workgroups and show you the recommended configuration.

## Update Your Configuration

Once you have a workgroup name, update your configuration:

### Option A: Environment Variable (Recommended)

```bash
export ATHENA_WORKGROUP="s3tables-workgroup"
export AWS_REGION="ap-southeast-5"
```

Then run your script:
```bash
python examples/s3tables_introspection.py
```

### Option B: Update Code Directly

```python
config = DataSourceConfig(
    datasource_id="s3tables_example",
    datasource_type="athena",
    connection_params={
        "region_name": "ap-southeast-5",
        "database": "olap_report",
        "s3_output_location": "s3://s3-bucket-apse5-dev-olap-athena-output/",
        "catalog": "s3tables",
        "workgroup": "s3tables-workgroup"  # ← Use your workgroup name
    }
)
```

### Option C: Via Web UI

1. Open http://localhost:3000
2. Click "Add Data Source"
3. Select "AWS Athena"
4. Fill in:
   - **Workgroup**: `s3tables-workgroup` (your workgroup name)
   - **Catalog**: `s3tables`
   - **Database**: `olap_report`
   - **S3 Output Location**: `s3://s3-bucket-apse5-dev-olap-athena-output/`
   - **Region**: `ap-southeast-5`

## AWS Credentials Issue

You're also getting:
```
ExpiredTokenException: The security token included in the request is expired
```

### Fix AWS Credentials

#### Option 1: Refresh AWS SSO Session

If using AWS SSO:
```bash
aws sso login --profile your-profile-name
```

#### Option 2: Set Environment Variables

```bash
export AWS_ACCESS_KEY_ID="your-access-key-id"
export AWS_SECRET_ACCESS_KEY="your-secret-access-key"
export AWS_SESSION_TOKEN="your-session-token"  # If using temporary credentials
export AWS_REGION="ap-southeast-5"
```

#### Option 3: Update ~/.aws/credentials

Edit `~/.aws/credentials`:
```ini
[default]
aws_access_key_id = YOUR_ACCESS_KEY_ID
aws_secret_access_key = YOUR_SECRET_ACCESS_KEY
```

Edit `~/.aws/config`:
```ini
[default]
region = ap-southeast-5
```

#### Option 4: Provide Credentials in Code

```python
config = DataSourceConfig(
    datasource_id="s3tables_example",
    datasource_type="athena",
    connection_params={
        "region_name": "ap-southeast-5",
        "database": "olap_report",
        "s3_output_location": "s3://s3-bucket-apse5-dev-olap-athena-output/",
        "catalog": "s3tables",
        "workgroup": "s3tables-workgroup",
        "aws_access_key_id": "YOUR_ACCESS_KEY_ID",
        "aws_secret_access_key": "YOUR_SECRET_ACCESS_KEY"
    }
)
```

## Verify Setup

After fixing credentials and workgroup, verify your setup:

### 1. Check Workgroups

```bash
python examples/check_athena_workgroups.py
```

Expected output:
```
✓ Found 1 workgroup(s):

✓ s3tables-workgroup
  State: ENABLED
  Output Location: s3://s3-bucket-apse5-dev-olap-athena-output/
```

### 2. Test Connection

```python
from src.connectors.base import DataSourceConfig
from src.connectors.athena import AthenaConnector

config = DataSourceConfig(
    datasource_id="test",
    datasource_type="athena",
    connection_params={
        "region_name": "ap-southeast-5",
        "database": "olap_report",
        "s3_output_location": "s3://s3-bucket-apse5-dev-olap-athena-output/",
        "catalog": "s3tables",
        "workgroup": "s3tables-workgroup"
    }
)

connector = AthenaConnector(config)
if connector.test_connection():
    print("✓ Connection successful!")
else:
    print("✗ Connection failed")
```

### 3. Run Full Example

```bash
export ATHENA_WORKGROUP="s3tables-workgroup"
python examples/s3tables_introspection.py
```

## Common Issues

### Issue 1: "WorkGroup is not found"

**Cause**: Workgroup doesn't exist or wrong name

**Solution**: 
- Create workgroup in AWS Console
- Or use existing workgroup name
- Check you're in the correct region

### Issue 2: "ExpiredTokenException"

**Cause**: AWS credentials expired

**Solution**:
- Refresh AWS SSO: `aws sso login`
- Or update credentials in ~/.aws/credentials
- Or set environment variables

### Issue 3: "Access Denied"

**Cause**: IAM permissions missing

**Solution**: Add these permissions to your IAM user/role:
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
        "athena:GetWorkGroup",
        "athena:ListWorkGroups",
        "s3:GetObject",
        "s3:PutObject",
        "s3:ListBucket",
        "s3tables:GetTable",
        "s3tables:ListTables",
        "s3tables:ListNamespaces"
      ],
      "Resource": "*"
    }
  ]
}
```

### Issue 4: "Database not found"

**Cause**: Database/namespace doesn't exist in S3 Tables catalog

**Solution**:
- Verify database name: `olap_report`
- List available databases using Athena Console
- Or create the database/namespace first

## Quick Start Checklist

- [ ] AWS credentials are valid (not expired)
- [ ] Athena workgroup exists in ap-southeast-5 region
- [ ] Workgroup is ENABLED
- [ ] S3 output location is configured in workgroup
- [ ] IAM permissions include Athena and S3 Tables access
- [ ] S3 Tables catalog exists
- [ ] Database/namespace exists in the catalog
- [ ] Environment variables set (optional but recommended)

## Complete Working Example

```bash
export AWS_REGION="ap-southeast-5"
export ATHENA_WORKGROUP="s3tables-workgroup"
export AWS_ACCESS_KEY_ID="your-key"
export AWS_SECRET_ACCESS_KEY="your-secret"

cd finx-engine
python examples/check_athena_workgroups.py
python examples/s3tables_introspection.py
```

## Need Help?

1. Check AWS Athena Console for workgroups
2. Run `check_athena_workgroups.py` to diagnose issues
3. Verify credentials: `aws sts get-caller-identity`
4. Check region: `aws configure get region`
5. Review CloudWatch logs for detailed errors

