from typing import Optional, Dict, Any
import httpx
from datetime import datetime
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
import base64
from pydantic import BaseModel, Field
from .models import SandboxAuthInfo

class ResourceStatus(BaseModel):
    """Model for resource status information."""
    ram_available: float
    disk_available: float
    cpu_available: float
    network_available: float

class ToolExecuteParams(BaseModel):
    tool_name: str = Field(..., description="Name of the tool to execute")
    params: Optional[Dict[str, Any]] = Field(default=None, description="Tool parameters")

class ToolInfoParams(BaseModel):
    tool_name: str = Field(..., description="Name of the tool to get info for")
class SandboxClient:
    def __init__(self, auth_info: SandboxAuthInfo, sandbox_id: str):
        self.api_url = auth_info.url
        self.sandbox_url = f"{auth_info.url}/api/v1/sandbox/{sandbox_id}"
        self.sandbox_id = sandbox_id
        
        # Load private key for signing
        self._private_key = serialization.load_pem_private_key(
            auth_info.private_key.get_secret_value().encode(),
            password=None
        )
        
        self._client = httpx.AsyncClient()
    
    def _sign_request(self) -> Dict[str, str]:
        """Generate headers with signed timestamp."""
        timestamp = datetime.utcnow().isoformat()
        
        # Sign timestamp
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
        await self._client.aclose()
    
    async def execute_tool(
        self,
        tool_name: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a tool in the sandbox."""
        # Validate inputs
        validated_params = ToolExecuteParams(tool_name=tool_name, params=params)
        response = await self._client.post(
            f"{self.sandbox_url}/tools/{validated_params.tool_name}",
            json=validated_params.params or {},
            headers=self._sign_request()
        )
        response.raise_for_status()
        return response.json()
    
    async def get_tool_info(self, tool_name: str) -> Dict[str, Any]:
        """Get information about a tool."""
        # Validate inputs
        validated_params = ToolInfoParams(tool_name=tool_name)
        response = await self._client.get(
            f"{self.sandbox_url}/tools/{validated_params.tool_name}",
            headers=self._sign_request()
        )
        response.raise_for_status()
        return response.json()
    
    async def list_tools(self) -> Dict[str, Any]:
        """List all available tools."""
        response = await self._client.get(
            f"{self.sandbox_url}/tools",
            headers=self._sign_request()
        )
        response.raise_for_status()
        return response.json()

    async def get_current_resources(self) -> ResourceStatus:
        """Get current available resources.

        Returns:
            ResourceStatus: Object containing current resource information
        """
        response = await self._client.get(
            f"{self.api_url}/api/v1/resources",
            headers=self._sign_request()
        )
        response.raise_for_status()
        return ResourceStatus(**response.json())

    async def adjust_resource_limits(self, x_percentage: float = 1.3) -> Dict[str, Any]:
        """Adjust resource limits of all running sandboxes based on their maximum usage.

        Args:
            x_percentage: Multiplier for maximum resource usage (default: 1.3)

        Returns:
            Dict[str, Any]: Response containing the adjustment results
        """
        response = await self._client.post(
            f"{self.api_url}/api/v1/sandboxes/adjust_resources",
            json={"x_percentage": x_percentage},
            headers=self._sign_request()
        )
        response.raise_for_status()
        return response.json()