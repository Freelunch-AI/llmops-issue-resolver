import pytest
import httpx
from unittest.mock import AsyncMock, Mock
from sandbox_sdk.sdk.sdk_sandbox.client import SandboxClient
from sandbox_sdk.helpers.models import SandboxAuthInfo
from sandbox_sdk.sdk.utils.exceptions import (
    NetworkError,
    SandboxOperationError,
    ValidationError
)

@pytest.fixture
def mock_httpx_client():
    return AsyncMock(spec=httpx.AsyncClient)

@pytest.fixture
def auth_info():
    return SandboxAuthInfo(
        url="https://sandbox-api.test",
        private_key="dummy-key"
    )

@pytest.fixture
def sandbox_client(auth_info, mock_httpx_client):
    client = SandboxClient(auth_info=auth_info, sandbox_id="test-sandbox")
    client._client = mock_httpx_client
    return client

class TestSandboxClient:
    @pytest.mark.asyncio
    async def test_execute_actions_success(self, sandbox_client, mock_httpx_client):
        actions = [{"type": "move", "direction": "forward"}]
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            "observations": ["moved forward"],
            "reward": 1.0,
            "done": False,
            "info": {}
        }
        mock_response.raise_for_status = AsyncMock()
        mock_httpx_client.post.return_value = mock_response

        result = await sandbox_client.execute_actions(actions)
        
        assert result["observations"] == ["moved forward"]
        assert result["reward"] == 1.0
        assert result["done"] is False
        mock_httpx_client.post.assert_called_once_with(
            f"{sandbox_client.base_url}/actions",
            json={"actions": actions}
        )

    @pytest.mark.asyncio
    async def test_execute_actions_network_error(self, sandbox_client, mock_httpx_client):
        actions = [{"type": "move", "direction": "forward"}]
        mock_httpx_client.post.side_effect = httpx.NetworkError("Connection failed")

        with pytest.raises(NetworkError):
            await sandbox_client.execute_actions(actions)

    @pytest.mark.asyncio
    async def test_execute_actions_validation_error(self, sandbox_client, mock_httpx_client):
        actions = [{"invalid": "action"}]
        mock_response = AsyncMock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            message="Invalid request",
            request=Mock(),
            response=Mock(status_code=400)
        )
        mock_httpx_client.post.return_value = mock_response

        with pytest.raises(ValidationError):
            await sandbox_client.execute_actions(actions)

    @pytest.mark.asyncio
    async def test_get_health_status_success(self, sandbox_client, mock_httpx_client):
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            "status": "healthy",
            "uptime": 3600,
            "version": "1.0.0"
        }
        mock_response.raise_for_status = AsyncMock()
        mock_httpx_client.get.return_value = mock_response

        result = await sandbox_client.get_health_status()
        
        assert result["status"] == "healthy"
        assert result["uptime"] == 3600
        assert result["version"] == "1.0.0"
        mock_httpx_client.get.assert_called_once_with(
            f"{sandbox_client.base_url}/health"
        )

    @pytest.mark.asyncio
    async def test_get_health_status_service_unavailable(self, sandbox_client, mock_httpx_client):
        mock_response = AsyncMock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            message="Service unavailable",
            request=Mock(),
            response=Mock(status_code=503)
        )
        mock_httpx_client.get.return_value = mock_response

        with pytest.raises(SandboxOperationError):
            await sandbox_client.get_health_status()

    @pytest.mark.asyncio
    async def test_get_health_status_network_error(self, sandbox_client, mock_httpx_client):
        mock_httpx_client.get.side_effect = httpx.NetworkError("Connection failed")

        with pytest.raises(NetworkError):
            await sandbox_client.get_health_status()

    @pytest.mark.asyncio
    async def test_execute_actions_empty_list(self, sandbox_client, mock_httpx_client):
        with pytest.raises(ValidationError):
            await sandbox_client.execute_actions([])
    @pytest.mark.asyncio
    async def test_execute_actions_none_actions(self, sandbox_client, mock_httpx_client):
        with pytest.raises(ValidationError):
            await sandbox_client.execute_actions(None)

    @pytest.mark.asyncio
    async def test_connect_success(self, sandbox_client, mock_httpx_client):
        mock_response = AsyncMock()
        mock_response.json.return_value = {"status": "healthy"}
        mock_response.raise_for_status = AsyncMock()
        mock_httpx_client.get.return_value = mock_response

        await sandbox_client.connect()
        
        assert sandbox_client._connected is True
        assert sandbox_client._client is not None

    @pytest.mark.asyncio
    async def test_connect_auth_error(self, sandbox_client, mock_httpx_client):
        mock_response = AsyncMock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            message="Unauthorized",
            request=Mock(),
            response=Mock(status_code=401)
        )
        mock_httpx_client.get.return_value = mock_response

        with pytest.raises(AuthenticationError):
            await sandbox_client.connect()

    @pytest.mark.asyncio
    async def test_disconnect(self, sandbox_client, mock_httpx_client):
        sandbox_client._connected = True
        await sandbox_client.disconnect()
        
        assert sandbox_client._connected is False
        assert sandbox_client._client is None
        mock_httpx_client.aclose.assert_called_once()

    @pytest.mark.asyncio
    async def test_reset_success(self, sandbox_client, mock_httpx_client):
        sandbox_client._connected = True
        mock_response = AsyncMock()
        mock_response.raise_for_status = AsyncMock()
        mock_httpx_client.post.return_value = mock_response

        await sandbox_client.reset()
        
        mock_httpx_client.post.assert_called_once_with("/reset")

    @pytest.mark.asyncio
    async def test_reset_not_connected(self, sandbox_client, mock_httpx_client):
        sandbox_client._connected = False
        
        with pytest.raises(SandboxConnectionError):
            await sandbox_client.reset()

    @pytest.mark.asyncio
    async def test_reset_network_error(self, sandbox_client, mock_httpx_client):
        sandbox_client._connected = True
        mock_httpx_client.post.side_effect = httpx.NetworkError("Connection failed")

        with pytest.raises(NetworkError):
            await sandbox_client.reset()

    @pytest.mark.asyncio
    async def test_context_manager(self, sandbox_client, mock_httpx_client):
        mock_response = AsyncMock()
        mock_response.json.return_value = {"status": "healthy"}
        mock_response.raise_for_status = AsyncMock()
        mock_httpx_client.get.return_value = mock_response

        async with sandbox_client as client:
            assert client._connected is True
            assert client._client is not None
        
        assert client._connected is False
        assert client._client is None
        mock_httpx_client.aclose.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_actions_not_connected(self, sandbox_client, mock_httpx_client):
        sandbox_client._connected = False
        actions = [{"type": "move", "direction": "forward"}]

        with pytest.raises(SandboxConnectionError):
            await sandbox_client.execute_actions(actions)