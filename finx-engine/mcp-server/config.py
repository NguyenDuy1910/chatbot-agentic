
import os
import logging
from typing import Optional
from pydantic_settings import BaseSettings


class MCPServerConfig(BaseSettings):
    """MCP Server configuration"""
    
    # Google AI Configuration
    google_api_key: str = os.getenv("GOOGLE_API_KEY", "")
    google_model: str = os.getenv("GOOGLE_MODEL", "gemini-2.0-flash-exp")
    google_timeout: int = int(os.getenv("GOOGLE_TIMEOUT", "600"))
    
    # Confluence Configuration
    confluence_url: str = os.getenv("CONFLUENCE_URL", "")
    confluence_username: str = os.getenv("CONFLUENCE_USERNAME", "")
    confluence_api_token: str = os.getenv("CONFLUENCE_API_TOKEN", "")
    confluence_space_key: Optional[str] = os.getenv("CONFLUENCE_SPACE_KEY", None)
    
    # Vector Database Configuration
    qdrant_url: str = os.getenv("QDRANT_URL", "http://localhost:6333")
    qdrant_api_key: Optional[str] = os.getenv("QDRANT_API_KEY", None)
    qdrant_collection_name: str = os.getenv("QDRANT_COLLECTION_NAME", "business_requirements")
    
    # MCP Server Configuration
    mcp_server_name: str = "finx-mcp-server"
    mcp_server_version: str = "1.0.0"
    
    # Logging Configuration
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # MDL Generation Configuration
    mdl_output_dir: str = os.getenv("MDL_OUTPUT_DIR", "./generated_mdl")
    mdl_include_descriptions: bool = os.getenv("MDL_INCLUDE_DESCRIPTIONS", "true").lower() == "true"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


def get_config() -> MCPServerConfig:
    """Get MCP server configuration"""
    return MCPServerConfig()


def setup_logging(config: MCPServerConfig) -> logging.Logger:
    """Setup logging for MCP server"""
    logging.basicConfig(
        level=getattr(logging, config.log_level),
        format=config.log_format
    )
    return logging.getLogger(__name__)


def validate_config(config: MCPServerConfig) -> dict:
    """Validate configuration"""
    errors = []
    
    # Validate Google AI configuration
    if not config.google_api_key:
        errors.append("GOOGLE_API_KEY is required")
    
    # Validate Confluence configuration (optional but warn if not set)
    if not config.confluence_url:
        logging.warning("CONFLUENCE_URL not set - Confluence tool will not be available")
    elif not config.confluence_username or not config.confluence_api_token:
        errors.append("CONFLUENCE_USERNAME and CONFLUENCE_API_TOKEN are required if CONFLUENCE_URL is set")
    
    # Validate Qdrant configuration (optional but warn if not set)
    if not config.qdrant_url:
        logging.warning("QDRANT_URL not set - Vector database tool will not be available")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }

