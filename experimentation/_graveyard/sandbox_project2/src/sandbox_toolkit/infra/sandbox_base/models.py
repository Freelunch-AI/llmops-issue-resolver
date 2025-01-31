from pydantic import BaseModel
from typing import Dict, Any, List

class ActionRequest(BaseModel):
    actions: Dict[str, Dict[str, Any]]

class ObservationModel(BaseModel):
    stdout: str
    stderr: str
    terminal_still_running: bool

class ActionResponse(BaseModel):
    observations: List[ObservationModel]

class StatusResponse(BaseModel):
    status: str

class SandboxGroupStartRequest(BaseModel):
    vector_db_config: dict
    graph_db_config: dict

class SandboxGroupStartResponse(BaseModel):
    status: str
    databases: dict

class SandboxCreateRequest(BaseModel):
    id: str
    resources: dict
    security: dict | None = None
    environment: dict | None = None
    tools: list[str] | None = None

class SandboxStopRequest(BaseModel):
    id: str

class ResourceAdjustmentRequest(BaseModel):
    x_percentage: float
    
class SandboxStatusResponse(BaseModel):
    id: str
    name: str
    endpoint: str
    status: str
    last_activity: str
    
class ResourceStatusResponse(BaseModel):
    available_cpu: int
    available_ram: int
    available_disk: int
    used_cpu: int
    used_ram: int
    used_disk: int
    sandbox_resource_usage: dict
    total_resource_usage: dict
    total_resources: dict
    total_sandbox_resources: dict