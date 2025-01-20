import pytest
from datetime import datetime, timedelta
from pydantic import ValidationError
from sandbox_sdk.sandbox_gateway.api.models import APIKey, ProxyConfig

class TestAPIKey:
    def test_valid_api_key(self):
        now = datetime.now()
        api_key = APIKey(
            key="test_key",
            sandbox_id="valid-id-123",
            created_at=now
        )
        assert api_key.key.get_secret_value() == "test_key"
        assert api_key.sandbox_id == "valid-id-123"
        assert api_key.created_at == now
        assert api_key.expires_at is None

    def test_api_key_with_expiration(self):
        now = datetime.now()
        expires = now + timedelta(days=30)
        api_key = APIKey(
            key="test_key",
            sandbox_id="valid-id-123",
            created_at=now,
            expires_at=expires
        )
        assert api_key.expires_at == expires

    def test_invalid_sandbox_id_format(self):
        with pytest.raises(ValidationError) as exc_info:
            APIKey(
                key="test_key",
                sandbox_id="invalid@id",
                created_at=datetime.now()
            )
        assert "Invalid sandbox ID format" in str(exc_info.value)

    def test_sandbox_id_length_constraints(self):
        now = datetime.now()
        # Test too short
        with pytest.raises(ValidationError):
            APIKey(key="test_key", sandbox_id="abc", created_at=now)
        
        # Test too long
        with pytest.raises(ValidationError):
            APIKey(key="test_key", sandbox_id="a" * 33, created_at=now)

class TestProxyConfig:
    def test_default_values(self):
        config = ProxyConfig()
        assert config.max_request_size == 10 * 1024 * 1024  # 10MB
        assert config.connect_timeout == 5.0
        assert config.read_timeout == 30.0
        assert config.total_timeout == 60.0
        assert config.max_retries == 3
        assert config.initial_backoff == 0.1
        assert config.max_backoff == 10.0
        assert config.backoff_factor == 2.0
        assert config.max_connections == 100
        assert config.allowed_url_patterns == []
        assert config.chunk_size == 8192
        assert "host" in config.filtered_headers
        assert "connection" in config.filtered_headers

    def test_custom_values(self):
        custom_config = ProxyConfig(
            max_request_size=5 * 1024 * 1024,
            connect_timeout=10.0,
            read_timeout=45.0,
            total_timeout=90.0,
            max_retries=5,
            allowed_url_patterns=["https://api.example.com/*"],
            chunk_size=4096
        )
        assert custom_config.max_request_size == 5 * 1024 * 1024
        assert custom_config.connect_timeout == 10.0
        assert custom_config.read_timeout == 45.0
        assert custom_config.total_timeout == 90.0
        assert custom_config.max_retries == 5
        assert custom_config.allowed_url_patterns == ["https://api.example.com/*"]
        assert custom_config.chunk_size == 4096

    def test_filtered_headers_immutability(self):
        config = ProxyConfig()
        original_headers = config.filtered_headers.copy()
        
        # Verify that filtered_headers is a set
        assert isinstance(config.filtered_headers, set)
        
        # Verify all default headers are present
        expected_headers = {
            "host", "connection", "keep-alive", "proxy-authenticate",
            "proxy-authorization", "te", "trailers", "transfer-encoding", "upgrade"
        }
        assert config.filtered_headers == expected_headers
        assert config.filtered_headers == original_headers