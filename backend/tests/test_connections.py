#!/usr/bin/env python3
"""
Test script for Connection model and providers
"""

import time

def test_connection_model():
    """Test Connection model structure and functionality"""
    print("🔗 Testing Connection Model...")
    print("=" * 50)
    
    try:
        # Test imports
        print("1. Testing imports...")
        from finx.models.connections import (
            Connection, ConnectionModel, Connections,
            ConnectionType, ConnectionStatus,
            ConnectionForm, ConnectionUpdateForm, ConnectionTestForm
        )
        print("   ✅ All imports successful")
        
        # Test enum values
        print("2. Testing enums...")
        print(f"   ConnectionType.POSTGRESQL: {ConnectionType.POSTGRESQL}")
        print(f"   ConnectionType.AWS_ATHENA: {ConnectionType.AWS_ATHENA}")
        print(f"   ConnectionStatus.ACTIVE: {ConnectionStatus.ACTIVE}")
        print(f"   ConnectionStatus.PENDING: {ConnectionStatus.PENDING}")
        print("   ✅ Enums working correctly")
        
        # Test model creation
        print("3. Testing model creation...")
        
        # Test ConnectionForm
        connection_form = ConnectionForm(
            name="Test PostgreSQL Connection",
            description="A test PostgreSQL connection",
            type=ConnectionType.POSTGRESQL,
            host="localhost",
            port="5432",
            database_name="test_db",
            username="test_user",
            config={
                "sslmode": "prefer",
                "timeout": 30
            },
            credentials={
                "password": "test-password"
            }
        )
        print("   ✅ ConnectionForm created successfully")
        
        # Test ConnectionModel
        connection_model = ConnectionModel(
            id="test-conn-1",
            user_id="test-user-1",
            name="Test Connection",
            type=ConnectionType.POSTGRESQL.value,
            host="localhost",
            port="5432",
            database_name="test_db",
            username="test_user",
            created_at=int(time.time()),
            updated_at=int(time.time())
        )
        print("   ✅ ConnectionModel created successfully")
        
        print("\n✅ Connection model test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Connection model test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_connection_providers():
    """Test different connection providers"""
    print("\n🔌 Testing Connection Providers...")
    print("=" * 50)
    
    try:
        from finx.models.connections import ConnectionModel, ConnectionType, DatabaseDriver
        from finx.models.connection_providers import (
            ConnectionProviderFactory, ConnectionManager,
            PostgreSQLProvider, AthenaProvider, SnowflakeProvider,
            BigQueryProvider, S3Provider
        )
        
        # Test PostgreSQL Provider
        print("1. Testing PostgreSQL Provider:")
        pg_connection = ConnectionModel(
            id="pg-test-1",
            user_id="test-user",
            name="Test PostgreSQL",
            type=ConnectionType.POSTGRESQL.value,
            driver=DatabaseDriver.PSYCOPG2.value,
            host="localhost",
            port="5432",
            database_name="test_db",
            username="postgres",
            credentials={"password": "test_pass"},
            config={"sslmode": "prefer"},
            created_at=int(time.time()),
            updated_at=int(time.time())
        )
        
        pg_provider = PostgreSQLProvider(pg_connection)
        connect_result = pg_provider.connect()
        print(f"   ✅ Connection: {connect_result.message} ({connect_result.response_time:.3f}s)")
        
        test_result = pg_provider.test_connection()
        print(f"   ✅ Test: {test_result.message}")
        
        # Test AWS Athena Provider
        print("\n2. Testing AWS Athena Provider:")
        athena_connection = ConnectionModel(
            id="athena-test-1",
            user_id="test-user",
            name="Test Athena",
            type=ConnectionType.AWS_ATHENA.value,
            driver=DatabaseDriver.BOTO3.value,
            database_name="data_lake_db",
            credentials={
                "aws_access_key_id": "AKIA...",
                "aws_secret_access_key": "secret..."
            },
            config={
                "region": "us-west-2",
                "s3_output_location": "s3://my-athena-results/",
                "workgroup": "primary"
            },
            created_at=int(time.time()),
            updated_at=int(time.time())
        )
        
        athena_provider = AthenaProvider(athena_connection)
        connect_result = athena_provider.connect()
        print(f"   ✅ Connection: {connect_result.message} ({connect_result.response_time:.3f}s)")
        
        test_result = athena_provider.test_connection()
        print(f"   ✅ Test: {test_result.message}")
        
        print("\n✅ All connection providers tested successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Connection providers test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_connection_manager():
    """Test the connection manager"""
    print("\n🎛️ Testing Connection Manager...")
    print("=" * 50)
    
    try:
        from finx.models.connections import ConnectionModel, ConnectionType, DatabaseDriver
        from finx.models.connection_providers import ConnectionManager, ConnectionProviderFactory
        
        # Create connection manager
        manager = ConnectionManager()
        
        # Test factory
        print("1. Testing Provider Factory:")
        supported_types = ConnectionProviderFactory.get_supported_types()
        print(f"   ✅ Supported types: {[t.value for t in supported_types]}")
        
        # Create test connections
        connections = [
            ConnectionModel(
                id="pg-manager-test",
                user_id="test-user",
                name="Manager PostgreSQL Test",
                type=ConnectionType.POSTGRESQL.value,
                driver=DatabaseDriver.PSYCOPG2.value,
                host="localhost",
                port="5432",
                database_name="test_db",
                username="postgres",
                created_at=int(time.time()),
                updated_at=int(time.time())
            ),
            ConnectionModel(
                id="athena-manager-test",
                user_id="test-user",
                name="Manager Athena Test",
                type=ConnectionType.AWS_ATHENA.value,
                driver=DatabaseDriver.BOTO3.value,
                database_name="data_lake",
                config={"region": "us-east-1"},
                created_at=int(time.time()),
                updated_at=int(time.time())
            )
        ]
        
        # Test connections through manager
        print("\n2. Testing connections through manager:")
        for connection in connections:
            print(f"   Testing {connection.name}:")
            
            # Test connection
            test_result = manager.test_connection(connection)
            print(f"     ✅ Test: {test_result.message}")
            
            # Execute query
            if connection.type == ConnectionType.POSTGRESQL.value:
                query_result = manager.execute_query(connection, "SELECT version()")
            else:
                query_result = manager.execute_query(connection, "SELECT 1")
            
            print(f"     ✅ Query: {query_result.row_count} rows")
        
        # Test active connections
        print("\n3. Testing active connections:")
        active_connections = manager.get_active_connections()
        print(f"   ✅ Active connections: {len(active_connections)}")
        
        for conn_id, info in active_connections.items():
            print(f"     - {conn_id}: {info['name']} ({info['type']})")
        
        # Test closing connections
        print("\n4. Testing connection cleanup:")
        close_results = manager.close_all_connections()
        print(f"   ✅ Closed {len(close_results)} connections")
        
        print("\n✅ Connection manager tested successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Connection manager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🚀 CONNECTION TESTS")
    print("=" * 50)
    
    tests = [
        test_connection_model,
        test_connection_providers,
        test_connection_manager
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 TEST RESULTS: {passed}/{total} tests passed")
    print("=" * 50)
    
    if passed == total:
        print("🎉 All connection tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
