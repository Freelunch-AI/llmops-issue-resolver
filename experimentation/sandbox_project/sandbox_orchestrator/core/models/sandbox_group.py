from typing import Dict, List, Optional
from pydantic import BaseModel, Field, SecretStr
from .sandbox import SandboxConfig
from .database import DatabaseConfig

class SandboxGroupConfig(BaseModel):
    """Configuration for a group of sandboxes."""
    id: str
    sandboxes: List[SandboxConfig]
    database_config: Optional[DatabaseConfig] = None
    shared_environment: Dict[str, str] = Field(default_factory=dict)

class SandboxAuthInfo(BaseModel):
    """Authentication information for a sandbox."""
    url: str
    api_key: SecretStr

class SandboxGroupStartResponse(BaseModel):
    """Response model for starting a sandbox group."""
    group_id: str
    sandbox_auth: Dict[str, SandboxAuthInfo]  # Maps sandbox_id to auth info
    database_urls: Optional[Dict[str, str]] = None  # Maps database_type to its URL