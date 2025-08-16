import os
import json
import base64
import hashlib
import secrets
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import logging

log = logging.getLogger(__name__)

class CredentialManager:
    """Secure credential management for connection data"""
    
    def __init__(self, master_key: Optional[str] = None):
        """Initialize with master key or generate one"""
        if master_key:
            self.master_key = master_key.encode()
        else:
            # In production, this should come from environment variables or secure key management
            self.master_key = os.environ.get('CONNECTION_MASTER_KEY', 'default-key-change-in-production').encode()
        
        # Generate encryption key from master key
        self.encryption_key = self._derive_key(self.master_key)
        self.cipher_suite = Fernet(self.encryption_key)
    
    def _derive_key(self, password: bytes, salt: Optional[bytes] = None) -> bytes:
        """Derive encryption key from password using PBKDF2"""
        if salt is None:
            salt = b'connection_salt_2024'  # In production, use random salt per credential
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key
    
    def encrypt_credentials(self, credentials: Dict[str, Any]) -> str:
        """Encrypt credential dictionary"""
        try:
            # Convert to JSON and encrypt
            credentials_json = json.dumps(credentials, sort_keys=True)
            encrypted_data = self.cipher_suite.encrypt(credentials_json.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
        except Exception as e:
            log.error(f"Error encrypting credentials: {str(e)}")
            raise SecurityError("Failed to encrypt credentials")
    
    def decrypt_credentials(self, encrypted_credentials: str) -> Dict[str, Any]:
        """Decrypt credential string back to dictionary"""
        try:
            # Decode and decrypt
            encrypted_data = base64.urlsafe_b64decode(encrypted_credentials.encode())
            decrypted_data = self.cipher_suite.decrypt(encrypted_data)
            return json.loads(decrypted_data.decode())
        except Exception as e:
            log.error(f"Error decrypting credentials: {str(e)}")
            return {}
    
    def mask_sensitive_data(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Mask sensitive credential data for safe display"""
        sensitive_fields = {
            'password', 'api_key', 'bearer_token', 'client_secret', 
            'private_key', 'access_token', 'refresh_token'
        }
        
        masked = {}
        for key, value in credentials.items():
            if key.lower() in sensitive_fields and value:
                # Show first 4 and last 4 characters with asterisks in between
                if len(str(value)) > 8:
                    masked[key] = f"{str(value)[:4]}{'*' * (len(str(value)) - 8)}{str(value)[-4:]}"
                else:
                    masked[key] = '*' * len(str(value))
            else:
                masked[key] = value
        
        return masked
    
    def validate_credentials(self, credentials: Dict[str, Any], auth_type: str) -> bool:
        """Validate that required credentials are present for auth type"""
        required_fields = {
            'api_key': ['api_key'],
            'bearer_token': ['bearer_token'],
            'basic_auth': ['username', 'password'],
            'oauth2': ['client_id', 'client_secret'],
            'oauth1': ['client_id', 'client_secret'],
            'custom_header': ['custom_headers'],
            'certificate': ['certificate'],
            'jwt': ['bearer_token']  # JWT is typically passed as bearer token
        }
        
        if auth_type not in required_fields:
            return True  # No validation for unknown types
        
        required = required_fields[auth_type]
        for field in required:
            if field not in credentials or not credentials[field]:
                return False
        
        return True

class SecurityError(Exception):
    """Custom exception for security-related errors"""
    pass

class ConnectionSecurity:
    """Security utilities for connection management"""
    
    @staticmethod
    def generate_api_key(length: int = 32) -> str:
        """Generate a secure API key"""
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def hash_connection_id(connection_id: str, salt: Optional[str] = None) -> str:
        """Hash connection ID for secure storage"""
        if salt is None:
            salt = "connection_id_salt_2024"
        
        combined = f"{connection_id}{salt}"
        return hashlib.sha256(combined.encode()).hexdigest()
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate URL format and security"""
        if not url:
            return False
        
        # Basic URL validation
        if not (url.startswith('http://') or url.startswith('https://')):
            return False
        
        # Block localhost and private IPs in production
        blocked_hosts = ['localhost', '127.0.0.1', '0.0.0.0']
        for blocked in blocked_hosts:
            if blocked in url.lower():
                log.warning(f"Blocked potentially unsafe URL: {url}")
                return False
        
        return True
    
    @staticmethod
    def sanitize_connection_name(name: str) -> str:
        """Sanitize connection name to prevent injection attacks"""
        # Remove potentially dangerous characters
        import re
        sanitized = re.sub(r'[<>"\';\\]', '', name)
        return sanitized.strip()
    
    @staticmethod
    def audit_log_connection_access(
        connection_id: str, 
        user_id: str, 
        action: str, 
        ip_address: Optional[str] = None
    ):
        """Log connection access for security auditing"""
        log.info(
            f"Connection Access - ID: {connection_id}, User: {user_id}, "
            f"Action: {action}, IP: {ip_address or 'unknown'}"
        )

class PermissionManager:
    """Manage permissions for connection operations"""
    
    @staticmethod
    def can_create_connection(user_role: str) -> bool:
        """Check if user can create connections"""
        allowed_roles = ['admin', 'manager', 'developer']
        return user_role in allowed_roles
    
    @staticmethod
    def can_edit_connection(user_role: str, connection_owner: str, user_id: str) -> bool:
        """Check if user can edit a specific connection"""
        # Admins can edit any connection
        if user_role == 'admin':
            return True
        
        # Managers can edit connections in their organization
        if user_role == 'manager':
            return True
        
        # Users can only edit their own connections
        return connection_owner == user_id
    
    @staticmethod
    def can_delete_connection(user_role: str, connection_owner: str, user_id: str) -> bool:
        """Check if user can delete a specific connection"""
        # Only admins and connection owners can delete
        return user_role == 'admin' or connection_owner == user_id
    
    @staticmethod
    def can_view_credentials(user_role: str, connection_owner: str, user_id: str) -> bool:
        """Check if user can view connection credentials"""
        # Only admins and connection owners can view credentials
        return user_role == 'admin' or connection_owner == user_id
    
    @staticmethod
    def can_test_connection(user_role: str) -> bool:
        """Check if user can test connections"""
        allowed_roles = ['admin', 'manager', 'developer', 'user']
        return user_role in allowed_roles

# Global instances
credential_manager = CredentialManager()
security = ConnectionSecurity()
permissions = PermissionManager()

# Convenience functions
def encrypt_credentials(credentials: Dict[str, Any]) -> str:
    """Encrypt credentials using global credential manager"""
    return credential_manager.encrypt_credentials(credentials)

def decrypt_credentials(encrypted_credentials: str) -> Dict[str, Any]:
    """Decrypt credentials using global credential manager"""
    return credential_manager.decrypt_credentials(encrypted_credentials)

def mask_credentials(credentials: Dict[str, Any]) -> Dict[str, Any]:
    """Mask sensitive credential data"""
    return credential_manager.mask_sensitive_data(credentials)

def validate_credentials(credentials: Dict[str, Any], auth_type: str) -> bool:
    """Validate credentials for auth type"""
    return credential_manager.validate_credentials(credentials, auth_type)

def audit_connection_access(connection_id: str, user_id: str, action: str, ip_address: Optional[str] = None):
    """Log connection access for auditing"""
    security.audit_log_connection_access(connection_id, user_id, action, ip_address)

def check_connection_permission(action: str, user_role: str, connection_owner: str = None, user_id: str = None) -> bool:
    """Check if user has permission for connection action"""
    if action == 'create':
        return permissions.can_create_connection(user_role)
    elif action == 'edit':
        return permissions.can_edit_connection(user_role, connection_owner, user_id)
    elif action == 'delete':
        return permissions.can_delete_connection(user_role, connection_owner, user_id)
    elif action == 'view_credentials':
        return permissions.can_view_credentials(user_role, connection_owner, user_id)
    elif action == 'test':
        return permissions.can_test_connection(user_role)
    else:
        return False
