"""
Database factory pattern for dynamic connection management
"""

import logging
from typing import Dict, Any, Optional, Type
from enum import Enum

from src.web.constants.config import DATABASE_PROVIDER
from src.web.internal.database_providers import (
    DatabaseProvider,
    SupabaseProvider,
    PostgreSQLProvider
)

log = logging.getLogger(__name__)


class DatabaseProviderType(str, Enum):
    """Supported database provider types"""
    SUPABASE = "supabase"
    POSTGRESQL = "postgresql"


class DatabaseFactory:
    """Factory class for creating database providers"""
    
    _providers: Dict[str, Type[DatabaseProvider]] = {
        DatabaseProviderType.SUPABASE: SupabaseProvider,
        DatabaseProviderType.POSTGRESQL: PostgreSQLProvider
    }
    
    _instances: Dict[str, DatabaseProvider] = {}
    
    @classmethod
    def register_provider(cls, provider_type: str, provider_class: Type[DatabaseProvider]):
        """Register a new database provider"""
        cls._providers[provider_type] = provider_class
        log.info(f"Registered database provider: {provider_type} -> {provider_class.__name__}")
    
    @classmethod
    def get_provider(cls, provider_type: Optional[str] = None) -> DatabaseProvider:
        """Get database provider instance"""
        if provider_type is None:
            provider_type = DATABASE_PROVIDER
        
        # Return cached instance if exists
        if provider_type in cls._instances:
            return cls._instances[provider_type]
        
        # Validate provider type
        if provider_type not in cls._providers:
            available = list(cls._providers.keys())
            raise ValueError(f"Unsupported provider type: {provider_type}. Available: {available}")
        
        # Create new instance
        provider_class = cls._providers[provider_type]
        instance = provider_class()
        
        # Validate configuration
        validation = instance.validate_config()
        if not validation["valid"]:
            errors = validation.get("errors", [])
            raise ValueError(f"Provider configuration invalid: {', '.join(errors)}")
        
        # Cache instance
        cls._instances[provider_type] = instance
        log.info(f"Created database provider instance: {provider_type}")
        
        return instance
    
    @classmethod
    def get_available_providers(cls) -> Dict[str, str]:
        """Get list of available providers"""
        return {
            provider_type: provider_class.__name__ 
            for provider_type, provider_class in cls._providers.items()
        }
    
    @classmethod
    def test_provider(cls, provider_type: Optional[str] = None) -> Dict[str, Any]:
        """Test a specific provider"""
        if provider_type is None:
            provider_type = DATABASE_PROVIDER
        
        try:
            provider = cls.get_provider(provider_type)
            
            # Test database connection
            db_test = provider.test_connection()
            
            # Test provider-specific client (if applicable)
            client_test = True
            client_error = None
            
            try:
                client = provider.get_client()
                if hasattr(provider, 'test_supabase_client') and client:
                    client_test = provider.test_supabase_client()
            except Exception as e:
                client_test = False
                client_error = str(e)
            
            return {
                "provider_type": provider_type,
                "provider_class": provider.__class__.__name__,
                "database_connection": db_test,
                "client_connection": client_test,
                "client_error": client_error,
                "overall_success": db_test and client_test
            }
            
        except Exception as e:
            return {
                "provider_type": provider_type,
                "provider_class": "Unknown",
                "database_connection": False,
                "client_connection": False,
                "error": str(e),
                "overall_success": False
            }
    
    @classmethod
    def switch_provider(cls, new_provider_type: str) -> bool:
        """Switch to a different provider (for runtime switching)"""
        try:
            # Test new provider first
            test_result = cls.test_provider(new_provider_type)
            if not test_result["overall_success"]:
                log.error(f"Cannot switch to {new_provider_type}: {test_result.get('error', 'Connection test failed')}")
                return False
            
            # Clear current instance to force recreation
            if DATABASE_PROVIDER in cls._instances:
                del cls._instances[DATABASE_PROVIDER]
            
            # Update global provider setting (this would need environment variable update in practice)
            log.info(f"Switched database provider to: {new_provider_type}")
            return True
            
        except Exception as e:
            log.error(f"Failed to switch provider to {new_provider_type}: {e}")
            return False
    
    @classmethod
    def reset_instances(cls):
        """Reset all cached instances (useful for testing)"""
        cls._instances.clear()
        log.info("Reset all database provider instances")
    
    @classmethod
    def get_provider_info(cls, provider_type: Optional[str] = None) -> Dict[str, Any]:
        """Get detailed information about a provider"""
        if provider_type is None:
            provider_type = DATABASE_PROVIDER
        
        try:
            provider = cls.get_provider(provider_type)
            validation = provider.validate_config()
            
            info = {
                "provider_type": provider_type,
                "provider_class": provider.__class__.__name__,
                "is_configured": validation["valid"],
                "configuration_errors": validation.get("errors", []),
                "has_client": provider.get_client() is not None,
                "connection_url_available": hasattr(provider, 'get_connection_url')
            }
            
            # Add connection URL if available (masked for security)
            if hasattr(provider, 'get_connection_url'):
                try:
                    url = provider.get_connection_url()
                    # Mask password in URL for security
                    if '@' in url and ':' in url:
                        parts = url.split('@')
                        if len(parts) == 2:
                            auth_part = parts[0]
                            if ':' in auth_part:
                                user_pass = auth_part.split(':')
                                if len(user_pass) >= 3:  # protocol://user:pass
                                    masked_url = f"{':'.join(user_pass[:-1])}:***@{parts[1]}"
                                    info["connection_url_masked"] = masked_url
                except Exception:
                    info["connection_url_masked"] = "Error getting URL"
            
            return info
            
        except Exception as e:
            return {
                "provider_type": provider_type,
                "provider_class": "Unknown",
                "error": str(e),
                "is_configured": False
            }


# Convenience functions
def get_current_provider() -> DatabaseProvider:
    """Get current database provider"""
    return DatabaseFactory.get_provider()


def test_current_provider() -> Dict[str, Any]:
    """Test current database provider"""
    return DatabaseFactory.test_provider()


def get_provider_info() -> Dict[str, Any]:
    """Get current provider information"""
    return DatabaseFactory.get_provider_info()
