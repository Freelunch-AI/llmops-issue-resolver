import time
from datetime import datetime
from typing import Dict, Optional

from cryptography.hazmat.primitives.asymmetric import rsa
from ..utils.auth import load_private_key, sign_data

class AuthenticationError(Exception):
    """Custom exception for authentication-related errors."""
    pass

def load_private_key_secure(private_key_pem: str) -> rsa.RSAPrivateKey:
    """
    Securely load and validate an RSA private key from PEM format.
    
    Args:
        private_key_pem (str): PEM-encoded RSA private key
        
    Returns:
        RSAPrivateKey: Loaded and validated private key object
        
    Raises:
        AuthenticationError: If the key is invalid or cannot be loaded
    """
    try:
        return load_private_key(private_key_pem)
    except (ValueError, TypeError) as e:
        raise AuthenticationError(f"Failed to load private key: {str(e)}")

def generate_timestamp() -> str:
    """
    Generate an ISO-8601 formatted UTC timestamp for request signing.
    
    Returns:
        str: ISO-8601 formatted timestamp
    """
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

def generate_auth_headers(
    api_key: str,
    private_key_pem: Optional[str] = None,
    timestamp: Optional[str] = None
) -> Dict[str, str]:
    """
    Generate authentication headers for API requests.
    
    Args:
        api_key (str): API key for authentication
        private_key_pem (str, optional): PEM-encoded private key for request signing
        timestamp (str, optional): Custom timestamp for testing purposes
        
    Returns:
        Dict[str, str]: Dictionary containing authentication headers
        
    Raises:
        AuthenticationError: If signing fails or inputs are invalid
    """
    if not api_key:
        raise AuthenticationError("API key is required")

    headers = {
        "X-API-Key": api_key
    }

    if private_key_pem:
        ts = timestamp or generate_timestamp()
        try:
            signature = sign_request(private_key_pem, ts)
            headers.update({
                "X-Timestamp": ts,
                "X-Signature": signature
            })
        except Exception as e:
            raise AuthenticationError(f"Failed to sign request: {str(e)}")

    return headers

def sign_request(private_key_pem: str, timestamp: str) -> str:
    """
    Sign a request using the provided private key and timestamp.
    
    Args:
        private_key_pem (str): PEM-encoded private key
        timestamp (str): ISO-8601 formatted timestamp to sign
        
    Returns:
        str: Base64-encoded signature
        
    Raises:
        AuthenticationError: If signing fails
    """
    try:
        return sign_data(private_key_pem, timestamp)
    except Exception as e:
        raise AuthenticationError(f"Failed to create signature: {str(e)}")