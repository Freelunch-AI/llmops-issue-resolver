from pydantic import BaseModel
from typing import Dict, Any, List, Union, Callable, Optional
from pathlib import Path
from sandbox_toolkit.helpers.schema_models.schema import SandboxConfig, ActionExecutionRequest, Observation, SandboxCapabilities, SandboxResourceUsage, SandboxStats, ComputeResourceStats, ToolAPIReference, TotalComputeResourceStats, SandboxComputeResourceStats

# --- Orchestrator API Request Models (from SDK) ---

class CreateSandboxRequest(BaseModel):
    sandbox_config: SandboxConfig

class SandboxIdRequest(BaseModel): # Reusable sandbox_id request model
    sandbox_id: str

class StartSandboxRequest(SandboxIdRequest):
    pass

class StopSandboxRequest(SandboxIdRequest):
    pass

class GetSandboxUrlRequest(SandboxIdRequest):
    pass

class GetSandboxCapabilitiesRequest(SandboxIdRequest):
    pass

class GetSandboxResourceUsageRequest(SandboxIdRequest):
    pass

class GetSandboxStatsRequest(SandboxIdRequest):
    pass

class GetTotalResourceStatsRequest(BaseModel):
    pass


# --- Orchestrator API Response Models (to SDK) ---

class CreateSandboxResponse(BaseModel):
    sandbox_id: str
    sandbox_url: str

class StartSandboxResponse(BaseModel):
    pass

class StopSandboxResponse(BaseModel):
    pass

class GetSandboxUrlResponse(BaseModel):
    sandbox_url: str

class GetSandboxCapabilitiesResponse(SandboxCapabilities):
    pass

class GetSandboxResourceUsageResponse(SandboxComputeResourceStats):
    pass

class GetSandboxStatsResponse(SandboxStats):
    pass

class GetTotalResourceStatsResponse(TotalComputeResourceStats):
    pass


# --- Orchestrator Internal Models (for Docker simulation) ---

class DockerImageBuildRequest(BaseModel):
    dockerfile_path: Path
    image_name: str

class DockerImageBuildResponse(BaseModel):
    image_id: str

class DockerContainerRunRequest(BaseModel):
    image_name: str
    container_name: str
    ports_mapping: Dict[int, int]
    network_name: str

class DockerContainerRunResponse(BaseModel):
    container_id: str
    container_url: str

class DockerContainerStopRequest(BaseModel):
    container_id: str

class DockerContainerStopResponse(BaseModel):
    pass

class DockerNetworkCreateRequest(BaseModel):
    network_name: str

class DockerNetworkCreateResponse(BaseModel):
    network_id: str

class DockerNetworkDeleteRequest(BaseModel):
    network_id: str

class DockerNetworkDeleteResponse(BaseModel):
    pass