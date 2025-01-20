from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

# Base Configuration Models
class ResourceConfig(BaseModel):
    cpu_limit: float
    memory_limit: float
    disk_limit: float
    network_limit: float

class SecurityConfig(BaseModel):
    enable_isolation: bool = True
    network_policy: str = "restricted"
    max_processes: int = 50

# Request Models
class SandboxGroupStartRequest(BaseModel):
    vector_db_config: Path
    graph_db_config: Path

class SandboxCreateRequest(BaseModel):
    id: str
    tools: List[str]
    resources: ResourceConfig
    security: Optional[SecurityConfig] = None
    environment: Dict[str, str] = {}

class SandboxStopRequest(BaseModel):
    id: str

class ResourceAdjustmentRequest(BaseModel):
    x_percentage: float = 1.3

# Response Models
class SandboxGroupStartResponse(BaseModel):
    status: str
    databases: Dict[str, str]  # type -> url

class SandboxCreateResponse(BaseModel):
    sandbox_url: str
    api_key: str

class StatusResponse(BaseModel):
    status: str

class ResourceStatusResponse(BaseModel):
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_usage: float
    cpu_available: float
    memory_available: float
    disk_available: float
    network_available: float

class SandboxStatusResponse(BaseModel):
    id: str
    name: str
    endpoint: str
    status: str
    last_activity: datetime