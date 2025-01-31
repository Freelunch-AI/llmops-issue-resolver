from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
import base64
from typing import Union

"""Authentication and Security Module for Sandbox SDK.

This module implements cryptographic security mechanisms for the Sandbox SDK,
providing robust authentication and data integrity verification capabilities.
It uses industry-standard cryptographic primitives from the cryptography library
to ensure secure communication between components.

Key Features:
    - RSA-based digital signatures for data authenticity
    - PSS padding for enhanced security
    - SHA256 hashing for message integrity
    - Base64 encoding for signature transport

Security Considerations:
    - Requires secure storage of private keys
    - Implements modern cryptographic standards
    - Uses secure padding and hashing algorithms

Example:
    >>> private_key_pem = load_private_key_from_secure_storage()
    >>> data = "sensitive_data"
    >>> signature = sign_data(private_key_pem, data)

Note:
    This module is critical for maintaining the security of the SDK.
    Any modifications should be thoroughly reviewed and tested.
"""

def sign_data(private_key_pem: str, data: str) -> str:
    """Generate a cryptographic signature for the provided data using RSA private key.

    This function creates a digital signature that can be used to verify the authenticity
    and integrity of the data. It uses RSA-PSS padding with SHA256 hashing for
    maximum security.

    Args:
        private_key_pem (str): The PEM-encoded RSA private key used for signing.
            Must be a valid RSA private key in PEM format.
        data (str): The data to be signed. Will be encoded to UTF-8 bytes before signing.

    Returns:
        str: Base64-encoded signature string that can be used for verification.

    Raises:
        ValueError: If the private key is invalid or cannot be loaded.
        TypeError: If inputs are not strings.
"""
    private_key = load_private_key(private_key_pem)
    
    signature = private_key.sign(
        data.encode(),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    
    return base64.b64encode(signature).decode()

def verify_signature(public_key_pem: str, data: str, signature: str) -> bool:
    """Verify a cryptographic signature using an RSA public key.

    This function verifies that a signature was created by the holder of the
    corresponding private key and that the data has not been tampered with.

    Args:
        public_key_pem (str): The PEM-encoded RSA public key for verification.
        data (str): The original data that was signed.
        signature (str): The Base64-encoded signature to verify.

    Returns:
        bool: True if the signature is valid, False otherwise.

    Raises:
        ValueError: If the public key is invalid or cannot be loaded.
        TypeError: If inputs are not strings.
    """
    try:
        public_key = load_public_key(public_key_pem)
        signature_bytes = base64.b64decode(signature)
        
        public_key.verify(
            signature_bytes,
            data.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except Exception:
        return False

def load_private_key(private_key_pem: str) -> rsa.RSAPrivateKey:
    """Load and validate an RSA private key from PEM format.

    Args:
        private_key_pem (str): PEM-encoded RSA private key.

    Returns:
        RSAPrivateKey: Loaded private key object.

    Raises:
        ValueError: If the key is invalid or cannot be loaded.
    """
    if not isinstance(private_key_pem, str):
        raise TypeError("Private key must be a string")

    try:
        private_key = serialization.load_pem_private_key(
            private_key_pem.encode(),
            password=None
        )
        if not isinstance(private_key, rsa.RSAPrivateKey):
            raise ValueError("Key is not an RSA private key")
        return private_key
    except Exception as e:
        raise ValueError(f"Invalid private key: {str(e)}")

def load_public_key(public_key_pem: str) -> rsa.RSAPublicKey:
    """Load and validate an RSA public key from PEM format.

    Args:
        public_key_pem (str): PEM-encoded RSA public key.

    Returns:
        RSAPublicKey: Loaded public key object.

    Raises:
        ValueError: If the key is invalid or cannot be loaded.
    """
    if not isinstance(public_key_pem, str):
        raise TypeError("Public key must be a string")

    try:
        public_key = serialization.load_pem_public_key(
            public_key_pem.encode()
        )
        if not isinstance(public_key, rsa.RSAPublicKey):
            raise ValueError("Key is not an RSA public key")
        return public_key
    except Exception as e:
        raise ValueError(f"Invalid public key: {str(e)}")