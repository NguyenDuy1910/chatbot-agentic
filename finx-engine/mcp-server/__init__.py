"""
FinX MCP Server
Model Context Protocol server for text-to-SQL chatbot system
"""

__version__ = "1.0.0"
__author__ = "FinX Team"
__description__ = "MCP server for FinX text-to-SQL chatbot with Confluence, vector DB, and MDL generation"

from .server import FinxMCPServer
from .config import get_config, setup_logging, validate_config
from .providers import GoogleAIProvider, ConfluenceProvider, VectorDatabaseProvider
from .tools import ConfluenceSearchTool, VectorSearchTool, MDLGeneratorTool

__all__ = [
    "FinxMCPServer",
    "get_config",
    "setup_logging",
    "validate_config",
    "GoogleAIProvider",
    "ConfluenceProvider",
    "VectorDatabaseProvider",
    "ConfluenceSearchTool",
    "VectorSearchTool",
    "MDLGeneratorTool"
]

