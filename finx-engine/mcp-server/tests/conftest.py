"""
Pytest configuration and fixtures for MCP Server tests
"""

import pytest
import os
from unittest.mock import Mock, MagicMock
from config import MCPServerConfig


@pytest.fixture
def mock_config():
    """Create a mock configuration for testing"""
    config = MCPServerConfig(
        google_api_key="test_key",
        google_model="gemini-2.0-flash-exp",
        confluence_url="https://test.atlassian.net",
        confluence_username="test@example.com",
        confluence_api_token="test_token",
        qdrant_url="http://localhost:6333",
        qdrant_collection_name="test_collection"
    )
    return config


@pytest.fixture
def mock_google_ai_provider(mock_config):
    """Create a mock Google AI provider"""
    from providers.google_ai import GoogleAIProvider
    
    provider = Mock(spec=GoogleAIProvider)
    provider.generate_text = Mock(return_value="Generated text response")
    provider.generate_json = Mock(return_value={"key": "value"})
    provider.analyze_text = Mock(return_value="Analysis result")
    provider.get_model_info = Mock(return_value={"model": "gemini-2.0-flash-exp"})
    
    return provider


@pytest.fixture
def mock_confluence_provider(mock_config):
    """Create a mock Confluence provider"""
    from providers.confluence import ConfluenceProvider
    
    provider = Mock(spec=ConfluenceProvider)
    provider.is_available = Mock(return_value=True)
    provider.search_content = Mock(return_value=[
        {
            "id": "123",
            "title": "Test Page",
            "type": "page",
            "url": "https://test.atlassian.net/wiki/spaces/TEST/pages/123",
            "space": "TEST",
            "excerpt": "Test excerpt"
        }
    ])
    provider.get_page_content = Mock(return_value={
        "id": "123",
        "title": "Test Page",
        "content": "<p>Test content</p>",
        "labels": ["test"],
        "url": "https://test.atlassian.net/wiki/spaces/TEST/pages/123",
        "created": "2025-01-01T00:00:00Z",
        "updated": "2025-01-02T00:00:00Z"
    })
    provider.search_by_label = Mock(return_value=[
        {
            "id": "123",
            "title": "Test Page",
            "type": "page",
            "url": "https://test.atlassian.net/wiki/spaces/TEST/pages/123",
            "space": "TEST"
        }
    ])
    
    return provider


@pytest.fixture
def mock_vector_db_provider(mock_config):
    """Create a mock vector database provider"""
    from providers.vector_db import VectorDatabaseProvider
    
    provider = Mock(spec=VectorDatabaseProvider)
    provider.is_available = Mock(return_value=True)
    provider.search_similar = Mock(return_value=[
        {
            "id": "doc1",
            "score": 0.95,
            "payload": {"text": "Similar document"}
        }
    ])
    provider.search_by_text = Mock(return_value=[
        {
            "id": "doc1",
            "score": 0.95,
            "payload": {"text": "Similar document"}
        }
    ])
    provider.get_collection_info = Mock(return_value={
        "name": "test_collection",
        "points_count": 100,
        "vectors_count": 100,
        "config": {
            "distance": "Cosine",
            "vector_size": 768
        }
    })
    
    return provider


@pytest.fixture
def mock_embedder():
    """Create a mock embedder function"""
    def embedder(text: str):
        # Return a mock vector of size 768
        return [0.1] * 768
    
    return embedder

