"""
Test script for testing both database providers
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


def test_provider(provider_type: str):
    """Test a specific provider"""
    logger.info(f"\n{'='*60}")
    logger.info(f"TESTING {provider_type.upper()} PROVIDER")
    logger.info(f"{'='*60}")
    
    try:
        from finx.internal.database_factory import DatabaseFactory
        
        # Test provider
        test_result = DatabaseFactory.test_provider(provider_type)
        
        logger.info(f"Provider Type: {test_result['provider_type']}")
        logger.info(f"Provider Class: {test_result['provider_class']}")
        logger.info(f"Database Connection: {'✅' if test_result['database_connection'] else '❌'}")
        logger.info(f"Client Connection: {'✅' if test_result['client_connection'] else '❌'}")
        
        if test_result.get('client_error'):
            logger.warning(f"Client Error: {test_result['client_error']}")
        
        if test_result.get('error'):
            logger.error(f"Error: {test_result['error']}")
        
        overall = test_result['overall_success']
        logger.info(f"Overall: {'✅ SUCCESS' if overall else '❌ FAILED'}")
        
        return overall
        
    except Exception as e:
        logger.error(f"❌ Failed to test {provider_type}: {e}")
        return False


def test_supabase():
    """Test Supabase provider"""
    return test_provider("supabase")


def test_postgresql():
    """Test PostgreSQL provider"""
    return test_provider("postgresql")


def get_provider_info(provider_type: str):
    """Get detailed provider information"""
    try:
        from finx.internal.database_factory import DatabaseFactory
        
        info = DatabaseFactory.get_provider_info(provider_type)
        
        logger.info(f"\n📋 {provider_type.upper()} PROVIDER INFO:")
        logger.info(f"  Provider Type: {info.get('provider_type', 'Unknown')}")
        logger.info(f"  Provider Class: {info.get('provider_class', 'Unknown')}")
        logger.info(f"  Is Configured: {'✅' if info.get('is_configured') else '❌'}")
        logger.info(f"  Has Client: {'✅' if info.get('has_client') else '❌'}")
        logger.info(f"  Connection URL Available: {'✅' if info.get('connection_url_available') else '❌'}")
        
        if info.get('connection_url_masked'):
            logger.info(f"  Connection URL: {info['connection_url_masked']}")
        
        if info.get('configuration_errors'):
            logger.error("  Configuration Errors:")
            for error in info['configuration_errors']:
                logger.error(f"    - {error}")
        
        if info.get('error'):
            logger.error(f"  Error: {info['error']}")
        
        return info.get('is_configured', False)
        
    except Exception as e:
        logger.error(f"❌ Failed to get {provider_type} info: {e}")
        return False


def main():
    """Test all available providers"""
    logger.info("🚀 Testing Database Providers...")
    
    # Test both providers
    providers = ["supabase", "postgresql"]
    results = {}
    
    for provider in providers:
        logger.info(f"\n🔍 Checking {provider} configuration...")
        configured = get_provider_info(provider)
        
        if configured:
            logger.info(f"✅ {provider} is configured, testing connection...")
            success = test_provider(provider)
            results[provider] = success
        else:
            logger.warning(f"⚠️  {provider} is not properly configured, skipping test")
            results[provider] = False
    
    # Summary
    logger.info(f"\n{'='*60}")
    logger.info("SUMMARY")
    logger.info(f"{'='*60}")
    
    working_providers = []
    for provider, success in results.items():
        status = "✅ WORKING" if success else "❌ FAILED"
        logger.info(f"{provider.upper()}: {status}")
        if success:
            working_providers.append(provider)
    
    logger.info(f"\nWorking providers: {working_providers}")
    
    if working_providers:
        logger.info("🎉 At least one provider is working!")
        
        # Show current provider
        try:
            from finx.constants import DATABASE_PROVIDER
            logger.info(f"Current provider: {DATABASE_PROVIDER}")
            
            if DATABASE_PROVIDER in working_providers:
                logger.info("✅ Current provider is working!")
            else:
                logger.warning("⚠️  Current provider is not working. Consider switching.")
                if working_providers:
                    logger.info(f"💡 Try setting DATABASE_PROVIDER to: {working_providers[0]}")
        except Exception as e:
            logger.error(f"Error checking current provider: {e}")
        
        return True
    else:
        logger.error("❌ No providers are working. Please check configuration.")
        logger.info("\n📖 Setup help:")
        logger.info("  - See SUPABASE_SETUP.md for detailed instructions")
        logger.info("  - Check .env.example for configuration template")
        logger.info("  - Make sure DATABASE_PROVIDER is set correctly")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
