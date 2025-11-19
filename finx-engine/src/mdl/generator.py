from typing import Any, Dict, List
from datetime import datetime

from src.introspection.models import SchemaMetadata


class MDLGenerator:
    """
    Generator for Model Definition Language.
    
    MDL is a structured representation of database schemas
    optimized for AI/LLM understanding and SQL generation.
    """
    
    def __init__(self, version: str = "1.0"):
        """Initialize MDL generator"""
        self.version = version
    
    def generate(self, schema_metadata: SchemaMetadata) -> Dict[str, Any]:
        """
        Generate MDL from schema metadata.
        
        Args:
            schema_metadata: Schema metadata to convert
            
        Returns:
            MDL dictionary
        """
        mdl = {
            "version": self.version,
            "database": schema_metadata.database,
            "models": self._generate_models(schema_metadata),
            "relationships": self._generate_relationships(schema_metadata),
            "metadata": {
                "total_models": len(schema_metadata.tables),
                "total_relationships": len(schema_metadata.relationships),
                "generated_at": datetime.utcnow().isoformat() + "Z"
            }
        }
        
        return mdl
    
    def _generate_models(self, schema_metadata: SchemaMetadata) -> List[Dict[str, Any]]:
        """Generate model definitions"""
        models = []
        
        for table in schema_metadata.tables:
            model = {
                "name": table.name,
                "description": table.description or f"Model for {table.name} table",
                "type": "table",
                "columns": [
                    {
                        "name": col.name,
                        "type": self._normalize_type(col.type),
                        "description": col.comment or f"{col.name} column",
                        "nullable": col.nullable,
                        "primary_key": col.is_primary_key,
                        "foreign_key": col.is_foreign_key,
                        "foreign_key_reference": {
                            "table": col.foreign_key_table,
                            "column": col.foreign_key_column
                        } if col.is_foreign_key else None
                    }
                    for col in table.columns
                ],
                "primary_key": table.primary_key,
                "indexes": [],  # Can be extended
                "constraints": []  # Can be extended
            }
            
            models.append(model)
        
        return models
    
    def _generate_relationships(self, schema_metadata: SchemaMetadata) -> List[Dict[str, Any]]:
        """Generate relationship definitions"""
        relationships = []
        
        for rel in schema_metadata.relationships:
            relationship = {
                "name": rel.name,
                "type": rel.join_type.lower(),
                "from": {
                    "model": rel.source_table,
                    "column": rel.source_column
                },
                "to": {
                    "model": rel.target_table,
                    "column": rel.target_column
                },
                "constraint_name": rel.constraint_name,
                "description": self._generate_relationship_description(rel)
            }
            
            relationships.append(relationship)
        
        return relationships
    
    def _normalize_type(self, db_type: str) -> str:
        """
        Normalize database-specific types to standard types.
        
        This helps LLMs understand types consistently across databases.
        """
        type_mapping = {
            # String types
            "VARCHAR": "STRING",
            "CHAR": "STRING",
            "TEXT": "STRING",
            "STRING": "STRING",
            
            # Numeric types
            "INTEGER": "INTEGER",
            "INT": "INTEGER",
            "BIGINT": "BIGINT",
            "SMALLINT": "INTEGER",
            "TINYINT": "INTEGER",
            "DECIMAL": "DECIMAL",
            "NUMERIC": "DECIMAL",
            "FLOAT": "FLOAT",
            "DOUBLE": "DOUBLE",
            "REAL": "FLOAT",
            
            # Date/Time types
            "TIMESTAMP": "TIMESTAMP",
            "DATETIME": "TIMESTAMP",
            "DATE": "DATE",
            "TIME": "TIME",
            
            # Boolean
            "BOOLEAN": "BOOLEAN",
            "BOOL": "BOOLEAN",
            
            # Binary
            "BYTEA": "BINARY",
            "BLOB": "BINARY",
            "BINARY": "BINARY",
            
            # JSON
            "JSON": "JSON",
            "JSONB": "JSON",
            
            # Array
            "ARRAY": "ARRAY",
        }
        
        return type_mapping.get(db_type.upper(), db_type.upper())
    
    def _generate_relationship_description(self, rel) -> str:
        """Generate human-readable relationship description"""
        join_desc = {
            "MANY_TO_ONE": "many",
            "ONE_TO_MANY": "one or more",
            "ONE_TO_ONE": "one",
            "MANY_TO_MANY": "many"
        }
        
        desc = join_desc.get(rel.join_type, "related")
        return f"{rel.source_table}.{rel.source_column} references {desc} {rel.target_table}.{rel.target_column}"
    
    def generate_ddl(self, mdl: Dict[str, Any]) -> str:
        """
        Generate DDL (Data Definition Language) from MDL.
        
        This is useful for LLMs to understand table structures.
        """
        ddl_statements = []
        
        for model in mdl.get("models", []):
            table_name = model["name"]
            columns = model["columns"]
            
            column_defs = []
            for col in columns:
                col_def = f"  {col['name']} {col['type']}"
                
                if col.get("primary_key"):
                    col_def += " PRIMARY KEY"
                
                if not col.get("nullable"):
                    col_def += " NOT NULL"
                
                # Add comment
                if col.get("description"):
                    col_def += f" -- {col['description']}"
                
                column_defs.append(col_def)
            
            ddl = f"CREATE TABLE {table_name} (\n"
            ddl += ",\n".join(column_defs)
            ddl += "\n);"
            
            # Add table comment
            if model.get("description"):
                ddl += f"\n-- {model['description']}"
            
            ddl_statements.append(ddl)
        
        return "\n\n".join(ddl_statements)
