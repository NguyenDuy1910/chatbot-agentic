"""
Utilities package for finx-ai-service.

This package contains utility functions and helper modules for:
- Schema building and DDL generation
- Data type conversions
- Common workflow functions
"""

from .schema_builder import (
    SchemaBuilder,
    ColumnSchema,
    TableSchema,
    Relationship,
    JoinType,
    DataType,
    build_ddl_from_json,
    parse_schema_from_json,
    get_table_info
)

__all__ = [
    # Classes
    "SchemaBuilder",
    "ColumnSchema",
    "TableSchema",
    "Relationship",
    
    # Enums
    "JoinType",
    "DataType",
    
    # Convenience functions
    "build_ddl_from_json",
    "parse_schema_from_json",
    "get_table_info",
]

__version__ = "1.0.0"
