import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.connectors.base import DataSourceConfig
from src.connectors.athena import AthenaConnector
from src.mdl.generator import MDLGenerator
from src.introspection.models import SchemaMetadata, TableMetadata, ColumnMetadata, RelationshipMetadata
import json


def example_s3tables_basic():
    print("=" * 80)
    print("Example 1: Basic S3 Tables Introspection")
    print("=" * 80)

    workgroup = os.getenv("ATHENA_WORKGROUP", "primary")

    config = DataSourceConfig(
        datasource_id="s3tables_example",
        datasource_type="athena",
        connection_params={
            "region_name": "ap-southeast-5",
            "database": "olap_report",
            "s3_output_location": "s3://s3-bucket-apse5-dev-olap-athena-output/",
            "catalog": "s3tables",
            "workgroup": workgroup
        }
    )

    connector = AthenaConnector(config)

    print(f"\nCatalog Type: {'S3 Tables' if connector.is_s3tables else 'Glue Data Catalog'}")
    print(f"Catalog Name: {connector.catalog}")
    print(f"Workgroup: {connector.workgroup}")
    print(f"Region: {connector.region_name}")

    try:
        connector.connect()
        print("✓ Connected to S3 Tables catalog")
        
        schemas = connector.get_schemas()
        print(f"\n✓ Found {len(schemas)} namespaces:")
        for schema in schemas[:5]:
            print(f"  - {schema}")
        
        if schemas:
            first_schema = schemas[0]
            tables = connector.get_tables(first_schema)
            print(f"\n✓ Found {len(tables)} tables in '{first_schema}':")
            for table in tables[:5]:
                print(f"  - {table}")
            
            if tables:
                first_table = tables[0]
                columns = connector.get_columns(first_table, first_schema)
                print(f"\n✓ Columns in '{first_table}':")
                for col in columns:
                    print(f"  - {col['name']}: {col['type']}")
        
        connector.disconnect()
        print("\n✓ Disconnected")
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        connector.disconnect()


def example_s3tables_with_credentials():
    print("\n" + "=" * 80)
    print("Example 2: S3 Tables with AWS Credentials")
    print("=" * 80)
    
    config = DataSourceConfig(
        datasource_id="s3tables_with_creds",
        datasource_type="athena",
        connection_params={
            "region_name": "us-west-2",
            "database": "analytics_namespace",
            "s3_output_location": "s3://analytics-results/",
            "catalog": "analytics-s3tables",
            "workgroup": "analytics",
            "aws_access_key_id": os.getenv("AWS_ACCESS_KEY_ID"),
            "aws_secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY")
        }
    )
    
    connector = AthenaConnector(config)
    
    print(f"\nUsing credentials: {'Yes' if connector.aws_access_key_id else 'No (default chain)'}")
    print(f"Catalog: {connector.catalog}")
    print(f"Region: {connector.region_name}")
    
    try:
        if connector.test_connection():
            print("✓ Connection test successful")
        else:
            print("✗ Connection test failed")
    except Exception as e:
        print(f"✗ Error: {str(e)}")


def example_s3tables_full_introspection():
    print("\n" + "=" * 80)
    print("Example 3: Full S3 Tables Introspection with MDL Generation")
    print("=" * 80)
    
    config = DataSourceConfig(
        datasource_id="s3tables_full",
        datasource_type="athena",
        connection_params={
            "region_name": "us-east-1",
            "database": "production_namespace",
            "s3_output_location": "s3://prod-athena-results/",
            "catalog": "prod-s3tables-catalog",
            "workgroup": "production"
        }
    )
    
    connector = AthenaConnector(config)
    
    try:
        connector.connect()
        print("✓ Connected to S3 Tables")
        
        database = connector.database
        tables = connector.get_tables(database)
        
        print(f"\n✓ Introspecting {len(tables)} tables...")
        
        table_metadata_list = []
        
        for table_name in tables[:3]:
            print(f"\n  Processing: {table_name}")
            
            columns_data = connector.get_columns(table_name, database)
            primary_keys = connector.get_primary_keys(table_name, database)
            
            columns = []
            for col_data in columns_data:
                column = ColumnMetadata(
                    name=col_data["name"],
                    type=col_data["type"],
                    comment=col_data.get("comment", ""),
                    nullable=col_data.get("nullable", True),
                    is_primary_key=col_data["name"] in primary_keys,
                    is_foreign_key=False
                )
                columns.append(column)
            
            table_metadata = TableMetadata(
                name=table_name,
                description=f"S3 Table {table_name}",
                columns=columns,
                primary_key=primary_keys[0] if primary_keys else None,
                properties={"catalog": connector.catalog, "namespace": database}
            )
            
            table_metadata_list.append(table_metadata)
            print(f"    ✓ {len(columns)} columns, PK: {primary_keys}")
        
        relationships = []
        for table in table_metadata_list:
            foreign_keys = connector.get_foreign_keys(table.name, database)
            
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
        
        schema_metadata = SchemaMetadata(
            database=database,
            tables=table_metadata_list,
            relationships=relationships,
            properties={"catalog": connector.catalog, "catalog_type": "s3tables"}
        )
        
        print(f"\n✓ Schema metadata created:")
        print(f"  - Tables: {len(schema_metadata.tables)}")
        print(f"  - Relationships: {len(schema_metadata.relationships)}")
        
        generator = MDLGenerator()
        mdl = generator.generate(schema_metadata)
        
        print(f"\n✓ MDL generated:")
        print(f"  - Models: {len(mdl['models'])}")
        print(f"  - Relationships: {len(mdl['relationships'])}")
        
        output_file = "s3tables_mdl.json"
        with open(output_file, 'w') as f:
            json.dump(mdl, f, indent=2)
        
        print(f"\n✓ MDL saved to: {output_file}")
        
        connector.disconnect()
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        connector.disconnect()


def example_catalog_detection():
    print("\n" + "=" * 80)
    print("Example 4: S3 Tables Catalog Detection")
    print("=" * 80)
    
    test_catalogs = [
        "AwsDataCatalog",
        "my-s3tables-catalog",
        "s3tables_production",
        "s3t_analytics",
        "glue-catalog-prod",
        "S3TablesDataCatalog"
    ]
    
    print("\nCatalog Detection Results:")
    print("-" * 60)
    
    for catalog_name in test_catalogs:
        config = DataSourceConfig(
            datasource_id="test",
            datasource_type="athena",
            connection_params={
                "region_name": "us-east-1",
                "database": "test",
                "s3_output_location": "s3://test/",
                "catalog": catalog_name
            }
        )
        
        connector = AthenaConnector(config)
        catalog_type = "S3 Tables" if connector.is_s3tables else "Glue Data Catalog"
        icon = "📊" if connector.is_s3tables else "🗄️"
        
        print(f"{icon} {catalog_name:30} → {catalog_type}")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("AWS S3 Tables Introspection Examples")
    print("=" * 80)
    
    example_catalog_detection()
    
    print("\n\nNote: The following examples require actual AWS S3 Tables setup.")
    print("Update the connection parameters with your actual S3 Tables configuration.\n")
    
    user_input = input("Do you want to run the connection examples? (y/n): ")
    
    if user_input.lower() == 'y':
        example_s3tables_basic()
        example_s3tables_with_credentials()
        example_s3tables_full_introspection()
    else:
        print("\nSkipping connection examples.")
    
    print("\n" + "=" * 80)
    print("Examples completed!")
    print("=" * 80)

