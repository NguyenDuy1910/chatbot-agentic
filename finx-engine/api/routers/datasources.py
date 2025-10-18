from fastapi import APIRouter, HTTPException, status
from typing import List
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from api.models import (
    DataSourceCreate,
    DataSourceResponse,
    SchemaResponse,
    TableListResponse,
    TableDetailResponse,
    ColumnInfo,
    ForeignKeyInfo
)
from api.storage import DataSourceStorage
from src.connectors import ConnectorFactory, DataSourceConfig

router = APIRouter()


@router.get("/datasources", response_model=List[DataSourceResponse])
async def list_datasources():
    datasources = DataSourceStorage.list_all()
    return [
        DataSourceResponse(
            datasource_id=ds["datasource_id"],
            datasource_type=ds["datasource_type"],
            connection_params=ds["connection_params"]
        )
        for ds in datasources
    ]


@router.post("/datasources", response_model=DataSourceResponse, status_code=status.HTTP_201_CREATED)
async def create_datasource(datasource: DataSourceCreate):
    if DataSourceStorage.exists(datasource.datasource_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Data source with ID '{datasource.datasource_id}' already exists"
        )
    
    config = DataSourceConfig(
        datasource_type=datasource.datasource_type,
        datasource_id=datasource.datasource_id,
        connection_params=datasource.connection_params
    )
    
    try:
        connector = ConnectorFactory.create_connector(config)
        if not connector.test_connection():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to connect to data source"
            )
        connector.disconnect()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error testing connection: {str(e)}"
        )
    
    DataSourceStorage.add(datasource.datasource_id, datasource.model_dump())
    
    return DataSourceResponse(
        datasource_id=datasource.datasource_id,
        datasource_type=datasource.datasource_type,
        connection_params=datasource.connection_params,
        status="connected"
    )


@router.get("/datasources/{datasource_id}", response_model=DataSourceResponse)
async def get_datasource(datasource_id: str):
    datasource = DataSourceStorage.get(datasource_id)
    if not datasource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Data source '{datasource_id}' not found"
        )
    
    return DataSourceResponse(**datasource)


@router.delete("/datasources/{datasource_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_datasource(datasource_id: str):
    if not DataSourceStorage.remove(datasource_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Data source '{datasource_id}' not found"
        )


@router.get("/datasources/{datasource_id}/test")
async def test_datasource_connection(datasource_id: str):
    datasource = DataSourceStorage.get(datasource_id)
    if not datasource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Data source '{datasource_id}' not found"
        )
    
    config = DataSourceConfig(**datasource)
    
    try:
        connector = ConnectorFactory.create_connector(config)
        is_connected = connector.test_connection()
        connector.disconnect()
        
        return {
            "datasource_id": datasource_id,
            "connected": is_connected,
            "status": "success" if is_connected else "failed"
        }
    except Exception as e:
        return {
            "datasource_id": datasource_id,
            "connected": False,
            "status": "error",
            "error": str(e)
        }


@router.get("/datasources/{datasource_id}/schemas", response_model=SchemaResponse)
async def list_schemas(datasource_id: str):
    datasource = DataSourceStorage.get(datasource_id)
    if not datasource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Data source '{datasource_id}' not found"
        )
    
    config = DataSourceConfig(**datasource)
    
    try:
        connector = ConnectorFactory.create_connector(config)
        connector.connect()
        schemas = connector.get_schemas()
        connector.disconnect()
        
        return SchemaResponse(schemas=schemas)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching schemas: {str(e)}"
        )


@router.get("/datasources/{datasource_id}/schemas/{schema_name}/tables", response_model=TableListResponse)
async def list_tables(datasource_id: str, schema_name: str):
    datasource = DataSourceStorage.get(datasource_id)
    if not datasource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Data source '{datasource_id}' not found"
        )
    
    config = DataSourceConfig(**datasource)
    
    try:
        connector = ConnectorFactory.create_connector(config)
        connector.connect()
        tables = connector.get_tables(schema=schema_name)
        connector.disconnect()
        
        return TableListResponse(tables=tables)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching tables: {str(e)}"
        )


@router.get("/datasources/{datasource_id}/schemas/{schema_name}/tables/{table_name}", response_model=TableDetailResponse)
async def get_table_details(datasource_id: str, schema_name: str, table_name: str):
    datasource = DataSourceStorage.get(datasource_id)
    if not datasource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Data source '{datasource_id}' not found"
        )
    
    config = DataSourceConfig(**datasource)
    
    try:
        connector = ConnectorFactory.create_connector(config)
        connector.connect()
        
        columns_data = connector.get_columns(table_name, schema=schema_name)
        primary_keys = connector.get_primary_keys(table_name, schema=schema_name)
        foreign_keys_data = connector.get_foreign_keys(table_name, schema=schema_name)
        metadata = connector.get_table_metadata(table_name, schema=schema_name)
        
        connector.disconnect()
        
        columns = [ColumnInfo(**col) for col in columns_data]
        foreign_keys = [ForeignKeyInfo(**fk) for fk in foreign_keys_data]
        
        return TableDetailResponse(
            name=table_name,
            schema_name=schema_name,
            columns=columns,
            primary_keys=primary_keys,
            foreign_keys=foreign_keys,
            metadata=metadata
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching table details: {str(e)}"
        )

