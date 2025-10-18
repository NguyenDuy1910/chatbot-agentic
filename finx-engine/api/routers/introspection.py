from fastapi import APIRouter, HTTPException, status
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from api.models import IntrospectionRequest, IntrospectionResponse
from api.storage import DataSourceStorage, MDLStorage
from src.connectors import ConnectorFactory, DataSourceConfig
from src.introspection.models import SchemaMetadata, TableMetadata, ColumnMetadata, RelationshipMetadata
from src.mdl.generator import MDLGenerator

router = APIRouter()


def introspect_datasource(connector, schema=None, tables=None, detect_relationships=True, detect_primary_keys=True):
    connector.connect()
    
    target_tables = tables if tables else connector.get_tables(schema=schema)
    
    table_metadata_list = []
    
    for table_name in target_tables:
        columns_data = connector.get_columns(table_name, schema=schema)
        
        columns = []
        for col_data in columns_data:
            column = ColumnMetadata(
                name=col_data["name"],
                type=col_data["type"],
                comment=col_data.get("comment", ""),
                nullable=col_data.get("nullable", True),
                is_primary_key=False,
                is_foreign_key=False
            )
            columns.append(column)
        
        primary_keys = []
        if detect_primary_keys:
            primary_keys = connector.get_primary_keys(table_name, schema=schema)
            for col in columns:
                if col.name in primary_keys:
                    col.is_primary_key = True
        
        table_metadata = TableMetadata(
            name=table_name,
            description=f"Table {table_name}",
            columns=columns,
            primary_key=primary_keys[0] if primary_keys else None,
            properties={"schema": schema} if schema else {}
        )
        
        table_metadata_list.append(table_metadata)
    
    relationships = []
    if detect_relationships:
        for table in table_metadata_list:
            foreign_keys = connector.get_foreign_keys(table.name, schema=schema)
            
            for fk in foreign_keys:
                for col in table.columns:
                    if col.name == fk["column"]:
                        col.is_foreign_key = True
                        col.foreign_key_table = fk["referenced_table"]
                
                relationship = RelationshipMetadata(
                    name=f"{table.name}_{fk['referenced_table']}",
                    source_table=table.name,
                    target_table=fk["referenced_table"],
                    source_column=fk["column"],
                    target_column=fk["referenced_column"],
                    join_type="MANY_TO_ONE"
                )
                relationships.append(relationship)
    
    connector.disconnect()
    
    schema_metadata = SchemaMetadata(
        database=schema or "default",
        tables=table_metadata_list,
        relationships=relationships
    )
    
    return schema_metadata


@router.post("/datasources/{datasource_id}/introspect", response_model=IntrospectionResponse)
async def introspect_schema(datasource_id: str, request: IntrospectionRequest):
    datasource = DataSourceStorage.get(datasource_id)
    if not datasource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Data source '{datasource_id}' not found"
        )
    
    config = DataSourceConfig(**datasource)
    
    try:
        connector = ConnectorFactory.create_connector(config)
        
        schema_metadata = introspect_datasource(
            connector=connector,
            schema=request.schema_name,
            tables=request.tables,
            detect_relationships=request.detect_relationships,
            detect_primary_keys=request.detect_primary_keys
        )
        
        generator = MDLGenerator()
        mdl = generator.generate(schema_metadata)
        
        MDLStorage.save(datasource_id, mdl)
        
        return IntrospectionResponse(
            datasource_id=datasource_id,
            status="success",
            tables_count=len(mdl["models"]),
            relationships_count=len(mdl["relationships"]),
            mdl_generated=True
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during introspection: {str(e)}"
        )

