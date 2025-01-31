import base64
from typing import Union

from cryptography.exceptions import InvalidKey
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.serialization import load_pem_private_key


class CryptoError(Exception):
    """Custom exception for cryptographic operation errors."""
    pass


def load_private_key(private_key_pem: str) -> rsa.RSAPrivateKey:
    """
    Load and validate an RSA private key from PEM format with security checks.

    Args:
        private_key_pem (str): PEM-encoded RSA private key

    Returns:
        rsa.RSAPrivateKey: Loaded and validated private key object

    Raises:
        CryptoError: If the key is invalid, too weak, or cannot be loaded
    """
    try:
        # Convert string PEM to bytes
        pem_bytes = private_key_pem.encode('utf-8')
        
        # Load the private key without password protection
        private_key = load_pem_private_key(
            pem_bytes,
            password=None,
        )

        # Verify it's an RSA key
        if not isinstance(private_key, rsa.RSAPrivateKey):
            raise CryptoError("Invalid key type: Expected RSA private key")

        # Check minimum key size (2048 bits)
        if private_key.key_size < 2048:
            raise CryptoError("RSA key size must be at least 2048 bits")

        return private_key

    except ValueError as e:
        raise CryptoError(f"Invalid private key format: {str(e)}")
    except TypeError as e:
        raise CryptoError(f"Invalid private key type: {str(e)}")
    except Exception as e:
        raise CryptoError(f"Failed to load private key: {str(e)}")


def sign_data(private_key_pem: str, data: Union[str, bytes]) -> str:
    """
    Sign data using RSA-PSS with SHA-256 hashing.

    Args:
        private_key_pem (str): PEM-encoded RSA private key
        data (Union[str, bytes]): Data to sign, either as string or bytes

    Returns:
        str: Base64-encoded signature

    Raises:
        CryptoError: If signing fails or inputs are invalid
    """
    try:
        # Load and validate the private key
        private_key = load_private_key(private_key_pem)

        # Convert string data to bytes if necessary
        if isinstance(data, str):
            data = data.encode('utf-8')
        elif not isinstance(data, bytes):
            raise CryptoError("Data must be either string or bytes")

        # Sign the data using PSS padding and SHA-256
        signature = private_key.sign(
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        # Return base64 encoded signature
        return base64.b64encode(signature).decode('utf-8')

    except InvalidKey as e:
        raise CryptoError(f"Invalid key for signing: {str(e)}")
    except ValueError as e:
        raise CryptoError(f"Invalid input for signing: {str(e)}")
    except Exception as e:
        raise CryptoError(f"Signing operation failed: {str(e)}")