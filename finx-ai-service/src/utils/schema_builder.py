"""
Schema Builder Utility for Database Metadata Management.

This module provides utilities for:
1. Parsing table schemas from JSON metadata
2. Building DDL statements from schema definitions
3. Managing database relationships and constraints
"""

import logging
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class JoinType(str, Enum):
    """Types of relationships between tables"""
    ONE_TO_ONE = "ONE_TO_ONE"
    ONE_TO_MANY = "ONE_TO_MANY"
    MANY_TO_ONE = "MANY_TO_ONE"
    MANY_TO_MANY = "MANY_TO_MANY"


class DataType(str, Enum):
    """Supported database data types"""
    # Numeric types
    INTEGER = "INTEGER"
    BIGINT = "BIGINT"
    SMALLINT = "SMALLINT"
    DECIMAL = "DECIMAL"
    NUMERIC = "NUMERIC"
    FLOAT = "FLOAT"
    DOUBLE = "DOUBLE"
    REAL = "REAL"
    
    # String types
    VARCHAR = "VARCHAR"
    CHAR = "CHAR"
    TEXT = "TEXT"
    
    # Date/Time types
    DATE = "DATE"
    TIME = "TIME"
    TIMESTAMP = "TIMESTAMP"
    DATETIME = "DATETIME"
    
    # Boolean
    BOOLEAN = "BOOLEAN"
    
    # Binary
    BYTEA = "BYTEA"
    BLOB = "BLOB"
    
    # Special
    JSON = "JSON"
    JSONB = "JSONB"
    UUID = "UUID"


@dataclass
class ColumnSchema:
    """Represents a column definition"""
    name: str
    type: str
    nullable: bool = True
    primary_key: bool = False
    unique: bool = False
    default: Optional[Any] = None
    comment: Optional[str] = None
    auto_increment: bool = False
    foreign_key: Optional[Dict[str, str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert column schema to dictionary"""
        return {
            "name": self.name,
            "type": self.type,
            "nullable": self.nullable,
            "primary_key": self.primary_key,
            "unique": self.unique,
            "default": self.default,
            "comment": self.comment,
            "auto_increment": self.auto_increment,
            "foreign_key": self.foreign_key
        }


@dataclass
class TableSchema:
    """Represents a table definition"""
    name: str
    columns: List[ColumnSchema]
    primary_key: Optional[str] = None
    properties: Dict[str, Any] = field(default_factory=dict)
    indexes: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert table schema to dictionary"""
        return {
            "name": self.name,
            "columns": [col.to_dict() for col in self.columns],
            "primary_key": self.primary_key,
            "properties": self.properties,
            "indexes": self.indexes
        }


@dataclass
class Relationship:
    """Represents a relationship between tables"""
    models: List[str]
    condition: str
    join_type: JoinType
    name: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert relationship to dictionary"""
        return {
            "models": self.models,
            "condition": self.condition,
            "joinType": self.join_type.value,
            "name": self.name
        }


class SchemaBuilder:
    """
    Main class for building database schemas and DDL statements.
    
    Example usage:
        ```python
        schema_data = {
            "models": [
                {
                    "name": "customers",
                    "columns": [
                        {"name": "id", "type": "INTEGER"},
                        {"name": "email", "type": "VARCHAR"}
                    ],
                    "primaryKey": "id",
                    "properties": {
                        "displayName": "Customers",
                        "description": "Customer information"
                    }
                }
            ],
            "relationships": [
                {
                    "models": ["customers", "orders"],
                    "condition": "customers.id = orders.customer_id",
                    "joinType": "ONE_TO_MANY"
                }
            ]
        }
        
        builder = SchemaBuilder()
        tables = builder.parse_schema(schema_data)
        ddl = builder.build_ddl(tables)
        ```
    """
    
    def __init__(self, dialect: str = "postgresql"):
        """
        Initialize Schema Builder.
        
        Args:
            dialect: Database dialect (postgresql, mysql, sqlite, etc.)
        """
        self.dialect = dialect.lower()
        logger.info(f"SchemaBuilder initialized with dialect: {self.dialect}")
    
    def parse_schema(self, schema_data: Dict[str, Any]) -> Dict[str, TableSchema]:
        """
        Parse schema data from JSON format to TableSchema objects.
        
        Args:
            schema_data: Dictionary containing models and relationships
            
        Returns:
            Dictionary mapping table names to TableSchema objects
        """
        try:
            models = schema_data.get("models", [])
            relationships = schema_data.get("relationships", [])
            
            tables = {}
            
            # Parse models/tables
            for model in models:
                table_name = model.get("name")
                columns_data = model.get("columns", [])
                primary_key = model.get("primaryKey")
                properties = model.get("properties", {})
                
                # Parse columns
                columns = []
                for col_data in columns_data:
                    column = ColumnSchema(
                        name=col_data.get("name"),
                        type=col_data.get("type", "VARCHAR"),
                        nullable=col_data.get("nullable", True),
                        primary_key=col_data.get("name") == primary_key,
                        unique=col_data.get("unique", False),
                        default=col_data.get("default"),
                        comment=col_data.get("comment"),
                        auto_increment=col_data.get("auto_increment", False)
                    )
                    columns.append(column)
                
                # Create table schema
                table = TableSchema(
                    name=table_name,
                    columns=columns,
                    primary_key=primary_key,
                    properties=properties
                )
                
                tables[table_name] = table
                logger.info(f"Parsed table schema: {table_name} with {len(columns)} columns")
            
            # Process relationships to add foreign keys
            self._process_relationships(tables, relationships)
            
            return tables
            
        except Exception as e:
            logger.error(f"Error parsing schema: {str(e)}")
            raise
    
    def _process_relationships(
        self,
        tables: Dict[str, TableSchema],
        relationships: List[Dict[str, Any]]
    ) -> None:
        """
        Process relationships and add foreign key constraints to columns.
        
        Args:
            tables: Dictionary of table schemas
            relationships: List of relationship definitions
        """
        for rel in relationships:
            models = rel.get("models", [])
            condition = rel.get("condition", "")
            join_type = rel.get("joinType", "ONE_TO_MANY")
            
            if len(models) != 2:
                logger.warning(f"Invalid relationship: {rel}")
                continue
            
            # Parse condition like "customers.id = orders.customer_id"
            if "=" in condition:
                parts = condition.split("=")
                if len(parts) == 2:
                    left = parts[0].strip().split(".")
                    right = parts[1].strip().split(".")
                    
                    if len(left) == 2 and len(right) == 2:
                        parent_table, parent_col = left
                        child_table, child_col = right
                        
                        # Add foreign key to child table column
                        if child_table in tables:
                            for col in tables[child_table].columns:
                                if col.name == child_col:
                                    col.foreign_key = {
                                        "table": parent_table,
                                        "column": parent_col
                                    }
                                    logger.info(
                                        f"Added foreign key: {child_table}.{child_col} -> "
                                        f"{parent_table}.{parent_col}"
                                    )
    
    def build_ddl(
        self,
        tables: Dict[str, TableSchema],
        include_comments: bool = True,
        include_if_not_exists: bool = True
    ) -> str:
        """
        Build DDL (Data Definition Language) statements from table schemas.
        
        Args:
            tables: Dictionary of table schemas
            include_comments: Whether to include column comments
            include_if_not_exists: Whether to include IF NOT EXISTS clause
            
        Returns:
            Complete DDL SQL string
        """
        try:
            ddl_statements = []
            
            for table_name, table in tables.items():
                ddl = self._build_table_ddl(
                    table,
                    include_comments=include_comments,
                    include_if_not_exists=include_if_not_exists
                )
                ddl_statements.append(ddl)
            
            full_ddl = "\n\n".join(ddl_statements)
            logger.info(f"Built DDL for {len(tables)} tables")
            
            return full_ddl
            
        except Exception as e:
            logger.error(f"Error building DDL: {str(e)}")
            raise
    
    def _build_table_ddl(
        self,
        table: TableSchema,
        include_comments: bool = True,
        include_if_not_exists: bool = True
    ) -> str:
        """
        Build DDL for a single table.
        
        Args:
            table: Table schema
            include_comments: Whether to include comments
            include_if_not_exists: Whether to include IF NOT EXISTS
            
        Returns:
            DDL SQL string for the table
        """
        lines = []
        
        # Table header with optional description comment
        if include_comments and table.properties.get("description"):
            lines.append(f"-- {table.properties.get('description')}")
        
        # CREATE TABLE statement
        if_not_exists = "IF NOT EXISTS " if include_if_not_exists else ""
        lines.append(f"CREATE TABLE {if_not_exists}{table.name} (")
        
        # Column definitions
        column_defs = []
        constraints = []
        
        for col in table.columns:
            col_def = self._build_column_definition(col, include_comments)
            column_defs.append(col_def)
            
            # Collect constraints
            if col.foreign_key:
                fk_constraint = self._build_foreign_key_constraint(table.name, col)
                if fk_constraint:
                    constraints.append(fk_constraint)
        
        # Combine columns and constraints
        all_definitions = column_defs + constraints
        lines.append("  " + ",\n  ".join(all_definitions))
        lines.append(");")
        
        return "\n".join(lines)
    
    def _build_column_definition(
        self,
        column: ColumnSchema,
        include_comments: bool = True
    ) -> str:
        """
        Build column definition string.
        
        Args:
            column: Column schema
            include_comments: Whether to include inline comments
            
        Returns:
            Column definition SQL string
        """
        parts = []
        
        # Column name and type
        col_type = self._normalize_data_type(column.type)
        parts.append(f"{column.name} {col_type}")
        
        # Primary key
        if column.primary_key:
            parts.append("PRIMARY KEY")
        
        # Auto increment (varies by dialect)
        if column.auto_increment:
            if self.dialect == "postgresql":
                parts[0] = f"{column.name} SERIAL"
            elif self.dialect in ["mysql", "sqlite"]:
                parts.append("AUTO_INCREMENT")
        
        # Nullable
        if not column.nullable:
            parts.append("NOT NULL")
        
        # Unique
        if column.unique:
            parts.append("UNIQUE")
        
        # Default value
        if column.default is not None:
            if isinstance(column.default, str):
                parts.append(f"DEFAULT '{column.default}'")
            else:
                parts.append(f"DEFAULT {column.default}")
        
        definition = " ".join(parts)
        
        # Add inline comment if supported
        if include_comments and column.comment and self.dialect == "postgresql":
            definition += f" -- {column.comment}"
        
        return definition
    
    def _build_foreign_key_constraint(
        self,
        table_name: str,
        column: ColumnSchema
    ) -> Optional[str]:
        """
        Build foreign key constraint.
        
        Args:
            table_name: Name of the table containing the foreign key
            column: Column with foreign key reference
            
        Returns:
            Foreign key constraint SQL string or None
        """
        if not column.foreign_key:
            return None
        
        ref_table = column.foreign_key.get("table")
        ref_column = column.foreign_key.get("column")
        
        if not ref_table or not ref_column:
            return None
        
        constraint_name = f"fk_{table_name}_{column.name}"
        return (
            f"CONSTRAINT {constraint_name} FOREIGN KEY ({column.name}) "
            f"REFERENCES {ref_table}({ref_column})"
        )
    
    def _normalize_data_type(self, data_type: str) -> str:
        """
        Normalize data type for the target dialect.
        
        Args:
            data_type: Input data type
            
        Returns:
            Normalized data type for the dialect
        """
        data_type_upper = data_type.upper()
        
        # Handle special cases by dialect
        if self.dialect == "postgresql":
            type_mapping = {
                "DATETIME": "TIMESTAMP",
                "BLOB": "BYTEA",
                "INT": "INTEGER",
                "INT64": "BIGINT",
                "FLOAT64": "DOUBLE PRECISION"
            }
        elif self.dialect == "mysql":
            type_mapping = {
                "BYTEA": "BLOB",
                "SERIAL": "INTEGER AUTO_INCREMENT",
                "DOUBLE PRECISION": "DOUBLE"
            }
        elif self.dialect == "sqlite":
            type_mapping = {
                "VARCHAR": "TEXT",
                "CHAR": "TEXT",
                "BYTEA": "BLOB",
                "TIMESTAMP": "TEXT",
                "DATETIME": "TEXT"
            }
        else:
            type_mapping = {}
        
        return type_mapping.get(data_type_upper, data_type)
    
    def get_table_schema(
        self,
        table: TableSchema,
        format: str = "dict"
    ) -> Dict[str, Any]:
        """
        Get detailed table schema information.
        
        Args:
            table: Table schema object
            format: Output format ('dict' or 'json')
            
        Returns:
            Schema information as dictionary
        """
        schema_info = {
            "name": table.name,
            "displayName": table.properties.get("displayName", table.name),
            "description": table.properties.get("description", ""),
            "primaryKey": table.primary_key,
            "columns": [],
            "foreignKeys": [],
            "indexes": table.indexes
        }
        
        for col in table.columns:
            col_info = {
                "name": col.name,
                "type": col.type,
                "nullable": col.nullable,
                "primaryKey": col.primary_key,
                "unique": col.unique,
                "default": col.default,
                "comment": col.comment
            }
            schema_info["columns"].append(col_info)
            
            if col.foreign_key:
                fk_info = {
                    "column": col.name,
                    "referencedTable": col.foreign_key.get("table"),
                    "referencedColumn": col.foreign_key.get("column")
                }
                schema_info["foreignKeys"].append(fk_info)
        
        return schema_info
    
    def build_schema_documentation(
        self,
        tables: Dict[str, TableSchema]
    ) -> str:
        """
        Build human-readable documentation for the schema.
        
        Args:
            tables: Dictionary of table schemas
            
        Returns:
            Markdown-formatted documentation
        """
        doc_lines = ["# Database Schema Documentation\n"]
        
        for table_name, table in tables.items():
            doc_lines.append(f"## Table: {table_name}")
            
            # Table description
            if table.properties.get("description"):
                doc_lines.append(f"\n**Description:** {table.properties['description']}\n")
            
            # Columns table
            doc_lines.append("### Columns\n")
            doc_lines.append("| Column | Type | Nullable | Primary Key | Foreign Key | Description |")
            doc_lines.append("|--------|------|----------|-------------|-------------|-------------|")
            
            for col in table.columns:
                fk_info = ""
                if col.foreign_key:
                    fk_table = col.foreign_key.get("table")
                    fk_col = col.foreign_key.get("column")
                    fk_info = f"{fk_table}.{fk_col}"
                
                doc_lines.append(
                    f"| {col.name} | {col.type} | "
                    f"{'Yes' if col.nullable else 'No'} | "
                    f"{'Yes' if col.primary_key else 'No'} | "
                    f"{fk_info} | {col.comment or ''} |"
                )
            
            doc_lines.append("\n")
        
        return "\n".join(doc_lines)


# Convenience functions for quick usage

def parse_schema_from_json(schema_data: Dict[str, Any], dialect: str = "postgresql") -> Dict[str, TableSchema]:
    """
    Quick function to parse schema from JSON data.
    
    Args:
        schema_data: Schema definition dictionary
        dialect: Database dialect
        
    Returns:
        Dictionary of table schemas
    """
    builder = SchemaBuilder(dialect=dialect)
    return builder.parse_schema(schema_data)


def build_ddl_from_json(schema_data: Dict[str, Any], dialect: str = "postgresql") -> str:
    """
    Quick function to build DDL from JSON data.
    
    Args:
        schema_data: Schema definition dictionary
        dialect: Database dialect
        
    Returns:
        DDL SQL string
    """
    builder = SchemaBuilder(dialect=dialect)
    tables = builder.parse_schema(schema_data)
    return builder.build_ddl(tables)


def get_table_info(schema_data: Dict[str, Any], table_name: str) -> Optional[Dict[str, Any]]:
    """
    Get detailed information about a specific table.
    
    Args:
        schema_data: Schema definition dictionary
        table_name: Name of the table
        
    Returns:
        Table information dictionary or None
    """
    builder = SchemaBuilder()
    tables = builder.parse_schema(schema_data)
    
    if table_name in tables:
        return builder.get_table_schema(tables[table_name])
    
    return None
