"""
AWS Redshift Connector

Connector for AWS Redshift data warehouse.
"""

import time
from typing import Any, Dict, List, Optional
import redshift_connector

from .base import BaseConnector, ConnectorFactory, DataSourceConfig


class RedshiftConnector(BaseConnector):
    """
    AWS Redshift connector for data warehouse access.
    
    Configuration:
    - host: Redshift cluster endpoint (e.g., 'my-cluster.xxxx.region.redshift.amazonaws.com')
    - port: Redshift port (default: 5439)
    - database: Redshift database name
    - username: Database username (or use IAM authentication)
    - password: Database password (or use IAM authentication)
    - extra_params:
        - ssl: Use SSL (default: True)
        - iam: Use IAM authentication (default: False)
        - cluster_identifier: Required if iam=True
        - region: AWS region (required if iam=True)
        - db_user: Database user for IAM auth
    """
    
    def __init__(self, config: DataSourceConfig):
        super().__init__(config)
        self.cursor = None
        
        # Extract Redshift-specific parameters
        self.ssl = config.extra_params.get("ssl", True)
        self.use_iam = config.extra_params.get("iam", False)
        self.cluster_identifier = config.extra_params.get("cluster_identifier")
        self.region = config.extra_params.get("region")
        self.db_user = config.extra_params.get("db_user", config.username)
    
    def connect(self) -> None:
        """Establish Redshift connection"""
        try:
            connection_params = {
                "host": self.config.host,
                "port": self.config.port or 5439,
                "database": self.config.database,
                "ssl": self.ssl,
                "timeout": 30
            }
            
            if self.use_iam:
                # IAM authentication
                if not self.cluster_identifier or not self.region:
                    raise ValueError(
                        "cluster_identifier and region are required for IAM authentication"
                    )
                
                connection_params.update({
                    "iam": True,
                    "cluster_identifier": self.cluster_identifier,
                    "region": self.region,
                    "db_user": self.db_user
                })
            else:
                # Standard username/password authentication
                connection_params.update({
                    "user": self.config.username,
                    "password": self.config.password
                })
            
            self.connection = redshift_connector.connect(**connection_params)
            self.cursor = self.connection.cursor()
            
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Redshift: {str(e)}")
    
    def disconnect(self) -> None:
        """Close Redshift connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
    
    def test_connection(self) -> Dict[str, Any]:
        """Test Redshift connection"""
        try:
            start_time = time.time()
            self.connect()
            
            # Test query
            self.cursor.execute("SELECT version()")
            version = self.cursor.fetchone()[0]
            
            latency_ms = (time.time() - start_time) * 1000
            self.disconnect()
            
            return {
                "success": True,
                "message": f"Connection successful to Redshift",
                "version": version,
                "latency_ms": round(latency_ms, 2)
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Connection failed: {str(e)}",
                "latency_ms": None
            }
    
    def get_tables(self, schema: Optional[str] = None) -> List[str]:
        """Get list of tables from Redshift"""
        try:
            schema_name = schema or "public"
            
            query = """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = %s 
                AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """
            
            self.cursor.execute(query, (schema_name,))
            tables = [row[0] for row in self.cursor.fetchall()]
            return tables
            
        except Exception as e:
            raise Exception(f"Failed to get tables: {str(e)}")
    
    def get_columns(
        self, 
        table_name: str, 
        schema: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get column information from Redshift table"""
        try:
            schema_name = schema or "public"
            
            query = """
                SELECT 
                    column_name,
                    data_type,
                    character_maximum_length,
                    numeric_precision,
                    numeric_scale,
                    is_nullable,
                    column_default
                FROM information_schema.columns
                WHERE table_schema = %s AND table_name = %s
                ORDER BY ordinal_position
            """
            
            self.cursor.execute(query, (schema_name, table_name))
            columns = []
            
            for row in self.cursor.fetchall():
                col_name, data_type, char_length, num_precision, num_scale, is_nullable, default = row
                
                # Format type with precision/scale
                full_type = data_type
                if char_length:
                    full_type = f"{data_type}({char_length})"
                elif num_precision:
                    if num_scale:
                        full_type = f"{data_type}({num_precision},{num_scale})"
                    else:
                        full_type = f"{data_type}({num_precision})"
                
                columns.append({
                    "name": col_name,
                    "type": self._normalize_type(full_type),
                    "nullable": is_nullable == "YES",
                    "default": default,
                    "comment": ""
                })
            
            return columns
            
        except Exception as e:
            raise Exception(f"Failed to get columns for {table_name}: {str(e)}")
    
    def _normalize_type(self, redshift_type: str) -> str:
        """Normalize Redshift data types"""
        type_lower = redshift_type.lower()
        
        # Map Redshift types to standard types
        if "character varying" in type_lower or "varchar" in type_lower:
            return redshift_type.replace("character varying", "VARCHAR")
        elif "character" in type_lower:
            return redshift_type.replace("character", "CHAR")
        elif type_lower == "integer":
            return "INTEGER"
        elif type_lower == "bigint":
            return "BIGINT"
        elif type_lower == "smallint":
            return "SMALLINT"
        elif "double precision" in type_lower:
            return "DOUBLE PRECISION"
        elif type_lower == "real":
            return "REAL"
        elif "timestamp" in type_lower:
            return redshift_type.upper()
        elif type_lower == "date":
            return "DATE"
        elif type_lower == "boolean":
            return "BOOLEAN"
        elif "numeric" in type_lower or "decimal" in type_lower:
            return redshift_type.upper()
        else:
            return redshift_type.upper()
    
    def get_primary_keys(
        self, 
        table_name: str, 
        schema: Optional[str] = None
    ) -> List[str]:
        """Get primary key columns from Redshift table"""
        try:
            schema_name = schema or "public"
            
            query = """
                SELECT 
                    kcu.column_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu
                    ON tc.constraint_name = kcu.constraint_name
                    AND tc.table_schema = kcu.table_schema
                WHERE tc.constraint_type = 'PRIMARY KEY'
                    AND tc.table_schema = %s
                    AND tc.table_name = %s
                ORDER BY kcu.ordinal_position
            """
            
            self.cursor.execute(query, (schema_name, table_name))
            return [row[0] for row in self.cursor.fetchall()]
            
        except Exception as e:
            return []
    
    def get_foreign_keys(
        self, 
        table_name: str, 
        schema: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """Get foreign key constraints from Redshift table"""
        try:
            schema_name = schema or "public"
            
            query = """
                SELECT 
                    kcu.column_name,
                    ccu.table_name AS referenced_table,
                    ccu.column_name AS referenced_column
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu
                    ON tc.constraint_name = kcu.constraint_name
                    AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage ccu
                    ON ccu.constraint_name = tc.constraint_name
                    AND ccu.table_schema = tc.table_schema
                WHERE tc.constraint_type = 'FOREIGN KEY'
                    AND tc.table_schema = %s
                    AND tc.table_name = %s
            """
            
            self.cursor.execute(query, (schema_name, table_name))
            
            foreign_keys = []
            for row in self.cursor.fetchall():
                foreign_keys.append({
                    "column": row[0],
                    "referenced_table": row[1],
                    "referenced_column": row[2]
                })
            
            return foreign_keys
            
        except Exception as e:
            return []


# Register Redshift connector
ConnectorFactory.register("redshift", RedshiftConnector)
