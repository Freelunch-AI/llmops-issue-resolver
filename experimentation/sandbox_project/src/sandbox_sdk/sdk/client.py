from typing import Optional, Dict, Any, List
from datetime import datetime
import httpx
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
import base64
from pydantic import ValidationError, BaseModel, Field
from ..models import SandboxResponse, SandboxError, SandboxAuthInfo, SandboxConfig, ResourceStatus, ToolExecuteParams, ToolInfoParams
from .http import HttpClient
from .validators import validate_config
from ..service_manager import ServiceManager

class SandboxClient:
    """Client for interacting with the Sandbox API."""
    def __init__(
        self,
        api_key: Optional[str] = None,
        auth_info: Optional[SandboxAuthInfo] = None,
        sandbox_id: Optional[str] = None,
        compose_file_path: Optional[str] = None,
        inactivity_timeout: int = 1800,
        base_url: str = "https://api.sandbox.com/v1",
        timeout: int = 30,
    ):
        """
        Initialize the Sandbox client.

        Args:
            api_key: Optional API key for basic authentication
            auth_info: Optional auth info for advanced authentication
            sandbox_id: Optional sandbox ID for specific sandbox operations
            compose_file_path: Optional path to docker-compose file
            inactivity_timeout: Timeout for service inactivity in seconds
            base_url: Base URL for the API
            timeout: Request timeout in seconds
        """
        if api_key:
            self.http_client = HttpClient(api_key=api_key, base_url=base_url, timeout=timeout)
            self._use_basic_auth = True
        elif auth_info and sandbox_id and compose_file_path:
            self.api_url = auth_info.url
            self.sandbox_url = f"{auth_info.url}/api/v1/sandbox/{sandbox_id}"
            self.sandbox_id = sandbox_id
            self.service_manager = ServiceManager(compose_file_path, inactivity_timeout)
            self._private_key = serialization.load_pem_private_key(
                auth_info.private_key.get_secret_value().encode(),
                password=None
            )
            self._client = httpx.AsyncClient()
            self._use_basic_auth = False
        else:
            raise ValueError("Either api_key or (auth_info, sandbox_id, compose_file_path) must be provided")

    def create_sandbox(self, config: Dict[str, Any]) -> SandboxResponse:
        """
        Create a new sandbox environment.

        Args:
            config: Configuration dictionary for the sandbox

        Returns:
            SandboxResponse object containing the created sandbox details

        Raises:
            ValidationError: If the config is invalid
            SandboxError: If the API request fails
        """
        try:
            validated_config = validate_config(SandboxConfig(**config))
            response = self.http_client.post("/sandboxes", json=validated_config.dict())
            return SandboxResponse(**response)
        except ValidationError as e:
            raise ValidationError(f"Invalid configuration: {str(e)}")
        except Exception as e:
            raise SandboxError(f"Failed to create sandbox: {str(e)}")

    def get_sandbox(self, sandbox_id: str) -> SandboxResponse:
        """
        Get details of a specific sandbox.

        Args:
            sandbox_id: ID of the sandbox to retrieve

        Returns:
            SandboxResponse object containing the sandbox details

        Raises:
            SandboxError: If the API request fails
        """
        try:
            response = self.http_client.get(f"/sandboxes/{sandbox_id}")
            return SandboxResponse(**response)
        except Exception as e:
            raise SandboxError(f"Failed to get sandbox: {str(e)}")

    def list_sandboxes(
        self, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> List[SandboxResponse]:
        """
        List all sandboxes.

        Args:
            limit: Maximum number of sandboxes to return
            offset: Number of sandboxes to skip

        Returns:
            List of SandboxResponse objects

        Raises:
            SandboxError: If the API request fails
        """
        try:
            params = {}
            if limit is not None:
                params["limit"] = limit
            if offset is not None:
                params["offset"] = offset

            response = self.http_client.get("/sandboxes", params=params)
            return [SandboxResponse(**item) for item in response]
        except Exception as e:
            raise SandboxError(f"Failed to list sandboxes: {str(e)}")

    def delete_sandbox(self, sandbox_id: str) -> None:
        """
        Delete a specific sandbox.

        Args:
            sandbox_id: ID of the sandbox to delete

        Raises:
            SandboxError: If the API request fails
        """
        try:
            self.http_client.delete(f"/sandboxes/{sandbox_id}")
        except Exception as e:
            raise SandboxError(f"Failed to delete sandbox: {str(e)}")

    def update_sandbox(self, sandbox_id: str, config: Dict[str, Any]) -> SandboxResponse:
        """
        Update a specific sandbox configuration.

        Args:
            sandbox_id: ID of the sandbox to update
            config: New configuration dictionary for the sandbox

        Returns:
            SandboxResponse object containing the updated sandbox details

        Raises:
            ValidationError: If the config is invalid
            SandboxError: If the API request fails
        """
        try:
            validated_config = validate_config(SandboxConfig(**config))
            response = self.http_client.put(
                f"/sandboxes/{sandbox_id}", json=validated_config.dict()
            )
            return SandboxResponse(**response)
        except ValidationError as e:
            raise ValidationError(f"Invalid configuration: {str(e)}")
        except Exception as e:
            raise SandboxError(f"Failed to update sandbox: {str(e)}")

    def _sign_request(self) -> Dict[str, str]:
        """Generate headers with signed timestamp."""
        timestamp = datetime.utcnow().isoformat()
        signature = self._private_key.sign(
            timestamp.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return {
            "X-API-Key": f"{self.sandbox_id}.{base64.b64encode(signature).decode()}",
            "X-Timestamp": timestamp
        }

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if not self._use_basic_auth:
            await self.service_manager.stop_services()
            await self._client.aclose()

    async def execute_tool(
        self,
        tool_name: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a tool in the sandbox."""
        if self._use_basic_auth:
            raise NotImplementedError("Tool execution requires advanced authentication")

        if not self.service_manager.is_service_running('orchestrator'):
            if not self.service_manager.start_services(['orchestrator']):
                raise RuntimeError("Failed to start orchestrator service")

        validated_params = ToolExecuteParams(tool_name=tool_name, params=params)
        response = await self._client.post(
            f"{self.sandbox_url}/tools/{validated_params.tool_name}",
            json=validated_params.params or {},
            headers=self._sign_request()
        )
        response.raise_for_status()

        self.service_manager.update_activity('orchestrator')
        return response.json()

    async def get_tool_info(self, tool_name: str) -> Dict[str, Any]:
        """Get information about a tool."""
        if self._use_basic_auth:
            raise NotImplementedError("Tool info requires advanced authentication")

        if not self.service_manager.is_service_running('orchestrator'):
            if not self.service_manager.start_services(['orchestrator']):
                raise RuntimeError("Failed to start orchestrator service")

        validated_params = ToolInfoParams(tool_name=tool_name)
        response = await self._client.get(
            f"{self.sandbox_url}/tools/{validated_params.tool_name}",
            headers=self._sign_request()
        )
        response.raise_for_status()

        self.service_manager.update_activity('orchestrator')
        return response.json()

    async def list_tools(self) -> Dict[str, Any]:
        """List all available tools."""
        if self._use_basic_auth:
            raise NotImplementedError("Tool listing requires advanced authentication")

        if not self.service_manager.is_service_running('orchestrator'):
            if not self.service_manager.start_services(['orchestrator']):
                raise RuntimeError("Failed to start orchestrator service")

        response = await self._client.get(
            f"{self.sandbox_url}/tools",
            headers=self._sign_request()
        )
        response.raise_for_status()

        self.service_manager.update_activity('orchestrator')
        return response.json()

    async def get_current_resources(self) -> ResourceStatus:
        """Get current available resources.

        Returns:
            ResourceStatus: Object containing current resource information
        """
        if self._use_basic_auth:
            raise NotImplementedError("Resource monitoring requires advanced authentication")

        if not self.service_manager.is_service_running('orchestrator'):
            if not self.service_manager.start_services(['orchestrator']):
                raise RuntimeError("Failed to start orchestrator service")

        response = await self._client.get(
            f"{self.api_url}/api/v1/resources",
            headers=self._sign_request()
        )
        response.raise_for_status()

        self.service_manager.update_activity('orchestrator')
        return ResourceStatus(**response.json())

    async def adjust_resource_limits(self, x_percentage: float = 1.3) -> Dict[str, Any]:
        """Adjust resource limits of all running sandboxes based on their maximum usage.

        Args:
            x_percentage: Multiplier for maximum resource usage (default: 1.3)

        Returns:
            Dict[str, Any]: Response containing the adjustment results
        """
        if self._use_basic_auth:
            raise NotImplementedError("Resource adjustment requires advanced authentication")

        if not self.service_manager.is_service_running('orchestrator'):
            if not self.service_manager.start_services(['orchestrator']):
                raise RuntimeError("Failed to start orchestrator service")

        response = await self._client.post(
            f"{self.api_url}/api/v1/sandboxes/adjust_resources",
            json={"x_percentage": x_percentage},
            headers=self._sign_request()
        )
        response.raise_for_status()

        self.service_manager.update_activity('orchestrator')
        return response.json()