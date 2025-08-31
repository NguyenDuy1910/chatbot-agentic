import logging
import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from src.web.internal.db import get_db
from src.web.models.connections import (
    Connection, ConnectionTemplate, ConnectionLog,
    ConnectionModel, ConnectionTemplateModel, ConnectionLogModel,
    ConnectionCreateForm, ConnectionUpdateForm, ConnectionTestForm,
    ConnectionResponse, ConnectionListResponse, ConnectionTemplateResponse,
    ConnectionStatsResponse, ConnectionTestResult,
    ConnectionType, ConnectionStatus
)
from src.web.utils.auth import get_current_user
from src.web.utils.connections import (
    test_connection, get_connection_templates, create_connection_log
)
from src.web.utils.security import (
    encrypt_credentials, decrypt_credentials, mask_credentials,
    check_connection_permission, audit_connection_access, SecurityError,
    validate_credentials
)
from src.web.utils.health_monitor import force_health_check, get_health_summary

log = logging.getLogger(__name__)

router = APIRouter()

####################
# CONNECTION CRUD
####################

@router.get("/", response_model=ConnectionListResponse)
async def get_connections(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    type_filter: Optional[ConnectionType] = Query(None, alias="type"),
    status_filter: Optional[ConnectionStatus] = Query(None, alias="status"),
    provider_filter: Optional[str] = Query(None, alias="provider"),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    try:
        query = db.query(Connection)
        
        # Apply filters
        if type_filter:
            query = query.filter(Connection.type == type_filter)
        if status_filter:
            query = query.filter(Connection.status == status_filter)
        if provider_filter:
            query = query.filter(Connection.provider.ilike(f"%{provider_filter}%"))
        if search:
            query = query.filter(
                or_(
                    Connection.name.ilike(f"%{search}%"),
                    Connection.description.ilike(f"%{search}%"),
                    Connection.provider.ilike(f"%{search}%")
                )
            )
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * limit
        connections = query.order_by(desc(Connection.updated_at)).offset(offset).limit(limit).all()
        
        # Convert to response models
        connection_models = []
        for conn in connections:
            # Decrypt credentials for response (remove sensitive data)
            decrypted_creds = decrypt_credentials(conn.credentials) if conn.credentials else {}
            # Remove sensitive fields from response
            safe_creds = {k: v for k, v in decrypted_creds.items() 
                         if k not in ['password', 'api_key', 'bearer_token', 'client_secret', 'private_key']}
            
            connection_model = ConnectionModel(
                id=str(conn.id),
                name=conn.name,
                description=conn.description,
                type=conn.type,
                provider=conn.provider,
                status=conn.status,
                is_active=conn.is_active,
                config=conn.config or {},
                credentials=safe_creds,
                health_check=conn.health_check or {},
                tags=conn.tags or [],
                category=conn.category,
                version=conn.version,
                last_connected=conn.last_connected,
                last_health_check=conn.last_health_check,
                last_error=conn.last_error,
                error_count=conn.error_count,
                success_count=conn.success_count,
                created_at=conn.created_at,
                updated_at=conn.updated_at,
                created_by=conn.created_by,
                updated_by=conn.updated_by
            )
            connection_models.append(connection_model)
        
        return ConnectionListResponse(
            connections=connection_models,
            total=total,
            page=page,
            limit=limit
        )
        
    except Exception as e:
        log.error(f"Error fetching connections: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch connections"
        )

@router.get("/{connection_id}", response_model=ConnectionResponse)
async def get_connection(
    connection_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific connection by ID"""
    try:
        connection = db.query(Connection).filter(Connection.id == connection_id).first()
        if not connection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Connection not found"
            )
        
        # Decrypt credentials for response (remove sensitive data)
        decrypted_creds = decrypt_credentials(connection.credentials) if connection.credentials else {}
        safe_creds = {k: v for k, v in decrypted_creds.items() 
                     if k not in ['password', 'api_key', 'bearer_token', 'client_secret', 'private_key']}
        
        connection_model = ConnectionModel(
            id=str(connection.id),
            name=connection.name,
            description=connection.description,
            type=connection.type,
            provider=connection.provider,
            status=connection.status,
            is_active=connection.is_active,
            config=connection.config or {},
            credentials=safe_creds,
            health_check=connection.health_check or {},
            tags=connection.tags or [],
            category=connection.category,
            version=connection.version,
            last_connected=connection.last_connected,
            last_health_check=connection.last_health_check,
            last_error=connection.last_error,
            error_count=connection.error_count,
            success_count=connection.success_count,
            created_at=connection.created_at,
            updated_at=connection.updated_at,
            created_by=connection.created_by,
            updated_by=connection.updated_by
        )
        
        return ConnectionResponse(connection=connection_model)
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error fetching connection {connection_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch connection"
        )

@router.post("/", response_model=ConnectionResponse)
async def create_connection(
    connection_data: ConnectionCreateForm,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new connection"""
    try:
        # Check permissions
        if not check_connection_permission('create', current_user.role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to create connections"
            )

        # Validate credentials
        if not validate_credentials(connection_data.credentials.dict(), connection_data.credentials.type):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid credentials for the specified authentication type"
            )
        # Encrypt credentials
        encrypted_creds = encrypt_credentials(connection_data.credentials.dict())
        
        # Create connection
        connection = Connection(
            name=connection_data.name,
            description=connection_data.description,
            type=connection_data.type,
            provider=connection_data.provider,
            config=connection_data.config.dict(),
            credentials=encrypted_creds,
            health_check=connection_data.health_check.dict(),
            tags=connection_data.tags,
            category=connection_data.category,
            is_active=connection_data.is_active,
            created_by=current_user.id,
            updated_by=current_user.id
        )
        
        db.add(connection)
        db.commit()
        db.refresh(connection)

        # Audit log
        audit_connection_access(str(connection.id), current_user.id, "create")

        # Log creation
        await create_connection_log(
            db, str(connection.id), "info",
            f"Connection '{connection.name}' created",
            {"user_id": current_user.id}
        )
        
        # Convert to response model
        connection_model = ConnectionModel(
            id=str(connection.id),
            name=connection.name,
            description=connection.description,
            type=connection.type,
            provider=connection.provider,
            status=connection.status,
            is_active=connection.is_active,
            config=connection.config or {},
            credentials=connection_data.credentials,  # Return original for immediate use
            health_check=connection.health_check or {},
            tags=connection.tags or [],
            category=connection.category,
            created_at=connection.created_at,
            updated_at=connection.updated_at,
            created_by=connection.created_by,
            updated_by=connection.updated_by
        )
        
        return ConnectionResponse(connection=connection_model)

    except Exception as e:
        log.error(f"Error creating connection: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create connection"
        )

@router.put("/{connection_id}", response_model=ConnectionResponse)
async def update_connection(
    connection_id: str,
    connection_data: ConnectionUpdateForm,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update an existing connection"""
    try:
        connection = db.query(Connection).filter(Connection.id == connection_id).first()
        if not connection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Connection not found"
            )

        # Check permissions
        if not check_connection_permission('edit', current_user.role, connection.created_by, current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to edit this connection"
            )

        # Update fields
        update_data = connection_data.dict(exclude_unset=True)

        for field, value in update_data.items():
            if field == "credentials" and value:
                # Encrypt new credentials
                setattr(connection, field, encrypt_credentials(value.dict()))
            elif field in ["config", "health_check"] and value:
                setattr(connection, field, value.dict())
            else:
                setattr(connection, field, value)

        connection.updated_by = current_user.id
        connection.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(connection)

        # Audit log
        audit_connection_access(str(connection.id), current_user.id, "update")

        # Log update
        await create_connection_log(
            db, str(connection.id), "info",
            f"Connection '{connection.name}' updated",
            {"user_id": current_user.id, "updated_fields": list(update_data.keys())}
        )

        # Convert to response model
        decrypted_creds = decrypt_credentials(connection.credentials) if connection.credentials else {}
        safe_creds = {k: v for k, v in decrypted_creds.items()
                     if k not in ['password', 'api_key', 'bearer_token', 'client_secret', 'private_key']}

        connection_model = ConnectionModel(
            id=str(connection.id),
            name=connection.name,
            description=connection.description,
            type=connection.type,
            provider=connection.provider,
            status=connection.status,
            is_active=connection.is_active,
            config=connection.config or {},
            credentials=safe_creds,
            health_check=connection.health_check or {},
            tags=connection.tags or [],
            category=connection.category,
            version=connection.version,
            last_connected=connection.last_connected,
            last_health_check=connection.last_health_check,
            last_error=connection.last_error,
            error_count=connection.error_count,
            success_count=connection.success_count,
            created_at=connection.created_at,
            updated_at=connection.updated_at,
            created_by=connection.created_by,
            updated_by=connection.updated_by
        )

        return ConnectionResponse(connection=connection_model)

    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error updating connection {connection_id}: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update connection"
        )

@router.delete("/{connection_id}")
async def delete_connection(
    connection_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete a connection"""
    try:
        connection = db.query(Connection).filter(Connection.id == connection_id).first()
        if not connection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Connection not found"
            )

        # Check permissions
        if not check_connection_permission('delete', current_user.role, connection.created_by, current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to delete this connection"
            )

        connection_name = connection.name

        # Delete related logs
        db.query(ConnectionLog).filter(ConnectionLog.connection_id == connection_id).delete()

        # Delete connection
        db.delete(connection)
        db.commit()

        # Audit log
        audit_connection_access(connection_id, current_user.id, "delete")

        # Log deletion
        await create_connection_log(
            db, connection_id, "info",
            f"Connection '{connection_name}' deleted",
            {"user_id": current_user.id}
        )

        return {"message": "Connection deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error deleting connection {connection_id}: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete connection"
        )

####################
# CONNECTION TESTING
####################

@router.post("/test", response_model=ConnectionTestResult)
async def test_connection_configuration(
    test_data: ConnectionTestForm,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Test a connection configuration"""
    try:
        result = await test_connection(test_data.connection_data, test_data.test_endpoint, test_data.test_method)

        # Log test result
        await create_connection_log(
            db, "test", "info" if result.success else "error",
            f"Connection test {'successful' if result.success else 'failed'}: {result.message}",
            {"user_id": current_user.id, "test_result": result.dict()}
        )

        return result

    except Exception as e:
        log.error(f"Error testing connection: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to test connection"
        )

@router.post("/{connection_id}/test", response_model=ConnectionTestResult)
async def test_existing_connection(
    connection_id: str,
    test_endpoint: Optional[str] = None,
    test_method: Optional[str] = "GET",
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Test an existing connection"""
    try:
        connection = db.query(Connection).filter(Connection.id == connection_id).first()
        if not connection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Connection not found"
            )

        # Decrypt credentials for testing
        decrypted_creds = decrypt_credentials(connection.credentials) if connection.credentials else {}

        # Create test form data
        from src.web.models.connections import ConnectionCredentials, ConnectionConfig, ConnectionHealthCheck
        test_data = ConnectionCreateForm(
            name=connection.name,
            type=connection.type,
            provider=connection.provider,
            config=ConnectionConfig(**connection.config) if connection.config else ConnectionConfig(),
            credentials=ConnectionCredentials(**decrypted_creds),
            health_check=ConnectionHealthCheck(**connection.health_check) if connection.health_check else ConnectionHealthCheck()
        )

        result = await test_connection(test_data, test_endpoint, test_method)

        # Update connection status based on test result
        if result.success:
            connection.status = ConnectionStatus.ACTIVE
            connection.last_connected = datetime.utcnow()
            connection.success_count += 1
            connection.last_error = None
        else:
            connection.status = ConnectionStatus.ERROR
            connection.error_count += 1
            connection.last_error = result.error or result.message

        connection.last_health_check = datetime.utcnow()
        db.commit()

        # Log test result
        await create_connection_log(
            db, connection_id, "info" if result.success else "error",
            f"Connection test {'successful' if result.success else 'failed'}: {result.message}",
            {"user_id": current_user.id, "test_result": result.dict()}
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error testing connection {connection_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to test connection"
        )

####################
# TEMPLATES & STATS
####################

@router.get("/templates", response_model=ConnectionTemplateResponse)
async def get_connection_templates(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get available connection templates"""
    try:
        templates = get_connection_templates()

        # Extract unique categories and providers
        categories = list(set(template.category for template in templates))
        providers = list(set(template.provider for template in templates))

        return ConnectionTemplateResponse(
            templates=templates,
            categories=sorted(categories),
            providers=sorted(providers)
        )

    except Exception as e:
        log.error(f"Error fetching connection templates: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch connection templates"
        )

@router.get("/statistics", response_model=ConnectionStatsResponse)
async def get_connection_statistics(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get connection statistics for dashboard"""
    try:
        # Get all connections
        connections = db.query(Connection).all()

        total_connections = len(connections)
        active_connections = len([c for c in connections if c.status == ConnectionStatus.ACTIVE])
        error_connections = len([c for c in connections if c.status == ConnectionStatus.ERROR])

        # Recently used (connected in last 24 hours)
        from datetime import timedelta
        recent_threshold = datetime.utcnow() - timedelta(hours=24)
        recently_used = len([c for c in connections if c.last_connected and c.last_connected > recent_threshold])

        # Calculate average response time (mock for now)
        average_response_time = 150.0  # milliseconds

        # Calculate uptime percentage
        uptime = (active_connections / total_connections * 100) if total_connections > 0 else 100.0

        # Group by type
        connections_by_type = {}
        for conn_type in ConnectionType:
            connections_by_type[conn_type.value] = len([c for c in connections if c.type == conn_type])

        # Group by status
        connections_by_status = {}
        for status_type in ConnectionStatus:
            connections_by_status[status_type.value] = len([c for c in connections if c.status == status_type])

        return ConnectionStatsResponse(
            total_connections=total_connections,
            active_connections=active_connections,
            error_connections=error_connections,
            recently_used=recently_used,
            average_response_time=average_response_time,
            uptime=uptime,
            connections_by_type=connections_by_type,
            connections_by_status=connections_by_status
        )

    except Exception as e:
        log.error(f"Error fetching connection stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch connection statistics"
        )

@router.get("/{connection_id}/logs")
async def get_connection_logs(
    connection_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    level: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get logs for a specific connection"""
    try:
        query = db.query(ConnectionLog).filter(ConnectionLog.connection_id == connection_id)

        if level:
            query = query.filter(ConnectionLog.level == level)

        total = query.count()
        offset = (page - 1) * limit
        logs = query.order_by(desc(ConnectionLog.timestamp)).offset(offset).limit(limit).all()

        log_models = [
            {
                "id": str(log.id),
                "connection_id": str(log.connection_id),
                "level": log.level,
                "message": log.message,
                "details": log.details,
                "timestamp": log.timestamp,
                "user_id": log.user_id
            }
            for log in logs
        ]

        return {
            "logs": log_models,
            "total": total,
            "page": page,
            "limit": limit
        }

    except Exception as e:
        log.error(f"Error fetching connection logs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch connection logs"
        )

####################
# HEALTH MONITORING
####################

@router.post("/{connection_id}/health-check")
async def force_connection_health_check(
    connection_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Force a health check for a specific connection"""
    try:
        # Check if connection exists
        connection = db.query(Connection).filter(Connection.id == connection_id).first()
        if not connection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Connection not found"
            )

        # Check permissions
        if not check_connection_permission('test', current_user.role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to test connections"
            )

        # Force health check
        success = await force_health_check(connection_id)

        if success:
            # Audit log
            audit_connection_access(connection_id, current_user.id, "health_check")

            return {"message": "Health check completed", "connection_id": connection_id}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to perform health check"
            )

    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error forcing health check for {connection_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to perform health check"
        )

@router.get("/health-summary")
async def get_connections_health_summary(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get overall health summary of all connections"""
    try:
        summary = await get_health_summary()
        return summary

    except Exception as e:
        log.error(f"Error fetching health summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch health summary"
        )

@router.get("/health-alerts")
async def get_connection_alerts(
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get recent connection alerts and errors"""
    try:
        # Get recent error logs
        error_logs = db.query(ConnectionLog).filter(
            ConnectionLog.level.in_(['error', 'warn'])
        ).order_by(desc(ConnectionLog.timestamp)).limit(limit).all()

        alerts = []
        for log_entry in error_logs:
            # Get connection info
            connection = db.query(Connection).filter(Connection.id == log_entry.connection_id).first()

            alert = {
                "id": str(log_entry.id),
                "connection_id": str(log_entry.connection_id),
                "connection_name": connection.name if connection else "Unknown",
                "level": log_entry.level,
                "message": log_entry.message,
                "timestamp": log_entry.timestamp,
                "details": log_entry.details
            }
            alerts.append(alert)

        return {
            "alerts": alerts,
            "total": len(alerts),
            "limit": limit
        }

    except Exception as e:
        log.error(f"Error fetching connection alerts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch connection alerts"
        )
