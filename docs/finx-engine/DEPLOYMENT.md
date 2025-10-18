# FinX Engine Deployment Guide

This guide provides instructions for deploying and using FinX Engine in production.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Deployment Options](#deployment-options)
3. [Production Configuration](#production-configuration)
4. [Monitoring and Logging](#monitoring-and-logging)
5. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### AWS Requirements

- AWS Account with appropriate permissions
- AWS Athena database(s) configured
- S3 bucket for Athena query results
- IAM user/role with required permissions (see [AWS_SETUP.md](docs/AWS_SETUP.md))

### FinX AI Service Requirements

- FinX AI Service deployed and running
- Vector database (Qdrant) accessible
- Embedder service configured (e.g., Google GenAI)

### Python Requirements

- Python 3.8 or higher
- pip package manager
- Virtual environment (recommended)

---

## Deployment Options

### Option 1: Local Development

For development and testing:

```bash
# Clone repository
git clone <repository-url>
cd finx-engine

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Run examples
python examples/athena_introspection.py
```

### Option 2: Docker Container

Create a Dockerfile:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY examples/ ./examples/

# Set environment variables
ENV PYTHONPATH=/app

# Run introspection
CMD ["python", "examples/end_to_end_example.py"]
```

Build and run:

```bash
# Build image
docker build -t finx-engine .

# Run container
docker run --env-file .env finx-engine
```

### Option 3: AWS Lambda

Deploy as a Lambda function for scheduled introspection:

```python
# lambda_handler.py
import json
import os
from src.config.aws_config import AWSConfig
from src.introspection.athena_introspector import AthenaIntrospector
from src.mdl.generator import MDLGenerator

def lambda_handler(event, context):
    # Configure from environment variables
    config = AWSConfig(
        region_name=os.environ['AWS_REGION'],
        database=os.environ['ATHENA_DATABASE'],
        s3_output_location=os.environ['ATHENA_S3_OUTPUT']
    )
    
    # Introspect schema
    introspector = AthenaIntrospector(config)
    schema = introspector.introspect()
    
    # Generate MDL
    generator = MDLGenerator()
    mdl = generator.generate(schema)
    
    # Save to S3 or trigger indexing
    # ...
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'tables': len(mdl['models']),
            'relationships': len(mdl['relationships'])
        })
    }
```

### Option 4: Kubernetes CronJob

Deploy as a scheduled job:

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: finx-engine-introspection
spec:
  schedule: "0 2 * * *"  # Run daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: finx-engine
            image: finx-engine:latest
            env:
            - name: AWS_REGION
              valueFrom:
                secretKeyRef:
                  name: aws-credentials
                  key: region
            - name: ATHENA_DATABASE
              value: "my_database"
            - name: ATHENA_S3_OUTPUT
              value: "s3://my-bucket/athena-results/"
          restartPolicy: OnFailure
```

---

## Production Configuration

### Environment Variables

```bash
# AWS Configuration
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_REGION="us-east-1"

# Athena Configuration
export ATHENA_DATABASE="production_db"
export ATHENA_S3_OUTPUT="s3://prod-bucket/athena-results/"
export ATHENA_WORKGROUP="production"

# FinX AI Service
export FINX_AI_SERVICE_PATH="/path/to/finx-ai-service"
export GOOGLE_API_KEY="your-google-api-key"
export QDRANT_URL="http://qdrant:6333"

# Logging
export LOG_LEVEL="INFO"
export LOG_FORMAT="json"
```

### Security Best Practices

1. **Use IAM Roles**: Prefer IAM roles over access keys when running on AWS infrastructure
2. **Encrypt Secrets**: Use AWS Secrets Manager or similar for sensitive credentials
3. **Least Privilege**: Grant minimum required IAM permissions
4. **Network Security**: Use VPC endpoints for Athena and S3 access
5. **Audit Logging**: Enable CloudTrail for AWS API calls

### Performance Tuning

```python
# Configure batch sizes
config = AWSConfig(
    region_name="us-east-1",
    database="my_database",
    s3_output_location="s3://my-bucket/athena-results/",
    # Performance settings
    max_workers=10,  # Parallel table introspection
    query_timeout=300,  # Query timeout in seconds
)

# Introspect specific tables for faster processing
introspector = AthenaIntrospector(config)
schema = introspector.introspect(
    tables=["important_table1", "important_table2"]
)
```

---

## Monitoring and Logging

### Logging Configuration

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('finx-engine.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('finx-engine')
```

### Metrics to Monitor

- **Introspection Duration**: Time taken to introspect schema
- **Table Count**: Number of tables discovered
- **Relationship Count**: Number of relationships detected
- **Error Rate**: Failed introspections
- **API Call Count**: AWS API calls made

### CloudWatch Integration

```python
import boto3
from datetime import datetime

cloudwatch = boto3.client('cloudwatch')

def publish_metrics(tables_count, relationships_count, duration):
    cloudwatch.put_metric_data(
        Namespace='FinXEngine',
        MetricData=[
            {
                'MetricName': 'TablesIntrospected',
                'Value': tables_count,
                'Unit': 'Count',
                'Timestamp': datetime.utcnow()
            },
            {
                'MetricName': 'IntrospectionDuration',
                'Value': duration,
                'Unit': 'Seconds',
                'Timestamp': datetime.utcnow()
            }
        ]
    )
```

---

## Troubleshooting

### Common Issues

#### 1. AWS Credentials Not Found

**Error**: `NoCredentialsError: Unable to locate credentials`

**Solution**:
- Verify AWS credentials are configured
- Check environment variables or AWS CLI configuration
- Ensure IAM role is attached (if running on AWS)

#### 2. Athena Query Timeout

**Error**: `QueryExecutionTimeout`

**Solution**:
- Increase query timeout in configuration
- Check Athena query history for slow queries
- Optimize table partitioning

#### 3. S3 Access Denied

**Error**: `AccessDenied: Access Denied`

**Solution**:
- Verify S3 bucket permissions
- Check IAM policy includes S3 access
- Ensure bucket is in the same region

#### 4. Table Not Found

**Error**: `TableNotFoundException`

**Solution**:
- Verify database name is correct
- Check table exists in Glue Data Catalog
- Run `SHOW TABLES` in Athena console

### Debug Mode

Enable debug logging:

```python
import logging

logging.basicConfig(level=logging.DEBUG)

# Run introspection with detailed logs
introspector = AthenaIntrospector(config)
schema = introspector.introspect()
```

### Health Check

Create a health check script:

```python
def health_check():
    """Verify FinX Engine can connect to AWS"""
    try:
        config = AWSConfig(
            region_name="us-east-1",
            database="my_database",
            s3_output_location="s3://my-bucket/athena-results/"
        )
        
        introspector = AthenaIntrospector(config)
        introspector.connector.connect()
        
        # Test query
        tables = introspector.connector.get_tables()
        
        return {
            "status": "healthy",
            "tables_count": len(tables)
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
```

---

## Scheduled Introspection

### Using Cron

```bash
# Add to crontab
0 2 * * * cd /path/to/finx-engine && /path/to/venv/bin/python examples/end_to_end_example.py >> /var/log/finx-engine.log 2>&1
```

### Using AWS EventBridge

```json
{
  "source": ["aws.events"],
  "detail-type": ["Scheduled Event"],
  "schedule": "cron(0 2 * * ? *)",
  "target": {
    "arn": "arn:aws:lambda:us-east-1:123456789012:function:finx-engine-introspection"
  }
}
```

---

## Next Steps

- Review [AWS_SETUP.md](docs/AWS_SETUP.md) for AWS configuration
- See [INTEGRATION.md](docs/INTEGRATION.md) for FinX AI Service integration
- Check [examples/](examples/) for usage examples

