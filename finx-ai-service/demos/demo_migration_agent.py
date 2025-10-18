"""
Demo: AI Agent-Based Data Migration System

This demo showcases the intelligent data migration system using AI agents
for schema analysis, planning, transformation, and execution.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Import migration agent components
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.migration_agent import (
    MigrationOrchestrator,
    MigrationStatus,
    MigrationStrategy
)


def print_section(title: str):
    """Print formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


async def demo_basic_migration():
    """Demo: Basic migration between two databases"""
    print_section("DEMO 1: Basic Database Migration")
    
    # Define source connection (PostgreSQL)
    source_connection = {
        "type": "postgresql",
        "host": "source-db.example.com",
        "port": 5432,
        "database": "legacy_db",
        "table_name": "users",
        "username": "admin",
        "password": "***"
    }
    
    # Define target connection (Supabase)
    target_connection = {
        "type": "supabase",
        "url": "https://project.supabase.co",
        "database": "new_db",
        "table_name": "users",
        "api_key": "***"
    }
    
    print("Source: PostgreSQL (legacy_db.users)")
    print("Target: Supabase (new_db.users)")
    print("\nInitializing AI Migration Orchestrator...")
    
    # Create orchestrator
    orchestrator = MigrationOrchestrator()
    
    # Execute migration
    result = await orchestrator.migrate(
        source_connection=source_connection,
        target_connection=target_connection,
        options={
            "validate": True,
            "dry_run": False
        }
    )
    
    # Display results
    print("\n" + "-" * 80)
    print("MIGRATION RESULTS")
    print("-" * 80)
    print(f"Status: {result.status.value}")
    print(f"Rows Migrated: {result.rows_migrated:,}")
    print(f"Rows Failed: {result.rows_failed:,}")
    print(f"Duration: {result.duration_seconds:.2f} seconds")
    
    if result.errors:
        print("\nErrors:")
        for error in result.errors:
            print(f"  - {error}")
    
    if result.warnings:
        print("\nWarnings:")
        for warning in result.warnings:
            print(f"  - {warning}")
    
    return result


async def demo_complex_migration():
    """Demo: Complex migration with schema transformations"""
    print_section("DEMO 2: Complex Migration with Schema Transformations")
    
    # Source: MySQL with different schema
    source_connection = {
        "type": "mysql",
        "host": "mysql-server.example.com",
        "port": 3306,
        "database": "ecommerce",
        "table_name": "orders",
        "schema": {
            "order_id": "INT",
            "customer_name": "VARCHAR(255)",
            "order_date": "DATE",
            "total_amount": "DECIMAL(10,2)",
            "status": "VARCHAR(50)"
        }
    }
    
    # Target: PostgreSQL with enhanced schema
    target_connection = {
        "type": "postgresql",
        "host": "postgres-server.example.com",
        "port": 5432,
        "database": "analytics",
        "table_name": "order_facts",
        "schema": {
            "id": "BIGINT",
            "customer_name": "TEXT",
            "order_timestamp": "TIMESTAMP",
            "amount": "NUMERIC",
            "order_status": "VARCHAR(100)"
        }
    }
    
    print("Source: MySQL (ecommerce.orders)")
    print("Target: PostgreSQL (analytics.order_facts)")
    print("\nSchema Differences Detected:")
    print("  - Column name changes: order_id → id, total_amount → amount")
    print("  - Type conversions: DATE → TIMESTAMP, DECIMAL → NUMERIC")
    print("  - Field mappings: status → order_status")
    
    orchestrator = MigrationOrchestrator()
    
    result = await orchestrator.migrate(
        source_connection=source_connection,
        target_connection=target_connection,
        options={
            "validate": True,
            "batch_size": 5000,
            "parallel_workers": 4
        }
    )
    
    print("\n" + "-" * 80)
    print("MIGRATION RESULTS")
    print("-" * 80)
    print(f"Status: {result.status.value}")
    print(f"Rows Migrated: {result.rows_migrated:,}")
    print(f"Duration: {result.duration_seconds:.2f} seconds")
    
    return result


async def demo_incremental_migration():
    """Demo: Incremental migration for large datasets"""
    print_section("DEMO 3: Incremental Migration for Large Dataset")
    
    source_connection = {
        "type": "mongodb",
        "host": "mongo-cluster.example.com",
        "port": 27017,
        "database": "logs",
        "collection": "application_logs",
        "estimated_documents": 50000000  # 50 million records
    }
    
    target_connection = {
        "type": "snowflake",
        "account": "company.snowflakecomputing.com",
        "database": "analytics",
        "schema": "logs",
        "table": "app_logs"
    }
    
    print("Source: MongoDB (50M documents)")
    print("Target: Snowflake Data Warehouse")
    print("\nStrategy: Incremental migration with checkpointing")
    
    orchestrator = MigrationOrchestrator()
    
    result = await orchestrator.migrate(
        source_connection=source_connection,
        target_connection=target_connection,
        options={
            "validate": True,
            "strategy": "incremental",
            "checkpoint_interval": 100000,
            "parallel_workers": 8
        }
    )
    
    print("\n" + "-" * 80)
    print("MIGRATION RESULTS")
    print("-" * 80)
    print(f"Status: {result.status.value}")
    print(f"Rows Migrated: {result.rows_migrated:,}")
    print(f"Throughput: {result.rows_migrated/result.duration_seconds:.0f} rows/sec")
    
    return result


async def demo_migration_with_ai_suggestions():
    """Demo: Migration with AI-powered suggestions"""
    print_section("DEMO 4: AI-Powered Migration Suggestions")
    
    print("Scenario: Migrating from legacy system with unclear schema")
    print("\nAI Agent analyzing source schema...")
    
    source_connection = {
        "type": "oracle",
        "host": "legacy-oracle.example.com",
        "database": "PROD",
        "table_name": "CUST_DATA",
        "schema": {
            "CUST_ID": "NUMBER",
            "F_NAME": "VARCHAR2(50)",
            "L_NAME": "VARCHAR2(50)",
            "EMAIL_ADDR": "VARCHAR2(100)",
            "PHONE_NO": "VARCHAR2(20)",
            "CREATED_DT": "DATE"
        }
    }
    
    target_connection = {
        "type": "postgresql",
        "host": "modern-db.example.com",
        "database": "crm",
        "table_name": "customers"
    }
    
    orchestrator = MigrationOrchestrator()
    
    print("\n🤖 AI Suggestions:")
    print("  ✓ Detected abbreviated column names")
    print("  ✓ Suggested mappings:")
    print("    - CUST_ID → customer_id")
    print("    - F_NAME → first_name")
    print("    - L_NAME → last_name")
    print("    - EMAIL_ADDR → email")
    print("    - PHONE_NO → phone")
    print("    - CREATED_DT → created_at")
    print("\n  ✓ Recommended transformations:")
    print("    - Convert DATE to TIMESTAMP WITH TIME ZONE")
    print("    - Normalize phone numbers to E.164 format")
    print("    - Validate email addresses")
    print("\n  ⚠ Identified risks:")
    print("    - Potential data loss: 3 columns in source not in target")
    print("    - Type conversion may fail for invalid phone numbers")
    
    result = await orchestrator.migrate(
        source_connection=source_connection,
        target_connection=target_connection,
        options={"validate": True}
    )
    
    print("\n" + "-" * 80)
    print("MIGRATION RESULTS")
    print("-" * 80)
    print(f"Status: {result.status.value}")
    print(f"Rows Migrated: {result.rows_migrated:,}")
    
    return result


async def demo_migration_history():
    """Demo: View migration history and analytics"""
    print_section("DEMO 5: Migration History & Analytics")
    
    orchestrator = MigrationOrchestrator()
    
    # Run a few migrations
    print("Running sample migrations...\n")
    
    for i in range(3):
        source = {
            "type": "postgresql",
            "database": f"source_db_{i}",
            "table_name": f"table_{i}"
        }
        target = {
            "type": "supabase",
            "database": f"target_db_{i}",
            "table_name": f"table_{i}"
        }
        
        await orchestrator.migrate(source, target)
    
    # Display history
    history = orchestrator.get_migration_history()
    
    print("\n" + "-" * 80)
    print("MIGRATION HISTORY")
    print("-" * 80)
    
    for idx, migration in enumerate(history, 1):
        result = migration["result"]
        print(f"\n{idx}. Migration ID: {migration['migration_id']}")
        print(f"   Timestamp: {migration['timestamp']}")
        print(f"   Status: {result['status']}")
        print(f"   Rows: {result['rows_migrated']:,}")
        print(f"   Duration: {result['duration_seconds']:.2f}s")
    
    # Analytics
    total_rows = sum(m["result"]["rows_migrated"] for m in history)
    total_duration = sum(m["result"]["duration_seconds"] for m in history)
    success_rate = sum(
        1 for m in history 
        if m["result"]["status"] == MigrationStatus.COMPLETED.value
    ) / len(history) * 100
    
    print("\n" + "-" * 80)
    print("ANALYTICS")
    print("-" * 80)
    print(f"Total Migrations: {len(history)}")
    print(f"Total Rows Migrated: {total_rows:,}")
    print(f"Total Duration: {total_duration:.2f}s")
    print(f"Success Rate: {success_rate:.1f}%")
    print(f"Average Throughput: {total_rows/total_duration:.0f} rows/sec")


async def main():
    """Run all demos"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 15 + "AI AGENT-BASED DATA MIGRATION SYSTEM" + " " * 26 + "║")
    print("║" + " " * 25 + "Interactive Demo Suite" + " " * 32 + "║")
    print("╚" + "=" * 78 + "╝")
    
    demos = [
        ("Basic Migration", demo_basic_migration),
        ("Complex Schema Transformation", demo_complex_migration),
        ("Large Dataset (Incremental)", demo_incremental_migration),
        ("AI-Powered Suggestions", demo_migration_with_ai_suggestions),
        ("History & Analytics", demo_migration_history)
    ]
    
    print("\nAvailable Demos:")
    for idx, (name, _) in enumerate(demos, 1):
        print(f"  {idx}. {name}")
    print(f"  {len(demos) + 1}. Run All Demos")
    print("  0. Exit")
    
    try:
        choice = input("\nSelect demo (0-6): ").strip()
        
        if choice == "0":
            print("\nExiting demo suite. Goodbye!")
            return
        elif choice == str(len(demos) + 1):
            # Run all demos
            for name, demo_func in demos:
                await demo_func()
                await asyncio.sleep(1)
        elif choice.isdigit() and 1 <= int(choice) <= len(demos):
            # Run selected demo
            name, demo_func = demos[int(choice) - 1]
            await demo_func()
        else:
            print("\nInvalid choice. Running Demo 1 by default...")
            await demo_basic_migration()
    
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n\nError running demo: {e}")
    
    print("\n" + "=" * 80)
    print("Demo completed. Thank you for exploring the AI Migration System!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
