"""
Schema Metadata Models

Data structures for representing database schemas.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum


class JoinType(str, Enum):
    """Relationship join types"""
    ONE_TO_ONE = "ONE_TO_ONE"
    ONE_TO_MANY = "ONE_TO_MANY"
    MANY_TO_ONE = "MANY_TO_ONE"
    MANY_TO_MANY = "MANY_TO_MANY"


@dataclass
class ColumnMetadata:
    """Metadata for a database column"""
    name: str
    type: str
    comment: str = ""
    nullable: bool = True
    default: Optional[Any] = None
    is_primary_key: bool = False
    is_foreign_key: bool = False
    foreign_key_table: Optional[str] = None
    foreign_key_column: Optional[str] = None
    max_length: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "type": self.type,
            "description": self.comment,
            "nullable": self.nullable,
            "default": self.default,
            "primary_key": self.is_primary_key,
            "foreign_key": self.is_foreign_key,
            "foreign_key_table": self.foreign_key_table,
            "foreign_key_column": self.foreign_key_column,
            "max_length": self.max_length
        }


@dataclass
class TableMetadata:
    """Metadata for a database table"""
    name: str
    description: str
    columns: List[ColumnMetadata] = field(default_factory=list)
    primary_key: Optional[str] = None
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "description": self.description,
            "columns": [col.to_dict() for col in self.columns],
            "primary_key": self.primary_key,
            "properties": self.properties
        }


@dataclass
class RelationshipMetadata:
    """Metadata for table relationships"""
    name: str
    source_table: str
    target_table: str
    source_column: str
    target_column: str
    join_type: str = "MANY_TO_ONE"
    constraint_name: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "type": self.join_type.lower(),
            "from_model": self.source_table,
            "from_column": self.source_column,
            "to_model": self.target_table,
            "to_column": self.target_column,
            "constraint_name": self.constraint_name
        }


@dataclass
class SchemaMetadata:
    """Complete database schema metadata"""
    database: str
    tables: List[TableMetadata] = field(default_factory=list)
    relationships: List[RelationshipMetadata] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "database": self.database,
            "tables": [table.to_dict() for table in self.tables],
            "relationships": [rel.to_dict() for rel in self.relationships],
            "properties": self.properties
        }
    
    def get_table(self, table_name: str) -> Optional[TableMetadata]:
        """Get table by name"""
        for table in self.tables:
            if table.name == table_name:
                return table
        return None
