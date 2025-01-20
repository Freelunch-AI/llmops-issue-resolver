import pytest
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
import base64
from sandbox_sdk.utils.auth import sign_data

@pytest.fixture
def rsa_private_key():
    """Generate a test RSA private key."""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    return private_pem.decode()

@pytest.fixture
def test_data():
    """Sample test data for signing."""
    return "test_message_123"

def test_sign_data_successful(rsa_private_key, test_data):
    """Test successful signature generation with valid inputs."""
    signature = sign_data(rsa_private_key, test_data)
    
    # Verify signature is a non-empty string
    assert isinstance(signature, str)
    assert len(signature) > 0
    
    # Verify signature is valid base64
    try:
        decoded = base64.b64decode(signature)
        assert len(decoded) > 0
    except Exception as e:
        pytest.fail(f"Invalid base64 encoding: {e}")

def test_sign_data_invalid_key():
    """Test error handling for invalid private key."""
    with pytest.raises(ValueError):
        sign_data("invalid_key", "test_data")

def test_sign_data_invalid_input_types():
    """Test error handling for invalid input types."""
    with pytest.raises(TypeError):
        sign_data(None, "test_data")
    
    with pytest.raises(TypeError):
        sign_data("valid_key", None)

def test_sign_data_empty_inputs(rsa_private_key):
    """Test handling of empty string inputs."""
    # Empty string is valid input, should not raise error
    signature = sign_data(rsa_private_key, "")
    assert isinstance(signature, str)
    assert len(signature) > 0

def test_signature_uniqueness(rsa_private_key):
    """Test that different messages produce different signatures."""
    sig1 = sign_data(rsa_private_key, "message1")
    sig2 = sign_data(rsa_private_key, "message2")
    assert sig1 != sig2

def test_signature_consistency(rsa_private_key, test_data):
    """Test that same message and key produce consistent signatures."""
    sig1 = sign_data(rsa_private_key, test_data)
    sig2 = sign_data(rsa_private_key, test_data)
    assert sig1 == sig2