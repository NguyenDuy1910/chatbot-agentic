"""
Test suite for DBSchema indexing pipeline

This module tests the database schema indexing functionality including:
- MDL validation
- DDL chunking
- Document embedding
- Schema indexing
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from haystack import Document
from haystack.document_stores.types import DuplicatePolicy

from src.pipelines.indexing.db_schema import DBSchema, DDLChunker

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# Mock Providers
# ============================================================================

class MockEmbedder:
    """Mock embedder for testing"""
    
    async def run(self, documents: List[Document]) -> Dict[str, Any]:
        """Mock embedding - adds fake embeddings to documents"""
        for doc in documents:
            doc.embedding = [0.1] * 384  # Fake embedding vector
        return {"documents": documents}


class MockDocumentStore:
    """Mock document store for testing"""
    
    def __init__(self):
        self.documents = []
        self.deleted_filters = []
    
    def write_documents(self, documents: List[Document], policy=None):
        """Mock write operation"""
        self.documents.extend(documents)
        return len(documents)
    
    def filter_documents(self, filters=None):
        """Mock filter operation"""
        return [doc for doc in self.documents]
    
    def delete_documents(self, filters=None):
        """Mock delete operation"""
        self.deleted_filters.append(filters)
        self.documents = []


class MockEmbedderProvider:
    """Mock embedder provider"""
    
    def __init__(self):
        self.embedder = MockEmbedder()
    
    def get_document_embedder(self):
        return self.embedder


class MockDocumentStoreProvider:
    """Mock document store provider"""
    
    def __init__(self):
        self.store = MockDocumentStore()
    
    def get_store(self):
        return self.store


# ============================================================================
# Test Data
# ============================================================================

SAMPLE_MDL = {
    "models": [
        {
            "name": "customers",
            "properties": {
                "displayName": "Customer Table",
                "description": "Main customer information"
            },
            "columns": [
                {
                    "name": "customer_id",
                    "type": "INTEGER",
                    "isHidden": False,
                },
                {
                    "name": "name",
                    "type": "VARCHAR",
                    "isHidden": False,
                },
                {
                    "name": "email",
                    "type": "VARCHAR",
                    "isHidden": False,
                },
                {
                    "name": "country",
                    "type": "VARCHAR",
                    "isHidden": False,
                }
            ],
            "primaryKey": "customer_id"
        },
        {
            "name": "orders",
            "properties": {
                "displayName": "Order Table",
                "description": "Customer orders"
            },
            "columns": [
                {
                    "name": "order_id",
                    "type": "INTEGER",
                    "isHidden": False,
                },
                {
                    "name": "customer_id",
                    "type": "INTEGER",
                    "isHidden": False,
                    "relationship": "customers"
                },
                {
                    "name": "order_date",
                    "type": "TIMESTAMP",
                    "isHidden": False,
                },
                {
                    "name": "total_amount",
                    "type": "DECIMAL",
                    "isHidden": False,
                }
            ],
            "primaryKey": "order_id"
        }
    ],
    "relationships": [
        {
            "name": "orders_customers",
            "models": ["orders", "customers"],
            "joinType": "MANY_TO_ONE",
            "condition": "orders.customer_id = customers.customer_id"
        }
    ],
    "views": [
        {
            "name": "customer_orders_view",
            "properties": {
                "description": "View combining customers and orders"
            },
            "statement": "SELECT c.*, o.* FROM customers c JOIN orders o ON c.customer_id = o.customer_id"
        }
    ],
    "metrics": [
        {
            "name": "total_revenue",
            "baseObject": "orders",
            "dimension": [
                {"name": "country", "type": "VARCHAR"}
            ],
            "measure": [
                {
                    "name": "revenue",
                    "type": "DECIMAL",
                    "expression": "SUM(total_amount)"
                }
            ]
        }
    ]
}

SAMPLE_MDL_STR = json.dumps(SAMPLE_MDL)


# ============================================================================
# Test Cases
# ============================================================================

class TestDDLChunker:
    """Test cases for DDLChunker component"""
    
    @pytest.mark.asyncio
    async def test_chunker_basic(self):
        """Test basic chunking functionality"""
        chunker = DDLChunker()
        result = await chunker.run(
            mdl=SAMPLE_MDL,
            column_batch_size=50,
            project_id="test_project_1"
        )
        
        documents = result["documents"]
        
        # Verify we got documents
        assert len(documents) > 0, "Should generate documents"
        
        # Verify all documents have required metadata
        for doc in documents:
            assert doc.meta.get("type") == "TABLE_SCHEMA"
            assert "name" in doc.meta
            assert doc.meta.get("project_id") == "test_project_1"
            assert doc.content is not None
        
        logger.info(f"Generated {len(documents)} document chunks")
    
    @pytest.mark.asyncio
    async def test_chunker_column_batching(self):
        """Test column batching with different batch sizes"""
        chunker = DDLChunker()
        
        # Test with small batch size
        result_small = await chunker.run(
            mdl=SAMPLE_MDL,
            column_batch_size=2,
            project_id="test_project_2"
        )
        
        # Test with large batch size
        result_large = await chunker.run(
            mdl=SAMPLE_MDL,
            column_batch_size=100,
            project_id="test_project_2"
        )
        
        # Small batch should create more chunks
        assert len(result_small["documents"]) >= len(result_large["documents"])
        
        logger.info(f"Small batch: {len(result_small['documents'])} chunks")
        logger.info(f"Large batch: {len(result_large['documents'])} chunks")
    
    @pytest.mark.asyncio
    async def test_chunker_model_conversion(self):
        """Test model to DDL conversion"""
        chunker = DDLChunker()
        result = await chunker.run(
            mdl=SAMPLE_MDL,
            column_batch_size=50,
            project_id="test_project_3"
        )
        
        documents = result["documents"]
        
        # Check that table names are preserved
        table_names = {doc.meta["name"] for doc in documents}
        assert "customers" in table_names or any("customers" in name for name in table_names)
        assert "orders" in table_names or any("orders" in name for name in table_names)
        
        logger.info(f"Found tables: {table_names}")
    
    @pytest.mark.asyncio
    async def test_chunker_with_views(self):
        """Test that views are processed correctly"""
        chunker = DDLChunker()
        result = await chunker.run(
            mdl=SAMPLE_MDL,
            column_batch_size=50,
            project_id="test_project_4"
        )
        
        documents = result["documents"]
        
        # Check for view documents
        view_docs = [doc for doc in documents if "view" in doc.meta["name"].lower()]
        assert len(view_docs) > 0, "Should have view documents"
        
        logger.info(f"Found {len(view_docs)} view documents")
    
    @pytest.mark.asyncio
    async def test_chunker_with_metrics(self):
        """Test that metrics are processed correctly"""
        chunker = DDLChunker()
        result = await chunker.run(
            mdl=SAMPLE_MDL,
            column_batch_size=50,
            project_id="test_project_5"
        )
        
        documents = result["documents"]
        
        # Check for metric documents
        metric_docs = [doc for doc in documents if "revenue" in doc.meta["name"].lower()]
        assert len(metric_docs) > 0, "Should have metric documents"
        
        logger.info(f"Found {len(metric_docs)} metric documents")


class TestDBSchema:
    """Test cases for DBSchema pipeline"""
    
    @pytest.mark.asyncio
    async def test_pipeline_initialization(self):
        """Test pipeline initialization"""
        embedder_provider = MockEmbedderProvider()
        document_store_provider = MockDocumentStoreProvider()
        
        pipeline = DBSchema(
            embedder_provider=embedder_provider,
            document_store_provider=document_store_provider,
            column_batch_size=50
        )
        
        assert pipeline is not None
        assert pipeline._components is not None
        assert "chunker" in pipeline._components
        assert "embedder" in pipeline._components
        assert "writer" in pipeline._components
        
        logger.info("Pipeline initialized successfully")
    
    @pytest.mark.asyncio
    async def test_pipeline_run_basic(self):
        """Test basic pipeline execution"""
        embedder_provider = MockEmbedderProvider()
        document_store_provider = MockDocumentStoreProvider()
        
        # Mock the validator to return valid MDL
        with patch('src.pipelines.indexing.db_schema.MDLValidator') as MockValidator:
            mock_validator_instance = Mock()
            mock_validator_instance.run.return_value = {"mdl": SAMPLE_MDL}
            MockValidator.return_value = mock_validator_instance
            
            # Mock the cleaner
            with patch('src.pipelines.indexing.db_schema.DocumentCleaner') as MockCleaner:
                mock_cleaner_instance = AsyncMock()
                mock_cleaner_instance.run = AsyncMock(return_value=None)
                MockCleaner.return_value = mock_cleaner_instance
                
                # Mock AsyncDocumentWriter
                with patch('src.pipelines.indexing.db_schema.AsyncDocumentWriter') as MockWriter:
                    mock_writer_instance = AsyncMock()
                    mock_writer_instance.run = AsyncMock(return_value={"documents_written": 10})
                    MockWriter.return_value = mock_writer_instance
                    
                    pipeline = DBSchema(
                        embedder_provider=embedder_provider,
                        document_store_provider=document_store_provider,
                        column_batch_size=50
                    )
                    
                    # Run the pipeline
                    result = await pipeline.run(
                        mdl_str=SAMPLE_MDL_STR,
                        project_id="test_project_run"
                    )
                    
                    assert result is not None
                    logger.info("Pipeline executed successfully")
    
    @pytest.mark.asyncio
    async def test_pipeline_clean(self):
        """Test the clean method"""
        embedder_provider = MockEmbedderProvider()
        document_store_provider = MockDocumentStoreProvider()
        
        with patch('src.pipelines.indexing.db_schema.DocumentCleaner') as MockCleaner:
            mock_cleaner_instance = AsyncMock()
            mock_cleaner_instance.run = AsyncMock(return_value=None)
            MockCleaner.return_value = mock_cleaner_instance
            
            with patch('src.pipelines.indexing.db_schema.MDLValidator'):
                with patch('src.pipelines.indexing.db_schema.AsyncDocumentWriter'):
                    pipeline = DBSchema(
                        embedder_provider=embedder_provider,
                        document_store_provider=document_store_provider,
                        column_batch_size=50
                    )
                    
                    # Test clean method
                    await pipeline.clean(project_id="test_project_clean")
                    
                    # Verify cleaner was called
                    mock_cleaner_instance.run.assert_called_once()
                    
                    logger.info("Clean method executed successfully")


# ============================================================================
# Integration Tests
# ============================================================================

class TestDBSchemaIntegration:
    """Integration tests for the complete pipeline"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_indexing(self):
        """Test complete end-to-end indexing flow"""
        embedder_provider = MockEmbedderProvider()
        document_store_provider = MockDocumentStoreProvider()
        
        with patch('src.pipelines.indexing.db_schema.MDLValidator') as MockValidator:
            mock_validator = Mock()
            mock_validator.run.return_value = {"mdl": SAMPLE_MDL}
            MockValidator.return_value = mock_validator
            
            with patch('src.pipelines.indexing.db_schema.DocumentCleaner') as MockCleaner:
                mock_cleaner = AsyncMock()
                mock_cleaner.run = AsyncMock(return_value=None)
                MockCleaner.return_value = mock_cleaner
                
                with patch('src.pipelines.indexing.db_schema.AsyncDocumentWriter') as MockWriter:
                    written_docs = []
                    
                    async def mock_write(documents):
                        written_docs.extend(documents)
                        return {"documents_written": len(documents)}
                    
                    mock_writer = AsyncMock()
                    mock_writer.run = mock_write
                    MockWriter.return_value = mock_writer
                    
                    # Create and run pipeline
                    pipeline = DBSchema(
                        embedder_provider=embedder_provider,
                        document_store_provider=document_store_provider,
                        column_batch_size=10
                    )
                    
                    result = await pipeline.run(
                        mdl_str=SAMPLE_MDL_STR,
                        project_id="integration_test"
                    )
                    
                    # Verify documents were processed
                    assert len(written_docs) > 0, "Should have written documents"
                    
                    # Verify all documents have embeddings
                    for doc in written_docs:
                        assert doc.embedding is not None, "All docs should have embeddings"
                        assert len(doc.embedding) > 0, "Embeddings should not be empty"
                    
                    logger.info(f"End-to-end test completed with {len(written_docs)} documents")


# ============================================================================
# Test Runner
# ============================================================================

async def run_all_tests():
    """Run all tests manually (without pytest)"""
    print("\n" + "=" * 80)
    print("Running DBSchema Pipeline Tests")
    print("=" * 80 + "\n")
    
    # Test DDLChunker
    print("\nTesting DDLChunker...")
    print("-" * 80)
    
    chunker_tests = TestDDLChunker()
    
    try:
        await chunker_tests.test_chunker_basic()
        print("[PASS] Basic chunker test passed")
    except Exception as e:
        print(f"[FAIL] Basic chunker test failed: {e}")
    
    try:
        await chunker_tests.test_chunker_column_batching()
        print("[PASS] Column batching test passed")
    except Exception as e:
        print(f"[FAIL] Column batching test failed: {e}")
    
    try:
        await chunker_tests.test_chunker_model_conversion()
        print("[PASS] Model conversion test passed")
    except Exception as e:
        print(f"[FAIL] Model conversion test failed: {e}")
    
    try:
        await chunker_tests.test_chunker_with_views()
        print("[PASS] Views test passed")
    except Exception as e:
        print(f"[FAIL] Views test failed: {e}")
    
    try:
        await chunker_tests.test_chunker_with_metrics()
        print("[PASS] Metrics test passed")
    except Exception as e:
        print(f"[FAIL] Metrics test failed: {e}")
    
    # Test DBSchema Pipeline
    print("\nTesting DBSchema Pipeline...")
    print("-" * 80)
    
    pipeline_tests = TestDBSchema()
    
    try:
        await pipeline_tests.test_pipeline_initialization()
        print("[PASS] Pipeline initialization test passed")
    except Exception as e:
        print(f"[FAIL] Pipeline initialization test failed: {e}")
    
    try:
        await pipeline_tests.test_pipeline_run_basic()
        print("[PASS] Pipeline run test passed")
    except Exception as e:
        print(f"[FAIL] Pipeline run test failed: {e}")
    
    try:
        await pipeline_tests.test_pipeline_clean()
        print("[PASS] Pipeline clean test passed")
    except Exception as e:
        print(f"[FAIL] Pipeline clean test failed: {e}")
    
    # Integration Tests
    print("\nTesting Integration...")
    print("-" * 80)
    
    integration_tests = TestDBSchemaIntegration()
    
    try:
        await integration_tests.test_end_to_end_indexing()
        print("[PASS] End-to-end integration test passed")
    except Exception as e:
        print(f"[FAIL] End-to-end integration test failed: {e}")
    
    print("\n" + "=" * 80)
    print("Test suite completed!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print(" " * 25 + "DBSchema Pipeline Tests")
    print("=" * 80)
    
    asyncio.run(run_all_tests())
