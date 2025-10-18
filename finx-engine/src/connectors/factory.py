from typing import Dict, Type, Optional
from .base import BaseConnector, DataSourceConfig
from .athena import AthenaConnector
from .duckdb_connector import DuckDBConnector
from .postgresql import PostgreSQLConnector


class ConnectorRegistry:
    
    _connectors: Dict[str, Type[BaseConnector]] = {}
    
    @classmethod
    def register(cls, datasource_type: str, connector_class: Type[BaseConnector]) -> None:
        cls._connectors[datasource_type.lower()] = connector_class
    
    @classmethod
    def get_connector_class(cls, datasource_type: str) -> Optional[Type[BaseConnector]]:
        return cls._connectors.get(datasource_type.lower())
    
    @classmethod
    def list_supported_types(cls) -> list:
        return list(cls._connectors.keys())
    
    @classmethod
    def is_supported(cls, datasource_type: str) -> bool:
        return datasource_type.lower() in cls._connectors


ConnectorRegistry.register("athena", AthenaConnector)
ConnectorRegistry.register("duckdb", DuckDBConnector)
ConnectorRegistry.register("postgresql", PostgreSQLConnector)


class ConnectorFactory:
    
    @staticmethod
    def create_connector(config: DataSourceConfig) -> BaseConnector:
        connector_class = ConnectorRegistry.get_connector_class(config.datasource_type)
        
        if not connector_class:
            raise ValueError(
                f"Unsupported datasource type: {config.datasource_type}. "
                f"Supported types: {ConnectorRegistry.list_supported_types()}"
            )
        
        return connector_class(config)
    
    @staticmethod
    def create_from_dict(config_dict: Dict) -> BaseConnector:
        config = DataSourceConfig(
            datasource_type=config_dict["datasource_type"],
            datasource_id=config_dict["datasource_id"],
            connection_params=config_dict.get("connection_params", {})
        )
        return ConnectorFactory.create_connector(config)
    
    @staticmethod
    def list_supported_types() -> list:
        return ConnectorRegistry.list_supported_types()

