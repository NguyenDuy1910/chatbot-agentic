# FINX Backend Quick Start Guide

Get up and running with FINX Backend in minutes.

## 🚀 Quick Setup

### 1. Project Setup
```bash
cd backend
python setup_project.py
```

### 2. Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit configuration
nano .env
```

### 3. Run Tests
```bash
cd tests
python run_all_tests.py
```

### 4. Try Demos
```bash
cd demos
python demo_logging.py
python demo_connections.py
```

## 📝 Basic Usage Examples

### Database Models
```python
from finx.models import Users

# Create user
user = Users.insert_new_user("user123", {
    "name": "John Doe",
    "email": "john@example.com"
})

# Get user
user = Users.get_user_by_id("user123")
```

### Logging
```python
from finx.utils import get_logger

logger = get_logger("my.app")
logger.info("Application started")
```

### Data Connections
```python
from finx.models.connection_providers import connection_manager

# Test connection
result = connection_manager.test_connection(connection)

# Execute query
result = connection_manager.execute_query(connection, "SELECT 1")
```

## 🎯 Next Steps

1. **[Complete Documentation](README.md)** - Full feature documentation
2. **[Testing Guide](README.md#testing-guide)** - Comprehensive testing
3. **[Demo Guide](README.md#demo-guide)** - Usage examples
4. **[API Documentation](README.md#api-documentation)** - API reference

## 🆘 Need Help?

- Check [Complete Documentation](README.md)
- Run demos for examples
- Review test files for usage patterns
- Check logs for detailed information
