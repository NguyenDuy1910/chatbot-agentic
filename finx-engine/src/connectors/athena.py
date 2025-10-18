import boto3
from typing import List, Dict, Any, Optional
from pyathena import connect as athena_connect
from .base import BaseConnector, DataSourceConfig


class AthenaConnector(BaseConnector):

    def __init__(self, config: DataSourceConfig):
        super().__init__(config)
        self.region_name = config.connection_params.get("region_name")
        self.database = config.connection_params.get("database")
        self.s3_output_location = config.connection_params.get("s3_output_location")
        self.catalog = config.connection_params.get("catalog", "AwsDataCatalog")
        self.workgroup = config.connection_params.get("workgroup", "primary")

        self.aws_access_key_id = config.connection_params.get("aws_access_key_id")
        self.aws_secret_access_key = config.connection_params.get("aws_secret_access_key")

        self.glue_client = None
        self.s3tables_client = None
        self.athena_connection = None
        self.is_s3tables = self._is_s3tables_catalog()

    def _is_s3tables_catalog(self) -> bool:
        catalog_lower = self.catalog.lower()
        return 's3tables' in catalog_lower or catalog_lower.startswith('s3t_')

    def connect(self) -> None:
        session_kwargs = {"region_name": self.region_name}

        if self.aws_access_key_id and self.aws_secret_access_key:
            session_kwargs["aws_access_key_id"] = self.aws_access_key_id
            session_kwargs["aws_secret_access_key"] = self.aws_secret_access_key

        session = boto3.Session(**session_kwargs)
        self.glue_client = session.client('glue')

        if self.is_s3tables:
            self.s3tables_client = session.client('s3tables')

        athena_kwargs = {
            "region_name": self.region_name,
            "schema_name": self.database,
            "s3_staging_dir": self.s3_output_location,
            "work_group": self.workgroup,
            "catalog_name": self.catalog
        }

        if self.aws_access_key_id and self.aws_secret_access_key:
            athena_kwargs["aws_access_key_id"] = self.aws_access_key_id
            athena_kwargs["aws_secret_access_key"] = self.aws_secret_access_key

        self.athena_connection = athena_connect(**athena_kwargs)
        self._connection = self.athena_connection

    def disconnect(self) -> None:
        if self.athena_connection:
            self.athena_connection.close()
            self.athena_connection = None
        self.glue_client = None
        self.s3tables_client = None
        self._connection = None

    def test_connection(self) -> bool:
        try:
            if not self.glue_client:
                self.connect()

            if self.is_s3tables:
                return self._test_s3tables_connection()
            else:
                self.glue_client.get_database(
                    CatalogId=self.catalog if self.catalog != "AwsDataCatalog" else None,
                    Name=self.database
                )
                return True
        except Exception:
            return False

    def _test_s3tables_connection(self) -> bool:
        try:
            cursor = self.athena_connection.cursor()
            cursor.execute(f"SHOW DATABASES IN {self.catalog}")
            cursor.close()
            return True
        except Exception:
            return False

    def get_schemas(self) -> List[str]:
        if not self.glue_client:
            self.connect()

        if self.is_s3tables:
            return self._get_s3tables_schemas()

        kwargs = {}
        if self.catalog != "AwsDataCatalog":
            kwargs['CatalogId'] = self.catalog

        response = self.glue_client.get_databases(**kwargs)
        return [db['Name'] for db in response.get('DatabaseList', [])]

    def _get_s3tables_schemas(self) -> List[str]:
        cursor = self.athena_connection.cursor()
        cursor.execute(f"SHOW DATABASES IN {self.catalog}")
        schemas = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return schemas

    def get_tables(self, schema: Optional[str] = None) -> List[str]:
        if not self.glue_client:
            self.connect()

        database = schema or self.database

        if self.is_s3tables:
            return self._get_s3tables_tables(database)

        tables = []
        paginator = self.glue_client.get_paginator('get_tables')

        kwargs = {'DatabaseName': database}
        if self.catalog != "AwsDataCatalog":
            kwargs['CatalogId'] = self.catalog

        for page in paginator.paginate(**kwargs):
            for table in page.get('TableList', []):
                tables.append(table['Name'])

        return tables

    def _get_s3tables_tables(self, database: str) -> List[str]:
        cursor = self.athena_connection.cursor()
        cursor.execute(f"SHOW TABLES IN {self.catalog}.{database}")
        tables = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return tables

    def get_table_metadata(self, table_name: str, schema: Optional[str] = None) -> Dict[str, Any]:
        if not self.glue_client:
            self.connect()

        database = schema or self.database

        if self.is_s3tables:
            return self._get_s3tables_metadata(table_name, database)

        kwargs = {
            'DatabaseName': database,
            'Name': table_name
        }
        if self.catalog != "AwsDataCatalog":
            kwargs['CatalogId'] = self.catalog

        response = self.glue_client.get_table(**kwargs)
        table = response['Table']

        return {
            "name": table['Name'],
            "database": database,
            "description": table.get('Description', ''),
            "location": table.get('StorageDescriptor', {}).get('Location', ''),
            "input_format": table.get('StorageDescriptor', {}).get('InputFormat', ''),
            "output_format": table.get('StorageDescriptor', {}).get('OutputFormat', ''),
            "parameters": table.get('Parameters', {}),
            "partition_keys": [
                {
                    "name": pk['Name'],
                    "type": pk['Type'],
                    "comment": pk.get('Comment', '')
                }
                for pk in table.get('PartitionKeys', [])
            ]
        }

    def _get_s3tables_metadata(self, table_name: str, database: str) -> Dict[str, Any]:
        return {
            "name": table_name,
            "database": database,
            "description": f"S3 Table {table_name}",
            "location": f"s3tables://{self.catalog}/{database}/{table_name}",
            "input_format": "S3Tables",
            "output_format": "S3Tables",
            "parameters": {"catalog_type": "s3tables"},
            "partition_keys": []
        }

    def get_columns(self, table_name: str, schema: Optional[str] = None) -> List[Dict[str, Any]]:
        if not self.glue_client:
            self.connect()

        database = schema or self.database

        if self.is_s3tables:
            return self._get_s3tables_columns(table_name, database)

        kwargs = {
            'DatabaseName': database,
            'Name': table_name
        }
        if self.catalog != "AwsDataCatalog":
            kwargs['CatalogId'] = self.catalog

        response = self.glue_client.get_table(**kwargs)

        columns = []
        for col in response['Table']['StorageDescriptor']['Columns']:
            columns.append({
                "name": col['Name'],
                "type": col['Type'],
                "comment": col.get('Comment', ''),
                "nullable": True
            })

        return columns

    def _get_s3tables_columns(self, table_name: str, database: str) -> List[Dict[str, Any]]:
        cursor = self.athena_connection.cursor()
        cursor.execute(f"DESCRIBE {self.catalog}.{database}.{table_name}")

        columns = []
        for row in cursor.fetchall():
            col_name = row[0]
            col_type = row[1]

            if col_name and not col_name.startswith('#'):
                columns.append({
                    "name": col_name,
                    "type": col_type,
                    "comment": "",
                    "nullable": True
                })

        cursor.close()
        return columns

    def get_primary_keys(self, table_name: str, schema: Optional[str] = None) -> List[str]:
        columns = self.get_columns(table_name, schema)

        primary_keys = []
        for col in columns:
            col_name = col['name'].lower()
            if col_name == 'id' or col_name == f"{table_name.lower()}_id":
                primary_keys.append(col['name'])

        return primary_keys

    def get_foreign_keys(self, table_name: str, schema: Optional[str] = None) -> List[Dict[str, Any]]:
        columns = self.get_columns(table_name, schema)
        all_tables = self.get_tables(schema)

        foreign_keys = []

        for col in columns:
            col_name = col['name'].lower()

            if col_name.endswith('_id') and col_name != f"{table_name.lower()}_id":
                potential_table = col_name[:-3]

                for table in all_tables:
                    if table.lower() == potential_table:
                        foreign_keys.append({
                            "column": col['name'],
                            "referenced_table": table,
                            "referenced_column": "id",
                            "constraint_name": f"fk_{table_name}_{col['name']}"
                        })
                        break

        return foreign_keys

    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        if not self.athena_connection:
            self.connect()

        cursor = self.athena_connection.cursor()
        cursor.execute(query)

        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        results = []

        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

        cursor.close()
        return results
