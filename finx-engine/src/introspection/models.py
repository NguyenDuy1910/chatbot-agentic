from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class ColumnMetadata:
    name: str
    type: str
    comment: str = ""
    nullable: bool = True
    is_primary_key: bool = False
    is_foreign_key: bool = False
    foreign_key_table: Optional[str] = None
    default: Optional[str] = None
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TableMetadata:
    name: str
    description: str = ""
    columns: List[ColumnMetadata] = field(default_factory=list)
    primary_key: Optional[str] = None
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RelationshipMetadata:
    name: str
    source_table: str
    target_table: str
    source_column: str
    target_column: str
    join_type: str = "MANY_TO_ONE"
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SchemaMetadata:
    database: str
    tables: List[TableMetadata] = field(default_factory=list)
    relationships: List[RelationshipMetadata] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)
