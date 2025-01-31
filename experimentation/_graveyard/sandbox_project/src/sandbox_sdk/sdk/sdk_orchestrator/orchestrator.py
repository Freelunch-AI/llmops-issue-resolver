from typing import Dict, Optional, Any, List
from datetime import datetime

from .client import SandboxOrchestratorClient
from ..utils.auth import Auth
from ..utils.config import Config
from ..utils.exceptions import SandboxError
from ..utils.logger import get_logger

logger = get_logger(__name__)

class SDKOrchestrator:
    """High-level orchestrator for managing sandboxes and resources."""

    def __init__(self, config: Config, auth: Auth):
        """
        Initialize the SDK Orchestrator.

        Args:
            config: Configuration object containing service endpoints and settings
            auth: Authentication object for managing tokens and credentials
        """
        self.client = SandboxOrchestratorClient(config, auth)
        self.config = config
        self.auth = auth

    def create_sandbox(self, name: str, resources: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new sandbox with specified resources.

        Args:
            name: Name of the sandbox
            resources: Dictionary containing resource configurations

        Returns:
            Dict containing the created sandbox details
        """
        sandbox_config = {
            "name": name,
            "resources": resources,
            "created_at": datetime.utcnow().isoformat()
        }
        return self.client.create_sandbox(sandbox_config)

    def get_sandbox(self, sandbox_id: str) -> Dict[str, Any]:
        """
        Get details of a specific sandbox.

        Args:
            sandbox_id: ID of the sandbox to retrieve

        Returns:
            Dict containing sandbox details
        """
        return self.client.get_sandbox(sandbox_id)

    def update_sandbox(self, sandbox_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a sandbox's configuration.

        Args:
            sandbox_id: ID of the sandbox to update
            updates: Dictionary containing the updates to apply

        Returns:
            Dict containing the updated sandbox details
        """
        return self.client.update_sandbox(sandbox_id, updates)

    def delete_sandbox(self, sandbox_id: str) -> None:
        """
        Delete a specific sandbox.

        Args:
            sandbox_id: ID of the sandbox to delete
        """
        self.client.delete_sandbox(sandbox_id)

    def list_sandboxes(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        List all sandboxes with optional filtering.

        Args:
            filters: Optional dictionary of filters to apply

        Returns:
            Dict containing list of sandboxes
        """
        return self.client.list_sandboxes(filters)

    def allocate_resources(self, sandbox_id: str, resources: Dict[str, Any]) -> Dict[str, Any]:
        """
        Allocate additional resources to a sandbox.

        Args:
            sandbox_id: ID of the sandbox
            resources: Dictionary containing resource specifications

        Returns:
            Dict containing the updated resource allocation details
        """
        current_sandbox = self.get_sandbox(sandbox_id)
        current_resources = current_sandbox.get("resources", {})
        updated_resources = {**current_resources, **resources}
        
        return self.update_sandbox(sandbox_id, {"resources": updated_resources})

    def deallocate_resources(self, sandbox_id: str, resource_ids: List[str]) -> Dict[str, Any]:
        """
        Deallocate specific resources from a sandbox.

        Args:
            sandbox_id: ID of the sandbox
            resource_ids: List of resource IDs to deallocate

        Returns:
            Dict containing the updated resource allocation details
        """
        current_sandbox = self.get_sandbox(sandbox_id)
        current_resources = current_sandbox.get("resources", {})
        
        for resource_id in resource_ids:
            current_resources.pop(resource_id, None)
            
        return self.update_sandbox(sandbox_id, {"resources": current_resources})

    def get_resource_usage(self, sandbox_id: str) -> Dict[str, Any]:
        """
        Get resource usage statistics for a sandbox.

        Args:
            sandbox_id: ID of the sandbox

        Returns:
            Dict containing resource usage details
        """
        sandbox_details = self.get_sandbox(sandbox_id)
        return {
            "sandbox_id": sandbox_id,
            "resources": sandbox_details.get("resources", {}),
            "usage_timestamp": datetime.utcnow().isoformat()
        }