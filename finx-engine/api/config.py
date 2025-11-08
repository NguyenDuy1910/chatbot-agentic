"""
API Configuration for FinX Engine
"""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""
    
    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 9000
    DEBUG: bool = False
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8000"
    ]
    
    # Storage
    STORAGE_PATH: str = "./data"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True
    )


settings = Settings()
