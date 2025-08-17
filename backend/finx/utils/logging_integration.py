"""
Logging Integration for FINX Models
Provides logging integration for database operations, API calls, and other components
"""

import time
import functools
from typing import Any, Dict, Optional, Callable
from finx.utils.logging import DatabaseLogger, APILogger, SecurityLogger, get_logger

####################
# Database Logging Integration
####################

class DatabaseLoggingMixin:
    """Mixin to add logging to database operations"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._db_logger = DatabaseLogger(self.__class__.__name__.lower())
    
    def _log_db_operation(self, operation: str, table: str, record_id: str = None, 
                         execution_time: float = None, success: bool = True, 
                         error: str = None, extra: Dict[str, Any] = None):
        """Log database operation"""
        log_data = {
            "operation": operation,
            "table": table,
            "success": success
        }
        
        if record_id:
            log_data["record_id"] = record_id
        if execution_time:
            log_data["execution_time"] = execution_time
        if error:
            log_data["error"] = error
        if extra:
            log_data.update(extra)
        
        if success:
            self._db_logger.info(f"Database {operation} on {table}", log_data)
        else:
            self._db_logger.error(f"Database {operation} failed on {table}", log_data)

def log_database_operation(operation_type: str):
    """Decorator to log database operations"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            start_time = time.time()
            table_name = getattr(self, '__tablename__', self.__class__.__name__)
            
            try:
                result = func(self, *args, **kwargs)
                execution_time = time.time() - start_time
                
                # Extract record ID if possible
                record_id = None
                if hasattr(result, 'id'):
                    record_id = str(result.id)
                elif isinstance(result, dict) and 'id' in result:
                    record_id = str(result['id'])
                
                # Log successful operation
                if hasattr(self, '_log_db_operation'):
                    self._log_db_operation(
                        operation=operation_type,
                        table=table_name,
                        record_id=record_id,
                        execution_time=execution_time,
                        success=True
                    )
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                
                # Log failed operation
                if hasattr(self, '_log_db_operation'):
                    self._log_db_operation(
                        operation=operation_type,
                        table=table_name,
                        execution_time=execution_time,
                        success=False,
                        error=str(e)
                    )
                
                raise
        
        return wrapper
    return decorator

####################
# Connection Logging Integration
####################

class ConnectionLoggingMixin:
    """Mixin to add logging to connection operations"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._conn_logger = get_logger("finx.connections")
    
    def _log_connection_event(self, event: str, connection_name: str = None, 
                            connection_type: str = None, success: bool = True,
                            execution_time: float = None, error: str = None,
                            extra: Dict[str, Any] = None):
        """Log connection event"""
        log_data = {
            "event": event,
            "success": success
        }
        
        if connection_name:
            log_data["connection_name"] = connection_name
        if connection_type:
            log_data["connection_type"] = connection_type
        if execution_time:
            log_data["execution_time"] = execution_time
        if error:
            log_data["error"] = error
        if extra:
            log_data.update(extra)
        
        if success:
            self._conn_logger.info(f"Connection {event}", log_data)
        else:
            self._conn_logger.error(f"Connection {event} failed", log_data)

def log_connection_operation(operation_type: str):
    """Decorator to log connection operations"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            start_time = time.time()
            
            # Extract connection info
            connection_name = getattr(self, 'name', 'unknown')
            connection_type = getattr(self, 'type', 'unknown')
            
            try:
                result = func(self, *args, **kwargs)
                execution_time = time.time() - start_time
                
                # Log successful operation
                if hasattr(self, '_log_connection_event'):
                    self._log_connection_event(
                        event=operation_type,
                        connection_name=connection_name,
                        connection_type=connection_type,
                        execution_time=execution_time,
                        success=True
                    )
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                
                # Log failed operation
                if hasattr(self, '_log_connection_event'):
                    self._log_connection_event(
                        event=operation_type,
                        connection_name=connection_name,
                        connection_type=connection_type,
                        execution_time=execution_time,
                        success=False,
                        error=str(e)
                    )
                
                raise
        
        return wrapper
    return decorator

####################
# API Logging Integration
####################

class APILoggingMixin:
    """Mixin to add logging to API operations"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._api_logger = APILogger()
    
    def _log_api_call(self, method: str, endpoint: str, user_id: str = None,
                     status_code: int = None, response_time: float = None,
                     request_id: str = None, extra: Dict[str, Any] = None):
        """Log API call"""
        # Log request
        self._api_logger.log_request(method, endpoint, user_id, request_id)
        
        # Log response if status code provided
        if status_code is not None:
            self._api_logger.log_response(status_code, response_time, request_id)

####################
# Security Logging Integration
####################

class SecurityLoggingMixin:
    """Mixin to add security logging"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._security_logger = SecurityLogger()
    
    def _log_auth_event(self, user_id: str, event_type: str, success: bool,
                       ip_address: str = None, extra: Dict[str, Any] = None):
        """Log authentication event"""
        if event_type == "login":
            self._security_logger.log_auth_attempt(user_id, success, ip_address)
        else:
            log_data = {
                "user_id": user_id,
                "event_type": event_type,
                "success": success
            }
            if ip_address:
                log_data["ip_address"] = ip_address
            if extra:
                log_data.update(extra)
            
            level = "info" if success else "warning"
            message = f"Security event: {event_type} for user {user_id}"
            getattr(self._security_logger, level)(message, log_data)
    
    def _log_permission_event(self, user_id: str, resource: str, action: str,
                            granted: bool, extra: Dict[str, Any] = None):
        """Log permission check event"""
        self._security_logger.log_permission_check(user_id, resource, action, granted)

####################
# Enhanced Table Classes
####################

def enhance_table_with_logging(table_class):
    """Enhance existing table class with logging capabilities"""
    
    class LoggingEnhancedTable(table_class, DatabaseLoggingMixin):
        """Enhanced table class with logging"""
        
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
        
        @log_database_operation("insert")
        def insert_new_record(self, *args, **kwargs):
            """Enhanced insert with logging"""
            return super().insert_new_record(*args, **kwargs) if hasattr(super(), 'insert_new_record') else None
        
        @log_database_operation("select")
        def get_record_by_id(self, *args, **kwargs):
            """Enhanced get with logging"""
            return super().get_record_by_id(*args, **kwargs) if hasattr(super(), 'get_record_by_id') else None
        
        @log_database_operation("update")
        def update_record_by_id(self, *args, **kwargs):
            """Enhanced update with logging"""
            return super().update_record_by_id(*args, **kwargs) if hasattr(super(), 'update_record_by_id') else None
        
        @log_database_operation("delete")
        def delete_record_by_id(self, *args, **kwargs):
            """Enhanced delete with logging"""
            return super().delete_record_by_id(*args, **kwargs) if hasattr(super(), 'delete_record_by_id') else None
    
    return LoggingEnhancedTable

####################
# Utility Functions
####################

def log_model_operation(model_name: str, operation: str, record_id: str = None,
                       user_id: str = None, success: bool = True, 
                       execution_time: float = None, error: str = None):
    """Utility function to log model operations"""
    logger = get_logger(f"finx.models.{model_name.lower()}")
    
    log_data = {
        "model": model_name,
        "operation": operation,
        "success": success
    }
    
    if record_id:
        log_data["record_id"] = record_id
    if user_id:
        log_data["user_id"] = user_id
    if execution_time:
        log_data["execution_time"] = execution_time
    if error:
        log_data["error"] = error
    
    if success:
        logger.info(f"{model_name} {operation} completed", log_data)
    else:
        logger.error(f"{model_name} {operation} failed", log_data)

def setup_model_logging():
    """Setup logging for all models"""
    from finx.config.logging_config import auto_setup_logging
    
    # Auto-setup logging based on environment
    auto_setup_logging()
    
    # Log that logging has been initialized
    logger = get_logger("finx.system")
    logger.info("Logging system initialized", {
        "component": "models",
        "status": "ready"
    })

####################
# Context Managers
####################

class LoggedOperation:
    """Context manager for logging operations"""
    
    def __init__(self, operation_name: str, logger_name: str = "finx.operations",
                 log_level: str = "INFO", extra: Dict[str, Any] = None):
        self.operation_name = operation_name
        self.logger = get_logger(logger_name)
        self.log_level = log_level
        self.extra = extra or {}
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        self.logger.log(
            getattr(self.logger, self.log_level.lower()),
            f"Starting operation: {self.operation_name}",
            extra={**self.extra, "operation": self.operation_name, "status": "started"}
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        execution_time = time.time() - self.start_time
        
        if exc_type is None:
            # Success
            self.logger.log(
                getattr(self.logger, self.log_level.lower()),
                f"Operation completed: {self.operation_name}",
                extra={
                    **self.extra,
                    "operation": self.operation_name,
                    "status": "completed",
                    "execution_time": execution_time
                }
            )
        else:
            # Error
            self.logger.error(
                f"Operation failed: {self.operation_name}",
                extra={
                    **self.extra,
                    "operation": self.operation_name,
                    "status": "failed",
                    "execution_time": execution_time,
                    "error_type": exc_type.__name__,
                    "error_message": str(exc_val)
                }
            )
        
        return False  # Don't suppress exceptions
