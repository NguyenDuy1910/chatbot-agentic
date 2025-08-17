#!/usr/bin/env python3
"""
Test script for FINX Logging System
Demonstrates all logging features and configurations
"""

import time
import os
from typing import Dict, Any

def test_basic_logging():
    """Test basic logging functionality"""
    print("📝 Testing Basic Logging...")
    print("-" * 40)
    
    try:
        from finx.utils.logging import get_logger, setup_logging, LogLevel, LogFormat
        
        # Setup logging for testing
        setup_logging(
            level=LogLevel.DEBUG,
            format_type=LogFormat.STRUCTURED,
            log_dir="tests/logs",
            console_enabled=True,
            file_enabled=True,
            json_enabled=False
        )
        
        # Get basic logger
        logger = get_logger("test.basic")
        
        # Test different log levels
        logger.debug("This is a debug message")
        logger.info("This is an info message")
        logger.warning("This is a warning message")
        logger.error("This is an error message")
        logger.critical("This is a critical message")
        
        print("✅ Basic logging test completed")
        return True
        
    except Exception as e:
        print(f"❌ Basic logging test failed: {e}")
        return False

def test_context_logging():
    """Test context logging"""
    print("\n🎯 Testing Context Logging...")
    print("-" * 40)
    
    try:
        from finx.utils.logging import get_logger
        
        # Create logger with context
        context = {
            "user_id": "user123",
            "session_id": "session456",
            "request_id": "req789"
        }
        
        context_logger = get_logger("test.context", context)
        
        # Log with context
        context_logger.info("User performed action", {
            "action": "login",
            "ip_address": "192.168.1.100"
        })
        
        context_logger.warning("Suspicious activity detected", {
            "activity": "multiple_failed_logins",
            "count": 5
        })
        
        print("✅ Context logging test completed")
        return True
        
    except Exception as e:
        print(f"❌ Context logging test failed: {e}")
        return False

def test_specialized_loggers():
    """Test specialized loggers"""
    print("\n🔧 Testing Specialized Loggers...")
    print("-" * 40)
    
    try:
        from finx.utils.logging import DatabaseLogger, APILogger, SecurityLogger
        
        # Test Database Logger
        db_logger = DatabaseLogger("postgres_main")
        db_logger.log_query(
            "SELECT * FROM users WHERE active = true",
            params={"active": True},
            execution_time=0.045
        )
        db_logger.log_connection_event("connection_established", {
            "host": "localhost",
            "database": "finx_db"
        })
        
        # Test API Logger
        api_logger = APILogger("/api/v1/users")
        api_logger.log_request("GET", "/api/v1/users", user_id="user123", request_id="req456")
        api_logger.log_response(200, response_time=0.123, request_id="req456")
        
        # Test Security Logger
        security_logger = SecurityLogger()
        security_logger.log_auth_attempt("user123", True, "192.168.1.100")
        security_logger.log_permission_check("user123", "users", "read", True)
        
        print("✅ Specialized loggers test completed")
        return True
        
    except Exception as e:
        print(f"❌ Specialized loggers test failed: {e}")
        return False

def test_decorators():
    """Test logging decorators"""
    print("\n🎨 Testing Logging Decorators...")
    print("-" * 40)
    
    try:
        from finx.utils.logging import log_function_call, log_performance
        
        @log_function_call("test.decorators", "INFO")
        @log_performance("test.performance", threshold_seconds=0.1)
        def sample_function(x: int, y: int) -> int:
            """Sample function for testing decorators"""
            time.sleep(0.05)  # Simulate some work
            return x + y
        
        @log_function_call("test.decorators", "DEBUG")
        def slow_function():
            """Function that exceeds performance threshold"""
            time.sleep(0.2)  # This will trigger performance warning
            return "completed"
        
        # Test the decorated functions
        result1 = sample_function(5, 3)
        print(f"   Sample function result: {result1}")
        
        result2 = slow_function()
        print(f"   Slow function result: {result2}")
        
        print("✅ Decorators test completed")
        return True
        
    except Exception as e:
        print(f"❌ Decorators test failed: {e}")
        return False

def test_configuration():
    """Test different logging configurations"""
    print("\n⚙️ Testing Logging Configurations...")
    print("-" * 40)
    
    try:
        from finx.config.logging_config import (
            LoggingConfigFactory, 
            mask_sensitive_data,
            performance_logger
        )
        
        # Test configuration factory
        dev_config = LoggingConfigFactory.create_config("development")
        print(f"   Dev config level: {dev_config.level}")
        print(f"   Dev config format: {dev_config.format_type}")
        
        prod_config = LoggingConfigFactory.create_config("production")
        print(f"   Prod config level: {prod_config.level}")
        print(f"   Prod config format: {prod_config.format_type}")
        
        # Test component configs
        db_config = LoggingConfigFactory.get_component_config("database")
        print(f"   Database logger: {db_config.get('logger_name')}")
        
        api_config = LoggingConfigFactory.get_component_config("api")
        print(f"   API logger: {api_config.get('logger_name')}")
        
        # Test sensitive data masking
        sensitive_data = {
            "username": "john_doe",
            "password": "secret123",
            "api_key": "sk-1234567890abcdef",
            "email": "john@example.com"
        }
        
        masked_data = mask_sensitive_data(sensitive_data)
        print(f"   Original: {sensitive_data}")
        print(f"   Masked: {masked_data}")
        
        # Test performance logger
        performance_logger.log_slow_operation("database_query", 1.5, threshold=1.0)
        performance_logger.log_resource_usage(cpu_percent=75.5, memory_mb=512.0)
        
        print("✅ Configuration test completed")
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_error_logging():
    """Test error logging and exception handling"""
    print("\n🚨 Testing Error Logging...")
    print("-" * 40)
    
    try:
        from finx.utils.logging import get_logger
        
        logger = get_logger("test.errors")
        
        # Test exception logging
        try:
            # Intentionally cause an error
            result = 10 / 0
        except ZeroDivisionError as e:
            logger.error("Division by zero error occurred", extra={
                "error_type": "ZeroDivisionError",
                "operation": "division",
                "operands": [10, 0]
            }, exc_info=True)
        
        # Test different error scenarios
        logger.error("Database connection failed", extra={
            "component": "database",
            "connection_string": "postgresql://localhost:5432/finx",
            "error_code": "CONNECTION_REFUSED"
        })
        
        logger.critical("System out of memory", extra={
            "component": "system",
            "memory_usage": "95%",
            "available_memory": "256MB"
        })
        
        print("✅ Error logging test completed")
        return True
        
    except Exception as e:
        print(f"❌ Error logging test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 LOGGING SYSTEM TESTS")
    print("=" * 50)
    
    tests = [
        test_basic_logging,
        test_context_logging,
        test_specialized_loggers,
        test_decorators,
        test_configuration,
        test_error_logging
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        time.sleep(0.1)  # Small delay between tests
    
    print("\n" + "=" * 50)
    print(f"📊 TEST RESULTS: {passed}/{total} tests passed")
    print("=" * 50)
    
    if passed == total:
        print("🎉 All logging tests passed!")
        return 0
    else:
        print("❌ Some logging tests failed!")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
