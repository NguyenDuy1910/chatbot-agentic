from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional


class DataSourceCreate(BaseModel):
    datasource_id: str = Field(..., description="Unique identifier for the data source")
    datasource_type: str = Field(..., description="Type of data source (athena, duckdb, postgresql)")
    connection_params: Dict[str, Any] = Field(..., description="Connection parameters specific to the data source type")
    
    class Config:
        json_schema_extra = {
            "example": {
                "datasource_id": "my_postgres_db",
                "datasource_type": "postgresql",
                "connection_params": {
                    "host": "localhost",
                    "port": 5432,
                    "database": "mydb",
                    "user": "postgres",
                    "password": "password",
                    "schema": "public"
                }
            }
        }


class DataSourceResponse(BaseModel):
    datasource_id: str
    datasource_type: str
    connection_params: Dict[str, Any]
    status: Optional[str] = None


class SchemaResponse(BaseModel):
    schemas: List[str]


class TableListResponse(BaseModel):
    tables: List[str]


class ColumnInfo(BaseModel):
    name: str
    type: str
    nullable: bool
    default: Optional[Any] = None
    comment: Optional[str] = None


class ForeignKeyInfo(BaseModel):
    column: str
    referenced_table: str
    referenced_column: str
    constraint_name: Optional[str] = None


class TableDetailResponse(BaseModel):
    name: str
    schema_name: Optional[str] = Field(None, alias="schema")
    columns: List[ColumnInfo]
    primary_keys: List[str]
    foreign_keys: List[ForeignKeyInfo]
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        populate_by_name = True


class IntrospectionRequest(BaseModel):
    schema_name: Optional[str] = Field(None, alias="schema")
    tables: Optional[List[str]] = None
    detect_relationships: bool = True
    detect_primary_keys: bool = True
    
    class Config:
        populate_by_name = True


class IntrospectionResponse(BaseModel):
    datasource_id: str
    status: str
    tables_count: int
    relationships_count: int
    mdl_generated: bool


class MDLResponse(BaseModel):
    datasource_id: str
    mdl: Dict[str, Any]


class ErrorResponse(BaseModel):
    detail: str

