import time
from typing import Any, Dict, List, Optional
from pyathena import connect
from pyathena.error import OperationalError, DatabaseError

from .base import BaseConnector, ConnectorFactory, DataSourceConfig


class AthenaConnector(BaseConnector):
    """
    AWS Athena connector for querying S3 data lake.
    
    Configuration requirements:
    - database: Athena database name
    - extra_params:
        - aws_region: AWS region (e.g., 'us-east-1')
        - s3_staging_dir: S3 bucket for query results (e.g., 's3://my-bucket/athena/')
        - catalog_name: (Optional) AWS Glue Data Catalog name (default: 'AwsDataCatalog')
        - aws_access_key_id: (Optional) AWS access key
        - aws_secret_access_key: (Optional) AWS secret key
        - aws_session_token: (Optional) AWS session token for temporary credentials
        - work_group: (Optional) Athena workgroup (default: 'primary')
    
    Note: If AWS credentials are not provided, will use IAM role or default credentials.
    """
    
    def __init__(self, config: DataSourceConfig):
        super().__init__(config)
        self.cursor = None
        
        # Extract AWS-specific parameters
        self.aws_region = config.extra_params.get("aws_region", "us-east-1")
        self.s3_staging_dir = config.extra_params.get("s3_staging_dir")
        self.catalog_name = config.extra_params.get("catalog_name", "AwsDataCatalog")
        self.work_group = config.extra_params.get("work_group", "primary")
        
        # AWS credentials (optional - will use IAM role if not provided)
        self.aws_access_key_id = config.extra_params.get("aws_access_key_id")
        self.aws_secret_access_key = config.extra_params.get("aws_secret_access_key")
        self.aws_session_token = config.extra_params.get("aws_session_token")
        
        if not self.s3_staging_dir:
            raise ValueError("s3_staging_dir is required in extra_params for Athena")
    
    def connect(self) -> None:
        """Establish Athena connection"""
        try:
            connection_params = {
                "database": self.config.database,
                "catalog_name": self.catalog_name,
                "region_name": self.aws_region,
                "s3_staging_dir": self.s3_staging_dir,
                "work_group": self.work_group
            }
            
            # Add credentials if provided
            if self.aws_access_key_id and self.aws_secret_access_key:
                connection_params["aws_access_key_id"] = self.aws_access_key_id
                connection_params["aws_secret_access_key"] = self.aws_secret_access_key
                
                # Add session token if provided (for temporary credentials)
                if self.aws_session_token:
                    connection_params["aws_session_token"] = self.aws_session_token
            
            self.connection = connect(**connection_params)
            self.cursor = self.connection.cursor()
            
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Athena: {str(e)}")
    
    def disconnect(self) -> None:
        """Close Athena connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
    
    def test_connection(self) -> Dict[str, Any]:
        """Test Athena connection"""
        try:
            start_time = time.time()
            self.connect()
            
            # Test query
            self.cursor.execute("SELECT 1")
            result = self.cursor.fetchone()
            
            latency_ms = (time.time() - start_time) * 1000
            self.disconnect()
            
            return {
                "success": True,
                "message": f"Connection successful to Athena database '{self.config.database}'",
                "latency_ms": round(latency_ms, 2)
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Connection failed: {str(e)}",
                "latency_ms": None
            }
    
    def get_tables(self, schema: Optional[str] = None) -> List[str]:
        """Get list of tables from Athena"""
        try:
            # In Athena, use SHOW TABLES
            query = "SHOW TABLES"
            if schema:
                query += f" IN {schema}"
            
            self.cursor.execute(query)
            tables = [row[0] for row in self.cursor.fetchall()]
            return tables
            
        except Exception as e:
            # Fallback: use information_schema
            try:
                schema_name = schema or self.config.database
                query = f"""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = '{schema_name}'
                    ORDER BY table_name
                """
                self.cursor.execute(query)
                return [row[0] for row in self.cursor.fetchall()]
            except:
                raise Exception(f"Failed to get tables: {str(e)}")
    
    def get_columns(
        self, 
        table_name: str, 
        schema: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get column information from Athena table"""
        try:
            # Use information_schema to get column info
            schema_name = schema or self.config.database
            
            # PyAthena doesn't support parameterized queries the same way
            # Use string formatting with proper escaping
            query = f"""
                SELECT 
                    column_name,
                    data_type,
                    is_nullable,
                    column_default
                FROM information_schema.columns
                WHERE table_schema = '{schema_name}'
                    AND table_name = '{table_name}'
                ORDER BY ordinal_position
            """
            
            self.cursor.execute(query)
            columns = []
            
            for row in self.cursor.fetchall():
                col_name = row[0]
                data_type = row[1]
                is_nullable = row[2]
                default_value = row[3] if len(row) > 3 else None
                
                columns.append({
                    "name": col_name,
                    "type": self._normalize_athena_type(data_type),
                    "nullable": is_nullable.upper() == "YES" if is_nullable else True,
                    "comment": "",
                    "default": default_value
                })
            
            return columns
            
        except Exception as e:
            raise Exception(f"Failed to get columns for {table_name}: {str(e)}")
    
    def _normalize_athena_type(self, athena_type: str) -> str:
        """Normalize Athena data types to standard types"""
        type_mapping = {
            "string": "VARCHAR",
            "varchar": "VARCHAR",
            "char": "CHAR",
            "int": "INTEGER",
            "integer": "INTEGER",
            "bigint": "BIGINT",
            "smallint": "SMALLINT",
            "tinyint": "TINYINT",
            "double": "DOUBLE",
            "float": "FLOAT",
            "decimal": "DECIMAL",
            "boolean": "BOOLEAN",
            "date": "DATE",
            "timestamp": "TIMESTAMP",
            "binary": "BINARY",
            "array": "ARRAY",
            "map": "MAP",
            "struct": "STRUCT"
        }
        
        # Handle complex types like array<string>, map<string,int>
        base_type = athena_type.lower().split("<")[0].split("(")[0].strip()
        return type_mapping.get(base_type, athena_type.upper())
    
    def get_primary_keys(
        self, 
        table_name: str, 
        schema: Optional[str] = None
    ) -> List[str]:
        """
        Get primary key columns from Athena table.
        
        Note: Athena/S3 tables typically don't have primary keys,
        but we can return partition columns as a proxy.
        """
        try:
            # Try to get partition columns
            query = f"SHOW PARTITIONS {table_name}"
            if schema:
                query = f"SHOW PARTITIONS {schema}.{table_name}"
            
            try:
                self.cursor.execute(query)
                # If table has partitions, return first partition column
                partitions = self.cursor.fetchall()
                if partitions:
                    # Parse partition columns from first row
                    # Format: col1=value1/col2=value2
                    first_partition = partitions[0][0]
                    partition_cols = [p.split("=")[0] for p in first_partition.split("/")]
                    return partition_cols[:1]  # Return first partition column as "primary key"
            except:
                pass
            
            # No primary keys in Athena tables
            return []
            
        except Exception as e:
            return []
    
    def get_foreign_keys(
        self, 
        table_name: str, 
        schema: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Get foreign key constraints from Athena table.
        
        Note: Athena/S3 tables don't have foreign key constraints.
        Returns empty list.
        """
        # Athena doesn't support foreign keys
        return []


# Register Athena connector
ConnectorFactory.register("athena", AthenaConnector)
