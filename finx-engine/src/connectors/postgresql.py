import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any, Optional
from .base import BaseConnector, DataSourceConfig


class PostgreSQLConnector(BaseConnector):
    
    def __init__(self, config: DataSourceConfig):
        super().__init__(config)
        self.host = config.connection_params.get("host", "localhost")
        self.port = config.connection_params.get("port", 5432)
        self.database = config.connection_params.get("database")
        self.user = config.connection_params.get("user")
        self.password = config.connection_params.get("password")
        self.schema = config.connection_params.get("schema", "public")
        self.connection = None
    
    def connect(self) -> None:
        self.connection = psycopg2.connect(
            host=self.host,
            port=self.port,
            database=self.database,
            user=self.user,
            password=self.password
        )
        self._connection = self.connection
    
    def disconnect(self) -> None:
        if self.connection:
            self.connection.close()
            self.connection = None
        self._connection = None
    
    def test_connection(self) -> bool:
        try:
            if not self.connection:
                self.connect()
            cursor = self.connection.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            return True
        except Exception:
            return False
    
    def get_schemas(self) -> List[str]:
        if not self.connection:
            self.connect()
        
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
            ORDER BY schema_name
        """)
        
        schemas = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return schemas
    
    def get_tables(self, schema: Optional[str] = None) -> List[str]:
        if not self.connection:
            self.connect()
        
        target_schema = schema or self.schema
        
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = %s AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """, (target_schema,))
        
        tables = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return tables
    
    def get_table_metadata(self, table_name: str, schema: Optional[str] = None) -> Dict[str, Any]:
        if not self.connection:
            self.connect()
        
        target_schema = schema or self.schema
        
        cursor = self.connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT 
                t.table_schema,
                t.table_name,
                t.table_type,
                obj_description((quote_ident(t.table_schema) || '.' || quote_ident(t.table_name))::regclass) as table_comment
            FROM information_schema.tables t
            WHERE t.table_schema = %s AND t.table_name = %s
        """, (target_schema, table_name))
        
        result = cursor.fetchone()
        cursor.close()
        
        if not result:
            return {}
        
        return {
            "name": result['table_name'],
            "schema": result['table_schema'],
            "type": result['table_type'],
            "comment": result['table_comment'] or ''
        }
    
    def get_columns(self, table_name: str, schema: Optional[str] = None) -> List[Dict[str, Any]]:
        if not self.connection:
            self.connect()
        
        target_schema = schema or self.schema
        
        cursor = self.connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT 
                c.column_name,
                c.data_type,
                c.is_nullable,
                c.column_default,
                c.ordinal_position,
                c.character_maximum_length,
                c.numeric_precision,
                c.numeric_scale,
                col_description((quote_ident(c.table_schema) || '.' || quote_ident(c.table_name))::regclass, c.ordinal_position) as column_comment
            FROM information_schema.columns c
            WHERE c.table_schema = %s AND c.table_name = %s
            ORDER BY c.ordinal_position
        """, (target_schema, table_name))
        
        columns = []
        for row in cursor.fetchall():
            columns.append({
                "name": row['column_name'],
                "type": row['data_type'],
                "nullable": row['is_nullable'] == 'YES',
                "default": row['column_default'],
                "position": row['ordinal_position'],
                "max_length": row['character_maximum_length'],
                "precision": row['numeric_precision'],
                "scale": row['numeric_scale'],
                "comment": row['column_comment'] or ''
            })
        
        cursor.close()
        return columns
    
    def get_primary_keys(self, table_name: str, schema: Optional[str] = None) -> List[str]:
        if not self.connection:
            self.connect()
        
        target_schema = schema or self.schema
        
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT a.attname
            FROM pg_index i
            JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
            WHERE i.indrelid = (
                SELECT oid 
                FROM pg_class 
                WHERE relname = %s 
                AND relnamespace = (SELECT oid FROM pg_namespace WHERE nspname = %s)
            )
            AND i.indisprimary
            ORDER BY a.attnum
        """, (table_name, target_schema))
        
        primary_keys = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return primary_keys
    
    def get_foreign_keys(self, table_name: str, schema: Optional[str] = None) -> List[Dict[str, Any]]:
        if not self.connection:
            self.connect()
        
        target_schema = schema or self.schema
        
        cursor = self.connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT
                tc.constraint_name,
                kcu.column_name,
                ccu.table_schema AS referenced_schema,
                ccu.table_name AS referenced_table,
                ccu.column_name AS referenced_column
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
                AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
                AND tc.table_schema = %s
                AND tc.table_name = %s
            ORDER BY kcu.ordinal_position
        """, (target_schema, table_name))
        
        foreign_keys = []
        for row in cursor.fetchall():
            foreign_keys.append({
                "constraint_name": row['constraint_name'],
                "column": row['column_name'],
                "referenced_schema": row['referenced_schema'],
                "referenced_table": row['referenced_table'],
                "referenced_column": row['referenced_column']
            })
        
        cursor.close()
        return foreign_keys
    
    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        if not self.connection:
            self.connect()
        
        cursor = self.connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute(query)
        
        results = cursor.fetchall()
        cursor.close()
        
        return [dict(row) for row in results]
    
    def get_indexes(self, table_name: str, schema: Optional[str] = None) -> List[Dict[str, Any]]:
        if not self.connection:
            self.connect()
        
        target_schema = schema or self.schema
        
        cursor = self.connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT
                i.relname as index_name,
                a.attname as column_name,
                ix.indisunique as is_unique,
                ix.indisprimary as is_primary
            FROM pg_class t
            JOIN pg_index ix ON t.oid = ix.indrelid
            JOIN pg_class i ON i.oid = ix.indexrelid
            JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = ANY(ix.indkey)
            WHERE t.relname = %s
                AND t.relnamespace = (SELECT oid FROM pg_namespace WHERE nspname = %s)
            ORDER BY i.relname, a.attnum
        """, (table_name, target_schema))
        
        indexes = []
        for row in cursor.fetchall():
            indexes.append({
                "index_name": row['index_name'],
                "column_name": row['column_name'],
                "is_unique": row['is_unique'],
                "is_primary": row['is_primary']
            })
        
        cursor.close()
        return indexes

