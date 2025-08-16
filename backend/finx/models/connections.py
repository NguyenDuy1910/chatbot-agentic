import logging
import uuid
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

from backend.finx.internal.db import Base, get_db
from pydantic import BaseModel, Field, validator
from sqlalchemy import Boolean, Column, String, Text, DateTime, Integer, JSON, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID

log = logging.getLogger(__name__)

####################
# ENUMS
####################

class ConnectionType(str, Enum):
    API = "api"
    DATABASE = "database"
    WEBHOOK = "webhook"
    OAUTH = "oauth"
    FILE_STORAGE = "file_storage"
    MESSAGING = "messaging"
    ANALYTICS = "analytics"
    PAYMENT = "payment"
    EMAIL = "email"
    SMS = "sms"
    SOCIAL_MEDIA = "social_media"
    CRM = "crm"
    ERP = "erp"
    CUSTOM = "custom"

class ConnectionStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    TESTING = "testing"
    PENDING = "pending"

class AuthenticationType(str, Enum):
    NONE = "none"
    API_KEY = "api_key"
    BEARER_TOKEN = "bearer_token"
    BASIC_AUTH = "basic_auth"
    OAUTH2 = "oauth2"
    OAUTH1 = "oauth1"
    CUSTOM_HEADER = "custom_header"
    CERTIFICATE = "certificate"
    JWT = "jwt"

####################
# DB MODELS
####################

class Connection(Base):
    __tablename__ = "connections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    type = Column(SQLEnum(ConnectionType), nullable=False)
    provider = Column(String(100), nullable=False)
    status = Column(SQLEnum(ConnectionStatus), default=ConnectionStatus.PENDING)
    is_active = Column(Boolean, default=True)
    
    # Configuration stored as JSON
    config = Column(JSON, nullable=True)
    credentials = Column(JSON, nullable=True)  # Encrypted
    health_check = Column(JSON, nullable=True)
    
    # Metadata
    tags = Column(JSON, nullable=True)  # Array of strings
    category = Column(String(100), nullable=True)
    version = Column(String(50), nullable=True)
    
    # Status tracking
    last_connected = Column(DateTime, nullable=True)
    last_health_check = Column(DateTime, nullable=True)
    last_error = Column(Text, nullable=True)
    error_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(255), nullable=False)
    updated_by = Column(String(255), nullable=False)

class ConnectionTemplate(Base):
    __tablename__ = "connection_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    type = Column(SQLEnum(ConnectionType), nullable=False)
    provider = Column(String(100), nullable=False)
    icon = Column(String(255), nullable=True)
    category = Column(String(100), nullable=False)
    
    # Template configuration
    config_schema = Column(JSON, nullable=True)
    credentials_schema = Column(JSON, nullable=True)
    default_config = Column(JSON, nullable=True)
    default_health_check = Column(JSON, nullable=True)
    
    # Documentation
    documentation = Column(Text, nullable=True)
    setup_instructions = Column(Text, nullable=True)
    example_usage = Column(Text, nullable=True)
    
    # Metadata
    is_popular = Column(Boolean, default=False)
    is_official = Column(Boolean, default=False)
    tags = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ConnectionLog(Base):
    __tablename__ = "connection_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    connection_id = Column(UUID(as_uuid=True), nullable=False)
    level = Column(String(10), nullable=False)  # info, warn, error, debug
    message = Column(Text, nullable=False)
    details = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_id = Column(String(255), nullable=True)

####################
# PYDANTIC MODELS
####################

class ConnectionCredentials(BaseModel):
    type: AuthenticationType
    api_key: Optional[str] = None
    bearer_token: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    custom_headers: Optional[Dict[str, str]] = None
    certificate: Optional[str] = None
    private_key: Optional[str] = None
    additional_fields: Optional[Dict[str, Any]] = None

class RateLimit(BaseModel):
    requests: int
    period: int  # in seconds

class ConnectionConfig(BaseModel):
    base_url: Optional[str] = None
    timeout: Optional[int] = 30
    retry_attempts: Optional[int] = 3
    retry_delay: Optional[int] = 1
    rate_limit: Optional[RateLimit] = None
    custom_settings: Optional[Dict[str, Any]] = None

class ConnectionHealthCheck(BaseModel):
    enabled: bool = True
    interval: int = 5  # in minutes
    endpoint: Optional[str] = None
    method: Optional[str] = "GET"
    expected_status: Optional[int] = 200
    timeout: Optional[int] = 10

class ConnectionModel(BaseModel):
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    type: ConnectionType
    provider: str
    status: ConnectionStatus = ConnectionStatus.PENDING
    is_active: bool = True

    config: ConnectionConfig
    credentials: ConnectionCredentials
    health_check: ConnectionHealthCheck

    tags: Optional[List[str]] = None
    category: Optional[str] = None
    version: Optional[str] = None

    last_connected: Optional[datetime] = None
    last_health_check: Optional[datetime] = None
    last_error: Optional[str] = None
    error_count: int = 0
    success_count: int = 0

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

class ConnectionTemplateModel(BaseModel):
    id: Optional[str] = None
    name: str
    description: str
    type: ConnectionType
    provider: str
    icon: Optional[str] = None
    category: str

    config_schema: Optional[Dict[str, Any]] = None
    credentials_schema: Optional[Dict[str, Any]] = None
    default_config: Optional[ConnectionConfig] = None
    default_health_check: Optional[ConnectionHealthCheck] = None

    documentation: Optional[str] = None
    setup_instructions: Optional[str] = None
    example_usage: Optional[str] = None

    is_popular: bool = False
    is_official: bool = False
    tags: Optional[List[str]] = None

class ConnectionTestResult(BaseModel):
    success: bool
    message: str
    response_time: Optional[float] = None
    status_code: Optional[int] = None
    error: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ConnectionLogModel(BaseModel):
    id: Optional[str] = None
    connection_id: str
    level: str  # info, warn, error, debug
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user_id: Optional[str] = None

####################
# FORMS
####################

class ConnectionCreateForm(BaseModel):
    name: str
    description: Optional[str] = None
    type: ConnectionType
    provider: str
    config: ConnectionConfig
    credentials: ConnectionCredentials
    health_check: ConnectionHealthCheck = Field(default_factory=lambda: ConnectionHealthCheck())
    tags: Optional[List[str]] = None
    category: Optional[str] = None
    is_active: bool = True

class ConnectionUpdateForm(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    config: Optional[ConnectionConfig] = None
    credentials: Optional[ConnectionCredentials] = None
    health_check: Optional[ConnectionHealthCheck] = None
    tags: Optional[List[str]] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None

class ConnectionTestForm(BaseModel):
    connection_data: ConnectionCreateForm
    test_endpoint: Optional[str] = None
    test_method: Optional[str] = "GET"

####################
# RESPONSES
####################

class ConnectionResponse(BaseModel):
    connection: ConnectionModel
    test_result: Optional[ConnectionTestResult] = None

class ConnectionListResponse(BaseModel):
    connections: List[ConnectionModel]
    total: int
    page: int
    limit: int

class ConnectionTemplateResponse(BaseModel):
    templates: List[ConnectionTemplateModel]
    categories: List[str]
    providers: List[str]

class ConnectionStatsResponse(BaseModel):
    total_connections: int
    active_connections: int
    error_connections: int
    recently_used: int
    average_response_time: float
    uptime: float
    connections_by_type: Dict[str, int]
    connections_by_status: Dict[str, int]
