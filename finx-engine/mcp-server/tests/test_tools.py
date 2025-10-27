"""
Tests for MCP tools
"""

import pytest
import json
import asyncio
from tools.confluence_search import ConfluenceSearchTool
from tools.vector_search import VectorSearchTool
from tools.mdl_generator import MDLGeneratorTool


class TestConfluenceSearchTool:
    """Tests for Confluence search tool"""
    
    def test_get_tool_definitions(self, mock_confluence_provider):
        """Test tool definitions"""
        tool = ConfluenceSearchTool(mock_confluence_provider)
        definitions = tool.get_tool_definitions()
        
        assert len(definitions) == 3
        assert definitions[0]["name"] == "confluence_search"
        assert definitions[1]["name"] == "confluence_get_page"
        assert definitions[2]["name"] == "confluence_search_by_label"
    
    def test_search_content(self, mock_confluence_provider):
        """Test search content"""
        tool = ConfluenceSearchTool(mock_confluence_provider)
        result = tool.search_content("test query")
        
        assert result["success"] is True
        assert result["query"] == "test query"
        assert len(result["results"]) > 0
    
    def test_get_page(self, mock_confluence_provider):
        """Test get page"""
        tool = ConfluenceSearchTool(mock_confluence_provider)
        result = tool.get_page("123")
        
        assert result["success"] is True
        assert result["page"]["id"] == "123"
        assert result["page"]["title"] == "Test Page"
    
    def test_search_by_label(self, mock_confluence_provider):
        """Test search by label"""
        tool = ConfluenceSearchTool(mock_confluence_provider)
        result = tool.search_by_label("test")
        
        assert result["success"] is True
        assert result["label"] == "test"
        assert len(result["results"]) > 0
    
    @pytest.mark.asyncio
    async def test_handle_tool_call(self, mock_confluence_provider):
        """Test handle tool call"""
        tool = ConfluenceSearchTool(mock_confluence_provider)
        result_str = await tool.handle_tool_call(
            "confluence_search",
            {"query": "test"}
        )
        result = json.loads(result_str)
        
        assert result["success"] is True


class TestVectorSearchTool:
    """Tests for vector search tool"""
    
    def test_get_tool_definitions(self, mock_vector_db_provider):
        """Test tool definitions"""
        tool = VectorSearchTool(mock_vector_db_provider)
        definitions = tool.get_tool_definitions()
        
        assert len(definitions) == 3
        assert definitions[0]["name"] == "vector_search_similar"
        assert definitions[1]["name"] == "vector_search_by_text"
        assert definitions[2]["name"] == "vector_get_collection_info"
    
    def test_search_similar(self, mock_vector_db_provider):
        """Test search similar"""
        tool = VectorSearchTool(mock_vector_db_provider)
        query_vector = [0.1] * 768
        result = tool.search_similar(query_vector)
        
        assert result["success"] is True
        assert len(result["results"]) > 0
    
    def test_search_by_text(self, mock_vector_db_provider, mock_embedder):
        """Test search by text"""
        tool = VectorSearchTool(mock_vector_db_provider, mock_embedder)
        result = tool.search_by_text("test query")
        
        assert result["success"] is True
        assert result["query"] == "test query"
    
    def test_get_collection_info(self, mock_vector_db_provider):
        """Test get collection info"""
        tool = VectorSearchTool(mock_vector_db_provider)
        result = tool.get_collection_info()
        
        assert result["success"] is True
        assert result["collection"]["name"] == "test_collection"
    
    @pytest.mark.asyncio
    async def test_handle_tool_call(self, mock_vector_db_provider):
        """Test handle tool call"""
        tool = VectorSearchTool(mock_vector_db_provider)
        result_str = await tool.handle_tool_call(
            "vector_get_collection_info",
            {}
        )
        result = json.loads(result_str)
        
        assert result["success"] is True


class TestMDLGeneratorTool:
    """Tests for MDL generator tool"""
    
    def test_get_tool_definitions(self, mock_google_ai_provider, mock_config):
        """Test tool definitions"""
        tool = MDLGeneratorTool(mock_google_ai_provider, mock_config)
        definitions = tool.get_tool_definitions()
        
        assert len(definitions) == 3
        assert definitions[0]["name"] == "mdl_generate_from_requirements"
        assert definitions[1]["name"] == "mdl_generate_from_schema"
        assert definitions[2]["name"] == "mdl_validate_syntax"
    
    def test_generate_from_requirements(self, mock_google_ai_provider, mock_config):
        """Test generate from requirements"""
        tool = MDLGeneratorTool(mock_google_ai_provider, mock_config)
        result = tool.generate_from_requirements(
            "Test requirements",
            "test_model"
        )
        
        assert result["success"] is True
        assert result["model_name"] == "test_model"
        assert "mdl_content" in result
    
    def test_generate_from_schema(self, mock_google_ai_provider, mock_config):
        """Test generate from schema"""
        tool = MDLGeneratorTool(mock_google_ai_provider, mock_config)
        result = tool.generate_from_schema(
            "CREATE TABLE test...",
            "test_model"
        )
        
        assert result["success"] is True
        assert result["model_name"] == "test_model"
    
    def test_validate_syntax(self, mock_google_ai_provider, mock_config):
        """Test validate syntax"""
        tool = MDLGeneratorTool(mock_google_ai_provider, mock_config)
        result = tool.validate_syntax("MODEL test { }")
        
        assert result["success"] is True
        assert "validation_report" in result
    
    @pytest.mark.asyncio
    async def test_handle_tool_call(self, mock_google_ai_provider, mock_config):
        """Test handle tool call"""
        tool = MDLGeneratorTool(mock_google_ai_provider, mock_config)
        result_str = await tool.handle_tool_call(
            "mdl_validate_syntax",
            {"mdl_content": "MODEL test { }"}
        )
        result = json.loads(result_str)
        
        assert result["success"] is True

