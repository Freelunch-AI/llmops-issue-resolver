from typing import Dict, Optional
from pydantic import BaseModel

class SandboxEndpoint(BaseModel):
    """Information about a sandbox endpoint."""
    id: str
    name: str
    endpoint: str

class SandboxGroupEndpoints(BaseModel):
    """Response model for sandbox group endpoints."""
    group_id: str
    sandboxes: Dict[str, SandboxEndpoint]