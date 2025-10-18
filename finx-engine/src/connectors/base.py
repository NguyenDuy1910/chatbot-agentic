from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class DataSourceConfig:
    datasource_type: str
    datasource_id: str
    connection_params: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "datasource_type": self.datasource_type,
            "datasource_id": self.datasource_id,
            "connection_params": self.connection_params
        }


class BaseConnector(ABC):
    
    def __init__(self, config: DataSourceConfig):
        self.config = config
        self.datasource_id = config.datasource_id
        self.datasource_type = config.datasource_type
        self._connection = None
    
    @abstractmethod
    def connect(self) -> None:
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        pass
    
    @abstractmethod
    def get_schemas(self) -> List[str]:
        pass
    
    @abstractmethod
    def get_tables(self, schema: Optional[str] = None) -> List[str]:
        pass
    
    @abstractmethod
    def get_table_metadata(self, table_name: str, schema: Optional[str] = None) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def get_columns(self, table_name: str, schema: Optional[str] = None) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def get_primary_keys(self, table_name: str, schema: Optional[str] = None) -> List[str]:
        pass
    
    @abstractmethod
    def get_foreign_keys(self, table_name: str, schema: Optional[str] = None) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        pass
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
    
    def get_datasource_info(self) -> Dict[str, Any]:
        return {
            "datasource_id": self.datasource_id,
            "datasource_type": self.datasource_type,
            "status": "connected" if self._connection else "disconnected"
        }

