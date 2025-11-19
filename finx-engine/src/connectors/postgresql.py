"""
PostgreSQL Connector
"""

import time
from typing import Any, Dict, List, Optional
import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor

from .base import BaseConnector, ConnectorFactory, DataSourceConfig


class PostgreSQLConnector(BaseConnector):
    """PostgreSQL database connector"""
    
    def __init__(self, config: DataSourceConfig):
        super().__init__(config)
        self.cursor = None
    
    def connect(self) -> None:
        """Establish PostgreSQL connection"""
        try:
            self.connection = psycopg2.connect(
                host=self.config.host,
                port=self.config.port,
                database=self.config.database,
                user=self.config.username,
                password=self.config.password,
                **(self.config.extra_params or {})
            )
            self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)
        except Exception as e:
            raise ConnectionError(f"Failed to connect to PostgreSQL: {str(e)}")
    
    def disconnect(self) -> None:
        """Close PostgreSQL connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
    
    def test_connection(self) -> Dict[str, Any]:
        """Test PostgreSQL connection"""
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
        """Get list of tables from PostgreSQL"""
        schema = schema or self.config.schema or "public"
        
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
        """Get column information from PostgreSQL"""
        schema = schema or self.config.schema or "public"
        
        query = """
            SELECT 
                column_name as name,
                data_type as type,
                is_nullable as nullable,
                column_default as default_value,
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
                "comment": "",  # PostgreSQL doesn't store column comments in information_schema
                "default": row["default_value"]
            })
        
        return columns
    
    def get_primary_keys(
        self, 
        table_name: str, 
        schema: Optional[str] = None
    ) -> List[str]:
        """Get primary key columns from PostgreSQL"""
        schema = schema or self.config.schema or "public"
        
        query = """
            SELECT a.attname as column_name
            FROM pg_index i
            JOIN pg_attribute a ON a.attrelid = i.indrelid 
                AND a.attnum = ANY(i.indkey)
            JOIN pg_class t ON t.oid = i.indrelid
            JOIN pg_namespace n ON n.oid = t.relnamespace
            WHERE i.indisprimary
            AND t.relname = %s
            AND n.nspname = %s
            ORDER BY a.attnum
        """
        
        self.cursor.execute(query, (table_name, schema))
        return [row["column_name"] for row in self.cursor.fetchall()]
    
    def get_foreign_keys(
        self, 
        table_name: str, 
        schema: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """Get foreign key constraints from PostgreSQL"""
        schema = schema or self.config.schema or "public"
        
        query = """
            SELECT
                kcu.column_name as column,
                ccu.table_name as referenced_table,
                ccu.column_name as referenced_column,
                tc.constraint_name as constraint_name
            FROM information_schema.table_constraints AS tc 
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
                AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_name = %s
            AND tc.table_schema = %s
            ORDER BY kcu.ordinal_position
        """
        
        self.cursor.execute(query, (table_name, schema))
        return [
            {
                "column": row["column"],
                "referenced_table": row["referenced_table"],
                "referenced_column": row["referenced_column"],
                "constraint_name": row["constraint_name"]
            }
            for row in self.cursor.fetchall()
        ]


# Register PostgreSQL connector
ConnectorFactory.register("postgresql", PostgreSQLConnector)
