from fastapi import APIRouter, HTTPException, status

from api.models import IntrospectionRequest, IntrospectionResponse
from api.storage import DataSourceStorage, MDLStorage
from src.connectors import ConnectorFactory, DataSourceConfig
from src.introspection.models import SchemaMetadata, TableMetadata, ColumnMetadata, RelationshipMetadata
from src.mdl.generator import MDLGenerator

router = APIRouter()


def introspect_datasource(connector, schema=None, tables=None, detect_relationships=True, detect_primary_keys=True):
    connector.connect()
    
    try:
        # Get tables to introspect
        target_tables = tables if tables else connector.get_tables(schema=schema)
        
        table_metadata_list = []
        
        for table_name in target_tables:
            # Get columns
            columns_data = connector.get_columns(table_name, schema=schema)
            print(f"Columns for {table_name}: {columns_data}")
            
            columns = []
            for col_data in columns_data:
                column = ColumnMetadata(
                    name=col_data["name"],
                    type=col_data["type"],
                    comment=col_data.get("comment", ""),
                    nullable=col_data.get("nullable", True),
                    default=col_data.get("default"),
                    is_primary_key=False,
                    is_foreign_key=False
                )
                columns.append(column)
            
            # Detect primary keys
            primary_keys = []
            if detect_primary_keys:
                primary_keys = connector.get_primary_keys(table_name, schema=schema)
                for col in columns:
                    if col.name in primary_keys:
                        col.is_primary_key = True
            
            # Create table metadata
            table_metadata = TableMetadata(
                name=table_name,
                description=f"Table {table_name}",
                columns=columns,
                primary_key=primary_keys[0] if primary_keys else None,
                properties={"schema": schema} if schema else {}
            )
            
            table_metadata_list.append(table_metadata)
        
        # Detect relationships
        relationships = []
        if detect_relationships:
            for table in table_metadata_list:
                foreign_keys = connector.get_foreign_keys(table.name, schema=schema)
                
                for fk in foreign_keys:
                    # Mark column as foreign key
                    for col in table.columns:
                        if col.name == fk["column"]:
                            col.is_foreign_key = True
                            col.foreign_key_table = fk["referenced_table"]
                            col.foreign_key_column = fk["referenced_column"]
                    
                    # Create relationship
                    relationship = RelationshipMetadata(
                        name=f"{table.name}_{fk['referenced_table']}",
                        source_table=table.name,
                        target_table=fk["referenced_table"],
                        source_column=fk["column"],
                        target_column=fk["referenced_column"],
                        join_type="MANY_TO_ONE",
                        constraint_name=fk.get("constraint_name")
                    )
                    relationships.append(relationship)
    
    finally:
        connector.disconnect()
    
    # Create schema metadata
    schema_metadata = SchemaMetadata(
        database=schema or "default",
        tables=table_metadata_list,
        relationships=relationships
    )
    
    return schema_metadata


@router.post("/datasources/{datasource_id}/introspect", response_model=IntrospectionResponse)
async def introspect_schema(datasource_id: str, request: IntrospectionRequest):
    """
    Introspect database schema.
    
    Connects to the database, extracts schema information,
    and generates MDL (Model Definition Language).
    
    This MDL can then be used by AI services for schema-aware operations.
    """
    # Get datasource
    datasource = DataSourceStorage.get(datasource_id)
    if not datasource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Data source '{datasource_id}' not found"
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
        
        # Introspect schema
        schema_metadata = introspect_datasource(
            connector=connector,
            schema=request.schema_name,
            tables=request.tables,
            detect_relationships=request.detect_relationships,
            detect_primary_keys=request.detect_primary_keys
        )
        
        # Generate MDL
        generator = MDLGenerator()
        mdl = generator.generate(schema_metadata)
        
        # Save MDL
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
