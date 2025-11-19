# AI Agent-Based Data Migration System

## 📖 Overview

The AI Agent-Based Data Migration System is an intelligent, automated solution for migrating data between different database systems. It leverages AI agents to analyze schemas, plan migrations, transform data, and validate results with minimal human intervention.

---

## 🎯 Key Features

### 🤖 **Intelligent Agents**
- **Schema Analyzer**: Automatically analyzes source and target schemas
- **Migration Planner**: Creates optimal migration strategies
- **Data Transformer**: Handles type conversions and data transformations
- **Migration Executor**: Executes migrations with parallel processing
- **Validator**: Ensures data integrity and completeness

### 🚀 **Advanced Capabilities**
- **Multi-Strategy Support**: Full copy, incremental, batch, and streaming
- **Parallel Processing**: Multiple workers for large datasets
- **Checkpoint System**: Resume interrupted migrations
- **AI-Powered Suggestions**: LLM-based recommendations for complex scenarios
- **Automatic Rollback**: Safe rollback on validation failures
- **Real-Time Monitoring**: Track progress and performance metrics

### 🔒 **Security & Compliance**
- **Credential Encryption**: Secure storage of database credentials
- **Audit Logging**: Complete audit trail of all operations
- **Data Masking**: Protect sensitive information
- **Access Control**: Role-based permissions

---

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                  Migration Orchestrator                      │
│  • Coordinates all agents                                    │
│  • Manages workflow                                          │
│  • Handles errors and retries                                │
└───────────────────────┬─────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┬──────────────┐
        │               │               │              │
        ▼               ▼               ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────┐ ┌──────────┐
│   Schema     │ │  Migration   │ │   Data   │ │Migration │
│  Analyzer    │ │   Planner    │ │Transform │ │ Executor │
└──────────────┘ └──────────────┘ └──────────┘ └──────────┘
        │               │               │              │
        └───────────────┴───────────────┴──────────────┘
                        │
                        ▼
                ┌──────────────┐
                │  Validator   │
                └──────────────┘
```

### Agent Responsibilities

| Agent | Responsibility | Key Functions |
|-------|---------------|---------------|
| **Schema Analyzer** | Analyze database schemas | • Introspect schemas<br>• Compare structures<br>• Calculate compatibility |
| **Migration Planner** | Create migration plans | • Determine strategy<br>• Map columns<br>• Assess risks |
| **Data Transformer** | Transform data | • Type conversion<br>• Data cleaning<br>• Enrichment |
| **Migration Executor** | Execute migrations | • Batch processing<br>• Parallel execution<br>• Progress tracking |
| **Validator** | Validate results | • Row count verification<br>• Data integrity checks<br>• Schema compliance |

---

## 🚀 Quick Start

### Installation

```bash
# Navigate to backend directory
cd finx-ai-service

# Install dependencies
uv pip sync requirements.txt

# Verify installation
python -c "from src.core.migration_agent import MigrationOrchestrator; print('✓ Installation successful')"
```

### Basic Usage

```python
import asyncio
from src.core.migration_agent import MigrationOrchestrator

async def migrate_data():
    # Define source connection
    source = {
        "type": "postgresql",
        "host": "source-db.example.com",
        "port": 5432,
        "database": "source_db",
        "table_name": "users",
        "username": "admin",
        "password": "password"
    }
    
    # Define target connection
    target = {
        "type": "supabase",
        "url": "https://project.supabase.co",
        "database": "target_db",
        "table_name": "users",
        "api_key": "your-api-key"
    }
    
    # Create orchestrator
    orchestrator = MigrationOrchestrator()
    
    # Execute migration
    result = await orchestrator.migrate(
        source_connection=source,
        target_connection=target,
        options={
            "validate": True,
            "batch_size": 1000,
            "parallel_workers": 2
        }
    )
    
    # Check results
    print(f"Status: {result.status}")
    print(f"Rows Migrated: {result.rows_migrated}")
    print(f"Duration: {result.duration_seconds}s")

# Run migration
asyncio.run(migrate_data())
```

### Run Demo

```bash
# Navigate to demos directory
cd finx-ai-service/demos

# Run interactive demo
python demo_migration_agent.py
```

---

## 📊 Migration Strategies

### 1. Full Copy Strategy

**Best for**: Small datasets (< 100K rows)

```python
options = {
    "strategy": "full_copy",
    "validate": True
}
```

**Characteristics**:
- Single transaction
- Fast for small datasets
- All-or-nothing approach
- Simple rollback

### 2. Incremental Strategy

**Best for**: Medium datasets (100K - 1M rows)

```python
options = {
    "strategy": "incremental",
    "checkpoint_interval": 10000,
    "validate": True
}
```

**Characteristics**:
- Checkpoint system
- Resume capability
- Incremental commits
- Progress tracking

### 3. Batch Strategy

**Best for**: Large datasets (> 1M rows)

```python
options = {
    "strategy": "batch",
    "batch_size": 5000,
    "parallel_workers": 4,
    "validate": True
}
```

**Characteristics**:
- Parallel processing
- Optimal for large datasets
- Resource efficient
- High throughput

### 4. Streaming Strategy

**Best for**: Real-time data sync

```python
options = {
    "strategy": "streaming",
    "buffer_size": 1000,
    "sync_interval": 60
}
```

**Characteristics**:
- Continuous sync
- Low latency
- Real-time updates
- CDC support

---

## 🔧 Configuration Options

### Connection Configuration

```python
connection = {
    # Required
    "type": "postgresql",  # Database type
    "host": "localhost",
    "port": 5432,
    "database": "mydb",
    "table_name": "users",
    
    # Authentication
    "username": "admin",
    "password": "password",
    
    # Optional
    "schema": "public",
    "ssl_mode": "require",
    "connection_timeout": 30,
    "pool_size": 10
}
```

### Migration Options

```python
options = {
    # Strategy
    "strategy": "batch",  # full_copy, incremental, batch, streaming
    
    # Performance
    "batch_size": 1000,
    "parallel_workers": 2,
    "buffer_size": 5000,
    
    # Validation
    "validate": True,
    "validation_sample_size": 100,
    
    # Checkpointing
    "checkpoint_enabled": True,
    "checkpoint_interval": 10000,
    
    # Error Handling
    "max_retries": 3,
    "retry_delay": 5,
    "continue_on_error": False,
    
    # Monitoring
    "progress_callback": my_progress_handler,
    "log_level": "INFO"
}
```

### LLM Configuration

```python
llm_config = {
    "provider": "openai",  # openai, anthropic, custom
    "model": "gpt-4",
    "api_key": "your-api-key",
    "temperature": 0.7,
    "max_tokens": 2000
}

orchestrator = MigrationOrchestrator(llm_config=llm_config)
```

---

## 📈 Monitoring & Analytics

### Real-Time Progress

```python
def progress_callback(progress_info):
    print(f"Progress: {progress_info['percentage']}%")
    print(f"Rows: {progress_info['rows_migrated']}/{progress_info['total_rows']}")
    print(f"Speed: {progress_info['rows_per_second']} rows/sec")
    print(f"ETA: {progress_info['estimated_time_remaining']} seconds")

options = {
    "progress_callback": progress_callback
}
```

### Migration History

```python
# Get migration history
history = orchestrator.get_migration_history()

for migration in history:
    print(f"ID: {migration['migration_id']}")
    print(f"Status: {migration['result']['status']}")
    print(f"Rows: {migration['result']['rows_migrated']}")
    print(f"Duration: {migration['result']['duration_seconds']}s")
```

### Performance Metrics

```python
# Get performance metrics
metrics = orchestrator.get_performance_metrics()

print(f"Total Migrations: {metrics['total_migrations']}")
print(f"Success Rate: {metrics['success_rate']}%")
print(f"Average Throughput: {metrics['avg_throughput']} rows/sec")
print(f"Total Rows Migrated: {metrics['total_rows']}")
```

---

## 🔍 Validation & Testing

### Validation Checks

The system performs three levels of validation:

#### 1. Row Count Validation
```python
# Ensures source and target have same number of rows
assert source_count == target_count
```

#### 2. Data Integrity Validation
```python
# Samples random rows and compares checksums
sample_size = 100
for row in random_sample(source, sample_size):
    assert checksum(source_row) == checksum(target_row)
```

#### 3. Schema Compliance Validation
```python
# Verifies data types and constraints
for column in target_schema:
    assert column.type == expected_type
    assert column.constraints == expected_constraints
```

### Dry Run Mode

```python
# Test migration without actually moving data
result = await orchestrator.migrate(
    source_connection=source,
    target_connection=target,
    options={"dry_run": True}
)

print(f"Estimated Duration: {result.estimated_duration_minutes} minutes")
print(f"Estimated Rows: {result.estimated_rows}")
print(f"Risks: {result.risks}")
```

---

## 🛡️ Error Handling & Recovery

### Automatic Retry

```python
options = {
    "max_retries": 3,
    "retry_delay": 5,  # seconds
    "retry_backoff": 2  # exponential backoff multiplier
}
```

### Checkpoint & Resume

```python
# Enable checkpointing
options = {
    "checkpoint_enabled": True,
    "checkpoint_interval": 10000,
    "checkpoint_path": "/tmp/migration_checkpoints"
}

# Resume from checkpoint
result = await orchestrator.resume_migration(
    migration_id="mig_20250118_120000"
)
```

### Rollback

```python
# Automatic rollback on validation failure
options = {
    "auto_rollback": True,
    "backup_before_migration": True
}

# Manual rollback
success = await orchestrator.rollback_migration(
    migration_id="mig_20250118_120000"
)
```

---

## 🎯 Use Cases

### Use Case 1: Database Upgrade

**Scenario**: Migrate from MySQL 5.7 to PostgreSQL 14

```python
source = {
    "type": "mysql",
    "host": "old-mysql.example.com",
    "database": "legacy_db"
}

target = {
    "type": "postgresql",
    "host": "new-postgres.example.com",
    "database": "modern_db"
}

result = await orchestrator.migrate(source, target)
```

### Use Case 2: Cloud Migration

**Scenario**: Migrate on-premise database to Supabase

```python
source = {
    "type": "postgresql",
    "host": "on-premise-db.company.local",
    "database": "production"
}

target = {
    "type": "supabase",
    "url": "https://project.supabase.co",
    "api_key": "your-key"
}

result = await orchestrator.migrate(source, target, options={
    "strategy": "incremental",
    "parallel_workers": 4
})
```

### Use Case 3: Data Warehouse ETL

**Scenario**: Load data into Snowflake for analytics

```python
source = {
    "type": "mongodb",
    "host": "mongo-cluster.example.com",
    "database": "operational_data"
}

target = {
    "type": "snowflake",
    "account": "company.snowflakecomputing.com",
    "database": "analytics",
    "warehouse": "ETL_WH"
}

result = await orchestrator.migrate(source, target, options={
    "strategy": "batch",
    "batch_size": 10000,
    "parallel_workers": 8
})
```

---

## 🔐 Security Best Practices

### 1. Credential Management

```python
# Use environment variables
import os

source = {
    "type": "postgresql",
    "host": os.getenv("SOURCE_DB_HOST"),
    "username": os.getenv("SOURCE_DB_USER"),
    "password": os.getenv("SOURCE_DB_PASSWORD")
}

# Or use credential vault
from src.web.utils.security import get_credentials

credentials = get_credentials("source_db")
```

### 2. Encryption

```python
# Enable encryption for credentials
from src.web.utils.security import encrypt_credentials

encrypted = encrypt_credentials({
    "username": "admin",
    "password": "secret"
})
```

### 3. Audit Logging

```python
# Enable comprehensive audit logging
options = {
    "audit_logging": True,
    "audit_log_path": "/var/log/migrations",
    "log_sensitive_data": False  # Mask sensitive info
}
```

---

## 📚 API Reference

### MigrationOrchestrator

```python
class MigrationOrchestrator:
    def __init__(self, llm_config: Optional[Dict] = None)
    
    async def migrate(
        self,
        source_connection: Dict[str, Any],
        target_connection: Dict[str, Any],
        options: Optional[Dict[str, Any]] = None
    ) -> MigrationResult
    
    async def resume_migration(
        self,
        migration_id: str
    ) -> MigrationResult
    
    async def rollback_migration(
        self,
        migration_id: str
    ) -> bool
    
    def get_migration_history(self) -> List[Dict[str, Any]]
    
    def get_performance_metrics(self) -> Dict[str, Any]
```

### MigrationResult

```python
class MigrationResult(BaseModel):
    migration_id: str
    status: MigrationStatus
    rows_migrated: int
    rows_failed: int
    duration_seconds: float
    errors: List[str]
    warnings: List[str]
    metadata: Dict[str, Any]
```

### MigrationPlan

```python
class MigrationPlan(BaseModel):
    migration_id: str
    source_schema: SchemaInfo
    target_schema: SchemaInfo
    strategy: MigrationStrategy
    column_mappings: Dict[str, str]
    transformations: List[Dict[str, Any]]
    batch_size: int
    parallel_workers: int
    estimated_duration_minutes: float
    risks: List[str]
    recommendations: List[str]
```

---

## 🐛 Troubleshooting

### Common Issues

#### Issue: Low Compatibility Score

**Solution**: Review schema differences and use AI suggestions

```python
# Get detailed analysis
analysis = await orchestrator.schema_analyzer.execute({
    "source_connection": source,
    "target_connection": target
})

print(f"Differences: {analysis['differences']}")
print(f"Suggestions: {analysis['ai_suggestions']}")
```

#### Issue: Migration Timeout

**Solution**: Increase batch size or add more workers

```python
options = {
    "batch_size": 10000,  # Increase from 1000
    "parallel_workers": 8,  # Increase from 2
    "connection_timeout": 300  # 5 minutes
}
```

#### Issue: Validation Failure

**Solution**: Check data integrity and schema compliance

```python
# Run detailed validation
validation = await orchestrator.validator.execute({
    "source_connection": source,
    "target_connection": target,
    "plan": plan
})

print(f"Row Count: {validation['row_count_match']}")
print(f"Data Integrity: {validation['data_integrity']}")
print(f"Schema: {validation['schema_compliance']}")
```

---

## 📞 Support

### Documentation
- [Architecture Diagrams](ARCHITECTURE.md)
- [Migration Diagrams](MIGRATION_DIAGRAMS.md)
- [API Documentation](README.md)

### Examples
- [Demo Scripts](../finx-ai-service/demos/)
- [Test Cases](../finx-ai-service/tests/)

### Community
- GitHub Issues: Report bugs and request features
- Discussions: Ask questions and share experiences

---

## 📝 License

MIT License - See LICENSE file for details

---

**Last Updated**: 2025-01-18  
**Version**: 1.0.0
