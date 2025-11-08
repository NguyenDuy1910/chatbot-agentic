"""
MySQL Connector
"""

import time
from typing import Any, Dict, List, Optional
import pymysql
from pymysql.cursors import DictCursor

from .base import BaseConnector, ConnectorFactory, DataSourceConfig


class MySQLConnector(BaseConnector):
    """MySQL database connector"""
    
    def __init__(self, config: DataSourceConfig):
        super().__init__(config)
        self.cursor = None
    
    def connect(self) -> None:
        """Establish MySQL connection"""
        try:
            self.connection = pymysql.connect(
                host=self.config.host,
                port=self.config.port,
                database=self.config.database,
                user=self.config.username,
                password=self.config.password,
                cursorclass=DictCursor,
                **(self.config.extra_params or {})
            )
            self.cursor = self.connection.cursor()
        except Exception as e:
            raise ConnectionError(f"Failed to connect to MySQL: {str(e)}")
    
    def disconnect(self) -> None:
        """Close MySQL connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
    
    def test_connection(self) -> Dict[str, Any]:
        """Test MySQL connection"""
        try:
            start_time = time.time()
            self.connect()
            
            self.cursor.execute("SELECT 1")
            result = self.cursor.fetchone()
            
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
        """Get list of tables from MySQL"""
        schema = schema or self.config.database
        
        query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = %s 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """
        
        self.cursor.execute(query, (schema,))
        return [row["table_name"] for row in self.cursor.fetchall()]
    
    def get_columns(
        self, 
        table_name: str, 
        schema: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get column information from MySQL"""
        schema = schema or self.config.database
        
        query = """
            SELECT 
                column_name as name,
                data_type as type,
                is_nullable as nullable,
                column_default as default_value,
                column_comment as comment,
                character_maximum_length as max_length
            FROM information_schema.columns
            WHERE table_schema = %s 
            AND table_name = %s
            ORDER BY ordinal_position
        """
        
        self.cursor.execute(query, (schema, table_name))
        columns = []
        
        for row in self.cursor.fetchall():
            columns.append({
                "name": row["name"],
                "type": row["type"].upper(),
                "nullable": row["nullable"] == "YES",
                "comment": row["comment"] or "",
                "default": row["default_value"]
            })
        
        return columns
    
    def get_primary_keys(
        self, 
        table_name: str, 
        schema: Optional[str] = None
    ) -> List[str]:
        """Get primary key columns from MySQL"""
        schema = schema or self.config.database
        
        query = """
            SELECT column_name
            FROM information_schema.key_column_usage
            WHERE table_schema = %s
            AND table_name = %s
            AND constraint_name = 'PRIMARY'
            ORDER BY ordinal_position
        """
        
        self.cursor.execute(query, (schema, table_name))
        return [row["column_name"] for row in self.cursor.fetchall()]
    
    def get_foreign_keys(
        self, 
        table_name: str, 
        schema: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """Get foreign key constraints from MySQL"""
        schema = schema or self.config.database
        
        query = """
            SELECT 
                kcu.column_name as `column`,
                kcu.referenced_table_name as referenced_table,
                kcu.referenced_column_name as referenced_column,
                kcu.constraint_name as constraint_name
            FROM information_schema.key_column_usage kcu
            WHERE kcu.table_schema = %s
            AND kcu.table_name = %s
            AND kcu.referenced_table_name IS NOT NULL
            ORDER BY kcu.ordinal_position
        """
        
        self.cursor.execute(query, (schema, table_name))
        return [
            {
                "column": row["column"],
                "referenced_table": row["referenced_table"],
                "referenced_column": row["referenced_column"],
                "constraint_name": row["constraint_name"]
            }
            for row in self.cursor.fetchall()
        ]


# Register MySQL connector
ConnectorFactory.register("mysql", MySQLConnector)
