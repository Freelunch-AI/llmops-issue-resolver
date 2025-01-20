import json
from typing import Dict, Optional, Any, Union
from datetime import datetime

from ..utils.auth import Auth
from ..utils.config import Config
from ..utils.exceptions import SandboxError, AuthenticationError, NetworkError, ResourceNotFoundError
from ..utils.http_client import HTTPClient
from ..utils.logger import get_logger

logger = get_logger(__name__)

class SandboxOrchestratorClient:
    """Client for interacting with the Sandbox Orchestrator service."""

    def __init__(self, config: Config, auth: Auth):
        """
        Initialize the Sandbox Orchestrator client.

        Args:
            config: Configuration object containing service endpoints and settings
            auth: Authentication object for managing tokens and credentials
        """
        self.config = config
        self.auth = auth
        self.http_client = HTTPClient(base_url=self.config.orchestrator_url)
        self._use_basic_auth = True
        self._private_key = None
        self._sandbox_id = None
        self._api_key = None
        
        # Initialize API key from orchestrator if available
        self._initialize_api_key()

    def create_sandbox(self, sandbox_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new sandbox environment.
        Args:
            sandbox_config: Configuration for the sandbox environment

        Returns:
            Dict containing the created sandbox details

        Raises:
            SandboxOrchestratorError: If sandbox creation fails
        """
        try:
            headers = self._get_auth_headers()
            response = self.http_client.post(
                "/sandboxes",
                json=sandbox_config,
                headers=headers
            )
            return response.json()
        except Exception as e:
            logger.error(f"Failed to create sandbox: {str(e)}")
            raise SandboxError(f"Sandbox creation failed: {str(e)}")

    def get_sandbox(self, sandbox_id: str) -> Dict[str, Any]:
        """
        Get details of a specific sandbox.

        Args:
            sandbox_id: ID of the sandbox to retrieve

        Returns:
            Dict containing sandbox details

        Raises:
            SandboxOrchestratorError: If sandbox retrieval fails
        """
        try:
            headers = self._get_auth_headers()
            response = self.http_client.get(
                f"/sandboxes/{sandbox_id}",
                headers=headers
            )
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get sandbox {sandbox_id}: {str(e)}")
            raise ResourceNotFoundError(f"Failed to retrieve sandbox: {str(e)}")

    def delete_sandbox(self, sandbox_id: str) -> None:
        """
        Delete a specific sandbox.

        Args:
            sandbox_id: ID of the sandbox to delete

        Raises:
            SandboxOrchestratorError: If sandbox deletion fails
        """
        try:
            headers = self._get_auth_headers()
            self.http_client.delete(
                f"/sandboxes/{sandbox_id}",
                headers=headers
            )
        except Exception as e:
            logger.error(f"Failed to delete sandbox {sandbox_id}: {str(e)}")
            raise SandboxError(f"Failed to delete sandbox: {str(e)}")

    def update_sandbox(self, sandbox_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a specific sandbox's configuration.

        Args:
            sandbox_id: ID of the sandbox to update
            updates: Dictionary containing the updates to apply

        Returns:
            Dict containing the updated sandbox details

        Raises:
            SandboxOrchestratorError: If sandbox update fails
        """
        try:
            headers = self._get_auth_headers()
            response = self.http_client.patch(
                f"/sandboxes/{sandbox_id}",
                json=updates,
                headers=headers
            )
            return response.json()
        except Exception as e:
            logger.error(f"Failed to update sandbox {sandbox_id}: {str(e)}")
            raise SandboxError(f"Failed to update sandbox: {str(e)}")

    def list_sandboxes(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        List all sandboxes, optionally filtered.

        Args:
            filters: Optional dictionary of filters to apply

        Returns:
            Dict containing list of sandboxes

        Raises:
            SandboxOrchestratorError: If sandbox listing fails
        """
        try:
            headers = self._get_auth_headers()
            params = filters if filters else {}
            response = self.http_client.get(
                "/sandboxes",
                params=params,
                headers=headers
            )
            return response.json()
        except Exception as e:
            logger.error(f"Failed to list sandboxes: {str(e)}")
            raise SandboxError(f"Failed to list sandboxes: {str(e)}")

    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for API requests using the Auth module."""
        if self._use_basic_auth:
            return self.auth.get_basic_auth_headers()
        else:
            return self.auth.get_signed_request_headers(self._sandbox_id)

    def _initialize_api_key(self) -> None:
        """Initialize API key from orchestrator if available."""
        try:
            response = self.http_client.post(
                "/sandbox/start",
                json={
                    "id": f"auto-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}",
                    "environment": {}
                }
            )
            data = response.json()
            if "api_key" in data:
                self._api_key = data["api_key"]
                self._sandbox_id = data.get("sandbox_id")
                if "private_key" in data:
                    self._private_key = self.auth.load_private_key(
                        data["private_key"]
                    )
                    self._use_basic_auth = False
        except Exception as e:
            logger.warning(f"Failed to initialize API key: {str(e)}")
            raise AuthenticationError(f"Failed to initialize API key: {str(e)}")