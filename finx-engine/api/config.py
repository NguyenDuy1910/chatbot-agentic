from pydantic_settings import BaseSettings
from typing import List
from pathlib import Path


class Settings(BaseSettings):
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = True

    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    STORAGE_FILE: str = "data/datasources/datasources.json"
    MDL_STORAGE_DIR: str = "data/mdl"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

Path(settings.STORAGE_FILE).parent.mkdir(parents=True, exist_ok=True)
Path(settings.MDL_STORAGE_DIR).mkdir(parents=True, exist_ok=True)

