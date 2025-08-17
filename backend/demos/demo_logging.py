#!/usr/bin/env python3
"""
Demo: How to use FINX Logging System in real applications
Shows practical examples of logging integration
"""

import sys
import time
import os
from pathlib import Path
from typing import Dict, Any

# Add backend to Python path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

def demo_basic_usage():
    """Demo basic logging usage"""
    print("📝 Basic Logging Usage Demo")
    print("-" * 40)
    
    # Setup logging for demo
    from finx.utils import setup_logging, get_logger, LogLevel, LogFormat
    
    setup_logging(
        level=LogLevel.INFO,
        format_type=LogFormat.STRUCTURED,
        log_dir="demos/logs",
        console_enabled=True,
        file_enabled=True
    )
    
    # Get logger for your module
    logger = get_logger("demo.basic")
    
    # Basic logging
    logger.info("Application started")
    logger.debug("Debug information (won't show with INFO level)")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    
    print("✅ Basic logging demo completed")

def demo_context_logging():
    """Demo context-aware logging"""
    print("\n🎯 Context Logging Demo")
    print("-" * 40)
    
    from finx.utils import get_logger
    
    # Create logger with context
    user_context = {
        "user_id": "user_12345",
        "session_id": "sess_abcdef",
        "ip_address": "192.168.1.100"
    }
    
    context_logger = get_logger("demo.context", user_context)
    
    # All logs will include the context
    context_logger.info("User logged in successfully")
    context_logger.info("User accessed dashboard", {
        "page": "dashboard",
        "load_time": 0.234
    })
    context_logger.warning("User attempted unauthorized action", {
        "action": "delete_user",
        "target_user": "user_67890"
    })
    
    print("✅ Context logging demo completed")

def demo_specialized_loggers():
    """Demo specialized loggers for different components"""
    print("\n🔧 Specialized Loggers Demo")
    print("-" * 40)
    
    from finx.utils import DatabaseLogger, APILogger, SecurityLogger
    
    # Database operations logging
    db_logger = DatabaseLogger("main_db")
    db_logger.log_query(
        "SELECT u.id, u.name FROM users u WHERE u.active = true",
        params={"active": True},
        execution_time=0.045
    )
    db_logger.log_connection_event("pool_exhausted", {
        "active_connections": 20,
        "max_connections": 20
    })
    
    # API operations logging
    api_logger = APILogger("/api/v1/users")
    api_logger.log_request("POST", "/api/v1/users", user_id="admin_123")
    api_logger.log_response(201, response_time=0.156)
    
    # Security events logging
    security_logger = SecurityLogger()
    security_logger.log_auth_attempt("user_12345", True, "192.168.1.100")
    security_logger.log_permission_check("user_12345", "users", "create", True)
    
    print("✅ Specialized loggers demo completed")

def demo_decorators():
    """Demo logging decorators"""
    print("\n🎨 Logging Decorators Demo")
    print("-" * 40)
    
    from finx.utils import log_function_call, log_performance
    
    @log_function_call("demo.functions", "INFO")
    def create_user(name: str, email: str) -> Dict[str, Any]:
        """Create a new user"""
        time.sleep(0.1)  # Simulate database operation
        return {
            "id": "user_12345",
            "name": name,
            "email": email,
            "created_at": time.time()
        }
    
    @log_performance("demo.performance", threshold_seconds=0.05)
    def slow_calculation(n: int) -> int:
        """Perform a slow calculation"""
        time.sleep(0.1)  # This will trigger performance warning
        return sum(range(n))
    
    # Use the decorated functions
    user = create_user("John Doe", "john@example.com")
    print(f"   Created user: {user['name']}")
    
    result = slow_calculation(100)
    print(f"   Calculation result: {result}")
    
    print("✅ Decorators demo completed")

def demo_integration_mixins():
    """Demo integration mixins for models"""
    print("\n🔗 Integration Mixins Demo")
    print("-" * 40)
    
    from finx.utils import DatabaseLoggingMixin, log_database_operation
    
    # Example model class with logging
    class UserModel(DatabaseLoggingMixin):
        __tablename__ = "users"
        
        def __init__(self):
            super().__init__()
        
        @log_database_operation("create")
        def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
            """Create a new user with logging"""
            # Simulate database operation
            time.sleep(0.05)
            
            user = {
                "id": "user_12345",
                "name": user_data["name"],
                "email": user_data["email"],
                "created_at": time.time()
            }
            
            return user
        
        @log_database_operation("read")
        def get_user_by_id(self, user_id: str) -> Dict[str, Any]:
            """Get user by ID with logging"""
            time.sleep(0.02)
            
            return {
                "id": user_id,
                "name": "John Doe",
                "email": "john@example.com"
            }
    
    # Use the model
    user_model = UserModel()
    
    new_user = user_model.create_user({
        "name": "Jane Smith",
        "email": "jane@example.com"
    })
    print(f"   Created user: {new_user['name']}")
    
    existing_user = user_model.get_user_by_id("user_12345")
    print(f"   Retrieved user: {existing_user['name']}")
    
    print("✅ Integration mixins demo completed")

def demo_context_manager():
    """Demo logging context manager"""
    print("\n📋 Context Manager Demo")
    print("-" * 40)
    
    from finx.utils import LoggedOperation
    
    # Use context manager for complex operations
    with LoggedOperation("user_registration", "demo.operations", extra={"source": "web_app"}):
        time.sleep(0.1)  # Simulate user validation
        print("   Validating user data...")
        
        time.sleep(0.05)  # Simulate database insert
        print("   Creating user record...")
        
        time.sleep(0.02)  # Simulate email sending
        print("   Sending welcome email...")
    
    # Example with error handling
    try:
        with LoggedOperation("risky_operation", "demo.operations"):
            time.sleep(0.05)
            raise ValueError("Something went wrong!")
    except ValueError:
        print("   Error was logged automatically")
    
    print("✅ Context manager demo completed")

def demo_environment_configs():
    """Demo different environment configurations"""
    print("\n⚙️ Environment Configurations Demo")
    print("-" * 40)
    
    from finx.config.logging_config import (
        LoggingConfigFactory, 
        mask_sensitive_data,
        performance_logger
    )
    
    # Show different environment configs
    environments = ["development", "production", "testing"]
    
    for env in environments:
        config = LoggingConfigFactory.create_config(env)
        print(f"   {env.upper()}:")
        print(f"     Level: {config.level}")
        print(f"     Format: {config.format_type}")
        print(f"     Console: {config.console_enabled}")
        print(f"     JSON: {config.json_enabled}")
    
    # Demo sensitive data masking
    sensitive_data = {
        "user_id": "user_12345",
        "password": "super_secret_password",
        "api_key": "sk-1234567890abcdef1234567890abcdef",
        "email": "user@example.com",
        "config": {
            "database_password": "db_secret_123",
            "redis_url": "redis://user:pass@localhost:6379"
        }
    }
    
    masked = mask_sensitive_data(sensitive_data)
    print(f"\n   Original data keys: {list(sensitive_data.keys())}")
    print(f"   Masked data: {masked}")
    
    # Demo performance logging
    performance_logger.log_slow_operation("complex_query", 2.5, threshold=1.0)
    performance_logger.log_resource_usage(cpu_percent=85.5, memory_mb=1024.0)
    
    print("✅ Environment configurations demo completed")

def demo_real_world_scenario():
    """Demo real-world logging scenario"""
    print("\n🌍 Real-World Scenario Demo")
    print("-" * 40)
    
    from finx.utils import get_logger, LoggedOperation
    
    # Simulate a complete user registration flow
    logger = get_logger("demo.registration")
    
    with LoggedOperation("user_registration_flow", "demo.registration"):
        # Step 1: Validate input
        logger.info("Starting user registration", {
            "step": "validation",
            "email": "new_user@example.com"
        })
        time.sleep(0.05)
        
        # Step 2: Check if user exists
        logger.info("Checking user existence", {
            "step": "duplicate_check",
            "email": "new_user@example.com"
        })
        time.sleep(0.1)
        
        # Step 3: Create user record
        logger.info("Creating user record", {
            "step": "database_insert",
            "user_id": "user_67890"
        })
        time.sleep(0.08)
        
        # Step 4: Send welcome email
        logger.info("Sending welcome email", {
            "step": "email_notification",
            "user_id": "user_67890",
            "email_template": "welcome_v2"
        })
        time.sleep(0.03)
        
        # Step 5: Log successful completion
        logger.info("User registration completed successfully", {
            "step": "completion",
            "user_id": "user_67890",
            "total_steps": 4
        })
    
    print("✅ Real-world scenario demo completed")

def main():
    """Main demo function"""
    print("🚀 FINX LOGGING SYSTEM USAGE DEMO")
    print("=" * 60)
    print("Demonstrating comprehensive logging in real applications")
    print("=" * 60)
    
    try:
        demo_basic_usage()
        demo_context_logging()
        demo_specialized_loggers()
        demo_decorators()
        demo_integration_mixins()
        demo_context_manager()
        demo_environment_configs()
        demo_real_world_scenario()
        
        print("\n" + "=" * 60)
        print("✅ ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("💡 Key Features Demonstrated:")
        print("   📝 Basic structured logging")
        print("   🎯 Context-aware logging")
        print("   🔧 Specialized component loggers")
        print("   🎨 Function decorators")
        print("   🔗 Model integration mixins")
        print("   📋 Context managers")
        print("   ⚙️ Environment configurations")
        print("   🌍 Real-world scenarios")
        print("\n📁 Check logs in: demos/logs/")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
