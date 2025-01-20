import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import redis
from fastapi import HTTPException
from sandbox_sdk.sandbox_gateway.api.auth import AuthManager
from sandbox_sdk.sandbox_gateway.api.models import APIKey

@pytest.fixture
def mock_redis():
    redis_client = Mock(spec=redis.Redis)
    redis_client.pipeline.return_value.__enter__.return_value = redis_client
    redis_client.pipeline.return_value.__exit__.return_value = None
    redis_client.register_script.return_value = Mock()
    return redis_client

@pytest.fixture
def auth_manager(mock_redis):
    return AuthManager(
        redis_client=mock_redis,
        key_ttl=3600,
        rate_limit_attempts=100,
        rate_limit_window=3600
    )

class TestAuthManager:
    def test_generate_api_key_success(self, auth_manager, mock_redis):
        sandbox_id = "sandbox-123"
        mock_redis.execute.return_value = True
        
        api_key = auth_manager.generate_api_key(sandbox_id)
        
        assert isinstance(api_key, APIKey)
        assert api_key.sandbox_id == sandbox_id
        assert isinstance(api_key.key, str)
        assert len(api_key.key) > 0
        assert isinstance(api_key.created_at, datetime)
        assert isinstance(api_key.expires_at, datetime)
        assert api_key.expires_at > api_key.created_at

    def test_generate_api_key_invalid_sandbox_id(self, auth_manager):
        with pytest.raises(ValueError, match="Invalid sandbox ID format"):
            auth_manager.generate_api_key("invalid-id")

    def test_generate_api_key_redis_error(self, auth_manager, mock_redis):
        mock_redis.execute.side_effect = redis.WatchError()
        
        with pytest.raises(HTTPException) as exc_info:
            auth_manager.generate_api_key("sandbox-123")
        
        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "Key generation failed"

    @pytest.mark.asyncio
    async def test_validate_api_key_success(self, auth_manager, mock_redis):
        api_key = "test-key"
        sandbox_id = "sandbox-123"
        mock_redis.incr.return_value = 1
        auth_manager.validate_script.return_value = sandbox_id.encode()

        result = await auth_manager.validate_api_key(api_key)

        assert result == sandbox_id
        mock_redis.incr.assert_called_once()
        mock_redis.expire.assert_called_once()

    @pytest.mark.asyncio
    async def test_validate_api_key_rate_limit_exceeded(self, auth_manager, mock_redis):
        api_key = "test-key"
        mock_redis.incr.return_value = 101

        with pytest.raises(HTTPException) as exc_info:
            await auth_manager.validate_api_key(api_key)

        assert exc_info.value.status_code == 429
        assert exc_info.value.detail == "Rate limit exceeded"

    @pytest.mark.asyncio
    async def test_validate_api_key_invalid(self, auth_manager, mock_redis):
        api_key = "invalid-key"
        mock_redis.incr.return_value = 1
        auth_manager.validate_script.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await auth_manager.validate_api_key(api_key)

        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "Invalid or expired API key"

    def test_revoke_api_key(self, auth_manager, mock_redis):
        api_key = "test-key"
        auth_manager.revoke_api_key(api_key)
        
        mock_redis.delete.assert_called_once_with(f"apikey:{api_key}")

    def test_rotate_api_key_success(self, auth_manager, mock_redis):
        old_key = "old-key"
        sandbox_id = "sandbox-123"
        mock_redis.get.return_value = sandbox_id.encode()
        mock_redis.execute.return_value = True

        new_api_key = auth_manager.rotate_api_key(old_key)

        assert isinstance(new_api_key, APIKey)
        assert new_api_key.sandbox_id == sandbox_id
        mock_redis.delete.assert_called_with(f"apikey:{old_key}")

    def test_rotate_api_key_invalid(self, auth_manager, mock_redis):
        old_key = "invalid-key"
        mock_redis.get.return_value = None

        result = auth_manager.rotate_api_key(old_key)

        assert result is None

    def test_rotate_api_key_redis_error(self, auth_manager, mock_redis):
        old_key = "test-key"
        mock_redis.execute.side_effect = redis.WatchError()

        result = auth_manager.rotate_api_key(old_key)

        assert result is None