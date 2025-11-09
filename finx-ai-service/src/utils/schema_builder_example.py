"""
Example usage of the Schema Builder utility.

This module demonstrates how to use the schema_builder to:
1. Parse table schemas from JSON
2. Generate DDL statements
3. Get table metadata
4. Generate documentation
"""

import json
import logging
from schema_builder import (
    SchemaBuilder,
    build_ddl_from_json,
    parse_schema_from_json,
    get_table_info
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Example 1: Simple schema with one table
SIMPLE_SCHEMA = {
    "models": [
        {
            "name": "users",
            "columns": [
                {"name": "id", "type": "INTEGER", "nullable": False},
                {"name": "email", "type": "VARCHAR", "nullable": False},
                {"name": "name", "type": "VARCHAR"},
                {"name": "created_at", "type": "TIMESTAMP"}
            ],
            "primaryKey": "id",
            "properties": {
                "displayName": "Users",
                "description": "User account information"
            }
        }
    ]
}


# Example 2: Complex schema with multiple tables and relationships
COMPLEX_SCHEMA = {
    "models": [
        {
            "name": "customers",
            "columns": [
                {"name": "id", "type": "INTEGER", "nullable": False, "auto_increment": True},
                {"name": "email", "type": "VARCHAR", "nullable": False, "unique": True},
                {"name": "first_name", "type": "VARCHAR"},
                {"name": "last_name", "type": "VARCHAR"},
                {"name": "phone", "type": "VARCHAR"},
                {"name": "address", "type": "TEXT"},
                {"name": "city", "type": "VARCHAR"},
                {"name": "country", "type": "VARCHAR"},
                {"name": "created_at", "type": "TIMESTAMP", "default": "CURRENT_TIMESTAMP"},
                {"name": "updated_at", "type": "TIMESTAMP"}
            ],
            "primaryKey": "id",
            "properties": {
                "displayName": "Customers",
                "description": "Customer information and contact details"
            }
        },
        {
            "name": "orders",
            "columns": [
                {"name": "id", "type": "INTEGER", "nullable": False, "auto_increment": True},
                {"name": "customer_id", "type": "INTEGER", "nullable": False},
                {"name": "order_date", "type": "TIMESTAMP"},
                {"name": "total_amount", "type": "DECIMAL"},
                {"name": "status", "type": "VARCHAR", "default": "pending"},
                {"name": "shipping_address", "type": "TEXT"},
                {"name": "created_at", "type": "TIMESTAMP"}
            ],
            "primaryKey": "id",
            "properties": {
                "displayName": "Orders",
                "description": "Customer orders and order details"
            }
        },
        {
            "name": "products",
            "columns": [
                {"name": "id", "type": "INTEGER", "nullable": False, "auto_increment": True},
                {"name": "name", "type": "VARCHAR", "nullable": False},
                {"name": "description", "type": "TEXT"},
                {"name": "price", "type": "DECIMAL", "nullable": False},
                {"name": "stock_quantity", "type": "INTEGER", "default": 0},
                {"name": "category", "type": "VARCHAR"},
                {"name": "sku", "type": "VARCHAR", "unique": True},
                {"name": "created_at", "type": "TIMESTAMP"}
            ],
            "primaryKey": "id",
            "properties": {
                "displayName": "Products",
                "description": "Product catalog with pricing and inventory"
            }
        },
        {
            "name": "order_items",
            "columns": [
                {"name": "id", "type": "INTEGER", "nullable": False, "auto_increment": True},
                {"name": "order_id", "type": "INTEGER", "nullable": False},
                {"name": "product_id", "type": "INTEGER", "nullable": False},
                {"name": "quantity", "type": "INTEGER", "nullable": False, "default": 1},
                {"name": "unit_price", "type": "DECIMAL", "nullable": False},
                {"name": "subtotal", "type": "DECIMAL"}
            ],
            "primaryKey": "id",
            "properties": {
                "displayName": "Order Items",
                "description": "Line items for each order"
            }
        }
    ],
    "relationships": [
        {
            "models": ["customers", "orders"],
            "condition": "customers.id = orders.customer_id",
            "joinType": "ONE_TO_MANY"
        },
        {
            "models": ["orders", "order_items"],
            "condition": "orders.id = order_items.order_id",
            "joinType": "ONE_TO_MANY"
        },
        {
            "models": ["products", "order_items"],
            "condition": "products.id = order_items.product_id",
            "joinType": "ONE_TO_MANY"
        }
    ]
}


def example_1_simple_usage():
    """Example 1: Simple usage with convenience functions"""
    print("\n" + "="*80)
    print("EXAMPLE 1: Simple Usage - Single Table")
    print("="*80)
    
    # Quick DDL generation
    ddl = build_ddl_from_json(SIMPLE_SCHEMA, dialect="postgresql")
    print("\nGenerated DDL:")
    print(ddl)
    
    # Get table info
    table_info = get_table_info(SIMPLE_SCHEMA, "users")
    print("\nTable Information:")
    print(json.dumps(table_info, indent=2))


def example_2_complex_schema():
    """Example 2: Complex schema with relationships"""
    print("\n" + "="*80)
    print("EXAMPLE 2: Complex Schema with Relationships")
    print("="*80)
    
    builder = SchemaBuilder(dialect="postgresql")
    
    # Parse schema
    tables = builder.parse_schema(COMPLEX_SCHEMA)
    print(f"\nParsed {len(tables)} tables")
    
    # Generate DDL
    ddl = builder.build_ddl(tables, include_comments=True)
    print("\nGenerated DDL:")
    print(ddl)
    
    # Get schema for specific table
    customers_schema = builder.get_table_schema(tables["customers"])
    print("\n\nCustomers Table Schema:")
    print(json.dumps(customers_schema, indent=2))


def example_3_different_dialects():
    """Example 3: Generate DDL for different database dialects"""
    print("\n" + "="*80)
    print("EXAMPLE 3: Multiple Database Dialects")
    print("="*80)
    
    dialects = ["postgresql", "mysql", "sqlite"]
    
    for dialect in dialects:
        print(f"\n--- {dialect.upper()} DDL ---")
        ddl = build_ddl_from_json(SIMPLE_SCHEMA, dialect=dialect)
        print(ddl)


def example_4_schema_documentation():
    """Example 4: Generate schema documentation"""
    print("\n" + "="*80)
    print("EXAMPLE 4: Schema Documentation")
    print("="*80)
    
    builder = SchemaBuilder()
    tables = builder.parse_schema(COMPLEX_SCHEMA)
    
    # Generate markdown documentation
    documentation = builder.build_schema_documentation(tables)
    print("\nGenerated Documentation:")
    print(documentation)


def example_5_custom_schema():
    """Example 5: Building schema programmatically"""
    print("\n" + "="*80)
    print("EXAMPLE 5: Custom Schema from Your Requirement")
    print("="*80)
    
    # Your schema requirement
    your_schema = {
        "models": [
            {
                "name": "customers",
                "columns": [
                    {"name": "id", "type": "INTEGER"},
                    {"name": "email", "type": "VARCHAR"},
                    {"name": "first_name", "type": "VARCHAR"},
                    {"name": "last_name", "type": "VARCHAR"},
                    {"name": "age", "type": "INTEGER"},
                    {"name": "city", "type": "VARCHAR"},
                    {"name": "country", "type": "VARCHAR"},
                    {"name": "created_at", "type": "TIMESTAMP"}
                    # ... 100 more columns can be added here
                ],
                "primaryKey": "id",
                "properties": {
                    "displayName": "Customers",
                    "description": "Customer information"
                }
            },
            {
                "name": "orders",
                "columns": [
                    {"name": "id", "type": "INTEGER"},
                    {"name": "customer_id", "type": "INTEGER"},
                    {"name": "order_date", "type": "TIMESTAMP"},
                    {"name": "total_amount", "type": "DECIMAL"}
                ],
                "primaryKey": "id",
                "properties": {
                    "displayName": "Orders",
                    "description": "Customer orders"
                }
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
    
    builder = SchemaBuilder(dialect="postgresql")
    tables = builder.parse_schema(your_schema)
    
    # Build DDL
    ddl = builder.build_ddl(tables)
    print("\nGenerated DDL:")
    print(ddl)
    
    # Get detailed table info
    for table_name in tables:
        info = builder.get_table_schema(tables[table_name])
        print(f"\n\n=== {table_name.upper()} TABLE INFO ===")
        print(json.dumps(info, indent=2))


def example_6_practical_workflow():
    """Example 6: Practical workflow for your use case"""
    print("\n" + "="*80)
    print("EXAMPLE 6: Practical Workflow")
    print("="*80)
    
    # Step 1: Load schema from JSON (could be from file or API)
    schema_json = json.dumps(COMPLEX_SCHEMA)
    schema_data = json.loads(schema_json)
    
    # Step 2: Parse and validate schema
    builder = SchemaBuilder(dialect="postgresql")
    tables = builder.parse_schema(schema_data)
    print(f"✓ Parsed {len(tables)} tables")
    
    # Step 3: Generate DDL for database creation
    ddl = builder.build_ddl(tables, include_if_not_exists=True)
    print("\n✓ Generated DDL (ready to execute):")
    print(ddl[:500] + "..." if len(ddl) > 500 else ddl)
    
    # Step 4: Get metadata for specific tables
    print("\n✓ Table Metadata:")
    for table_name in ["customers", "orders"]:
        if table_name in tables:
            info = builder.get_table_schema(tables[table_name])
            print(f"\n{table_name}: {len(info['columns'])} columns, "
                  f"{len(info['foreignKeys'])} foreign keys")
    
    # Step 5: Generate documentation
    docs = builder.build_schema_documentation(tables)
    print(f"\n✓ Generated documentation: {len(docs)} characters")
    
    # Step 6: Export schema for further processing
    export_data = {
        table_name: table.to_dict() 
        for table_name, table in tables.items()
    }
    print(f"\n✓ Exported {len(export_data)} table schemas")


if __name__ == "__main__":
    print("\n" + "#"*80)
    print("# SCHEMA BUILDER UTILITY - EXAMPLES")
    print("#"*80)
    
    # Run all examples
    example_1_simple_usage()
    example_2_complex_schema()
    example_3_different_dialects()
    example_4_schema_documentation()
    example_5_custom_schema()
    example_6_practical_workflow()
    
    print("\n" + "#"*80)
    print("# ALL EXAMPLES COMPLETED")
    print("#"*80 + "\n")
