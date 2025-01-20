from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
import base64
import redis
from typing import Optional

class KeyManager:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    def store_public_key(self, sandbox_id: str, public_key: str) -> None:
        """Store a public key for a sandbox."""
        self.redis.set(f"sandbox:{sandbox_id}:public_key", public_key)

    def get_public_key(self, sandbox_id: str) -> Optional[str]:
        """Retrieve public key for a sandbox."""
        key = self.redis.get(f"sandbox:{sandbox_id}:public_key")
        return key.decode() if key else None

    def remove_public_key(self, sandbox_id: str) -> None:
        """Remove a sandbox's public key."""
        self.redis.delete(f"sandbox:{sandbox_id}:public_key")

    def verify_signature(self, sandbox_id: str, signature: str, data: str) -> bool:
        """Verify a signature using the sandbox's public key."""
        public_key_pem = self.get_public_key(sandbox_id)
        if not public_key_pem:
            return False
        
        try:
            public_key = serialization.load_pem_public_key(
                public_key_pem.encode()
            )
            
            # Verify signature
            public_key.verify(
                base64.b64decode(signature),
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

    def sign_data(self, sandbox_id: str, data: str) -> Optional[str]:
        """Sign data using the sandbox's private key."""
        private_key_pem = self.get_private_key(sandbox_id)
        if not private_key_pem:
            return None
        
        try:
            private_key = serialization.load_pem_private_key(
                private_key_pem.encode(),
                password=None
            )
            
            # Sign data
            signature = private_key.sign(
                data.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return base64.b64encode(signature).decode()
        except Exception:
            return None