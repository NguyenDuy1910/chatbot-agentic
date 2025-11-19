"""
Base Connector Interface for Database Connections
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass


@dataclass
class DataSourceConfig:
    """Configuration for database connection"""
    type: str
    host: str
    port: int
    database: str
    username: str
    password: str
    schema: Optional[str] = None
    extra_params: Optional[Dict[str, Any]] = None


class BaseConnector(ABC):
    """
    Abstract base class for database connectors.
    
    All database connectors must implement these methods.
    """
    
    def __init__(self, config: DataSourceConfig):
        """Initialize connector with configuration"""
        self.config = config
        self.connection = None
    
    @abstractmethod
    def connect(self) -> None:
        """Establish connection to database"""
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """Close database connection"""
        pass
    
    @abstractmethod
    def test_connection(self) -> Dict[str, Any]:
        """
        Test database connection.
        
        Returns:
            Dict with 'success' (bool), 'message' (str), and 'latency_ms' (float)
        """
        pass
    
    @abstractmethod
    def get_tables(self, schema: Optional[str] = None) -> List[str]:
        """
        Get list of table names.
        
        Args:
            schema: Schema name (uses default if None)
            
        Returns:
            List of table names
        """
        pass
    
    @abstractmethod
    def get_columns(
        self, 
        table_name: str, 
        schema: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get column information for a table.
        
        Args:
            table_name: Name of the table
            schema: Schema name
            
        Returns:
            List of dicts with keys: name, type, nullable, comment
        """
        pass
    
    @abstractmethod
    def get_primary_keys(
        self, 
        table_name: str, 
        schema: Optional[str] = None
    ) -> List[str]:
        """
        Get primary key columns for a table.
        
        Args:
            table_name: Name of the table
            schema: Schema name
            
        Returns:
            List of primary key column names
        """
        pass
    
    @abstractmethod
    def get_foreign_keys(
        self, 
        table_name: str, 
        schema: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Get foreign key constraints for a table.
        
        Args:
            table_name: Name of the table
            schema: Schema name
            
        Returns:
            List of dicts with keys: column, referenced_table, referenced_column
        """
        pass
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()


class ConnectorFactory:
    """Factory for creating database connectors"""
    
    _connectors = {}
    
    @classmethod
    def register(cls, db_type: str, connector_class):
        """Register a connector class for a database type"""
        cls._connectors[db_type] = connector_class
    
    @classmethod
    def create_connector(cls, config: DataSourceConfig) -> BaseConnector:
        """
        Create connector instance for given configuration.
        
        Args:
            config: Database configuration
            
        Returns:
            Connector instance
            
        Raises:
            ValueError: If database type is not supported
        """
        connector_class = cls._connectors.get(config.type)
        if not connector_class:
            raise ValueError(f"Unsupported database type: {config.type}")
        
        return connector_class(config)
