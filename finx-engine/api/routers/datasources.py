from fastapi import APIRouter, HTTPException, status
from typing import List

from api.models import (
    DataSourceCreate,
    DataSourceUpdate,
    DataSourceResponse,
    ConnectionTestResponse
)
from api.storage import DataSourceStorage
from src.connectors import ConnectorFactory, DataSourceConfig

router = APIRouter()


@router.post("/datasources", response_model=DataSourceResponse, status_code=status.HTTP_201_CREATED)
async def create_datasource(datasource: DataSourceCreate):
    """
    Create a new datasource.
    
    Creates a datasource configuration for connecting to a database.
    The password is stored securely.
    """
    try:
        # Convert to dict and create
        datasource_data = datasource.model_dump()
        created = DataSourceStorage.create(datasource_data)
        
        # Don't return password in response
        response_data = {k: v for k, v in created.items() if k != "password"}
        
        return DataSourceResponse(**response_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create datasource: {str(e)}"
        )


@router.get("/datasources", response_model=List[DataSourceResponse])
async def list_datasources():
    """
    List all datasources.
    
    Returns a list of all configured datasources (without passwords).
    """
    datasources = DataSourceStorage.list_all()
    
    # Remove passwords from response
    return [
        DataSourceResponse(**{k: v for k, v in ds.items() if k != "password"})
        for ds in datasources
    ]


@router.get("/datasources/{datasource_id}", response_model=DataSourceResponse)
async def get_datasource(datasource_id: str):
    """
    Get a specific datasource by ID.
    
    Returns datasource configuration (without password).
    """
    datasource = DataSourceStorage.get(datasource_id)
    
    if not datasource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Datasource '{datasource_id}' not found"
        )
    
    # Remove password from response
    response_data = {k: v for k, v in datasource.items() if k != "password"}
    return DataSourceResponse(**response_data)


@router.put("/datasources/{datasource_id}", response_model=DataSourceResponse)
async def update_datasource(datasource_id: str, datasource: DataSourceUpdate):
    """
    Update an existing datasource.
    
    Updates datasource configuration. Only provided fields will be updated.
    """
    existing = DataSourceStorage.get(datasource_id)
    
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Datasource '{datasource_id}' not found"
        )
    
    # Update only provided fields
    update_data = datasource.model_dump(exclude_unset=True)
    updated = DataSourceStorage.update(datasource_id, update_data)
    
    # Remove password from response
    response_data = {k: v for k, v in updated.items() if k != "password"}
    return DataSourceResponse(**response_data)


@router.delete("/datasources/{datasource_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_datasource(datasource_id: str):
    """
    Delete a datasource.
    
    Removes datasource configuration and associated MDL.
    """
    if not DataSourceStorage.get(datasource_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Datasource '{datasource_id}' not found"
        )
    
    # Delete datasource
    DataSourceStorage.delete(datasource_id)
    
    # Also delete associated MDL
    from api.storage import MDLStorage
    MDLStorage.delete(datasource_id)
    
    return None


@router.post("/datasources/{datasource_id}/test", response_model=ConnectionTestResponse)
async def test_datasource_connection(datasource_id: str):
    """
    Test database connection.
    
    Tests connectivity to the database and returns latency.
    """
    datasource = DataSourceStorage.get(datasource_id)
    
    if not datasource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Datasource '{datasource_id}' not found"
        )
    
    try:
        # Create connector config - filter only the fields needed by DataSourceConfig
        config_data = {
            "type": datasource["type"],
            "host": datasource.get("host", ""),
            "port": datasource.get("port", 443),
            "database": datasource["database"],
            "username": datasource.get("username", ""),
            "password": datasource.get("password", ""),
            "schema": datasource.get("schema"),
            "extra_params": datasource.get("extra_params", {})
        }
        config = DataSourceConfig(**config_data)
        
        # Create connector
        connector = ConnectorFactory.create_connector(config)
        
        # Test connection
        result = connector.test_connection()
        
        return ConnectionTestResponse(
            status="connected" if result["success"] else "failed",
            message=result["message"],
            latency_ms=result.get("latency_ms")
        )
    except Exception as e:
        return ConnectionTestResponse(
            status="error",
            message=f"Connection test failed: {str(e)}",
            latency_ms=None
        )
