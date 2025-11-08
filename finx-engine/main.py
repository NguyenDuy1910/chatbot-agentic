"""
FinX Engine - Main Application

Database Schema Introspection & MDL Generation Service
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from api.routers import datasources, introspection, mdl
from api.config import settings
from api.storage import DataSourceStorage, MDLStorage


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Handles startup and shutdown events.
    """
    # Startup
    print("🚀 Starting FinX Engine...")
    
    # Load data from storage
    DataSourceStorage.load_from_file()
    MDLStorage.load_from_file()
    
    print(f"✅ Loaded {len(DataSourceStorage.list_all())} datasources")
    print(f"✅ Loaded {len(MDLStorage.list_all())} MDLs")
    print(f"🌐 Server running on http://{settings.API_HOST}:{settings.API_PORT}")
    print(f"📚 API docs available at http://{settings.API_HOST}:{settings.API_PORT}/docs")
    
    yield
    
    # Shutdown
    print("\n👋 Shutting down FinX Engine...")
    
    # Save data to storage
    DataSourceStorage.save_to_file()
    MDLStorage.save_to_file()
    
    print("💾 Data saved successfully")


# Create FastAPI application
app = FastAPI(
    title="FinX Engine API",
    description="Database Schema Introspection and MDL Generation Service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(datasources.router, prefix="/api/v1", tags=["datasources"])
app.include_router(introspection.router, prefix="/api/v1", tags=["introspection"])
app.include_router(mdl.router, prefix="/api/v1", tags=["mdl"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "FinX Engine API",
        "version": "1.0.0",
        "description": "Database Schema Introspection & MDL Generation Service",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    datasources_count = len(DataSourceStorage.list_all())
    mdls_count = len(MDLStorage.list_all())
    
    return {
        "status": "healthy",
        "service": "finx-engine",
        "version": "1.0.0",
        "datasources_count": datasources_count,
        "mdls_count": mdls_count
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "detail": str(exc),
            "type": type(exc).__name__
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
