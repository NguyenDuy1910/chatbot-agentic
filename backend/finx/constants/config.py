"""
Configuration constants for the FinX application
"""
import os
import logging
from typing import Dict, Any

# Logging levels configuration
SRC_LOG_LEVELS = {
    "DB": logging.INFO,
    "API": logging.INFO,
    "AUTH": logging.INFO,
    "CONNECTIONS": logging.INFO,
    "HEALTH": logging.INFO,
    "SECURITY": logging.WARNING,
    "DEFAULT": logging.INFO
}

# Database configuration
DATABASE_CONFIG = {
    "POOL_SIZE": 10,
    "MAX_OVERFLOW": 20,
    "POOL_TIMEOUT": 30,
    "POOL_RECYCLE": 3600,
    "ECHO": os.getenv("DB_ECHO", "false").lower() == "true"
}

# Database provider configuration
DATABASE_PROVIDER = os.getenv("DATABASE_PROVIDER", "supabase").lower()  # "supabase" or "postgresql"

# Supabase configuration
SUPABASE_CONFIG = {
    "URL": os.getenv("SUPABASE_URL"),
    "ANON_KEY": os.getenv("SUPABASE_ANON_KEY"),
    "SERVICE_ROLE_KEY": os.getenv("SUPABASE_SERVICE_ROLE_KEY"),
    "DB_URL": os.getenv("SUPABASE_DB_URL"),
    "JWT_SECRET": os.getenv("SUPABASE_JWT_SECRET")
}

# Local PostgreSQL configuration
POSTGRESQL_CONFIG = {
    "HOST": os.getenv("POSTGRES_HOST", "localhost"),
    "PORT": int(os.getenv("POSTGRES_PORT", "5432")),
    "DATABASE": os.getenv("POSTGRES_DATABASE", "finx_db"),
    "USERNAME": os.getenv("POSTGRES_USERNAME", "postgres"),
    "PASSWORD": os.getenv("POSTGRES_PASSWORD", ""),
    "SCHEMA": os.getenv("POSTGRES_SCHEMA", "public")
}

# API configuration
API_CONFIG = {
    "HOST": os.getenv("API_HOST", "0.0.0.0"),
    "PORT": int(os.getenv("API_PORT", "8000")),
    "DEBUG": os.getenv("API_DEBUG", "false").lower() == "true",
    "RELOAD": os.getenv("API_RELOAD", "false").lower() == "true",
    "CORS_ORIGINS": os.getenv("CORS_ORIGINS", "*").split(","),
    "API_PREFIX": "/api/v1"
}

# Security configuration
SECURITY_CONFIG = {
    "SECRET_KEY": os.getenv("SECRET_KEY", "your-secret-key-change-in-production"),
    "ALGORITHM": "HS256",
    "ACCESS_TOKEN_EXPIRE_MINUTES": int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")),
    "REFRESH_TOKEN_EXPIRE_DAYS": int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
}

# Connection health check configuration
HEALTH_CHECK_CONFIG = {
    "DEFAULT_INTERVAL": 300,  # 5 minutes
    "DEFAULT_TIMEOUT": 10,
    "MAX_RETRIES": 3,
    "RETRY_DELAY": 5
}

# Rate limiting configuration
RATE_LIMIT_CONFIG = {
    "DEFAULT_REQUESTS": 100,
    "DEFAULT_PERIOD": 60,  # 1 minute
    "BURST_REQUESTS": 200,
    "BURST_PERIOD": 10
}

def get_database_url() -> str:
    """
    Get the database URL for SQLAlchemy connection based on provider
    """
    if DATABASE_PROVIDER == "supabase":
        db_url = SUPABASE_CONFIG["DB_URL"]
        if not db_url:
            raise ValueError("SUPABASE_DB_URL environment variable is required when using Supabase")
        return db_url

    elif DATABASE_PROVIDER == "postgresql":
        # Build PostgreSQL connection string
        host = POSTGRESQL_CONFIG["HOST"]
        port = POSTGRESQL_CONFIG["PORT"]
        database = POSTGRESQL_CONFIG["DATABASE"]
        username = POSTGRESQL_CONFIG["USERNAME"]
        password = POSTGRESQL_CONFIG["PASSWORD"]

        if not all([host, database, username]):
            raise ValueError("POSTGRES_HOST, POSTGRES_DATABASE, and POSTGRES_USERNAME are required for PostgreSQL")

        # Build connection string
        if password:
            db_url = f"postgresql://{username}:{password}@{host}:{port}/{database}"
        else:
            db_url = f"postgresql://{username}@{host}:{port}/{database}"

        return db_url

    else:
        raise ValueError(f"Unsupported database provider: {DATABASE_PROVIDER}. Use 'supabase' or 'postgresql'")

def validate_config() -> Dict[str, Any]:
    """
    Validate required configuration values based on database provider
    """
    errors = []

    # Validate database provider
    if DATABASE_PROVIDER not in ["supabase", "postgresql"]:
        errors.append(f"Invalid DATABASE_PROVIDER: {DATABASE_PROVIDER}. Must be 'supabase' or 'postgresql'")
        return {"valid": False, "errors": errors}

    # Check required config based on provider
    if DATABASE_PROVIDER == "supabase":
        required_supabase = ["URL", "ANON_KEY", "DB_URL"]
        for key in required_supabase:
            if not SUPABASE_CONFIG[key]:
                errors.append(f"SUPABASE_{key} environment variable is required when using Supabase")

    elif DATABASE_PROVIDER == "postgresql":
        required_postgres = ["HOST", "DATABASE", "USERNAME"]
        for key in required_postgres:
            if not POSTGRESQL_CONFIG[key]:
                errors.append(f"POSTGRES_{key} environment variable is required when using PostgreSQL")

    # Check secret key in production
    if not API_CONFIG["DEBUG"] and SECURITY_CONFIG["SECRET_KEY"] == "your-secret-key-change-in-production":
        errors.append("SECRET_KEY must be changed in production")

    if errors:
        return {"valid": False, "errors": errors}

    return {"valid": True, "errors": [], "provider": DATABASE_PROVIDER}

# Environment detection
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
IS_PRODUCTION = ENVIRONMENT == "production"
IS_DEVELOPMENT = ENVIRONMENT == "development"
IS_TESTING = ENVIRONMENT == "testing"
