import unittest
from unittest.mock import Mock, patch
import redis
import base64
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from sandbox_sdk.sandbox_gateway.api.key_manager import KeyManager

class TestKeyManager(unittest.TestCase):
    def setUp(self):
        self.redis_mock = Mock(spec=redis.Redis)
        self.key_manager = KeyManager(self.redis_mock)
        
        # Generate test key pair
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        self.public_key = self.private_key.public_key()
        
        # Get PEM format of keys
        self.public_key_pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode()

    def test_store_public_key(self):
        sandbox_id = "test-sandbox"
        self.key_manager.store_public_key(sandbox_id, self.public_key_pem)
        self.redis_mock.set.assert_called_once_with(
            f"sandbox:{sandbox_id}:public_key",
            self.public_key_pem
        )

    def test_get_public_key(self):
        sandbox_id = "test-sandbox"
        self.redis_mock.get.return_value = self.public_key_pem.encode()
        
        result = self.key_manager.get_public_key(sandbox_id)
        self.assertEqual(result, self.public_key_pem)
        self.redis_mock.get.assert_called_once_with(
            f"sandbox:{sandbox_id}:public_key"
        )

    def test_get_public_key_not_found(self):
        sandbox_id = "nonexistent-sandbox"
        self.redis_mock.get.return_value = None
        
        result = self.key_manager.get_public_key(sandbox_id)
        self.assertIsNone(result)

    def test_remove_public_key(self):
        sandbox_id = "test-sandbox"
        self.key_manager.remove_public_key(sandbox_id)
        self.redis_mock.delete.assert_called_once_with(
            f"sandbox:{sandbox_id}:public_key"
        )

    def test_verify_signature_valid(self):
        sandbox_id = "test-sandbox"
        test_data = "test-data"
        
        # Create signature
        signature = self.private_key.sign(
            test_data.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        signature_b64 = base64.b64encode(signature).decode()
        
        # Mock public key retrieval
        self.redis_mock.get.return_value = self.public_key_pem.encode()
        
        result = self.key_manager.verify_signature(sandbox_id, signature_b64, test_data)
        self.assertTrue(result)

    def test_verify_signature_invalid(self):
        sandbox_id = "test-sandbox"
        test_data = "test-data"
        invalid_signature = base64.b64encode(b"invalid-signature").decode()
        
        # Mock public key retrieval
        self.redis_mock.get.return_value = self.public_key_pem.encode()
        
        result = self.key_manager.verify_signature(sandbox_id, invalid_signature, test_data)
        self.assertFalse(result)

    def test_verify_signature_no_public_key(self):
        sandbox_id = "test-sandbox"
        self.redis_mock.get.return_value = None
        
        result = self.key_manager.verify_signature(sandbox_id, "signature", "data")
        self.assertFalse(result)

    @patch('sandbox_sdk.sandbox_gateway.api.key_manager.KeyManager.get_private_key')
    def test_sign_data(self, mock_get_private_key):
        sandbox_id = "test-sandbox"
        test_data = "test-data"
        
        # Mock private key retrieval
        private_key_pem = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        mock_get_private_key.return_value = private_key_pem.decode()
        
        signature = self.key_manager.sign_data(sandbox_id, test_data)
        self.assertIsNotNone(signature)
        
        # Verify the signature
        self.redis_mock.get.return_value = self.public_key_pem.encode()
        verification_result = self.key_manager.verify_signature(sandbox_id, signature, test_data)
        self.assertTrue(verification_result)

    @patch('sandbox_sdk.sandbox_gateway.api.key_manager.KeyManager.get_private_key')
    def test_sign_data_no_private_key(self, mock_get_private_key):
        mock_get_private_key.return_value = None
        result = self.key_manager.sign_data("test-sandbox", "test-data")
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()