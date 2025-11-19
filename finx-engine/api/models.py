"""
Pydantic Models for API
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class DatabaseType(str, Enum):
    """Supported database types"""
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MONGODB = "mongodb"
    ATHENA = "athena"
    REDSHIFT = "redshift"
    SNOWFLAKE = "snowflake"


class DataSourceCreate(BaseModel):
    """Request model for creating datasource"""
    name: str = Field(..., description="Datasource name")
    type: DatabaseType = Field(..., description="Database type")
    host: str = Field(None, description="Database host (not required for Athena)")
    port: int = Field(None, description="Database port (not required for Athena)")
    database: str = Field(..., description="Database name or Athena workgroup/catalog")
    username: str = Field(None, description="Username (not required for Athena with IAM)")
    password: str = Field(None, description="Password (not required for Athena with IAM)")
    schema: Optional[str] = Field(None, description="Default schema")
    extra_params: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Extra connection parameters (AWS region, S3 bucket, etc.)")


class DataSourceUpdate(BaseModel):
    """Request model for updating datasource"""
    name: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    schema: Optional[str] = None
    extra_params: Optional[Dict[str, Any]] = None


class DataSourceResponse(BaseModel):
    """Response model for datasource"""
    id: str
    name: str
    type: DatabaseType
    host: str
    port: int
    database: str
    username: str
    schema: Optional[str] = None
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


class ConnectionTestResponse(BaseModel):
    """Response for connection test"""
    status: str
    message: str
    latency_ms: Optional[float] = None


class IntrospectionRequest(BaseModel):
    """Request model for introspection"""
    schema_name: Optional[str] = Field(None, description="Schema to introspect")
    tables: Optional[List[str]] = Field(None, description="Specific tables to introspect")
    detect_relationships: bool = Field(True, description="Detect foreign key relationships")
    detect_primary_keys: bool = Field(True, description="Detect primary keys")


class IntrospectionResponse(BaseModel):
    """Response model for introspection"""
    datasource_id: str
    status: str
    tables_count: int
    relationships_count: int
    mdl_generated: bool


class MDLResponse(BaseModel):
    """Response model for MDL"""
    datasource_id: str
    version: str = "1.0"
    database: str
    models: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]
    generated_at: str
