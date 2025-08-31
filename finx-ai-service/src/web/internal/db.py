import json
import logging
from contextlib import contextmanager
from typing import Any, Optional, Generator, Dict
from sqlalchemy import Dialect, create_engine, MetaData, types, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, Session
from sqlalchemy.pool import QueuePool
from sqlalchemy.sql.type_api import _T
from typing_extensions import Self
from supabase import create_client, Client

# Import configuration and providers
from src.web.constants.config import (
    SRC_LOG_LEVELS,
    DATABASE_PROVIDER
) 
from src.web.internal.database_providers import (
    get_provider_instance,
    DatabaseProvider
)

# Setup logging
log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["DB"])

# Create SQLAlchemy base
Base = declarative_base()

# Global variables for database connection
engine = None
SessionLocal = None
supabase_client: Optional[Client] = None
_db_provider: Optional[DatabaseProvider] = None
class JSONField(types.TypeDecorator):
    impl = types.Text
    cache_ok = True

    def process_bind_param(self, value: Optional[_T], dialect: Dialect) -> Any:
        return json.dumps(value)

    def process_result_value(self, value: Optional[_T], dialect: Dialect) -> Any:
        if value is not None:
            return json.loads(value)

    def copy(self, **kw: Any) -> Self:
        return JSONField(self.impl.length)

    def db_value(self, value):
        return json.dumps(value)

    def python_value(self, value):
        if value is not None:
            return json.loads(value)


def get_database_provider() -> DatabaseProvider:
    """
    Get database provider instance
    """
    global _db_provider

    if _db_provider is None:
        _db_provider = get_provider_instance()
        log.info(f"Database provider initialized: {DATABASE_PROVIDER}")

    return _db_provider


def init_supabase() -> Optional[Client]:
    """
    Initialize Supabase client (only if using Supabase provider)
    """
    global supabase_client

    if DATABASE_PROVIDER == "supabase" and supabase_client is None:
        provider = get_database_provider()
        supabase_client = provider.get_client()
        log.info("Supabase client initialized")

    return supabase_client


def init_database():
    """
    Initialize database connection and session using provider
    """
    global engine, SessionLocal

    if engine is None:
        provider = get_database_provider()

        # Create engine using provider
        engine = provider.create_engine()

        # Create session factory using provider
        SessionLocal = provider.create_session_factory()

        # Set up event listeners after engine is created
        setup_event_listeners()

        log.info(f"Database initialized with {provider.__class__.__name__}")

    return engine, SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    Get database session for dependency injection
    """
    if SessionLocal is None:
        init_database()

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_supabase() -> Optional[Client]:
    """
    Get Supabase client for dependency injection (only if using Supabase)
    """
    if DATABASE_PROVIDER == "supabase":
        if supabase_client is None:
            init_supabase()
        return supabase_client
    else:
        return None


@contextmanager
def get_db_context():
    """
    Context manager for database sessions
    """
    if SessionLocal is None:
        init_database()

    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def create_tables():
    """
    Create all tables in the database
    """
    if engine is None:
        init_database()

    Base.metadata.create_all(bind=engine)
    log.info("Database tables created")


def drop_tables():
    """
    Drop all tables in the database (use with caution!)
    """
    if engine is None:
        init_database()

    Base.metadata.drop_all(bind=engine)
    log.info("Database tables dropped")


def test_connection() -> bool:
    """
    Test database connection using current provider
    """
    try:
        provider = get_database_provider()
        return provider.test_connection()
    except Exception as e:
        log.error(f"Connection test failed: {e}")
        return False


def get_provider_info() -> Dict[str, Any]:
    """
    Get information about current database provider
    """
    provider = get_database_provider()
    return {
        "provider": DATABASE_PROVIDER,
        "provider_class": provider.__class__.__name__,
        "connection_url": provider.get_connection_url() if hasattr(provider, 'get_connection_url') else None,
        "has_client": provider.get_client() is not None if hasattr(provider, 'get_client') else False
    }


def setup_event_listeners():
    """
    Set up database event listeners after engine is created
    """
    global engine
    if engine is not None:
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            """
            Set database connection parameters
            """
            # This is mainly for PostgreSQL optimizations
            pass


# Event listeners will be set up after engine initialization