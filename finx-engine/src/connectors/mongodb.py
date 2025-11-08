"""
MongoDB Connector
"""

import time
from typing import Any, Dict, List, Optional
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure

from .base import BaseConnector, ConnectorFactory, DataSourceConfig


class MongoDBConnector(BaseConnector):
    """MongoDB connector"""
    
    def __init__(self, config: DataSourceConfig):
        super().__init__(config)
        self.db = None
    
    def connect(self) -> None:
        """Establish MongoDB connection"""
        try:
            connection_string = self._build_connection_string()
            self.connection = MongoClient(
                connection_string,
                serverSelectionTimeoutMS=5000,
                **(self.config.extra_params or {})
            )
            self.db = self.connection[self.config.database]
        except Exception as e:
            raise ConnectionError(f"Failed to connect to MongoDB: {str(e)}")
    
    def _build_connection_string(self) -> str:
        """Build MongoDB connection string"""
        return f"mongodb://{self.config.username}:{self.config.password}@{self.config.host}:{self.config.port}"
    
    def disconnect(self) -> None:
        """Close MongoDB connection"""
        if self.connection:
            self.connection.close()
    
    def test_connection(self) -> Dict[str, Any]:
        """Test MongoDB connection"""
        try:
            start_time = time.time()
            self.connect()
            
            # Test connection by listing databases
            self.connection.server_info()
            
            latency_ms = (time.time() - start_time) * 1000
            self.disconnect()
            
            return {
                "success": True,
                "message": "Connection successful",
                "latency_ms": round(latency_ms, 2)
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Connection failed: {str(e)}",
                "latency_ms": None
            }
    
    def get_tables(self, schema: Optional[str] = None) -> List[str]:
        """Get list of collections (tables) from MongoDB"""
        return self.db.list_collection_names()
    
    def get_columns(
        self, 
        table_name: str, 
        schema: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get field information from MongoDB collection.
        MongoDB is schema-less, so we sample documents to infer schema.
        """
        collection = self.db[table_name]
        
        # Sample first 100 documents to infer schema
        sample = list(collection.find().limit(100))
        
        if not sample:
            return []
        
        # Collect all unique fields
        fields = {}
        for doc in sample:
            for key, value in doc.items():
                if key not in fields:
                    fields[key] = {
                        "name": key,
                        "type": self._infer_type(value),
                        "nullable": True,
                        "comment": "Inferred from sample documents"
                    }
        
        return list(fields.values())
    
    def _infer_type(self, value: Any) -> str:
        """Infer MongoDB field type"""
        if isinstance(value, bool):
            return "BOOLEAN"
        elif isinstance(value, int):
            return "INTEGER"
        elif isinstance(value, float):
            return "DOUBLE"
        elif isinstance(value, str):
            return "STRING"
        elif isinstance(value, list):
            return "ARRAY"
        elif isinstance(value, dict):
            return "OBJECT"
        elif value is None:
            return "NULL"
        else:
            return "UNKNOWN"
    
    def get_primary_keys(
        self, 
        table_name: str, 
        schema: Optional[str] = None
    ) -> List[str]:
        """Get primary key for MongoDB collection (always _id)"""
        return ["_id"]
    
    def get_foreign_keys(
        self, 
        table_name: str, 
        schema: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        MongoDB doesn't have foreign keys.
        We could potentially detect references by field naming convention.
        """
        return []


# Register MongoDB connector
ConnectorFactory.register("mongodb", MongoDBConnector)
