#!/usr/bin/env python3
"""
Demo: How to use Connection Providers in a real application
Shows practical examples of managing data connections
"""

import sys
import time
from pathlib import Path
from typing import List, Dict, Any

# Add backend to Python path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

def demo_postgresql_usage():
    """Demo PostgreSQL connection usage"""
    print("🐘 PostgreSQL Connection Demo")
    print("-" * 40)
    
    from finx.models.connections import ConnectionForm, ConnectionType, DatabaseDriver
    from finx.models.connection_providers import connection_manager
    
    # Create PostgreSQL connection
    pg_form = ConnectionForm(
        name="Production PostgreSQL",
        description="Main production database for user data",
        type=ConnectionType.POSTGRESQL,
        driver=DatabaseDriver.PSYCOPG2,
        host="prod-db.company.com",
        port="5432",
        database_name="user_analytics",
        username="analytics_user",
        credentials={
            "password": "secure_password_123"
        },
        config={
            "sslmode": "require",
            "connect_timeout": 10,
            "application_name": "finx_analytics"
        },
        metadata={
            "environment": "production",
            "team": "data-engineering",
            "cost_center": "analytics"
        }
    )
    
    # Convert to ConnectionModel (normally done by Connections.insert_new_connection)
    from finx.models.connections import ConnectionModel
    pg_connection = ConnectionModel(
        id="pg-prod-001",
        user_id="data-engineer-1",
        name=pg_form.name,
        description=pg_form.description,
        type=pg_form.type.value,
        driver=pg_form.driver.value,
        host=pg_form.host,
        port=pg_form.port,
        database_name=pg_form.database_name,
        username=pg_form.username,
        credentials=pg_form.credentials,
        config=pg_form.config,
        metadata=pg_form.metadata,
        created_at=int(time.time()),
        updated_at=int(time.time())
    )
    
    # Test connection
    print("1. Testing PostgreSQL connection...")
    test_result = connection_manager.test_connection(pg_connection)
    print(f"   Result: {test_result.message}")
    print(f"   Response time: {test_result.response_time:.3f}s")
    
    # Execute queries
    print("\n2. Executing PostgreSQL queries...")
    
    queries = [
        "SELECT version()",
        "SELECT COUNT(*) FROM users",
        "SELECT date_trunc('day', created_at) as day, COUNT(*) FROM users GROUP BY day ORDER BY day DESC LIMIT 7"
    ]
    
    for query in queries:
        print(f"   Query: {query}")
        result = connection_manager.execute_query(pg_connection, query)
        if result.success:
            print(f"   ✅ Success: {result.row_count} rows in {result.execution_time:.3f}s")
        else:
            print(f"   ❌ Error: {result.error}")
    
    return pg_connection

def demo_athena_usage():
    """Demo AWS Athena connection usage"""
    print("\n🏔️ AWS Athena Connection Demo")
    print("-" * 40)
    
    from finx.models.connections import ConnectionForm, ConnectionType, DatabaseDriver, ConnectionModel
    from finx.models.connection_providers import connection_manager
    
    # Create Athena connection for data lake analytics
    athena_connection = ConnectionModel(
        id="athena-datalake-001",
        user_id="data-analyst-1",
        name="Data Lake Analytics",
        description="AWS Athena for querying S3 data lake",
        type=ConnectionType.AWS_ATHENA.value,
        driver=DatabaseDriver.BOTO3.value,
        database_name="datalake_analytics",
        credentials={
            "aws_access_key_id": "AKIA1234567890EXAMPLE",
            "aws_secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
        },
        config={
            "region": "us-west-2",
            "s3_output_location": "s3://company-athena-results/",
            "workgroup": "analytics_team",
            "encryption_option": "SSE_S3"
        },
        metadata={
            "environment": "production",
            "data_source": "s3_data_lake",
            "use_case": "business_intelligence"
        },
        created_at=int(time.time()),
        updated_at=int(time.time())
    )
    
    # Test connection
    print("1. Testing Athena connection...")
    test_result = connection_manager.test_connection(athena_connection)
    print(f"   Result: {test_result.message}")
    
    # Execute analytics queries
    print("\n2. Executing Athena analytics queries...")
    
    analytics_queries = [
        "SELECT COUNT(*) FROM user_events WHERE date = '2024-01-15'",
        "SELECT event_type, COUNT(*) as count FROM user_events WHERE date >= '2024-01-01' GROUP BY event_type",
        "SELECT date, SUM(revenue) as daily_revenue FROM sales_data WHERE date >= '2024-01-01' GROUP BY date ORDER BY date"
    ]
    
    for query in analytics_queries:
        print(f"   Query: {query[:60]}...")
        result = connection_manager.execute_query(athena_connection, query)
        if result.success:
            print(f"   ✅ Success: {result.row_count} rows in {result.execution_time:.3f}s")
        else:
            print(f"   ❌ Error: {result.error}")
    
    return athena_connection

def demo_snowflake_usage():
    """Demo Snowflake connection usage"""
    print("\n❄️ Snowflake Connection Demo")
    print("-" * 40)
    
    from finx.models.connections import ConnectionModel, ConnectionType, DatabaseDriver
    from finx.models.connection_providers import connection_manager
    
    # Create Snowflake connection for data warehouse
    snowflake_connection = ConnectionModel(
        id="snowflake-dw-001",
        user_id="data-engineer-2",
        name="Enterprise Data Warehouse",
        description="Snowflake data warehouse for enterprise analytics",
        type=ConnectionType.SNOWFLAKE.value,
        driver=DatabaseDriver.SNOWFLAKE_CONNECTOR.value,
        host="company.snowflakecomputing.com",
        database_name="ENTERPRISE_DW",
        username="DW_ANALYST",
        credentials={
            "password": "SnowflakePassword123!",
            "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----"
        },
        config={
            "account": "company",
            "warehouse": "ANALYTICS_WH",
            "schema": "MARTS",
            "role": "ANALYST_ROLE",
            "session_parameters": {
                "QUERY_TAG": "finx_analytics",
                "TIMEZONE": "UTC"
            }
        },
        metadata={
            "environment": "production",
            "tier": "enterprise",
            "sla": "99.9%"
        },
        created_at=int(time.time()),
        updated_at=int(time.time())
    )
    
    # Test connection
    print("1. Testing Snowflake connection...")
    test_result = connection_manager.test_connection(snowflake_connection)
    print(f"   Result: {test_result.message}")
    
    # Execute data warehouse queries
    print("\n2. Executing Snowflake DW queries...")
    
    dw_queries = [
        "SELECT CURRENT_VERSION(), CURRENT_WAREHOUSE(), CURRENT_DATABASE()",
        "SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'MARTS' LIMIT 10",
        "SELECT date_trunc('month', order_date) as month, SUM(total_amount) FROM fact_orders GROUP BY month ORDER BY month"
    ]
    
    for query in dw_queries:
        print(f"   Query: {query[:60]}...")
        result = connection_manager.execute_query(snowflake_connection, query)
        if result.success:
            print(f"   ✅ Success: {result.row_count} rows in {result.execution_time:.3f}s")
        else:
            print(f"   ❌ Error: {result.error}")
    
    return snowflake_connection

def demo_connection_management():
    """Demo connection management features"""
    print("\n🎛️ Connection Management Demo")
    print("-" * 40)
    
    from finx.models.connection_providers import connection_manager
    
    # Create multiple connections
    connections = [
        demo_postgresql_usage(),
        demo_athena_usage(), 
        demo_snowflake_usage()
    ]
    
    print("\n3. Connection Management Features:")
    
    # Show active connections
    active_connections = connection_manager.get_active_connections()
    print(f"   Active connections: {len(active_connections)}")
    
    for conn_id, info in active_connections.items():
        print(f"     - {info['name']} ({info['type']}) - Connected: {info['is_connected']}")
    
    # Demonstrate connection pooling concept
    print("\n4. Connection Performance Monitoring:")
    
    for connection in connections:
        # Simulate multiple queries to show performance
        start_time = time.time()
        
        for i in range(3):
            result = connection_manager.execute_query(connection, "SELECT 1")
            if not result.success:
                print(f"   ❌ Query {i+1} failed for {connection.name}")
        
        total_time = time.time() - start_time
        print(f"   📊 {connection.name}: 3 queries in {total_time:.3f}s")
    
    # Clean up connections
    print("\n5. Cleaning up connections...")
    close_results = connection_manager.close_all_connections()
    print(f"   ✅ Closed {len(close_results)} connections")

def main():
    """Main demo function"""
    print("🚀 DATA CONNECTION PROVIDERS DEMO")
    print("=" * 60)
    print("Demonstrating real-world usage of data connection providers")
    print("=" * 60)
    
    try:
        demo_connection_management()
        
        print("\n" + "=" * 60)
        print("✅ DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("💡 Key Features Demonstrated:")
        print("   - PostgreSQL connection for OLTP queries")
        print("   - AWS Athena for data lake analytics")
        print("   - Snowflake for data warehouse operations")
        print("   - Connection pooling and management")
        print("   - Performance monitoring")
        print("   - Graceful connection cleanup")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
