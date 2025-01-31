import time
from datetime import datetime
from typing import Dict, Optional
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import rsa
from .crypto_utils import load_private_key, sign_data
from dataclasses import dataclass

class AuthenticationError(Exception):
    """Custom exception for authentication-related errors."""
    pass

class Auth:
    """Class to handle authentication operations for the SDK."""
    
    def __init__(self, api_key: str, private_key_pem: Optional[str] = None):
        """Initialize Auth with API key and optional private key.
        
        Args:
            api_key (str): API key for authentication
            private_key_pem (str, optional): PEM-encoded RSA private key for signed requests
        """
        if not api_key:
            raise AuthenticationError("API key is required")
        
        self.api_key = api_key
        self.private_key_pem = private_key_pem
        self.private_key = None
        
        if private_key_pem:
            try:
                self.private_key = self._load_private_key_secure(private_key_pem)
            except Exception as e:
                raise AuthenticationError(f"Failed to load private key: {str(e)}")
    
    def _load_private_key_secure(self, private_key_pem: str) -> rsa.RSAPrivateKey:
        """Securely load and validate an RSA private key."""
        try:
            return load_private_key(private_key_pem)
        except (ValueError, TypeError) as e:
            raise AuthenticationError(f"Failed to load private key: {str(e)}")
    
    def _generate_timestamp(self) -> str:
        """Generate ISO-8601 formatted UTC timestamp."""
        return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    def get_basic_auth_headers(self) -> Dict[str, str]:
        """Get basic authentication headers with API key.
        
        Returns:
            Dict[str, str]: Headers with API key
        """
        return {"X-API-Key": self.api_key}
    
    def get_signed_request_headers(self, timestamp: Optional[str] = None) -> Dict[str, str]:
        """Get headers for signed requests including API key, timestamp and signature.
        
        Args:
            timestamp (str, optional): Custom timestamp for testing
            
        Returns:
            Dict[str, str]: Headers with API key, timestamp and signature
            
        Raises:
            AuthenticationError: If private key is not configured or signing fails
        """
        if not self.private_key_pem:
            raise AuthenticationError("Private key required for signed requests")
        
        ts = timestamp or self._generate_timestamp()
        try:
            signature = sign_data(self.private_key_pem, ts)
            return {
                "X-API-Key": self.api_key,
                "X-Timestamp": ts,
                "X-Signature": signature
            }
        except Exception as e:
            raise AuthenticationError(f"Failed to sign request: {str(e)}")