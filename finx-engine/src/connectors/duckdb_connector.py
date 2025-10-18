import duckdb
from typing import List, Dict, Any, Optional
from .base import BaseConnector, DataSourceConfig


class DuckDBConnector(BaseConnector):
    
    def __init__(self, config: DataSourceConfig):
        super().__init__(config)
        self.database_path = config.connection_params.get("database_path", ":memory:")
        self.read_only = config.connection_params.get("read_only", False)
        self.connection = None
    
    def connect(self) -> None:
        self.connection = duckdb.connect(
            database=self.database_path,
            read_only=self.read_only
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
            self.connection.execute("SELECT 1").fetchone()
            return True
        except Exception:
            return False
    
    def get_schemas(self) -> List[str]:
        if not self.connection:
            self.connect()
        
        result = self.connection.execute("""
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name NOT IN ('information_schema', 'pg_catalog')
            ORDER BY schema_name
        """).fetchall()
        
        return [row[0] for row in result]
    
    def get_tables(self, schema: Optional[str] = None) -> List[str]:
        if not self.connection:
            self.connect()
        
        if schema:
            query = """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = ? AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """
            result = self.connection.execute(query, [schema]).fetchall()
        else:
            query = """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_type = 'BASE TABLE' 
                AND table_schema NOT IN ('information_schema', 'pg_catalog')
                ORDER BY table_name
            """
            result = self.connection.execute(query).fetchall()
        
        return [row[0] for row in result]
    
    def get_table_metadata(self, table_name: str, schema: Optional[str] = None) -> Dict[str, Any]:
        if not self.connection:
            self.connect()
        
        full_table_name = f"{schema}.{table_name}" if schema else table_name
        
        query = """
            SELECT 
                table_schema,
                table_name,
                table_type
            FROM information_schema.tables
            WHERE table_name = ?
        """
        
        params = [table_name]
        if schema:
            query += " AND table_schema = ?"
            params.append(schema)
        
        result = self.connection.execute(query, params).fetchone()
        
        if not result:
            return {}
        
        return {
            "name": result[1],
            "schema": result[0],
            "type": result[2],
            "full_name": full_table_name
        }
    
    def get_columns(self, table_name: str, schema: Optional[str] = None) -> List[Dict[str, Any]]:
        if not self.connection:
            self.connect()
        
        query = """
            SELECT 
                column_name,
                data_type,
                is_nullable,
                column_default,
                ordinal_position
            FROM information_schema.columns
            WHERE table_name = ?
        """
        
        params = [table_name]
        if schema:
            query += " AND table_schema = ?"
            params.append(schema)
        
        query += " ORDER BY ordinal_position"
        
        result = self.connection.execute(query, params).fetchall()
        
        columns = []
        for row in result:
            columns.append({
                "name": row[0],
                "type": row[1],
                "nullable": row[2] == 'YES',
                "default": row[3],
                "position": row[4]
            })
        
        return columns
    
    def get_primary_keys(self, table_name: str, schema: Optional[str] = None) -> List[str]:
        if not self.connection:
            self.connect()
        
        full_table_name = f"{schema}.{table_name}" if schema else table_name
        
        try:
            query = f"PRAGMA table_info('{full_table_name}')"
            result = self.connection.execute(query).fetchall()
            
            primary_keys = []
            for row in result:
                if row[5] > 0:
                    primary_keys.append(row[1])
            
            return primary_keys
        except Exception:
            return []
    
    def get_foreign_keys(self, table_name: str, schema: Optional[str] = None) -> List[Dict[str, Any]]:
        if not self.connection:
            self.connect()
        
        full_table_name = f"{schema}.{table_name}" if schema else table_name
        
        try:
            query = f"PRAGMA foreign_key_list('{full_table_name}')"
            result = self.connection.execute(query).fetchall()
            
            foreign_keys = []
            for row in result:
                foreign_keys.append({
                    "column": row[3],
                    "referenced_table": row[2],
                    "referenced_column": row[4],
                    "constraint_name": f"fk_{table_name}_{row[0]}"
                })
            
            return foreign_keys
        except Exception:
            return []
    
    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        if not self.connection:
            self.connect()
        
        result = self.connection.execute(query)
        columns = [desc[0] for desc in result.description]
        rows = result.fetchall()
        
        return [dict(zip(columns, row)) for row in rows]
    
    def load_csv(self, table_name: str, csv_path: str, schema: Optional[str] = None) -> None:
        if not self.connection:
            self.connect()
        
        full_table_name = f"{schema}.{table_name}" if schema else table_name
        
        self.connection.execute(f"""
            CREATE TABLE IF NOT EXISTS {full_table_name} AS 
            SELECT * FROM read_csv_auto('{csv_path}')
        """)
    
    def load_parquet(self, table_name: str, parquet_path: str, schema: Optional[str] = None) -> None:
        if not self.connection:
            self.connect()
        
        full_table_name = f"{schema}.{table_name}" if schema else table_name
        
        self.connection.execute(f"""
            CREATE TABLE IF NOT EXISTS {full_table_name} AS 
            SELECT * FROM read_parquet('{parquet_path}')
        """)

