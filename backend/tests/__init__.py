# FINX Backend Tests Package
# Centralized testing for all components

__version__ = "1.0.0"
__description__ = "Test suite for FINX backend components"

# Test categories
TEST_CATEGORIES = {
    "models": "Database models and CRUD operations",
    "connections": "Data connection providers and management", 
    "logging": "Logging system and integrations",
    "api": "API endpoints and routing",
    "auth": "Authentication and authorization",
    "utils": "Utility functions and helpers"
}

# Test configuration
TEST_CONFIG = {
    "log_level": "WARNING",
    "test_db": "sqlite:///tests/test.db",
    "test_log_dir": "tests/logs",
    "cleanup_after_tests": True
}

print("FINX Backend Test Suite Initialized")
print(f"Available test categories: {list(TEST_CATEGORIES.keys())}")
