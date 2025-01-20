from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
import base64

def sign_data(private_key_pem: str, data: str) -> str:
    """Sign data using a private key."""
    private_key = serialization.load_pem_private_key(
        private_key_pem.encode(),
        password=None
    )
    
    signature = private_key.sign(
        data.encode(),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    
    return base64.b64encode(signature).decode()