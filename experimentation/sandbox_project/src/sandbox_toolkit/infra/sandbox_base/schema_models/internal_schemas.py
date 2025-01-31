from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union
from urllib.parse import urlparse

from pydantic import BaseModel, validator


class Tool(BaseModel):
    function_name: str
    function: str
    module_name: str

class HTTPUrl(str):
    http_url: str

    #validator that validates the string is indeed a valid URL
    @validator('shttp_url')
    def validate_http_url(cls, value: str) -> str:
        parsed_url = urlparse(value)
        if parsed_url.scheme.lower() not in ('http', 'https'):
            raise TypeError("Not an HTTP URL")
        return value

class ResourceUnit(str, Enum):
    ABSOLUTE = "absolute (cpu: cores; ram:GB; disk:GB; memory_bandwidth:Gbps; \
    networking_bandwidth:Gbps)"
    PERCENTAGE = "percentage"

class Compute(BaseModel):
    cpu: int
    ram: int
    disk: int
    memory_bandwidth: int
    networking_bandwith: int
    unit: ResourceUnit = ResourceUnit.ABSOLUTE

class DatabaseType(str, Enum):
    VECTOR = "vector"
    GRAPH = "graph"

class DatabaseAccessType(str, Enum):
    READ_ONLY = "read_only"
    READ_WRITE = "read_write"

class DatabaseConfig(BaseModel):
    database_type: DatabaseType = DatabaseType.VECTOR
    access_type: DatabaseAccessType = DatabaseAccessType.READ_WRITE
    namespaces: List[str] = ["default"]

class Tools(BaseModel):
    tools: Optional[Union[List[Callable], List[Path]]] = None

class SandboxConfig(BaseModel):
    compute_config: Compute
    database_config: DatabaseConfig
    tools: Tools
    user_knowledge_files_dir: Optional[str] = None

class Actions(BaseModel):
    actions: Dict[str, Dict[str, Any]]

class Observation(BaseModel):
    function_name: str
    terminal_output: str
    process_still_running: bool

class ActionsObservationsPair(BaseModel):
    actions: Actions
    observations: List[Observation]

class SandboxStats(BaseModel):
    sandbox_running_duration: float
    actions_sent_count: int

class HostResourceSummary(BaseModel):
    host_resources: Compute
    host_resource_usage: Compute

class GroupResourceUsage(BaseModel):
    sandboxes_resource_usage: Dict[str, Compute]

class GroupResourceSummary(BaseModel):
    sandboxes_allocated_resources: Dict[str, Compute]
    sandboxes_resource_usage: Dict[str, Compute]

class SandboxResourceSummary(BaseModel): # Represents resource stats for a single sandbox
    sandbox_allocated_resources: Compute
    sandbox_resource_usage: Compute

class ToolAPIReference(BaseModel):
    function_name: str
    signature: str
    description: str

class ToolReturn(BaseModel):
    return_value: Any
    std_out: str
    std_err: str
    logs: str

class SandboxTools(BaseModel):
    available_tools: List[ToolAPIReference]
