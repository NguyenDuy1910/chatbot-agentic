# FINX Backend Documentation

Welcome to the FINX Backend documentation. This comprehensive guide covers all aspects of the FINX backend system.

## 📚 Documentation Structure

- [**Main README**](../README.md) - Project overview and quick start
- [**Testing Guide**](#testing-guide) - How to run and write tests
- [**Demo Guide**](#demo-guide) - Usage examples and demonstrations
- [**API Documentation**](#api-documentation) - API endpoints and usage
- [**Database Models**](#database-models) - Model structure and relationships
- [**Connection Management**](#connection-management) - Data source connections
- [**Logging System**](#logging-system) - Comprehensive logging features
- [**Configuration**](#configuration) - Environment and system configuration
- [**Deployment**](#deployment) - Production deployment guide

---

## Testing Guide

### Overview
The FINX backend includes a comprehensive test suite organized in the `tests/` directory.

### Test Structure
```
tests/
├── __init__.py              # Test package initialization
├── test_models.py          # Database models and CRUD operations
├── test_connections.py     # Data connection providers and management
├── test_logging.py         # Logging system and integrations
└── run_all_tests.py        # Main test runner with reporting
```

### Running Tests

#### Run All Tests
```bash
cd backend/tests
python run_all_tests.py
```

#### Run Specific Test Module
```bash
python run_all_tests.py --test models
python run_all_tests.py --test connections
python run_all_tests.py --test logging
```

#### Run Tests by Category
```bash
python run_all_tests.py --category core     # Essential functionality
python run_all_tests.py --category utils    # Utility functions
python run_all_tests.py --category api      # API endpoints
python run_all_tests.py --category auth     # Authentication
```

#### Generate Detailed Report
```bash
python run_all_tests.py --report
```

#### Verbose Output
```bash
python run_all_tests.py --verbose
```

### Test Categories

- **core**: Essential functionality (models, connections)
- **utils**: Utility functions (logging, auth)
- **api**: API endpoints and routing
- **auth**: Authentication and authorization

### Test Configuration
Tests use the following configuration:
- Log level: WARNING (to reduce noise)
- Test database: SQLite in-memory
- Test logs: `tests/logs/` directory
- Auto cleanup after tests

### Writing New Tests
When adding new tests:
1. Follow the existing test structure
2. Use descriptive test names
3. Include both positive and negative test cases
4. Add proper error handling
5. Update the test runner if needed

---

## Demo Guide

### Overview
The `demos/` directory contains practical examples showing how to use various FINX backend components.

### Demo Structure
```
demos/
├── __init__.py              # Demo package initialization
├── demo_connections.py     # Data connection providers usage
└── demo_logging.py         # Logging system features
```

### Running Demos

#### Connection Providers Demo
```bash
cd backend/demos
python demo_connections.py
```

**Features demonstrated:**
- PostgreSQL connection setup and usage
- AWS Athena for data lake analytics
- Snowflake data warehouse operations
- Connection pooling and management
- Performance monitoring
- Graceful connection cleanup

#### Logging System Demo
```bash
cd backend/demos
python demo_logging.py
```

**Features demonstrated:**
- Basic structured logging
- Context-aware logging
- Specialized component loggers (Database, API, Security)
- Function decorators for automatic logging
- Model integration mixins
- Context managers for operation tracking
- Environment-based configurations
- Real-world usage scenarios

### Demo Output
- Demo logs are saved to `demos/logs/` directory
- Console output provides real-time feedback
- All demos use mock implementations by default

### Requirements for Real Usage
For production usage, install appropriate drivers:
- PostgreSQL: `psycopg2` or `asyncpg`
- AWS services: `boto3`
- Snowflake: `snowflake-connector-python`
- BigQuery: `google-cloud-bigquery`

---

## API Documentation

### Overview
The FINX backend provides RESTful APIs for all major operations.

### API Structure
```
finx/routers/
├── users.py               # User management endpoints
├── connections.py         # Data connection management
└── __init__.py           # Router initialization
```

### Authentication
All API endpoints require authentication. Use the following headers:
```
Authorization: Bearer <your-token>
Content-Type: application/json
```

### Common Response Format
```json
{
  "success": true,
  "data": {...},
  "message": "Operation completed successfully",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Error Response Format
```json
{
  "success": false,
  "error": "Error description",
  "error_code": "ERROR_CODE",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## Database Models

### Overview
The FINX backend includes 17 core models with complete CRUD operations.

### Model Structure
```
finx/models/
├── users.py              # User management
├── auths.py              # Authentication
├── chats.py              # Chat and folder management
├── groups.py             # User groups
├── channels.py           # Communication channels
├── messages.py           # Messages and reactions
├── files.py              # File management
├── models.py             # AI model management
├── tags.py               # Tagging system
├── memories.py           # Memory storage
├── feedback.py           # User feedback
├── knowledge.py          # Knowledge bases
├── prompts.py            # Prompt templates
└── connections.py        # Data connections
```

### Model Features
- **Complete CRUD Operations**: Create, Read, Update, Delete
- **Relationship Management**: Foreign keys and complex relationships
- **Data Validation**: Pydantic models for type safety
- **Logging Integration**: Automatic operation logging
- **Performance Tracking**: Query execution monitoring

### Usage Example
```python
from finx.models import Users, UserModel

# Create a new user
user_data = {
    "name": "John Doe",
    "email": "john@example.com",
    "role": "user"
}
user = Users.insert_new_user("user123", user_data)

# Get user by ID
user = Users.get_user_by_id("user123")

# Update user
Users.update_user_by_id("user123", {"name": "John Smith"})
```

---

## Connection Management

### Overview
The FINX backend supports connections to multiple data sources with unified management.

### Supported Data Sources
- **Relational Databases**: PostgreSQL, MySQL, SQLite, Oracle, SQL Server
- **NoSQL Databases**: MongoDB, Redis, Cassandra, Elasticsearch
- **Cloud Data Warehouses**: Snowflake, BigQuery, Redshift, Databricks
- **Analytics Engines**: AWS Athena, Presto, Trino, Spark
- **File Storage**: AWS S3, Azure Blob, GCS, HDFS, MinIO
- **Streaming**: Kafka, Kinesis, PubSub, RabbitMQ

### Connection Providers
```
finx/models/connection_providers.py
├── BaseConnectionProvider     # Abstract base class
├── PostgreSQLProvider        # PostgreSQL connections
├── AthenaProvider            # AWS Athena connections
├── SnowflakeProvider         # Snowflake connections
├── BigQueryProvider          # Google BigQuery connections
├── S3Provider                # AWS S3 connections
└── ConnectionManager         # Connection lifecycle management
```

### Usage Example
```python
from finx.models import ConnectionType, DatabaseDriver
from finx.models.connection_providers import connection_manager

# Create connection
connection = ConnectionModel(
    name="Production DB",
    type=ConnectionType.POSTGRESQL,
    driver=DatabaseDriver.PSYCOPG2,
    host="localhost",
    port="5432",
    database_name="prod_db"
)

# Test connection
result = connection_manager.test_connection(connection)

# Execute query
query_result = connection_manager.execute_query(
    connection, 
    "SELECT COUNT(*) FROM users"
)
```

---

## Logging System

### Overview
The FINX backend includes a comprehensive logging system with structured output, context awareness, and specialized loggers.

### Logging Features
- **Multiple Formats**: Simple, Detailed, Structured, JSON
- **Environment-based Configuration**: Development, Production, Testing
- **Specialized Loggers**: Database, API, Security, Performance
- **Context Propagation**: Automatic context tracking
- **Integration Mixins**: Easy model integration
- **Performance Monitoring**: Slow operation detection

### Logging Structure
```
finx/utils/
├── logging.py                # Core logging system
├── logging_integration.py    # Model integration mixins
└── __init__.py              # Logging utilities export

finx/config/
└── logging_config.py        # Environment configurations
```

### Usage Examples

#### Basic Logging
```python
from finx.utils import get_logger

logger = get_logger("my.module")
logger.info("Application started")
```

#### Context Logging
```python
context_logger = get_logger("my.module", {
    "user_id": "user123",
    "session_id": "sess456"
})
context_logger.info("User action", {"action": "login"})
```

#### Specialized Loggers
```python
from finx.utils import DatabaseLogger, APILogger, SecurityLogger

# Database operations
db_logger = DatabaseLogger("main_db")
db_logger.log_query("SELECT * FROM users", execution_time=0.045)

# API operations
api_logger = APILogger("/api/v1/users")
api_logger.log_request("GET", "/api/v1/users", user_id="user123")

# Security events
security_logger = SecurityLogger()
security_logger.log_auth_attempt("user123", True, "192.168.1.100")
```

---

## Configuration

### Environment Variables
```bash
# Application Environment
ENVIRONMENT=development|production|testing

# Logging Configuration
LOG_LEVEL=DEBUG|INFO|WARNING|ERROR|CRITICAL
LOG_FORMAT=simple|detailed|structured|json
LOG_DIR=logs
LOG_CONSOLE_ENABLED=true
LOG_FILE_ENABLED=true
LOG_JSON_ENABLED=false

# Database Configuration
DATABASE_URL=your_database_connection_string

# Supabase Configuration
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
```

### Environment Configurations

#### Development
- Log Level: DEBUG
- Format: Structured
- Output: Console + File
- JSON Logs: Disabled

#### Production
- Log Level: INFO
- Format: JSON
- Output: File + JSON logs
- Sensitive Data: Masked

#### Testing
- Log Level: WARNING
- Format: Simple
- Output: File only
- Cleanup: Automatic

---

## Deployment

### Production Setup

#### 1. Environment Configuration
```bash
export ENVIRONMENT=production
export LOG_LEVEL=INFO
export DATABASE_URL=your_production_db_url
```

#### 2. Logging Setup
```python
from finx.config.logging_config import auto_setup_logging
auto_setup_logging()
```

#### 3. Database Initialization
```python
from finx.internal.db import init_db
init_db()
```

#### 4. Connection Health Checks
```python
from finx.models.connection_providers import connection_manager

for connection in active_connections:
    result = connection_manager.test_connection(connection)
    if not result.success:
        logger.error(f"Connection {connection.name} failed: {result.error}")
```

### Monitoring & Observability

#### Logging Features
- Structured JSON logs for log aggregation
- Performance metrics for slow operations
- Error tracking with stack traces
- Security event logging
- Database operation monitoring

#### Connection Monitoring
- Health checks for all data sources
- Performance tracking for queries
- Error rate monitoring
- Resource usage tracking

---

## Support

For issues and questions:
1. Check the demos for usage examples
2. Run tests to verify functionality
3. Check logs for detailed error information
4. Review the documentation in each module

---

**FINX Backend** - A robust foundation for financial data management applications.
