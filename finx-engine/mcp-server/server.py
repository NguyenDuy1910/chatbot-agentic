"""
MCP Server for FinX Text-to-SQL Chatbot
Provides tools for Confluence search, vector database search, and MDL generation
"""

import logging
import asyncio
import json
from typing import Any, Dict, List, Optional
from mcp.server import Server
from mcp.types import Tool, TextContent, ToolResult

from config import get_config, setup_logging, validate_config
from providers.google_ai import GoogleAIProvider
from providers.confluence import ConfluenceProvider
from providers.vector_db import VectorDatabaseProvider
from tools.confluence_search import ConfluenceSearchTool
from tools.vector_search import VectorSearchTool
from tools.mdl_generator import MDLGeneratorTool


logger = logging.getLogger(__name__)


class FinxMCPServer:
    """MCP Server for FinX text-to-SQL system"""
    
    def __init__(self):
        """Initialize MCP server"""
        self.config = get_config()
        setup_logging(self.config)
        
        # Validate configuration
        validation = validate_config(self.config)
        if not validation["valid"]:
            logger.warning("Configuration validation warnings:")
            for error in validation["errors"]:
                logger.warning(f"  - {error}")
        
        # Initialize providers
        self.google_ai_provider = GoogleAIProvider(self.config)
        self.confluence_provider = ConfluenceProvider(self.config)
        self.vector_db_provider = VectorDatabaseProvider(self.config)
        
        # Initialize tools
        self.confluence_tool = ConfluenceSearchTool(self.confluence_provider)
        self.vector_tool = VectorSearchTool(self.vector_db_provider)
        self.mdl_tool = MDLGeneratorTool(self.google_ai_provider, self.config)
        
        # Initialize MCP server
        self.server = Server(self.config.mcp_server_name)
        self._register_tools()
        
        logger.info(f"FinX MCP Server initialized (v{self.config.mcp_server_version})")
    
    def _register_tools(self):
        """Register all MCP tools"""
        all_tools = []
        
        # Register Confluence tools
        if self.confluence_provider.is_available():
            all_tools.extend(self.confluence_tool.get_tool_definitions())
            logger.info("Confluence tools registered")
        else:
            logger.warning("Confluence tools not available")
        
        # Register vector search tools
        if self.vector_db_provider.is_available():
            all_tools.extend(self.vector_tool.get_tool_definitions())
            logger.info("Vector search tools registered")
        else:
            logger.warning("Vector search tools not available")
        
        # Register MDL generation tools
        all_tools.extend(self.mdl_tool.get_tool_definitions())
        logger.info("MDL generation tools registered")
        
        # Register tools with MCP server
        for tool_def in all_tools:
            self.server.add_tool(
                Tool(
                    name=tool_def["name"],
                    description=tool_def["description"],
                    inputSchema=tool_def["inputSchema"]
                )
            )
    
    async def handle_tool_call(self, tool_name: str, tool_input: Dict[str, Any]) -> str:
        """Handle tool calls from MCP"""
        logger.info(f"Handling tool call: {tool_name}")
        
        try:
            # Route to appropriate tool
            if tool_name.startswith("confluence_"):
                result = await self.confluence_tool.handle_tool_call(tool_name, tool_input)
            elif tool_name.startswith("vector_"):
                result = await self.vector_tool.handle_tool_call(tool_name, tool_input)
            elif tool_name.startswith("mdl_"):
                result = await self.mdl_tool.handle_tool_call(tool_name, tool_input)
            else:
                result = json.dumps({"error": f"Unknown tool: {tool_name}"})
            
            logger.info(f"Tool call completed: {tool_name}")
            return result
            
        except Exception as e:
            logger.error(f"Error handling tool call {tool_name}: {e}")
            return json.dumps({"error": str(e)})
    
    async def run(self):
        """Run the MCP server"""
        logger.info("Starting FinX MCP Server...")
        
        # Set up tool call handler
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            result = await self.handle_tool_call(name, arguments)
            return [TextContent(type="text", text=result)]
        
        # Start server
        async with self.server:
            logger.info("FinX MCP Server is running")
            await asyncio.Event().wait()


async def main():
    """Main entry point"""
    server = FinxMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())

