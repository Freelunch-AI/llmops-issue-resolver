import pytest
import httpx
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
from cryptography.hazmat.primitives import serialization
from pydantic import ValidationError

from sandbox_sdk.sdk.sdk_orchestrator.client2 import SandboxClient
from sandbox_sdk.helpers.models import SandboxAuthInfo, SandboxError, SandboxResponse, ResourceStatus
from sandbox_sdk.sdk.infra_management.service_manager import ServiceManager

@pytest.fixture
def mock_http_client():
    return Mock()

@pytest.fixture
def mock_service_manager():
    return Mock(spec=ServiceManager)

@pytest.fixture
def mock_httpx_client():
    return AsyncMock(spec=httpx.AsyncClient)

@pytest.fixture
def sandbox_config():
    return {
        "name": "test-sandbox",
        "resources": {
            "cpu": 1,
            "memory": "1G"
        }
    }

@pytest.fixture
def auth_info():
    private_key = serialization.load_pem_private_key(
        b"-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC9QFi6lF4hHCnQ\n-----END PRIVATE KEY-----",
        password=None
    )
    return SandboxAuthInfo(
        url="https://sandbox-api.test",
        private_key="dummy-key"
    )

class TestSandboxClient:
    def test_init_with_api_key(self):
        client = SandboxClient(api_key="test-key")
        assert client._use_basic_auth is True
        assert hasattr(client, "http_client")

    def test_init_with_auth_info(self, auth_info):
        client = SandboxClient(
            auth_info=auth_info,
            sandbox_id="test-sandbox",
            compose_file_path="docker-compose.yml"
        )
        assert client._use_basic_auth is False
        assert client.sandbox_id == "test-sandbox"
        assert hasattr(client, "service_manager")

    def test_init_invalid_params(self):
        with pytest.raises(ValueError):
            SandboxClient()

    @pytest.mark.asyncio
    async def test_async_context_manager(self, auth_info):
        client = SandboxClient(
            auth_info=auth_info,
            sandbox_id="test-sandbox",
            compose_file_path="docker-compose.yml"
        )
        async with client as c:
            assert c == client

    def test_create_sandbox(self, mock_http_client, sandbox_config):
        client = SandboxClient(api_key="test-key")
        client.http_client = mock_http_client
        mock_http_client.post.return_value = {"id": "test-id", "status": "created"}

        response = client.create_sandbox(sandbox_config)
        assert isinstance(response, SandboxResponse)
        mock_http_client.post.assert_called_once()

    def test_create_sandbox_validation_error(self, mock_http_client):
        client = SandboxClient(api_key="test-key")
        client.http_client = mock_http_client

        with pytest.raises(ValidationError):
            client.create_sandbox({"invalid": "config"})

    def test_get_sandbox(self, mock_http_client):
        client = SandboxClient(api_key="test-key")
        client.http_client = mock_http_client
        mock_http_client.get.return_value = {"id": "test-id", "status": "running"}

        response = client.get_sandbox("test-id")
        assert isinstance(response, SandboxResponse)
        mock_http_client.get.assert_called_once_with("/sandboxes/test-id")

    def test_list_sandboxes(self, mock_http_client):
        client = SandboxClient(api_key="test-key")
        client.http_client = mock_http_client
        mock_http_client.get.return_value = [
            {"id": "test-id-1", "status": "running"},
            {"id": "test-id-2", "status": "stopped"}
        ]

        response = client.list_sandboxes(limit=10, offset=0)
        assert len(response) == 2
        assert all(isinstance(item, SandboxResponse) for item in response)

    def test_delete_sandbox(self, mock_http_client):
        client = SandboxClient(api_key="test-key")
        client.http_client = mock_http_client

        client.delete_sandbox("test-id")
        mock_http_client.delete.assert_called_once_with("/sandboxes/test-id")

    def test_update_sandbox(self, mock_http_client, sandbox_config):
        client = SandboxClient(api_key="test-key")
        client.http_client = mock_http_client
        mock_http_client.put.return_value = {"id": "test-id", "status": "updated"}

        response = client.update_sandbox("test-id", sandbox_config)
        assert isinstance(response, SandboxResponse)
        mock_http_client.put.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_tool(self, auth_info, mock_service_manager, mock_httpx_client):
        client = SandboxClient(
            auth_info=auth_info,
            sandbox_id="test-sandbox",
            compose_file_path="docker-compose.yml"
        )
        client.service_manager = mock_service_manager
        client._client = mock_httpx_client

        mock_service_manager.is_service_running.return_value = True
        mock_response = AsyncMock()
        mock_response.json.return_value = {"result": "success"}
        mock_response.raise_for_status = AsyncMock()
        mock_httpx_client.post.return_value = mock_response

        result = await client.execute_tool("test-tool", {"param": "value"})
        assert result == {"result": "success"}

    @pytest.mark.asyncio
    async def test_get_tool_info(self, auth_info, mock_service_manager, mock_httpx_client):
        client = SandboxClient(
            auth_info=auth_info,
            sandbox_id="test-sandbox",
            compose_file_path="docker-compose.yml"
        )
        client.service_manager = mock_service_manager
        client._client = mock_httpx_client

        mock_service_manager.is_service_running.return_value = True
        mock_response = AsyncMock()
        mock_response.json.return_value = {"tool": "info"}
        mock_response.raise_for_status = AsyncMock()
        mock_httpx_client.get.return_value = mock_response

        result = await client.get_tool_info("test-tool")
        assert result == {"tool": "info"}

    @pytest.mark.asyncio
    async def test_list_tools(self, auth_info, mock_service_manager, mock_httpx_client):
        client = SandboxClient(
            auth_info=auth_info,
            sandbox_id="test-sandbox",
            compose_file_path="docker-compose.yml"
        )
        client.service_manager = mock_service_manager
        client._client = mock_httpx_client

        mock_service_manager.is_service_running.return_value = True
        mock_response = AsyncMock()
        mock_response.json.return_value = {"tools": ["tool1", "tool2"]}
        mock_response.raise_for_status = AsyncMock()
        mock_httpx_client.get.return_value = mock_response

        result = await client.list_tools()
        assert result == {"tools": ["tool1", "tool2"]}

    @pytest.mark.asyncio
    async def test_get_current_resources(self, auth_info, mock_service_manager, mock_httpx_client):
        client = SandboxClient(
            auth_info=auth_info,
            sandbox_id="test-sandbox",
            compose_file_path="docker-compose.yml"
        )
        client.service_manager = mock_service_manager
        client._client = mock_httpx_client

        mock_service_manager.is_service_running.return_value = True
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            "cpu_usage": 50,
            "memory_usage": 500,
            "disk_usage": 1000
        }
        mock_response.raise_for_status = AsyncMock()
        mock_httpx_client.get.return_value = mock_response

        result = await client.get_current_resources()
        assert isinstance(result, ResourceStatus)

    @pytest.mark.asyncio
    async def test_adjust_resource_limits(self, auth_info, mock_service_manager, mock_httpx_client):
        client = SandboxClient(
            auth_info=auth_info,
            sandbox_id="test-sandbox",
            compose_file_path="docker-compose.yml"
        )
        client.service_manager = mock_service_manager
        client._client = mock_httpx_client

        mock_service_manager.is_service_running.return_value = True
        mock_response = AsyncMock()
        mock_response.json.return_value = {"adjusted": True}
        mock_response.raise_for_status = AsyncMock()
        mock_httpx_client.post.return_value = mock_response

        result = await client.adjust_resource_limits(1.5)
        assert result == {"adjusted": True}