from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from api.routers import datasources, introspection, mdl
from api.config import settings
from api.storage import DataSourceStorage


@asynccontextmanager
async def lifespan(app: FastAPI):
    DataSourceStorage.load_from_file()
    yield
    DataSourceStorage.save_to_file()


app = FastAPI(
    title="FinX Engine API",
    description="Data source introspection and MDL generation API",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(datasources.router, prefix="/api/v1", tags=["datasources"])
app.include_router(introspection.router, prefix="/api/v1", tags=["introspection"])
app.include_router(mdl.router, prefix="/api/v1", tags=["mdl"])


@app.get("/")
async def root():
    return {
        "name": "FinX Engine API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "datasources_count": len(DataSourceStorage.list_all())
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": str(exc)}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )

