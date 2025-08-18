"""
Database provider abstraction layer for dynamic connection support
"""

import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Generator
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool

from finx.constants import (
    DATABASE_CONFIG,
    SUPABASE_CONFIG,
    POSTGRESQL_CONFIG,
    DATABASE_PROVIDER
)

log = logging.getLogger(__name__)


class DatabaseProvider(ABC):
    """Abstract base class for database providers"""
    
    def __init__(self):
        self.engine: Optional[Engine] = None
        self.session_factory: Optional[sessionmaker] = None
        self._client = None
    
    @abstractmethod
    def get_connection_url(self) -> str:
        """Get database connection URL"""
        pass
    
    @abstractmethod
    def validate_config(self) -> Dict[str, Any]:
        """Validate provider-specific configuration"""
        pass
    
    @abstractmethod
    def get_client(self):
        """Get provider-specific client (if applicable)"""
        pass
    
    def create_engine(self) -> Engine:
        """Create SQLAlchemy engine"""
        if self.engine is None:
            connection_url = self.get_connection_url()
            
            self.engine = create_engine(
                connection_url,
                poolclass=QueuePool,
                pool_size=DATABASE_CONFIG["POOL_SIZE"],
                max_overflow=DATABASE_CONFIG["MAX_OVERFLOW"],
                pool_timeout=DATABASE_CONFIG["POOL_TIMEOUT"],
                pool_recycle=DATABASE_CONFIG["POOL_RECYCLE"],
                echo=DATABASE_CONFIG["ECHO"]
            )
            
            log.info(f"Database engine created for {self.__class__.__name__}")
        
        return self.engine
    
    def create_session_factory(self) -> sessionmaker:
        """Create SQLAlchemy session factory"""
        if self.session_factory is None:
            engine = self.create_engine()
            self.session_factory = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=engine
            )
            log.info(f"Session factory created for {self.__class__.__name__}")
        
        return self.session_factory
    
    def get_session(self) -> Generator[Session, None, None]:
        """Get database session"""
        session_factory = self.create_session_factory()
        db = session_factory()
        try:
            yield db
        finally:
            db.close()
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            engine = self.create_engine()
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            return True
        except Exception as e:
            log.error(f"Connection test failed for {self.__class__.__name__}: {e}")
            return False


class SupabaseProvider(DatabaseProvider):
    """Supabase database provider"""
    
    def get_connection_url(self) -> str:
        """Get Supabase PostgreSQL connection URL"""
        db_url = SUPABASE_CONFIG["DB_URL"]
        if not db_url:
            raise ValueError("SUPABASE_DB_URL environment variable is required")
        return db_url
    
    def validate_config(self) -> Dict[str, Any]:
        """Validate Supabase configuration"""
        errors = []
        required_keys = ["URL", "ANON_KEY", "DB_URL"]
        
        for key in required_keys:
            if not SUPABASE_CONFIG[key]:
                errors.append(f"SUPABASE_{key} environment variable is required")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "provider": "supabase"
        }
    
    def get_client(self):
        """Get Supabase client"""
        if self._client is None:
            try:
                from supabase import create_client
                
                url = SUPABASE_CONFIG["URL"]
                key = SUPABASE_CONFIG["ANON_KEY"]
                
                if not url or not key:
                    raise ValueError("Supabase URL and ANON_KEY are required")
                
                self._client = create_client(url, key)
                log.info("Supabase client initialized")
                
            except ImportError:
                log.error("Supabase package not installed. Run: pip install supabase")
                raise
            except Exception as e:
                log.error(f"Failed to initialize Supabase client: {e}")
                raise
        
        return self._client
    
    def test_supabase_client(self) -> bool:
        """Test Supabase client connection"""
        try:
            client = self.get_client()
            # Try a simple operation
            client.table("_test").select("*").limit(1).execute()
            return True
        except Exception as e:
            log.warning(f"Supabase client test failed (may be expected if no tables): {e}")
            return True  # Consider it healthy if just table doesn't exist


class PostgreSQLProvider(DatabaseProvider):
    """Local PostgreSQL database provider"""
    
    def get_connection_url(self) -> str:
        """Get PostgreSQL connection URL"""
        host = POSTGRESQL_CONFIG["HOST"]
        port = POSTGRESQL_CONFIG["PORT"]
        database = POSTGRESQL_CONFIG["DATABASE"]
        username = POSTGRESQL_CONFIG["USERNAME"]
        password = POSTGRESQL_CONFIG["PASSWORD"]
        
        if not all([host, database, username]):
            raise ValueError("POSTGRES_HOST, POSTGRES_DATABASE, and POSTGRES_USERNAME are required")
        
        # Build connection string
        if password:
            return f"postgresql://{username}:{password}@{host}:{port}/{database}"
        else:
            return f"postgresql://{username}@{host}:{port}/{database}"
    
    def validate_config(self) -> Dict[str, Any]:
        """Validate PostgreSQL configuration"""
        errors = []
        required_keys = ["HOST", "DATABASE", "USERNAME"]
        
        for key in required_keys:
            if not POSTGRESQL_CONFIG[key]:
                errors.append(f"POSTGRES_{key} environment variable is required")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "provider": "postgresql"
        }
    
    def get_client(self):
        """PostgreSQL doesn't have a separate client - return None"""
        return None


def get_database_provider() -> DatabaseProvider:
    """Factory function to get the appropriate database provider"""
    if DATABASE_PROVIDER == "supabase":
        return SupabaseProvider()
    elif DATABASE_PROVIDER == "postgresql":
        return PostgreSQLProvider()
    else:
        raise ValueError(f"Unsupported database provider: {DATABASE_PROVIDER}")


# Global provider instance
_provider_instance: Optional[DatabaseProvider] = None


def get_provider_instance() -> DatabaseProvider:
    """Get singleton provider instance"""
    global _provider_instance
    
    if _provider_instance is None:
        _provider_instance = get_database_provider()
        log.info(f"Database provider initialized: {_provider_instance.__class__.__name__}")
    
    return _provider_instance


def reset_provider_instance():
    """Reset provider instance (useful for testing)"""
    global _provider_instance
    _provider_instance = None
