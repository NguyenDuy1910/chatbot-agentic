"""
Centralized Logging System for FINX Backend
Provides structured logging with multiple handlers, formatters, and configurations
"""

import os
import sys
import json
import time
import logging
import logging.handlers
from datetime import datetime
from typing import Dict, Any, Optional, Union
from enum import Enum
from pathlib import Path

####################
# Enums & Constants
####################

class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class LogFormat(str, Enum):
    SIMPLE = "simple"
    DETAILED = "detailed"
    JSON = "json"
    STRUCTURED = "structured"

####################
# Custom Formatters
####################

class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record):
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "process_id": os.getpid(),
            "thread_id": record.thread,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
        
        return json.dumps(log_entry, ensure_ascii=False)

class StructuredFormatter(logging.Formatter):
    """Structured formatter with consistent field layout"""
    
    def __init__(self):
        super().__init__()
    
    def format(self, record):
        timestamp = datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        
        # Build structured message
        parts = [
            f"[{timestamp}]",
            f"[{record.levelname:8}]",
            f"[{record.name:20}]",
            f"[{record.module}:{record.funcName}:{record.lineno}]",
            f"- {record.getMessage()}"
        ]
        
        message = " ".join(parts)
        
        # Add exception if present
        if record.exc_info:
            message += "\n" + self.formatException(record.exc_info)
        
        return message

####################
# Logger Configuration
####################

class LoggerConfig:
    """Configuration class for logger settings"""
    
    def __init__(self):
        # Default settings
        self.level = LogLevel.INFO
        self.format_type = LogFormat.STRUCTURED
        self.log_dir = "logs"
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.backup_count = 5
        self.console_enabled = True
        self.file_enabled = True
        self.json_enabled = False
        
        # Load from environment
        self._load_from_env()
    
    def _load_from_env(self):
        """Load configuration from environment variables"""
        self.level = LogLevel(os.getenv("LOG_LEVEL", self.level.value))
        self.format_type = LogFormat(os.getenv("LOG_FORMAT", self.format_type.value))
        self.log_dir = os.getenv("LOG_DIR", self.log_dir)
        self.max_file_size = int(os.getenv("LOG_MAX_FILE_SIZE", self.max_file_size))
        self.backup_count = int(os.getenv("LOG_BACKUP_COUNT", self.backup_count))
        self.console_enabled = os.getenv("LOG_CONSOLE_ENABLED", "true").lower() == "true"
        self.file_enabled = os.getenv("LOG_FILE_ENABLED", "true").lower() == "true"
        self.json_enabled = os.getenv("LOG_JSON_ENABLED", "false").lower() == "true"

####################
# Main Logger Class
####################

class FinxLogger:
    """Main logger class for FINX backend"""
    
    _instance = None
    _loggers: Dict[str, logging.Logger] = {}
    _config: LoggerConfig = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._config = LoggerConfig()
            cls._setup_logging()
        return cls._instance
    
    @classmethod
    def _setup_logging(cls):
        """Setup logging configuration"""
        # Create log directory
        log_dir = Path(cls._config.log_dir)
        log_dir.mkdir(exist_ok=True)
        
        # Set root logger level
        logging.getLogger().setLevel(getattr(logging, cls._config.level.value))
    
    @classmethod
    def get_logger(cls, name: str, extra_fields: Optional[Dict[str, Any]] = None) -> logging.Logger:
        """Get or create a logger with the given name"""
        if name not in cls._loggers:
            cls._loggers[name] = cls._create_logger(name, extra_fields)
        return cls._loggers[name]
    
    @classmethod
    def _create_logger(cls, name: str, extra_fields: Optional[Dict[str, Any]] = None) -> logging.Logger:
        """Create a new logger with handlers"""
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, cls._config.level.value))
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # Add console handler
        if cls._config.console_enabled:
            console_handler = cls._create_console_handler()
            logger.addHandler(console_handler)
        
        # Add file handler
        if cls._config.file_enabled:
            file_handler = cls._create_file_handler(name)
            logger.addHandler(file_handler)
        
        # Add JSON handler if enabled
        if cls._config.json_enabled:
            json_handler = cls._create_json_handler(name)
            logger.addHandler(json_handler)
        
        # Prevent propagation to root logger
        logger.propagate = False
        
        return logger
    
    @classmethod
    def _create_console_handler(cls) -> logging.StreamHandler:
        """Create console handler"""
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(getattr(logging, cls._config.level.value))
        
        # Set formatter based on config
        if cls._config.format_type == LogFormat.JSON:
            formatter = JSONFormatter()
        elif cls._config.format_type == LogFormat.STRUCTURED:
            formatter = StructuredFormatter()
        elif cls._config.format_type == LogFormat.DETAILED:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s'
            )
        else:  # SIMPLE
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        
        handler.setFormatter(formatter)
        return handler
    
    @classmethod
    def _create_file_handler(cls, logger_name: str) -> logging.handlers.RotatingFileHandler:
        """Create rotating file handler"""
        log_file = Path(cls._config.log_dir) / f"{logger_name}.log"
        
        handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=cls._config.max_file_size,
            backupCount=cls._config.backup_count,
            encoding='utf-8'
        )
        handler.setLevel(getattr(logging, cls._config.level.value))
        
        # Use structured format for files
        formatter = StructuredFormatter()
        handler.setFormatter(formatter)
        
        return handler
    
    @classmethod
    def _create_json_handler(cls, logger_name: str) -> logging.handlers.RotatingFileHandler:
        """Create JSON file handler"""
        log_file = Path(cls._config.log_dir) / f"{logger_name}.json"
        
        handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=cls._config.max_file_size,
            backupCount=cls._config.backup_count,
            encoding='utf-8'
        )
        handler.setLevel(getattr(logging, cls._config.level.value))
        
        formatter = JSONFormatter()
        handler.setFormatter(formatter)
        
        return handler
    
    @classmethod
    def configure(cls, config: LoggerConfig):
        """Update logger configuration"""
        cls._config = config
        # Recreate all loggers with new config
        for name in list(cls._loggers.keys()):
            cls._loggers[name] = cls._create_logger(name)
    
    @classmethod
    def set_level(cls, level: Union[str, LogLevel]):
        """Set logging level for all loggers"""
        if isinstance(level, str):
            level = LogLevel(level.upper())
        
        cls._config.level = level
        log_level = getattr(logging, level.value)
        
        # Update all existing loggers
        for logger in cls._loggers.values():
            logger.setLevel(log_level)
            for handler in logger.handlers:
                handler.setLevel(log_level)

####################
# Context Logger
####################

class ContextLogger:
    """Logger with context information"""
    
    def __init__(self, logger_name: str, context: Dict[str, Any] = None):
        self.logger = FinxLogger.get_logger(logger_name)
        self.context = context or {}
    
    def _log_with_context(self, level: str, message: str, extra: Dict[str, Any] = None):
        """Log message with context"""
        combined_extra = {**self.context}
        if extra:
            combined_extra.update(extra)
        
        # Create log record with extra fields
        record = self.logger.makeRecord(
            self.logger.name, getattr(logging, level), 
            "", 0, message, (), None
        )
        record.extra_fields = combined_extra
        
        self.logger.handle(record)
    
    def debug(self, message: str, extra: Dict[str, Any] = None):
        self._log_with_context("DEBUG", message, extra)
    
    def info(self, message: str, extra: Dict[str, Any] = None):
        self._log_with_context("INFO", message, extra)
    
    def warning(self, message: str, extra: Dict[str, Any] = None):
        self._log_with_context("WARNING", message, extra)
    
    def error(self, message: str, extra: Dict[str, Any] = None):
        self._log_with_context("ERROR", message, extra)
    
    def critical(self, message: str, extra: Dict[str, Any] = None):
        self._log_with_context("CRITICAL", message, extra)

####################
# Convenience Functions
####################

def get_logger(name: str, context: Dict[str, Any] = None) -> Union[logging.Logger, ContextLogger]:
    """Get logger instance"""
    if context:
        return ContextLogger(name, context)
    return FinxLogger.get_logger(name)

def setup_logging(
    level: Union[str, LogLevel] = LogLevel.INFO,
    format_type: LogFormat = LogFormat.STRUCTURED,
    log_dir: str = "logs",
    console_enabled: bool = True,
    file_enabled: bool = True,
    json_enabled: bool = False
):
    """Setup logging with custom configuration"""
    config = LoggerConfig()
    config.level = LogLevel(level) if isinstance(level, str) else level
    config.format_type = format_type
    config.log_dir = log_dir
    config.console_enabled = console_enabled
    config.file_enabled = file_enabled
    config.json_enabled = json_enabled
    
    FinxLogger.configure(config)

# Global logger instance
logger = FinxLogger()

# Module-level convenience functions
def debug(message: str, logger_name: str = "finx", **kwargs):
    get_logger(logger_name).debug(message, extra=kwargs)

def info(message: str, logger_name: str = "finx", **kwargs):
    get_logger(logger_name).info(message, extra=kwargs)

def warning(message: str, logger_name: str = "finx", **kwargs):
    get_logger(logger_name).warning(message, extra=kwargs)

def error(message: str, logger_name: str = "finx", **kwargs):
    get_logger(logger_name).error(message, extra=kwargs)

def critical(message: str, logger_name: str = "finx", **kwargs):
    get_logger(logger_name).critical(message, extra=kwargs)

####################
# Decorators
####################

def log_function_call(logger_name: str = None, level: str = "INFO"):
    """Decorator to log function calls"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            func_logger = get_logger(logger_name or func.__module__)

            # Log function entry
            func_logger.log(
                getattr(logging, level),
                f"Calling function {func.__name__}",
                extra={
                    "function": func.__name__,
                    "module": func.__module__,
                    "args_count": len(args),
                    "kwargs_count": len(kwargs)
                }
            )

            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time

                # Log successful completion
                func_logger.log(
                    getattr(logging, level),
                    f"Function {func.__name__} completed successfully",
                    extra={
                        "function": func.__name__,
                        "execution_time": execution_time,
                        "status": "success"
                    }
                )
                return result

            except Exception as e:
                execution_time = time.time() - start_time

                # Log error
                func_logger.error(
                    f"Function {func.__name__} failed with error: {str(e)}",
                    extra={
                        "function": func.__name__,
                        "execution_time": execution_time,
                        "status": "error",
                        "error_type": type(e).__name__,
                        "error_message": str(e)
                    }
                )
                raise

        return wrapper
    return decorator

def log_performance(logger_name: str = None, threshold_seconds: float = 1.0):
    """Decorator to log performance metrics"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            func_logger = get_logger(logger_name or func.__module__)

            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time

            # Log if execution time exceeds threshold
            if execution_time > threshold_seconds:
                func_logger.warning(
                    f"Slow function execution: {func.__name__}",
                    extra={
                        "function": func.__name__,
                        "execution_time": execution_time,
                        "threshold": threshold_seconds,
                        "performance_issue": True
                    }
                )
            else:
                func_logger.debug(
                    f"Function {func.__name__} performance",
                    extra={
                        "function": func.__name__,
                        "execution_time": execution_time
                    }
                )

            return result
        return wrapper
    return decorator

####################
# Specialized Loggers
####################

class DatabaseLogger(ContextLogger):
    """Specialized logger for database operations"""

    def __init__(self, connection_name: str = "default"):
        super().__init__("finx.database", {"connection": connection_name})

    def log_query(self, query: str, params: Any = None, execution_time: float = None):
        """Log database query"""
        extra = {
            "query": query[:200] + "..." if len(query) > 200 else query,
            "has_params": params is not None,
            "query_type": query.strip().split()[0].upper() if query.strip() else "UNKNOWN"
        }

        if execution_time is not None:
            extra["execution_time"] = execution_time

        self.info("Database query executed", extra)

    def log_connection_event(self, event: str, details: Dict[str, Any] = None):
        """Log database connection events"""
        extra = {"event": event}
        if details:
            extra.update(details)

        self.info(f"Database connection event: {event}", extra)

class APILogger(ContextLogger):
    """Specialized logger for API operations"""

    def __init__(self, endpoint: str = None):
        context = {}
        if endpoint:
            context["endpoint"] = endpoint
        super().__init__("finx.api", context)

    def log_request(self, method: str, path: str, user_id: str = None, request_id: str = None):
        """Log API request"""
        extra = {
            "method": method,
            "path": path,
            "request_type": "incoming"
        }

        if user_id:
            extra["user_id"] = user_id
        if request_id:
            extra["request_id"] = request_id

        self.info(f"{method} {path}", extra)

    def log_response(self, status_code: int, response_time: float = None, request_id: str = None):
        """Log API response"""
        extra = {
            "status_code": status_code,
            "response_type": "outgoing"
        }

        if response_time is not None:
            extra["response_time"] = response_time
        if request_id:
            extra["request_id"] = request_id

        level = "error" if status_code >= 500 else "warning" if status_code >= 400 else "info"
        getattr(self, level)(f"API response {status_code}", extra)

class SecurityLogger(ContextLogger):
    """Specialized logger for security events"""

    def __init__(self):
        super().__init__("finx.security")

    def log_auth_attempt(self, user_id: str, success: bool, ip_address: str = None):
        """Log authentication attempt"""
        extra = {
            "user_id": user_id,
            "auth_success": success,
            "event_type": "authentication"
        }

        if ip_address:
            extra["ip_address"] = ip_address

        level = "info" if success else "warning"
        message = f"Authentication {'successful' if success else 'failed'} for user {user_id}"
        getattr(self, level)(message, extra)

    def log_permission_check(self, user_id: str, resource: str, action: str, granted: bool):
        """Log permission check"""
        extra = {
            "user_id": user_id,
            "resource": resource,
            "action": action,
            "permission_granted": granted,
            "event_type": "authorization"
        }

        level = "info" if granted else "warning"
        message = f"Permission {'granted' if granted else 'denied'} for {user_id} on {resource}:{action}"
        getattr(self, level)(message, extra)
