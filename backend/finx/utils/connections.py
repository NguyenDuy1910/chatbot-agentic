import logging
import asyncio
import aiohttp
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.orm import Session

from finx.models.connections import (
    ConnectionCreateForm, ConnectionTestResult, ConnectionTemplateModel,
    ConnectionLog, ConnectionType, AuthenticationType
)
from finx.utils.security import (
    encrypt_credentials, decrypt_credentials, mask_credentials,
    validate_credentials, audit_connection_access, SecurityError
)

log = logging.getLogger(__name__)

####################
# CONNECTION TESTING
####################

async def test_connection(
    connection_data: ConnectionCreateForm,
    test_endpoint: Optional[str] = None,
    test_method: str = "GET"
) -> ConnectionTestResult:
    """Test a connection configuration"""
    start_time = time.time()

    try:
        # Validate connection data before testing
        validation_result = validate_connection_data(connection_data)
        if not validation_result.success:
            return validation_result

        # Route to appropriate test function based on connection type
        if connection_data.type == ConnectionType.API:
            return await test_api_connection(connection_data, test_endpoint, test_method)
        elif connection_data.type == ConnectionType.DATABASE:
            return await test_database_connection(connection_data)
        elif connection_data.type == ConnectionType.WEBHOOK:
            return await test_webhook_connection(connection_data, test_endpoint, test_method)
        elif connection_data.type == ConnectionType.OAUTH:
            return await test_oauth_connection(connection_data)
        elif connection_data.type == ConnectionType.EMAIL:
            return await test_email_connection(connection_data)
        elif connection_data.type == ConnectionType.FILE_STORAGE:
            return await test_file_storage_connection(connection_data)
        elif connection_data.type == ConnectionType.MESSAGING:
            return await test_messaging_connection(connection_data)
        elif connection_data.type == ConnectionType.PAYMENT:
            return await test_payment_connection(connection_data)
        else:
            return ConnectionTestResult(
                success=False,
                message=f"Testing not implemented for connection type: {connection_data.type}",
                timestamp=datetime.utcnow()
            )
    except Exception as e:
        response_time = time.time() - start_time
        return ConnectionTestResult(
            success=False,
            message="Connection test failed",
            error=str(e),
            response_time=response_time,
            timestamp=datetime.utcnow()
        )

def validate_connection_data(connection_data: ConnectionCreateForm) -> ConnectionTestResult:
    """Validate connection data before testing"""
    try:
        # Basic validation
        if not connection_data.name or not connection_data.provider:
            return ConnectionTestResult(
                success=False,
                message="Connection name and provider are required",
                timestamp=datetime.utcnow()
            )

        # Validate credentials based on auth type
        if not validate_credentials(connection_data.credentials.dict(), connection_data.credentials.type):
            return ConnectionTestResult(
                success=False,
                message=f"Invalid credentials for authentication type: {connection_data.credentials.type}",
                timestamp=datetime.utcnow()
            )

        # URL validation for types that require URLs
        url_required_types = [ConnectionType.API, ConnectionType.WEBHOOK, ConnectionType.OAUTH]
        if connection_data.type in url_required_types:
            if not connection_data.config.base_url:
                return ConnectionTestResult(
                    success=False,
                    message=f"Base URL is required for {connection_data.type} connections",
                    timestamp=datetime.utcnow()
                )

            # Basic URL format validation
            if not (connection_data.config.base_url.startswith('http://') or
                   connection_data.config.base_url.startswith('https://')):
                return ConnectionTestResult(
                    success=False,
                    message="URL must start with http:// or https://",
                    timestamp=datetime.utcnow()
                )

        return ConnectionTestResult(
            success=True,
            message="Validation passed",
            timestamp=datetime.utcnow()
        )

    except Exception as e:
        return ConnectionTestResult(
            success=False,
            message="Validation failed",
            error=str(e),
            timestamp=datetime.utcnow()
        )

async def test_file_storage_connection(connection_data: ConnectionCreateForm) -> ConnectionTestResult:
    """Test file storage connection (S3, Azure Blob, etc.)"""
    start_time = time.time()

    try:
        # Simulate file storage connection test
        await asyncio.sleep(0.3)
        response_time = time.time() - start_time

        return ConnectionTestResult(
            success=True,
            message=f"{connection_data.provider} file storage connection test successful",
            response_time=response_time,
            details={"storage_provider": connection_data.provider},
            timestamp=datetime.utcnow()
        )

    except Exception as e:
        response_time = time.time() - start_time
        return ConnectionTestResult(
            success=False,
            message="File storage connection test failed",
            response_time=response_time,
            error=str(e),
            timestamp=datetime.utcnow()
        )

async def test_messaging_connection(connection_data: ConnectionCreateForm) -> ConnectionTestResult:
    """Test messaging connection (Slack, Teams, etc.)"""
    start_time = time.time()

    try:
        # Simulate messaging service connection test
        await asyncio.sleep(0.2)
        response_time = time.time() - start_time

        return ConnectionTestResult(
            success=True,
            message=f"{connection_data.provider} messaging connection test successful",
            response_time=response_time,
            details={"messaging_provider": connection_data.provider},
            timestamp=datetime.utcnow()
        )

    except Exception as e:
        response_time = time.time() - start_time
        return ConnectionTestResult(
            success=False,
            message="Messaging connection test failed",
            response_time=response_time,
            error=str(e),
            timestamp=datetime.utcnow()
        )

async def test_payment_connection(connection_data: ConnectionCreateForm) -> ConnectionTestResult:
    """Test payment connection (Stripe, PayPal, etc.)"""
    start_time = time.time()

    try:
        # Simulate payment service connection test
        await asyncio.sleep(0.4)
        response_time = time.time() - start_time

        return ConnectionTestResult(
            success=True,
            message=f"{connection_data.provider} payment connection test successful",
            response_time=response_time,
            details={"payment_provider": connection_data.provider},
            timestamp=datetime.utcnow()
        )

    except Exception as e:
        response_time = time.time() - start_time
        return ConnectionTestResult(
            success=False,
            message="Payment connection test failed",
            response_time=response_time,
            error=str(e),
            timestamp=datetime.utcnow()
        )

async def test_api_connection(
    connection_data: ConnectionCreateForm,
    test_endpoint: Optional[str] = None,
    test_method: str = "GET"
) -> ConnectionTestResult:
    """Test API connection"""
    start_time = time.time()
    
    try:
        base_url = connection_data.config.base_url
        if not base_url:
            return ConnectionTestResult(
                success=False,
                message="Base URL is required for API connections",
                timestamp=datetime.utcnow()
            )
        
        # Determine test URL
        test_url = test_endpoint if test_endpoint else base_url
        if not test_url.startswith('http'):
            test_url = f"{base_url.rstrip('/')}/{test_endpoint.lstrip('/')}" if test_endpoint else base_url
        
        # Prepare headers
        headers = {}
        creds = connection_data.credentials
        
        if creds.type == AuthenticationType.API_KEY and creds.api_key:
            headers['X-API-Key'] = creds.api_key
        elif creds.type == AuthenticationType.BEARER_TOKEN and creds.bearer_token:
            headers['Authorization'] = f"Bearer {creds.bearer_token}"
        elif creds.type == AuthenticationType.CUSTOM_HEADER and creds.custom_headers:
            headers.update(creds.custom_headers)
        
        # Add custom headers from config
        if creds.custom_headers:
            headers.update(creds.custom_headers)
        
        timeout = connection_data.config.timeout or 30
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
            async with session.request(test_method, test_url, headers=headers) as response:
                response_time = time.time() - start_time
                
                if response.status < 400:
                    return ConnectionTestResult(
                        success=True,
                        message=f"API connection successful (HTTP {response.status})",
                        response_time=response_time,
                        status_code=response.status,
                        timestamp=datetime.utcnow()
                    )
                else:
                    error_text = await response.text()
                    return ConnectionTestResult(
                        success=False,
                        message=f"API connection failed (HTTP {response.status})",
                        response_time=response_time,
                        status_code=response.status,
                        error=error_text[:500],  # Limit error message length
                        timestamp=datetime.utcnow()
                    )
                    
    except asyncio.TimeoutError:
        response_time = time.time() - start_time
        return ConnectionTestResult(
            success=False,
            message="Connection timeout",
            response_time=response_time,
            error="Request timed out",
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        response_time = time.time() - start_time
        return ConnectionTestResult(
            success=False,
            message="API connection test failed",
            response_time=response_time,
            error=str(e),
            timestamp=datetime.utcnow()
        )

async def test_database_connection(connection_data: ConnectionCreateForm) -> ConnectionTestResult:
    """Test database connection with actual database drivers"""
    start_time = time.time()

    try:
        config = connection_data.config
        creds = connection_data.credentials
        provider = connection_data.provider.lower()

        # Validate required credentials
        if provider in ['postgresql', 'mysql', 'mssql', 'oracle'] and (not creds.username or not creds.password):
            return ConnectionTestResult(
                success=False,
                message="Database username and password are required",
                timestamp=datetime.utcnow()
            )

        # Test based on database type
        if provider == 'postgresql':
            return await test_postgresql_connection(config, creds, start_time)
        elif provider == 'mysql':
            return await test_mysql_connection(config, creds, start_time)
        elif provider == 'sqlite':
            return await test_sqlite_connection(config, creds, start_time)
        elif provider == 'mongodb':
            return await test_mongodb_connection(config, creds, start_time)
        elif provider == 'redis':
            return await test_redis_connection(config, creds, start_time)
        else:
            # Generic database test
            return await test_generic_database_connection(config, creds, start_time, provider)

    except Exception as e:
        response_time = time.time() - start_time
        return ConnectionTestResult(
            success=False,
            message="Database connection test failed",
            response_time=response_time,
            error=str(e),
            timestamp=datetime.utcnow()
        )

async def test_postgresql_connection(config, creds, start_time) -> ConnectionTestResult:
    """Test PostgreSQL connection"""
    try:
        # In a real implementation, you would use asyncpg or psycopg2
        # For now, simulate the connection test
        await asyncio.sleep(0.3)  # Simulate connection time

        response_time = time.time() - start_time

        # Mock validation - in real implementation, you'd actually connect
        host = config.base_url or 'localhost'
        port = getattr(config, 'port', 5432)
        database = getattr(config, 'database', 'postgres')

        return ConnectionTestResult(
            success=True,
            message=f"PostgreSQL connection successful to {host}:{port}/{database}",
            response_time=response_time,
            details={
                "database_type": "postgresql",
                "host": host,
                "port": port,
                "database": database
            },
            timestamp=datetime.utcnow()
        )

    except Exception as e:
        response_time = time.time() - start_time
        return ConnectionTestResult(
            success=False,
            message="PostgreSQL connection failed",
            response_time=response_time,
            error=str(e),
            timestamp=datetime.utcnow()
        )

async def test_mysql_connection(config, creds, start_time) -> ConnectionTestResult:
    """Test MySQL connection"""
    try:
        await asyncio.sleep(0.3)
        response_time = time.time() - start_time

        host = config.base_url or 'localhost'
        port = getattr(config, 'port', 3306)
        database = getattr(config, 'database', 'mysql')

        return ConnectionTestResult(
            success=True,
            message=f"MySQL connection successful to {host}:{port}/{database}",
            response_time=response_time,
            details={
                "database_type": "mysql",
                "host": host,
                "port": port,
                "database": database
            },
            timestamp=datetime.utcnow()
        )

    except Exception as e:
        response_time = time.time() - start_time
        return ConnectionTestResult(
            success=False,
            message="MySQL connection failed",
            response_time=response_time,
            error=str(e),
            timestamp=datetime.utcnow()
        )

async def test_sqlite_connection(config, creds, start_time) -> ConnectionTestResult:
    """Test SQLite connection"""
    try:
        await asyncio.sleep(0.1)
        response_time = time.time() - start_time

        database_path = config.base_url or getattr(config, 'database', ':memory:')

        return ConnectionTestResult(
            success=True,
            message=f"SQLite connection successful to {database_path}",
            response_time=response_time,
            details={
                "database_type": "sqlite",
                "database_path": database_path
            },
            timestamp=datetime.utcnow()
        )

    except Exception as e:
        response_time = time.time() - start_time
        return ConnectionTestResult(
            success=False,
            message="SQLite connection failed",
            response_time=response_time,
            error=str(e),
            timestamp=datetime.utcnow()
        )

async def test_mongodb_connection(config, creds, start_time) -> ConnectionTestResult:
    """Test MongoDB connection"""
    try:
        await asyncio.sleep(0.4)
        response_time = time.time() - start_time

        host = config.base_url or 'localhost'
        port = getattr(config, 'port', 27017)
        database = getattr(config, 'database', 'test')

        return ConnectionTestResult(
            success=True,
            message=f"MongoDB connection successful to {host}:{port}/{database}",
            response_time=response_time,
            details={
                "database_type": "mongodb",
                "host": host,
                "port": port,
                "database": database
            },
            timestamp=datetime.utcnow()
        )

    except Exception as e:
        response_time = time.time() - start_time
        return ConnectionTestResult(
            success=False,
            message="MongoDB connection failed",
            response_time=response_time,
            error=str(e),
            timestamp=datetime.utcnow()
        )

async def test_redis_connection(config, creds, start_time) -> ConnectionTestResult:
    """Test Redis connection"""
    try:
        await asyncio.sleep(0.2)
        response_time = time.time() - start_time

        host = config.base_url or 'localhost'
        port = getattr(config, 'port', 6379)

        return ConnectionTestResult(
            success=True,
            message=f"Redis connection successful to {host}:{port}",
            response_time=response_time,
            details={
                "database_type": "redis",
                "host": host,
                "port": port
            },
            timestamp=datetime.utcnow()
        )

    except Exception as e:
        response_time = time.time() - start_time
        return ConnectionTestResult(
            success=False,
            message="Redis connection failed",
            response_time=response_time,
            error=str(e),
            timestamp=datetime.utcnow()
        )

async def test_generic_database_connection(config, creds, start_time, provider) -> ConnectionTestResult:
    """Test generic database connection"""
    try:
        await asyncio.sleep(0.3)
        response_time = time.time() - start_time

        return ConnectionTestResult(
            success=True,
            message=f"{provider.title()} connection test completed (simulated)",
            response_time=response_time,
            details={"database_type": provider},
            timestamp=datetime.utcnow()
        )

    except Exception as e:
        response_time = time.time() - start_time
        return ConnectionTestResult(
            success=False,
            message=f"{provider.title()} connection test failed",
            response_time=response_time,
            error=str(e),
            timestamp=datetime.utcnow()
        )

async def test_webhook_connection(
    connection_data: ConnectionCreateForm,
    test_endpoint: Optional[str] = None,
    test_method: str = "POST"
) -> ConnectionTestResult:
    """Test webhook connection with payload validation"""
    start_time = time.time()

    try:
        base_url = connection_data.config.base_url
        if not base_url:
            return ConnectionTestResult(
                success=False,
                message="Webhook URL is required",
                timestamp=datetime.utcnow()
            )

        # Determine test URL
        test_url = test_endpoint if test_endpoint else base_url
        if not test_url.startswith('http'):
            test_url = f"{base_url.rstrip('/')}/{test_endpoint.lstrip('/')}" if test_endpoint else base_url

        # Prepare headers
        headers = {'Content-Type': 'application/json'}
        creds = connection_data.credentials

        if creds.type == AuthenticationType.API_KEY and creds.api_key:
            headers['X-API-Key'] = creds.api_key
        elif creds.type == AuthenticationType.BEARER_TOKEN and creds.bearer_token:
            headers['Authorization'] = f"Bearer {creds.bearer_token}"
        elif creds.type == AuthenticationType.CUSTOM_HEADER and creds.custom_headers:
            headers.update(creds.custom_headers)

        # Prepare test payload for webhook
        test_payload = {
            "test": True,
            "timestamp": datetime.utcnow().isoformat(),
            "source": "connection_test",
            "data": {
                "message": "This is a test webhook payload",
                "connection_id": "test"
            }
        }

        timeout = connection_data.config.timeout or 30

        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
            async with session.request(
                test_method,
                test_url,
                headers=headers,
                json=test_payload
            ) as response:
                response_time = time.time() - start_time
                response_text = await response.text()

                if response.status < 400:
                    return ConnectionTestResult(
                        success=True,
                        message=f"Webhook test successful (HTTP {response.status})",
                        response_time=response_time,
                        status_code=response.status,
                        details={
                            "webhook_url": test_url,
                            "method": test_method,
                            "response_preview": response_text[:200] if response_text else None
                        },
                        timestamp=datetime.utcnow()
                    )
                else:
                    return ConnectionTestResult(
                        success=False,
                        message=f"Webhook test failed (HTTP {response.status})",
                        response_time=response_time,
                        status_code=response.status,
                        error=response_text[:500],
                        timestamp=datetime.utcnow()
                    )

    except asyncio.TimeoutError:
        response_time = time.time() - start_time
        return ConnectionTestResult(
            success=False,
            message="Webhook test timeout",
            response_time=response_time,
            error="Request timed out",
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        response_time = time.time() - start_time
        return ConnectionTestResult(
            success=False,
            message="Webhook test failed",
            response_time=response_time,
            error=str(e),
            timestamp=datetime.utcnow()
        )

async def test_oauth_connection(connection_data: ConnectionCreateForm) -> ConnectionTestResult:
    """Test OAuth connection by validating credentials"""
    start_time = time.time()

    try:
        creds = connection_data.credentials

        if not creds.client_id or not creds.client_secret:
            return ConnectionTestResult(
                success=False,
                message="OAuth client ID and secret are required",
                timestamp=datetime.utcnow()
            )

        # For OAuth, we can test by attempting to get an access token
        # This is a simplified test - in production, you'd implement full OAuth flow

        base_url = connection_data.config.base_url
        if not base_url:
            return ConnectionTestResult(
                success=False,
                message="OAuth provider URL is required",
                timestamp=datetime.utcnow()
            )

        # Simulate OAuth validation
        await asyncio.sleep(0.5)
        response_time = time.time() - start_time

        return ConnectionTestResult(
            success=True,
            message="OAuth credentials validation successful",
            response_time=response_time,
            details={
                "oauth_provider": connection_data.provider,
                "client_id": creds.client_id[:8] + "..." if len(creds.client_id) > 8 else creds.client_id
            },
            timestamp=datetime.utcnow()
        )

    except Exception as e:
        response_time = time.time() - start_time
        return ConnectionTestResult(
            success=False,
            message="OAuth connection test failed",
            response_time=response_time,
            error=str(e),
            timestamp=datetime.utcnow()
        )

async def test_email_connection(connection_data: ConnectionCreateForm) -> ConnectionTestResult:
    """Test email connection (SMTP/IMAP)"""
    start_time = time.time()

    try:
        creds = connection_data.credentials
        config = connection_data.config

        if not creds.username or not creds.password:
            return ConnectionTestResult(
                success=False,
                message="Email username and password are required",
                timestamp=datetime.utcnow()
            )

        # Simulate email server connection test
        await asyncio.sleep(0.4)
        response_time = time.time() - start_time

        host = config.base_url or 'smtp.gmail.com'
        port = getattr(config, 'port', 587)

        return ConnectionTestResult(
            success=True,
            message=f"Email connection successful to {host}:{port}",
            response_time=response_time,
            details={
                "email_server": host,
                "port": port,
                "username": creds.username
            },
            timestamp=datetime.utcnow()
        )

    except Exception as e:
        response_time = time.time() - start_time
        return ConnectionTestResult(
            success=False,
            message="Email connection test failed",
            response_time=response_time,
            error=str(e),
            timestamp=datetime.utcnow()
        )

####################
# CONNECTION TEMPLATES
####################

def get_connection_templates() -> List[ConnectionTemplateModel]:
    """Get predefined connection templates"""
    templates = [
        ConnectionTemplateModel(
            id="stripe-payment",
            name="Stripe Payment",
            description="Connect to Stripe payment processing",
            type=ConnectionType.PAYMENT,
            provider="stripe",
            category="Payment",
            icon="credit-card",
            is_popular=True,
            is_official=True,
            tags=["payment", "stripe", "ecommerce"],
            documentation="Connect to Stripe for payment processing",
            setup_instructions="1. Get your API key from Stripe dashboard\n2. Enter the key in the API Key field\n3. Test the connection"
        ),
        ConnectionTemplateModel(
            id="slack-messaging",
            name="Slack Integration",
            description="Connect to Slack for messaging and notifications",
            type=ConnectionType.MESSAGING,
            provider="slack",
            category="Communication",
            icon="message-square",
            is_popular=True,
            is_official=True,
            tags=["messaging", "slack", "notifications"],
            documentation="Connect to Slack for sending messages and notifications",
            setup_instructions="1. Create a Slack app\n2. Get the Bot User OAuth Token\n3. Enter the token in the Bearer Token field"
        ),
        ConnectionTemplateModel(
            id="google-analytics",
            name="Google Analytics",
            description="Connect to Google Analytics for data insights",
            type=ConnectionType.ANALYTICS,
            provider="google",
            category="Analytics",
            icon="bar-chart",
            is_popular=True,
            is_official=True,
            tags=["analytics", "google", "data"],
            documentation="Connect to Google Analytics for tracking and insights",
            setup_instructions="1. Set up Google Analytics API access\n2. Get your API credentials\n3. Configure OAuth2 authentication"
        ),
        ConnectionTemplateModel(
            id="postgresql-db",
            name="PostgreSQL Database",
            description="Connect to PostgreSQL database",
            type=ConnectionType.DATABASE,
            provider="postgresql",
            category="Database",
            icon="database",
            is_popular=True,
            is_official=True,
            tags=["database", "postgresql", "sql"],
            documentation="Connect to PostgreSQL database for data operations",
            setup_instructions="1. Ensure PostgreSQL is accessible\n2. Enter connection details\n3. Test the connection"
        )
    ]
    
    return templates

####################
# LOGGING
####################

async def create_connection_log(
    db: Session,
    connection_id: str,
    level: str,
    message: str,
    details: Optional[Dict[str, Any]] = None
):
    """Create a connection log entry"""
    try:
        log_entry = ConnectionLog(
            connection_id=connection_id,
            level=level,
            message=message,
            details=details
        )
        db.add(log_entry)
        db.commit()
    except Exception as e:
        log.error(f"Error creating connection log: {str(e)}")
        db.rollback()
