"""
Logging Configuration for FINX Backend
Centralized configuration for different environments and use cases
"""

import os
from typing import Dict, Any
from finx.utils.logging import LogLevel, LogFormat, LoggerConfig

####################
# Environment Configurations
####################

class DevelopmentLoggingConfig(LoggerConfig):
    """Development environment logging configuration"""
    
    def __init__(self):
        super().__init__()
        self.level = LogLevel.DEBUG
        self.format_type = LogFormat.STRUCTURED
        self.console_enabled = True
        self.file_enabled = True
        self.json_enabled = False
        self.log_dir = "logs/dev"

class ProductionLoggingConfig(LoggerConfig):
    """Production environment logging configuration"""
    
    def __init__(self):
        super().__init__()
        self.level = LogLevel.INFO
        self.format_type = LogFormat.JSON
        self.console_enabled = True
        self.file_enabled = True
        self.json_enabled = True
        self.log_dir = "/var/log/finx"
        self.max_file_size = 50 * 1024 * 1024  # 50MB
        self.backup_count = 10

class TestingLoggingConfig(LoggerConfig):
    """Testing environment logging configuration"""
    
    def __init__(self):
        super().__init__()
        self.level = LogLevel.WARNING
        self.format_type = LogFormat.SIMPLE
        self.console_enabled = False
        self.file_enabled = True
        self.json_enabled = False
        self.log_dir = "logs/test"

####################
# Component-Specific Configurations
####################

class DatabaseLoggingConfig:
    """Database-specific logging configuration"""
    
    @staticmethod
    def get_config() -> Dict[str, Any]:
        return {
            "logger_name": "finx.database",
            "level": LogLevel.INFO,
            "log_slow_queries": True,
            "slow_query_threshold": 1.0,  # seconds
            "log_connection_events": True,
            "log_query_params": False,  # Security: don't log sensitive params
        }

class APILoggingConfig:
    """API-specific logging configuration"""
    
    @staticmethod
    def get_config() -> Dict[str, Any]:
        return {
            "logger_name": "finx.api",
            "level": LogLevel.INFO,
            "log_request_body": False,  # Security: don't log request bodies
            "log_response_body": False,  # Security: don't log response bodies
            "log_headers": False,  # Security: don't log headers (may contain tokens)
            "slow_request_threshold": 2.0,  # seconds
            "log_user_actions": True,
        }

class SecurityLoggingConfig:
    """Security-specific logging configuration"""
    
    @staticmethod
    def get_config() -> Dict[str, Any]:
        return {
            "logger_name": "finx.security",
            "level": LogLevel.INFO,
            "log_all_auth_attempts": True,
            "log_failed_auth_attempts": True,
            "log_permission_checks": True,
            "log_sensitive_operations": True,
            "alert_on_multiple_failures": True,
            "failure_threshold": 5,  # Alert after 5 failed attempts
        }

class ConnectionLoggingConfig:
    """Data connection-specific logging configuration"""
    
    @staticmethod
    def get_config() -> Dict[str, Any]:
        return {
            "logger_name": "finx.connections",
            "level": LogLevel.INFO,
            "log_connection_tests": True,
            "log_query_execution": True,
            "log_connection_errors": True,
            "log_performance_metrics": True,
            "mask_credentials": True,  # Security: mask credentials in logs
        }

####################
# Configuration Factory
####################

class LoggingConfigFactory:
    """Factory to create logging configurations based on environment"""
    
    _configs = {
        "development": DevelopmentLoggingConfig,
        "production": ProductionLoggingConfig,
        "testing": TestingLoggingConfig,
        "dev": DevelopmentLoggingConfig,
        "prod": ProductionLoggingConfig,
        "test": TestingLoggingConfig,
    }
    
    @classmethod
    def create_config(cls, environment: str = None) -> LoggerConfig:
        """Create logging configuration for specified environment"""
        if environment is None:
            environment = os.getenv("ENVIRONMENT", "development").lower()
        
        config_class = cls._configs.get(environment, DevelopmentLoggingConfig)
        return config_class()
    
    @classmethod
    def get_component_config(cls, component: str) -> Dict[str, Any]:
        """Get component-specific logging configuration"""
        component_configs = {
            "database": DatabaseLoggingConfig.get_config(),
            "api": APILoggingConfig.get_config(),
            "security": SecurityLoggingConfig.get_config(),
            "connections": ConnectionLoggingConfig.get_config(),
        }
        
        return component_configs.get(component, {})

####################
# Logging Setup Functions
####################

def setup_development_logging():
    """Setup logging for development environment"""
    from finx.utils.logging import setup_logging
    
    setup_logging(
        level=LogLevel.DEBUG,
        format_type=LogFormat.STRUCTURED,
        log_dir="logs/dev",
        console_enabled=True,
        file_enabled=True,
        json_enabled=False
    )

def setup_production_logging():
    """Setup logging for production environment"""
    from finx.utils.logging import setup_logging
    
    setup_logging(
        level=LogLevel.INFO,
        format_type=LogFormat.JSON,
        log_dir="/var/log/finx",
        console_enabled=True,
        file_enabled=True,
        json_enabled=True
    )

def setup_testing_logging():
    """Setup logging for testing environment"""
    from finx.utils.logging import setup_logging
    
    setup_logging(
        level=LogLevel.WARNING,
        format_type=LogFormat.SIMPLE,
        log_dir="logs/test",
        console_enabled=False,
        file_enabled=True,
        json_enabled=False
    )

def auto_setup_logging():
    """Automatically setup logging based on environment"""
    environment = os.getenv("ENVIRONMENT", "development").lower()
    
    setup_functions = {
        "development": setup_development_logging,
        "production": setup_production_logging,
        "testing": setup_testing_logging,
        "dev": setup_development_logging,
        "prod": setup_production_logging,
        "test": setup_testing_logging,
    }
    
    setup_function = setup_functions.get(environment, setup_development_logging)
    setup_function()

####################
# Logging Utilities
####################

def get_logger_for_module(module_name: str):
    """Get logger configured for specific module"""
    from finx.utils.logging import get_logger
    
    # Extract component from module name
    if "database" in module_name or "db" in module_name:
        component = "database"
    elif "api" in module_name or "routes" in module_name:
        component = "api"
    elif "auth" in module_name or "security" in module_name:
        component = "security"
    elif "connection" in module_name:
        component = "connections"
    else:
        component = "general"
    
    config = LoggingConfigFactory.get_component_config(component)
    logger_name = config.get("logger_name", f"finx.{component}")
    
    return get_logger(logger_name)

def mask_sensitive_data(data: Dict[str, Any], sensitive_keys: list = None) -> Dict[str, Any]:
    """Mask sensitive data in log entries"""
    if sensitive_keys is None:
        sensitive_keys = [
            "password", "token", "key", "secret", "credential",
            "auth", "authorization", "api_key", "access_key"
        ]
    
    masked_data = data.copy()
    
    for key, value in masked_data.items():
        if any(sensitive_key in key.lower() for sensitive_key in sensitive_keys):
            if isinstance(value, str) and len(value) > 4:
                masked_data[key] = value[:2] + "*" * (len(value) - 4) + value[-2:]
            else:
                masked_data[key] = "***MASKED***"
        elif isinstance(value, dict):
            masked_data[key] = mask_sensitive_data(value, sensitive_keys)
    
    return masked_data

####################
# Performance Monitoring
####################

class PerformanceLogger:
    """Logger for performance monitoring"""
    
    def __init__(self, component: str = "performance"):
        from finx.utils.logging import get_logger
        self.logger = get_logger(f"finx.{component}")
    
    def log_slow_operation(self, operation: str, duration: float, threshold: float = 1.0):
        """Log slow operations"""
        if duration > threshold:
            self.logger.warning(
                f"Slow operation detected: {operation}",
                extra={
                    "operation": operation,
                    "duration": duration,
                    "threshold": threshold,
                    "performance_issue": True
                }
            )
    
    def log_resource_usage(self, cpu_percent: float = None, memory_mb: float = None):
        """Log resource usage"""
        extra = {"resource_monitoring": True}
        
        if cpu_percent is not None:
            extra["cpu_percent"] = cpu_percent
        if memory_mb is not None:
            extra["memory_mb"] = memory_mb
        
        self.logger.info("Resource usage", extra=extra)

# Global performance logger
performance_logger = PerformanceLogger()
