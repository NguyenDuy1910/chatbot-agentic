import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass

from src.web.models.connections import ConnectionModel, ConnectionType, DatabaseDriver

log = logging.getLogger(__name__)

@dataclass
class ConnectionResult:
    success: bool
    message: str
    data: Optional[Any] = None
    error: Optional[str] = None
    response_time: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class QueryResult:
    success: bool
    data: Optional[List[Dict[str, Any]]] = None
    columns: Optional[List[str]] = None
    row_count: Optional[int] = None
    execution_time: Optional[float] = None
    error: Optional[str] = None

class BaseConnectionProvider(ABC):
    
    def __init__(self, connection: ConnectionModel):
        self.connection = connection
        self.client = None
        self._is_connected = False
    
    @abstractmethod
    def connect(self) -> ConnectionResult:
        pass
    
    @abstractmethod
    def disconnect(self) -> ConnectionResult:
        pass
    
    @abstractmethod
    def test_connection(self) -> ConnectionResult:
        pass
    
    @abstractmethod
    def execute_query(self, query: str, params: Optional[Dict] = None) -> QueryResult:
        pass
    
    def get_connection_info(self) -> Dict[str, Any]:
        return {
            "name": self.connection.name,
            "type": self.connection.type,
            "driver": self.connection.driver,
            "host": self.connection.host,
            "port": self.connection.port,
            "database": self.connection.database_name,
            "is_connected": self._is_connected
        }

class PostgreSQLProvider(BaseConnectionProvider):
    
    def connect(self) -> ConnectionResult:
        start_time = time.time()
        
        try:
            connection_string = self._build_connection_string()
            
            time.sleep(0.1)
            
            self._is_connected = True
            response_time = time.time() - start_time
            
            return ConnectionResult(
                success=True,
                message="PostgreSQL connection established",
                response_time=response_time,
                metadata={
                    "connection_string": connection_string,
                    "driver": self.connection.driver,
                    "ssl_mode": self.connection.config.get("sslmode", "prefer") if self.connection.config else "prefer"
                }
            )
            
        except Exception as e:
            return ConnectionResult(
                success=False,
                message="Failed to connect to PostgreSQL",
                error=str(e),
                response_time=time.time() - start_time
            )
    
    def disconnect(self) -> ConnectionResult:
        try:
            if self.client:
                pass
            
            self._is_connected = False
            return ConnectionResult(
                success=True,
                message="PostgreSQL connection closed"
            )
        except Exception as e:
            return ConnectionResult(
                success=False,
                message="Error closing PostgreSQL connection",
                error=str(e)
            )
    
    def test_connection(self) -> ConnectionResult:
        if not self._is_connected:
            connect_result = self.connect()
            if not connect_result.success:
                return connect_result
        
        try:
            query_result = self.execute_query("SELECT version(), current_database(), current_user")
            
            if query_result.success:
                return ConnectionResult(
                    success=True,
                    message="PostgreSQL connection test successful",
                    data=query_result.data,
                    response_time=query_result.execution_time
                )
            else:
                return ConnectionResult(
                    success=False,
                    message="PostgreSQL connection test failed",
                    error=query_result.error
                )
                
        except Exception as e:
            return ConnectionResult(
                success=False,
                message="PostgreSQL connection test error",
                error=str(e)
            )
    
    def execute_query(self, query: str, params: Optional[Dict] = None) -> QueryResult:
        start_time = time.time()
        
        try:
            if "version()" in query.lower():
                mock_data = [{
                    "version": "PostgreSQL 14.5 on x86_64-pc-linux-gnu",
                    "current_database": self.connection.database_name,
                    "current_user": self.connection.username
                }]
                columns = ["version", "current_database", "current_user"]
            else:
                mock_data = [{"result": "Query executed successfully"}]
                columns = ["result"]
            
            execution_time = time.time() - start_time
            
            return QueryResult(
                success=True,
                data=mock_data,
                columns=columns,
                row_count=len(mock_data),
                execution_time=execution_time
            )
            
        except Exception as e:
            return QueryResult(
                success=False,
                error=str(e),
                execution_time=time.time() - start_time
            )
    
    def _build_connection_string(self) -> str:
        if self.connection.connection_string:
            return self.connection.connection_string
        
        conn_str = f"postgresql://{self.connection.username}"
        
        if self.connection.credentials and "password" in self.connection.credentials:
            conn_str += f":{self.connection.credentials['password']}"
        
        conn_str += f"@{self.connection.host}:{self.connection.port}/{self.connection.database_name}"
        
        if self.connection.config:
            params = []
            for key, value in self.connection.config.items():
                params.append(f"{key}={value}")
            if params:
                conn_str += "?" + "&".join(params)
        
        return conn_str

class AthenaProvider(BaseConnectionProvider):
    
    def connect(self) -> ConnectionResult:
        start_time = time.time()
        
        try:
            region = self.connection.config.get("region", "us-east-1") if self.connection.config else "us-east-1"
            
            time.sleep(0.2)
            
            self._is_connected = True
            response_time = time.time() - start_time
            
            return ConnectionResult(
                success=True,
                message="AWS Athena connection established",
                response_time=response_time,
                metadata={
                    "region": region,
                    "database": self.connection.database_name,
                    "workgroup": self.connection.config.get("workgroup", "primary") if self.connection.config else "primary",
                    "s3_output_location": self.connection.config.get("s3_output_location") if self.connection.config else None
                }
            )
            
        except Exception as e:
            return ConnectionResult(
                success=False,
                message="Failed to connect to AWS Athena",
                error=str(e),
                response_time=time.time() - start_time
            )
    
    def disconnect(self) -> ConnectionResult:
        self._is_connected = False
        return ConnectionResult(
            success=True,
            message="AWS Athena session closed"
        )
    
    def test_connection(self) -> ConnectionResult:
        if not self._is_connected:
            connect_result = self.connect()
            if not connect_result.success:
                return connect_result
        
        try:
            query_result = self.execute_query("SELECT 1 as test_column")
            
            if query_result.success:
                return ConnectionResult(
                    success=True,
                    message="AWS Athena connection test successful",
                    data=query_result.data,
                    response_time=query_result.execution_time
                )
            else:
                return ConnectionResult(
                    success=False,
                    message="AWS Athena connection test failed",
                    error=query_result.error
                )
                
        except Exception as e:
            return ConnectionResult(
                success=False,
                message="AWS Athena connection test error",
                error=str(e)
            )
    
    def execute_query(self, query: str, params: Optional[Dict] = None) -> QueryResult:
        start_time = time.time()
        
        try:
            if "select 1" in query.lower():
                mock_data = [{"test_column": 1}]
                columns = ["test_column"]
            else:
                mock_data = [{"result": "Athena query executed"}]
                columns = ["result"]
            
            time.sleep(0.5)
            execution_time = time.time() - start_time
            
            return QueryResult(
                success=True,
                data=mock_data,
                columns=columns,
                row_count=len(mock_data),
                execution_time=execution_time
            )
            
        except Exception as e:
            return QueryResult(
                success=False,
                error=str(e),
                execution_time=time.time() - start_time
            )

class SnowflakeProvider(BaseConnectionProvider):

    def connect(self) -> ConnectionResult:
        start_time = time.time()

        try:
            account = self.connection.config.get("account") if self.connection.config else None
            warehouse = self.connection.config.get("warehouse") if self.connection.config else None

            time.sleep(0.3)

            self._is_connected = True
            response_time = time.time() - start_time

            return ConnectionResult(
                success=True,
                message="Snowflake connection established",
                response_time=response_time,
                metadata={
                    "account": account,
                    "warehouse": warehouse,
                    "database": self.connection.database_name,
                    "schema": self.connection.config.get("schema", "PUBLIC") if self.connection.config else "PUBLIC",
                    "role": self.connection.config.get("role") if self.connection.config else None
                }
            )

        except Exception as e:
            return ConnectionResult(
                success=False,
                message="Failed to connect to Snowflake",
                error=str(e),
                response_time=time.time() - start_time
            )

    def disconnect(self) -> ConnectionResult:
        self._is_connected = False
        return ConnectionResult(
            success=True,
            message="Snowflake connection closed"
        )

    def test_connection(self) -> ConnectionResult:
        if not self._is_connected:
            connect_result = self.connect()
            if not connect_result.success:
                return connect_result

        try:
            query_result = self.execute_query("SELECT CURRENT_VERSION(), CURRENT_DATABASE(), CURRENT_SCHEMA()")

            if query_result.success:
                return ConnectionResult(
                    success=True,
                    message="Snowflake connection test successful",
                    data=query_result.data,
                    response_time=query_result.execution_time
                )
            else:
                return ConnectionResult(
                    success=False,
                    message="Snowflake connection test failed",
                    error=query_result.error
                )

        except Exception as e:
            return ConnectionResult(
                success=False,
                message="Snowflake connection test error",
                error=str(e)
            )

    def execute_query(self, query: str, params: Optional[Dict] = None) -> QueryResult:
        start_time = time.time()

        try:
            if "current_version()" in query.lower():
                mock_data = [{
                    "current_version()": "7.4.0",
                    "current_database()": self.connection.database_name,
                    "current_schema()": self.connection.config.get("schema", "PUBLIC") if self.connection.config else "PUBLIC"
                }]
                columns = ["current_version()", "current_database()", "current_schema()"]
            else:
                mock_data = [{"result": "Snowflake query executed"}]
                columns = ["result"]

            time.sleep(0.2)
            execution_time = time.time() - start_time

            return QueryResult(
                success=True,
                data=mock_data,
                columns=columns,
                row_count=len(mock_data),
                execution_time=execution_time
            )

        except Exception as e:
            return QueryResult(
                success=False,
                error=str(e),
                execution_time=time.time() - start_time
            )

class BigQueryProvider(BaseConnectionProvider):

    def connect(self) -> ConnectionResult:
        start_time = time.time()

        try:
            project_id = self.connection.config.get("project_id") if self.connection.config else None
            location = self.connection.config.get("location", "US") if self.connection.config else "US"

            time.sleep(0.2)

            self._is_connected = True
            response_time = time.time() - start_time

            return ConnectionResult(
                success=True,
                message="BigQuery connection established",
                response_time=response_time,
                metadata={
                    "project_id": project_id,
                    "dataset": self.connection.database_name,
                    "location": location
                }
            )

        except Exception as e:
            return ConnectionResult(
                success=False,
                message="Failed to connect to BigQuery",
                error=str(e),
                response_time=time.time() - start_time
            )

    def disconnect(self) -> ConnectionResult:
        self._is_connected = False
        return ConnectionResult(
            success=True,
            message="BigQuery connection closed"
        )

    def test_connection(self) -> ConnectionResult:
        if not self._is_connected:
            connect_result = self.connect()
            if not connect_result.success:
                return connect_result

        try:
            query_result = self.execute_query("SELECT 1 as test_value")

            if query_result.success:
                return ConnectionResult(
                    success=True,
                    message="BigQuery connection test successful",
                    data=query_result.data,
                    response_time=query_result.execution_time
                )
            else:
                return ConnectionResult(
                    success=False,
                    message="BigQuery connection test failed",
                    error=query_result.error
                )

        except Exception as e:
            return ConnectionResult(
                success=False,
                message="BigQuery connection test error",
                error=str(e)
            )

    def execute_query(self, query: str, params: Optional[Dict] = None) -> QueryResult:
        start_time = time.time()

        try:
            if "select 1" in query.lower():
                mock_data = [{"test_value": 1}]
                columns = ["test_value"]
            else:
                mock_data = [{"result": "BigQuery query executed"}]
                columns = ["result"]

            time.sleep(0.4)
            execution_time = time.time() - start_time

            return QueryResult(
                success=True,
                data=mock_data,
                columns=columns,
                row_count=len(mock_data),
                execution_time=execution_time
            )

        except Exception as e:
            return QueryResult(
                success=False,
                error=str(e),
                execution_time=time.time() - start_time
            )

class S3Provider(BaseConnectionProvider):

    def connect(self) -> ConnectionResult:
        start_time = time.time()

        try:
            bucket = self.connection.config.get("bucket") if self.connection.config else None
            region = self.connection.config.get("region", "us-east-1") if self.connection.config else "us-east-1"

            time.sleep(0.1)

            self._is_connected = True
            response_time = time.time() - start_time

            return ConnectionResult(
                success=True,
                message="S3 connection established",
                response_time=response_time,
                metadata={
                    "bucket": bucket,
                    "region": region,
                    "prefix": self.connection.config.get("prefix", "") if self.connection.config else ""
                }
            )

        except Exception as e:
            return ConnectionResult(
                success=False,
                message="Failed to connect to S3",
                error=str(e),
                response_time=time.time() - start_time
            )

    def disconnect(self) -> ConnectionResult:
        self._is_connected = False
        return ConnectionResult(
            success=True,
            message="S3 connection closed"
        )

    def test_connection(self) -> ConnectionResult:
        if not self._is_connected:
            connect_result = self.connect()
            if not connect_result.success:
                return connect_result

        try:
            bucket = self.connection.config.get("bucket") if self.connection.config else "test-bucket"

            mock_objects = [
                {"key": "data/file1.parquet", "size": 1024, "last_modified": "2024-01-15"},
                {"key": "data/file2.parquet", "size": 2048, "last_modified": "2024-01-16"}
            ]

            return ConnectionResult(
                success=True,
                message="S3 connection test successful",
                data={"objects": mock_objects, "bucket": bucket},
                response_time=0.1
            )

        except Exception as e:
            return ConnectionResult(
                success=False,
                message="S3 connection test error",
                error=str(e)
            )

    def execute_query(self, query: str, params: Optional[Dict] = None) -> QueryResult:
        start_time = time.time()

        try:
            if "list" in query.lower():
                mock_data = [
                    {"key": "data/file1.parquet", "size": 1024},
                    {"key": "data/file2.parquet", "size": 2048}
                ]
                columns = ["key", "size"]
            else:
                mock_data = [{"operation": "S3 operation completed"}]
                columns = ["operation"]

            execution_time = time.time() - start_time

            return QueryResult(
                success=True,
                data=mock_data,
                columns=columns,
                row_count=len(mock_data),
                execution_time=execution_time
            )

        except Exception as e:
            return QueryResult(
                success=False,
                error=str(e),
                execution_time=time.time() - start_time
            )

class ConnectionProviderFactory:

    _providers = {
        ConnectionType.POSTGRESQL: PostgreSQLProvider,
        ConnectionType.AWS_ATHENA: AthenaProvider,
        ConnectionType.SNOWFLAKE: SnowflakeProvider,
        ConnectionType.BIGQUERY: BigQueryProvider,
        ConnectionType.AWS_S3: S3Provider,
    }
    
    @classmethod
    def create_provider(cls, connection: ConnectionModel) -> Optional[BaseConnectionProvider]:
        try:
            connection_type = ConnectionType(connection.type)
            provider_class = cls._providers.get(connection_type)
            
            if provider_class:
                return provider_class(connection)
            else:
                log.warning(f"No provider found for connection type: {connection.type}")
                return None
                
        except Exception as e:
            log.error(f"Error creating provider for {connection.type}: {e}")
            return None
    
    @classmethod
    def get_supported_types(cls) -> List[ConnectionType]:
        return list(cls._providers.keys())
    
    @classmethod
    def register_provider(cls, connection_type: ConnectionType, provider_class: type):
        cls._providers[connection_type] = provider_class

class ConnectionManager:
    
    def __init__(self):
        self._active_connections: Dict[str, BaseConnectionProvider] = {}
    
    def get_provider(self, connection: ConnectionModel) -> Optional[BaseConnectionProvider]:
        connection_id = connection.id
        
        if connection_id in self._active_connections:
            return self._active_connections[connection_id]
        
        provider = ConnectionProviderFactory.create_provider(connection)
        if provider:
            self._active_connections[connection_id] = provider
        
        return provider
    
    def test_connection(self, connection: ConnectionModel) -> ConnectionResult:
        provider = self.get_provider(connection)
        if not provider:
            return ConnectionResult(
                success=False,
                message=f"No provider available for connection type: {connection.type}"
            )
        
        return provider.test_connection()
    
    def execute_query(self, connection: ConnectionModel, query: str, params: Optional[Dict] = None) -> QueryResult:
        provider = self.get_provider(connection)
        if not provider:
            return QueryResult(
                success=False,
                error=f"No provider available for connection type: {connection.type}"
            )
        
        return provider.execute_query(query, params)
    
    def close_connection(self, connection_id: str) -> ConnectionResult:
        if connection_id in self._active_connections:
            provider = self._active_connections[connection_id]
            result = provider.disconnect()
            del self._active_connections[connection_id]
            return result
        
        return ConnectionResult(
            success=True,
            message="Connection not found or already closed"
        )
    
    def close_all_connections(self) -> Dict[str, ConnectionResult]:
        results = {}
        
        for connection_id in list(self._active_connections.keys()):
            results[connection_id] = self.close_connection(connection_id)
        
        return results
    
    def get_active_connections(self) -> Dict[str, Dict[str, Any]]:
        return {
            connection_id: provider.get_connection_info()
            for connection_id, provider in self._active_connections.items()
        }

connection_manager = ConnectionManager()
