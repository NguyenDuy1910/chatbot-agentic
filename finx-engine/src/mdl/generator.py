from typing import Dict, Any
from src.introspection.models import SchemaMetadata, TableMetadata, RelationshipMetadata


class MDLGenerator:

    def generate(self, schema_metadata: SchemaMetadata) -> Dict[str, Any]:
        mdl = {
            "models": [],
            "relationships": [],
            "views": [],
            "metrics": []
        }

        for table in schema_metadata.tables:
            model = self._generate_model(table)
            mdl["models"].append(model)

        for relationship in schema_metadata.relationships:
            rel = self._generate_relationship(relationship)
            mdl["relationships"].append(rel)

        return mdl

    def _generate_model(self, table: TableMetadata) -> Dict[str, Any]:
        model = {
            "name": table.name,
            "properties": {
                "displayName": table.name.replace("_", " ").title(),
                "description": table.description or f"Table {table.name}"
            },
            "columns": []
        }

        if table.primary_key:
            model["primaryKey"] = table.primary_key

        for column in table.columns:
            col_def = {
                "name": column.name,
                "type": column.type,
                "isHidden": False,
                "properties": {
                    "description": column.comment or ""
                }
            }

            if column.is_primary_key:
                col_def["isPrimaryKey"] = True

            if column.is_foreign_key:
                col_def["isForeignKey"] = True
                if column.foreign_key_table:
                    col_def["referencedTable"] = column.foreign_key_table

            model["columns"].append(col_def)

        return model

    def _generate_relationship(self, relationship: RelationshipMetadata) -> Dict[str, Any]:
        return {
            "name": relationship.name,
            "models": [relationship.source_table, relationship.target_table],
            "joinType": relationship.join_type,
            "condition": f"{relationship.source_table}.{relationship.source_column} = {relationship.target_table}.{relationship.target_column}"
        }

    def generate_json(self, schema_metadata: SchemaMetadata) -> str:
        import json
        mdl = self.generate(schema_metadata)
        return json.dumps(mdl, indent=2)
