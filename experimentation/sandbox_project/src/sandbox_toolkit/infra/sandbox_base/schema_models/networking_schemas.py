from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from sandbox_toolkit.helpers.schema_models.internal_schemas import *
from sandbox_toolkit.sdk.core.core import Sandbox

# --- SDK-Orchestrator Networking Models ---

class SandboxCreateRequest(BaseModel):
    sandbox: Sandbox
    user_knowledge_compressed_content: Optional[bytes] = None

class SandboxCreateResponse(BaseModel):
    sandbox_id: str

class SandboxStartRequest(BaseModel):
    sandbox_id: str

class SandboxStartResponse(BaseModel):
    sandbox_url: str

class SandboxStopRequest(BaseModel):
    sandbox_id: str

class SandboxStopResponse(BaseModel):
    pass

class SandboxGetUrlRequest(BaseModel):
    sandbox_id: str

class SandboxGetUrlResponse(BaseModel):
    sandbox_url: str

class HostGetResourceUsageRequest(BaseModel):
    pass

class HostGetResourceUsageResponse(SandboxResourceUsage):
    pass

class HostGetResourcesRequest(BaseModel):
    pass

class HostGetResourcesResponse(SandboxResourceUsage):
    pass

class SandboxGroupStartRequest(BaseModel):
    sandboxgroup_id: str

class SandboxGroupStartResponse(BaseModel):
    urls: List[HTTPUrl]

class SandboxGroupStopRequest(BaseModel):
    sandboxgroup_id: str

class SandboxGroupStopResponse(BaseModel):
    pass

class ResourceAdjustmentRequest(BaseModel):
    multiplier: float

class ResourceAdjustmentResponse(BaseModel):
    pass
    
class SandboxStatus(BaseModel):
    container_status: str
    id: str
    name: str
    endpoint: str
    last_activity: str

class SandboxStatusRequest(BaseModel):
    sandbox_id: str

class SandboxStatusResponse(SandboxStatus):
    pass

class SandboxGroupStatusRequest(BaseModel):
    sandboxgroup_id: str

class SandboxGroupStatusResponse(BaseModel):
    sandbox_group_status: Dict[str, SandboxStatus]

# --- SDK-Sandbox Networking Models ---

class SandboxGetToolsRequest(BaseModel):
    sandbox_id: str

class SandboxGetToolsResponse(SandboxTools):
    pass

class SandboxGetResourceUsageRequest(BaseModel):
    sandbox_id: str

class SandboxGetResourceUsageResponse(Compute):
    pass

class SandboxGetStatsRequest(BaseModel):
    sandbox_id: str

class SandboxGetStatsResponse(SandboxStats):
    pass

class SandboxGetHistoryRequest(BaseModel):
    pass

class SandboxGetHistoryResponse(BaseModel):
    history: List[ActionsObservationsPair]

class SendActionsRequest(BaseModel):
    actions: Actions
    file_content: Optional[bytes] = None

class SendActionsResponse(BaseModel):
    observations: List[Observation]

class StatusResponse(BaseModel):
    status: str
