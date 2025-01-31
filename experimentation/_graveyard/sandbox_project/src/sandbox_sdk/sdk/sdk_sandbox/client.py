"""Client for interacting with sandbox instances."""
import httpx
from typing import Dict, Optional, List
import json

from sandbox_sdk.helpers.models import SandboxAuthInfo
from sandbox_sdk.sdk.schema_models.sandbox_models import (
    ActionRequest,
    ActionResponse,
    ObservationModel
)
from sandbox_sdk.sdk.utils.exceptions import (
    NetworkError,
    AuthenticationError,
    SandboxOperationError,
    ValidationError,
    SandboxConnectionError,
    SandboxExecutionError
)

class SandboxClient:
    """Client for interacting with sandbox instances."""

    def __init__(self, auth_info: SandboxAuthInfo):
        """Initialize the sandbox client.

        Args:
            auth_info: Authentication information for the sandbox.
        """
        self.auth_info = auth_info
        self._client: Optional[httpx.AsyncClient] = None
        self._connected = False

    def _get_auth_headers(self) -> Dict[str, str]:
        """Generate authentication headers for requests.

        Returns:
            Dict containing authentication headers.
        """
        headers = {
            "Authorization": f"Bearer {self.auth_info.api_key.key.get_secret_value()}",
            "X-Sandbox-ID": self.auth_info.sandbox_id
        }
        if self.auth_info.auth_token:
            headers["X-Auth-Token"] = self.auth_info.auth_token
        return headers

    async def connect(self) -> None:
        """Establish connection to the sandbox.

        Raises:
            SandboxConnectionError: If connection cannot be established.
            AuthenticationError: If authentication fails.
        """
        try:
            self._client = httpx.AsyncClient(
                base_url=self.auth_info.endpoint,
                headers=self._get_auth_headers(),
                timeout=30.0
            )
            # Verify connection with a health check
            await self.get_health_status()
            self._connected = True
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise AuthenticationError("Failed to authenticate with sandbox")
            raise SandboxConnectionError(
                f"Failed to connect to sandbox: {str(e)}",
                sandbox_id=self.auth_info.sandbox_id,
                endpoint=self.auth_info.endpoint
            )
        except httpx.RequestError as e:
            raise NetworkError(
                f"Network error while connecting to sandbox: {str(e)}",
                endpoint=self.auth_info.endpoint
            )

    async def disconnect(self) -> None:
        """Close the connection to the sandbox."""
        if self._client:
            await self._client.aclose()
            self._connected = False
            self._client = None

    async def execute_actions(self, actions: Dict[str, Dict]) -> ActionResponse:
        """Execute actions in the sandbox.

        Args:
            actions: Dictionary of actions to execute.

        Returns:
            ActionResponse containing observations from the execution.

        Raises:
            ValidationError: If the actions are invalid.
            SandboxExecutionError: If execution fails.
            NetworkError: If there are network issues.
        """
        if not self._connected or not self._client:
            raise SandboxConnectionError(
                "Not connected to sandbox",
                sandbox_id=self.auth_info.sandbox_id
            )

        try:
            request = ActionRequest(actions=actions)
            response = await self._client.post(
                "/execute",
                json=request.model_dump()
            )
            response.raise_for_status()
            return ActionResponse(**response.json())
        except ValidationError as e:
            raise ValidationError(f"Invalid action request: {str(e)}")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 400:
                raise ValidationError(f"Invalid request: {e.response.text}")
            raise SandboxExecutionError(
                f"Failed to execute actions: {e.response.text}",
                action=actions,
                sandbox_id=self.auth_info.sandbox_id
            )
        except httpx.RequestError as e:
            raise NetworkError(
                f"Network error while executing actions: {str(e)}",
                endpoint=f"{self.auth_info.endpoint}/execute"
            )

    async def get_health_status(self) -> bool:
        """Check the health status of the sandbox.

        Returns:
            bool indicating if the sandbox is healthy.

        Raises:
            NetworkError: If there are network issues.
            SandboxOperationError: If the health check fails.
        """
        if not self._client:
            raise SandboxConnectionError(
                "Not connected to sandbox",
                sandbox_id=self.auth_info.sandbox_id
            )

        try:
            response = await self._client.get("/health")
            response.raise_for_status()
            return response.json().get("status") == "healthy"
        except httpx.RequestError as e:
            raise NetworkError(
                f"Network error while checking health: {str(e)}",
                endpoint=f"{self.auth_info.endpoint}/health"
            )
        except httpx.HTTPStatusError as e:
            raise SandboxOperationError(
                f"Health check failed: {e.response.text}",
                operation="health_check",
                resource_id=self.auth_info.sandbox_id
            )

    async def reset(self) -> None:
        """Reset the sandbox to its initial state.

        Raises:
            NetworkError: If there are network issues.
            SandboxOperationError: If the reset operation fails.
        """
        if not self._connected or not self._client:
            raise SandboxConnectionError(
                "Not connected to sandbox",
                sandbox_id=self.auth_info.sandbox_id
            )

        try:
            response = await self._client.post("/reset")
            response.raise_for_status()
        except httpx.RequestError as e:
            raise NetworkError(
                f"Network error while resetting sandbox: {str(e)}",
                endpoint=f"{self.auth_info.endpoint}/reset"
            )
        except httpx.HTTPStatusError as e:
            raise SandboxOperationError(
                f"Failed to reset sandbox: {e.response.text}",
                operation="reset",
                resource_id=self.auth_info.sandbox_id
            )

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()