"""
Test script for Supabase connection
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_configuration():
    """Test configuration loading"""
    logger.info("Testing configuration...")

    try:
        from finx.constants import validate_config, DATABASE_PROVIDER, SUPABASE_CONFIG, POSTGRESQL_CONFIG

        logger.info(f"Database Provider: {DATABASE_PROVIDER}")

        # Validate configuration
        config_result = validate_config()

        if config_result["valid"]:
            logger.info("✅ Configuration is valid")

            if DATABASE_PROVIDER == "supabase":
                logger.info(f"Supabase URL: {SUPABASE_CONFIG['URL']}")
                logger.info(f"Has Anon Key: {'Yes' if SUPABASE_CONFIG['ANON_KEY'] else 'No'}")
                logger.info(f"Has DB URL: {'Yes' if SUPABASE_CONFIG['DB_URL'] else 'No'}")
            elif DATABASE_PROVIDER == "postgresql":
                logger.info(f"PostgreSQL Host: {POSTGRESQL_CONFIG['HOST']}")
                logger.info(f"PostgreSQL Database: {POSTGRESQL_CONFIG['DATABASE']}")
                logger.info(f"PostgreSQL Username: {POSTGRESQL_CONFIG['USERNAME']}")
                logger.info(f"Has Password: {'Yes' if POSTGRESQL_CONFIG['PASSWORD'] else 'No'}")

            return True
        else:
            logger.error("❌ Configuration validation failed:")
            for error in config_result["errors"]:
                logger.error(f"  - {error}")
            return False

    except Exception as e:
        logger.error(f"❌ Configuration test failed: {e}")
        return False

def test_provider_client():
    """Test provider-specific client"""
    logger.info("Testing provider client...")

    try:
        from finx.constants import DATABASE_PROVIDER
        from finx.internal.database_factory import test_current_provider

        if DATABASE_PROVIDER == "supabase":
            logger.info("Testing Supabase client...")

            # Use factory to test
            test_result = test_current_provider()

            if test_result["client_connection"]:
                logger.info("✅ Supabase client connection successful")
            else:
                logger.warning(f"⚠️  Supabase client test failed: {test_result.get('client_error', 'Unknown error')}")

            return test_result["client_connection"]

        elif DATABASE_PROVIDER == "postgresql":
            logger.info("✅ PostgreSQL doesn't require separate client")
            return True

        return True

    except Exception as e:
        logger.error(f"❌ Provider client test failed: {e}")
        return False

def test_database_connection():
    """Test database connection using factory"""
    logger.info("Testing database connection...")

    try:
        from finx.internal.database_factory import test_current_provider, get_provider_info

        # Get provider info
        provider_info = get_provider_info()
        logger.info(f"Provider: {provider_info['provider_type']} ({provider_info['provider_class']})")

        # Test connection using factory
        test_result = test_current_provider()

        if test_result["database_connection"]:
            logger.info("✅ Database connection test successful")
            return True
        else:
            logger.error(f"❌ Database connection test failed: {test_result.get('error', 'Unknown error')}")
            return False

    except Exception as e:
        logger.error(f"❌ Database connection test failed: {e}")
        return False

def test_table_creation():
    """Test table creation"""
    logger.info("Testing table creation...")
    
    try:
        from finx.internal.db import create_tables
        
        create_tables()
        logger.info("✅ Tables created successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Table creation failed: {e}")
        return False

def test_provider_switching():
    """Test switching between providers (if both are configured)"""
    logger.info("Testing provider switching...")

    try:
        from finx.internal.database_factory import DatabaseFactory

        available_providers = DatabaseFactory.get_available_providers()
        logger.info(f"Available providers: {list(available_providers.keys())}")

        # Test each available provider
        working_providers = []
        for provider_type in available_providers.keys():
            logger.info(f"Testing {provider_type}...")
            test_result = DatabaseFactory.test_provider(provider_type)

            if test_result["overall_success"]:
                logger.info(f"✅ {provider_type} is working")
                working_providers.append(provider_type)
            else:
                logger.warning(f"⚠️  {provider_type} failed: {test_result.get('error', 'Connection failed')}")

        logger.info(f"Working providers: {working_providers}")
        return len(working_providers) > 0

    except Exception as e:
        logger.error(f"❌ Provider switching test failed: {e}")
        return False


def main():
    """Run all tests"""
    logger.info("🚀 Starting dynamic database connection tests...")

    tests = [
        ("Configuration", test_configuration),
        ("Provider Client", test_provider_client),
        ("Database Connection", test_database_connection),
        ("Table Creation", test_table_creation),
        ("Provider Switching", test_provider_switching)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n--- {test_name} Test ---")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "="*50)
    logger.info("TEST SUMMARY")
    logger.info("="*50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{test_name}: {status}")
        if result:
            passed += 1
    
    logger.info(f"\nPassed: {passed}/{len(results)}")
    
    if passed == len(results):
        logger.info("🎉 All tests passed! Database connection is ready.")
        return True
    else:
        logger.error("❌ Some tests failed. Please check configuration and setup.")
        logger.info("\n📖 For setup help, see:")
        logger.info("  - SUPABASE_SETUP.md for detailed instructions")
        logger.info("  - .env.example for configuration template")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
