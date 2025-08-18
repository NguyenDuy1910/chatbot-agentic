"""
Main FastAPI application for FinX Backend with Supabase integration
"""

import logging
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Import configuration and database
from finx.constants import (
    API_CONFIG,
    SECURITY_CONFIG,
    validate_config,
    SRC_LOG_LEVELS
)
from finx.internal.db import init_database, init_supabase, create_tables, get_db, get_supabase
from finx.internal.database_factory import get_current_provider, test_current_provider
from finx.routers import connections, users, chats, messages, knowledge, files, prompts, auth

# Setup logging
logging.basicConfig(
    level=SRC_LOG_LEVELS["DEFAULT"],
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events
    """
    # Startup
    logger.info("Starting FinX Backend Application...")
    
    # Validate configuration
    config_validation = validate_config()
    if not config_validation["valid"]:
        logger.error("Configuration validation failed:")
        for error in config_validation["errors"]:
            logger.error(f"  - {error}")
        raise RuntimeError("Invalid configuration")
    
    # Initialize database using factory pattern
    try:
        # Get current provider info
        provider = get_current_provider()
        logger.info(f"Using database provider: {provider.__class__.__name__}")

        # Initialize database
        # init_database()

        # # Initialize provider-specific client (if applicable)
        # init_supabase()

        # logger.info("Database initialized successfully")

        # # Create tables if they don't exist
        # create_tables()
        logger.info("Database tables ensured")

    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    
    logger.info("Application startup completed")
    
    yield
    
    # Shutdown
    logger.info("Shutting down FinX Backend Application...")


# Create FastAPI app
app = FastAPI(
    title="FinX Backend API",
    description="Backend API for FinX Chatbot Agentic with Supabase integration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    # allow_origins=API_CONFIG["CORS_ORIGINS"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers
app.include_router(
    auth.router,
    prefix=f"{API_CONFIG['API_PREFIX']}/auth",
    tags=["auth"]
)

app.include_router(
    connections.router,
    prefix=f"{API_CONFIG['API_PREFIX']}/connections",
    tags=["connections"]
)

app.include_router(
    users.router,
    prefix=f"{API_CONFIG['API_PREFIX']}/users",
    tags=["users"]
)

app.include_router(
    chats.router,
    prefix=f"{API_CONFIG['API_PREFIX']}/chats",
    tags=["chats"]
)

app.include_router(
    messages.router,
    prefix=f"{API_CONFIG['API_PREFIX']}/messages",
    tags=["messages"]
)

app.include_router(
    knowledge.router,
    prefix=f"{API_CONFIG['API_PREFIX']}/knowledge",
    tags=["knowledge"]
)

app.include_router(
    files.router,
    prefix=f"{API_CONFIG['API_PREFIX']}/files",
    tags=["files"]
)

app.include_router(
    prompts.router,
    prefix=f"{API_CONFIG['API_PREFIX']}/prompts",
    tags=["prompts"]
)


@app.get("/")
async def root():
    """
    Root endpoint
    """
    return {
        "message": "FinX Backend API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint using factory pattern
    """
    from datetime import datetime

    try:
        # Test current provider
        test_result = test_current_provider()

        db_status = "healthy" if test_result["database_connection"] else "unhealthy"
        client_status = "healthy" if test_result["client_connection"] else "unhealthy"
        overall_status = "healthy" if test_result["overall_success"] else "unhealthy"

        # Get provider info
        provider = get_current_provider()

        return {
            "status": overall_status,
            "provider": provider.__class__.__name__,
            "database": db_status,
            "client": client_status,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }


@app.get("/config")
async def get_config():
    """
    Get application configuration (non-sensitive data only)
    """
    return {
        "api": {
            "host": API_CONFIG["HOST"],
            "port": API_CONFIG["PORT"],
            "debug": API_CONFIG["DEBUG"],
            "api_prefix": API_CONFIG["API_PREFIX"]
        },
        "cors_origins": API_CONFIG["CORS_ORIGINS"],
        "environment": "development"  # You might want to get this from config
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred"
        }
    )


if __name__ == "__main__":
    # Run the application
    uvicorn.run(
        "main:app",
        host=API_CONFIG["HOST"],
        port=API_CONFIG["PORT"],
        reload=API_CONFIG["RELOAD"],
        log_level="info"
    )
