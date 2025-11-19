"""
Unit tests for Schema Builder utility.
"""

import unittest
import json
from schema_builder import (
    SchemaBuilder,
    ColumnSchema,
    TableSchema,
    build_ddl_from_json,
    parse_schema_from_json,
    get_table_info
)


class TestSchemaBuilder(unittest.TestCase):
    """Test cases for SchemaBuilder class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.simple_schema = {
            "models": [
                {
                    "name": "users",
                    "columns": [
                        {"name": "id", "type": "INTEGER"},
                        {"name": "email", "type": "VARCHAR"}
                    ],
                    "primaryKey": "id"
                }
            ]
        }
        
        self.complex_schema = {
            "models": [
                {
                    "name": "customers",
                    "columns": [
                        {"name": "id", "type": "INTEGER", "nullable": False},
                        {"name": "email", "type": "VARCHAR", "nullable": False}
                    ],
                    "primaryKey": "id"
                },
                {
                    "name": "orders",
                    "columns": [
                        {"name": "id", "type": "INTEGER"},
                        {"name": "customer_id", "type": "INTEGER"}
                    ],
                    "primaryKey": "id"
                }
            ],
            "relationships": [
                {
                    "models": ["customers", "orders"],
                    "condition": "customers.id = orders.customer_id",
                    "joinType": "ONE_TO_MANY"
                }
            ]
        }
    
    def test_builder_initialization(self):
        """Test SchemaBuilder initialization"""
        builder = SchemaBuilder(dialect="postgresql")
        self.assertEqual(builder.dialect, "postgresql")
        
        builder_mysql = SchemaBuilder(dialect="mysql")
        self.assertEqual(builder_mysql.dialect, "mysql")
    
    def test_parse_simple_schema(self):
        """Test parsing simple schema"""
        builder = SchemaBuilder()
        tables = builder.parse_schema(self.simple_schema)
        
        self.assertEqual(len(tables), 1)
        self.assertIn("users", tables)
        
        users_table = tables["users"]
        self.assertEqual(users_table.name, "users")
        self.assertEqual(len(users_table.columns), 2)
        self.assertEqual(users_table.primary_key, "id")
    
    def test_parse_complex_schema(self):
        """Test parsing complex schema with relationships"""
        builder = SchemaBuilder()
        tables = builder.parse_schema(self.complex_schema)
        
        self.assertEqual(len(tables), 2)
        self.assertIn("customers", tables)
        self.assertIn("orders", tables)
        
        # Check foreign key was added
        orders_table = tables["orders"]
        customer_id_col = next(
            (col for col in orders_table.columns if col.name == "customer_id"),
            None
        )
        self.assertIsNotNone(customer_id_col)
        self.assertIsNotNone(customer_id_col.foreign_key)
        self.assertEqual(customer_id_col.foreign_key["table"], "customers")
        self.assertEqual(customer_id_col.foreign_key["column"], "id")
    
    def test_build_ddl_postgresql(self):
        """Test DDL generation for PostgreSQL"""
        ddl = build_ddl_from_json(self.simple_schema, dialect="postgresql")
        
        self.assertIn("CREATE TABLE", ddl)
        self.assertIn("users", ddl)
        self.assertIn("id", ddl)
        self.assertIn("email", ddl)
        self.assertIn("PRIMARY KEY", ddl)
    
    def test_build_ddl_mysql(self):
        """Test DDL generation for MySQL"""
        ddl = build_ddl_from_json(self.simple_schema, dialect="mysql")
        
        self.assertIn("CREATE TABLE", ddl)
        self.assertIn("users", ddl)
    
    def test_build_ddl_sqlite(self):
        """Test DDL generation for SQLite"""
        ddl = build_ddl_from_json(self.simple_schema, dialect="sqlite")
        
        self.assertIn("CREATE TABLE", ddl)
        self.assertIn("users", ddl)
    
    def test_foreign_key_constraint(self):
        """Test foreign key constraint generation"""
        builder = SchemaBuilder(dialect="postgresql")
        tables = builder.parse_schema(self.complex_schema)
        ddl = builder.build_ddl(tables)
        
        self.assertIn("FOREIGN KEY", ddl)
        self.assertIn("REFERENCES", ddl)
        self.assertIn("customers", ddl)
    
    def test_get_table_schema(self):
        """Test getting table schema information"""
        builder = SchemaBuilder()
        tables = builder.parse_schema(self.complex_schema)
        
        customers_info = builder.get_table_schema(tables["customers"])
        
        self.assertEqual(customers_info["name"], "customers")
        self.assertEqual(customers_info["primaryKey"], "id")
        self.assertEqual(len(customers_info["columns"]), 2)
        self.assertIn("foreignKeys", customers_info)
    
    def test_column_constraints(self):
        """Test column constraint handling"""
        schema = {
            "models": [
                {
                    "name": "test_table",
                    "columns": [
                        {
                            "name": "id",
                            "type": "INTEGER",
                            "nullable": False,
                            "primary_key": True,
                            "auto_increment": True
                        },
                        {
                            "name": "email",
                            "type": "VARCHAR",
                            "nullable": False,
                            "unique": True
                        },
                        {
                            "name": "status",
                            "type": "VARCHAR",
                            "default": "active"
                        }
                    ],
                    "primaryKey": "id"
                }
            ]
        }
        
        ddl = build_ddl_from_json(schema, dialect="postgresql")
        
        self.assertIn("NOT NULL", ddl)
        self.assertIn("UNIQUE", ddl)
        self.assertIn("DEFAULT", ddl)
        self.assertIn("SERIAL", ddl)  # PostgreSQL auto-increment
    
    def test_get_table_info_convenience(self):
        """Test convenience function get_table_info"""
        info = get_table_info(self.simple_schema, "users")
        
        self.assertIsNotNone(info)
        self.assertEqual(info["name"], "users")
        self.assertEqual(len(info["columns"]), 2)
    
    def test_schema_documentation(self):
        """Test schema documentation generation"""
        builder = SchemaBuilder()
        tables = builder.parse_schema(self.complex_schema)
        
        docs = builder.build_schema_documentation(tables)
        
        self.assertIn("# Database Schema Documentation", docs)
        self.assertIn("customers", docs)
        self.assertIn("orders", docs)
        self.assertIn("| Column |", docs)  # Markdown table
    
    def test_data_type_normalization(self):
        """Test data type normalization for different dialects"""
        builder_pg = SchemaBuilder(dialect="postgresql")
        builder_mysql = SchemaBuilder(dialect="mysql")
        
        # Test PostgreSQL normalization
        self.assertEqual(builder_pg._normalize_data_type("DATETIME"), "TIMESTAMP")
        self.assertEqual(builder_pg._normalize_data_type("INT64"), "BIGINT")
        
        # Test MySQL normalization
        self.assertEqual(builder_mysql._normalize_data_type("BYTEA"), "BLOB")
    
    def test_empty_schema(self):
        """Test handling empty schema"""
        empty_schema = {"models": []}
        
        builder = SchemaBuilder()
        tables = builder.parse_schema(empty_schema)
        
        self.assertEqual(len(tables), 0)
        
        ddl = builder.build_ddl(tables)
        self.assertEqual(ddl, "")
    
    def test_column_dataclass(self):
        """Test ColumnSchema dataclass"""
        col = ColumnSchema(
            name="test_col",
            type="VARCHAR",
            nullable=False,
            primary_key=True
        )
        
        self.assertEqual(col.name, "test_col")
        self.assertEqual(col.type, "VARCHAR")
        self.assertFalse(col.nullable)
        self.assertTrue(col.primary_key)
        
        # Test to_dict
        col_dict = col.to_dict()
        self.assertEqual(col_dict["name"], "test_col")
        self.assertEqual(col_dict["type"], "VARCHAR")
    
    def test_table_dataclass(self):
        """Test TableSchema dataclass"""
        columns = [
            ColumnSchema(name="id", type="INTEGER", primary_key=True),
            ColumnSchema(name="name", type="VARCHAR")
        ]
        
        table = TableSchema(
            name="test_table",
            columns=columns,
            primary_key="id"
        )
        
        self.assertEqual(table.name, "test_table")
        self.assertEqual(len(table.columns), 2)
        self.assertEqual(table.primary_key, "id")
        
        # Test to_dict
        table_dict = table.to_dict()
        self.assertEqual(table_dict["name"], "test_table")
        self.assertEqual(len(table_dict["columns"]), 2)


class TestConvenienceFunctions(unittest.TestCase):
    """Test convenience functions"""
    
    def test_parse_schema_from_json(self):
        """Test parse_schema_from_json function"""
        schema = {
            "models": [
                {
                    "name": "test",
                    "columns": [{"name": "id", "type": "INTEGER"}],
                    "primaryKey": "id"
                }
            ]
        }
        
        tables = parse_schema_from_json(schema)
        
        self.assertEqual(len(tables), 1)
        self.assertIn("test", tables)
    
    def test_build_ddl_from_json(self):
        """Test build_ddl_from_json function"""
        schema = {
            "models": [
                {
                    "name": "test",
                    "columns": [{"name": "id", "type": "INTEGER"}],
                    "primaryKey": "id"
                }
            ]
        }
        
        ddl = build_ddl_from_json(schema)
        
        self.assertIn("CREATE TABLE", ddl)
        self.assertIn("test", ddl)


if __name__ == "__main__":
    # Run tests
    unittest.main(verbosity=2)
