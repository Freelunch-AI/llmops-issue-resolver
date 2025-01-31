from pydantic import BaseModel
from typing import Dict, Any, List, Union, Callable, Optional
from pathlib import Path
from sandbox_toolkit.helpers.schema_models.schema import SandboxConfig, ActionExecutionRequest, Observation, SandboxCapabilities, SandboxResourceUsage, SandboxStats, ActionsObservationsPair

# --- Orchestrator Communication Models ---

class SandboxCreateRequest(BaseModel):
    sandbox_config: SandboxConfig

class SandboxCreateResponse(BaseModel):
    sandbox_id: str
    sandbox_url: str

class SandboxStartRequest(BaseModel):
    sandbox_id: str

class SandboxStartResponse(BaseModel):
    pass

class SandboxStopRequest(BaseModel):
    sandbox_id: str

class SandboxStopResponse(BaseModel):
    pass

class SandboxGetUrlRequest(BaseModel):
    sandbox_id: str

class SandboxGetUrlResponse(BaseModel):
    sandbox_url: str

class SandboxGetCapabilitiesRequest(BaseModel):
    sandbox_id: str

class SandboxGetCapabilitiesResponse(SandboxCapabilities):
    pass

class SandboxGetResourceUsageRequest(BaseModel):
    sandbox_id: str

class SandboxGetResourceUsageResponse(SandboxResourceUsage):
    pass

class SandboxGetStatsRequest(BaseModel):
    sandbox_id: str

class SandboxGetStatsResponse(SandboxStats):
    pass


# --- Sandbox Communication Models ---

class SendActionsRequest(BaseModel):
    actions: ActionExecutionRequest

class SendActionsResponse(BaseModel):
    observations: List[Observation]

class GetCapabilitiesRequest(BaseModel):
    pass

class GetCapabilitiesResponse(SandboxCapabilities):
    pass

class GetResourceUsageRequest(BaseModel):
    pass

class GetResourceUsageResponse(SandboxResourceUsage):
    pass

class GetStatsRequest(BaseModel):
    pass

class GetStatsResponse(SandboxStats):
    pass

class GetHistoryRequest(BaseModel):
    pass

class GetHistoryResponse(BaseModel):
    history: List[ActionsObservationsPair] # Assuming ActionHistory is not needed for internal simulation for now
