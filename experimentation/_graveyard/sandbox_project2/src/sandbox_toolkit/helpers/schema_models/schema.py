from pydantic import BaseModel
from typing import Dict, Any, List, Union, Callable, Optional
from enum import Enum
from pathlib import Path

class ResourceUnit(str, Enum):
    ABSOLUTE = "absolute"
    PERCENTAGE = "percentage"

class ComputeConfig(BaseModel):
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
    compute_config: ComputeConfig
    database_config: DatabaseConfig
    tools: Tools

class ActionExecutionRequest(BaseModel):
    actions: Dict[str, Dict[str, Any]]

class Observation(BaseModel):
    function_name: str
    terminal_output: str
    process_still_running: bool

class ActionsObservationsPair(BaseModel):
    actions: ActionExecutionRequest
    observations: List[Observation]

class SandboxResourceUsage(BaseModel):
    sandbox_name: str
    sandbox_id: str
    cpu_usage: float
    cpu_unit: str = "CPU %"
    ram_usage: float
    ram_unit: str = "GB"
    disk_usage: float
    disk_unit: str = "GB"
    memory_bandwidth_usage: float
    memory_bandwidth_unit: str = "Gbps"
    networking_bandwith_usage: float
    networking_bandwith_unit: str = "Gbps"

class SandboxStats(BaseModel):
    sandbox_running_duration: float
    actions_sent_count: int

class TotalResourceUsage(BaseModel):
    cpu_usage: float
    cpu_unit: str = "CPU %"
    ram_usage: float
    ram_unit: str = "GB"
    disk_usage: float
    disk_unit: str = "GB"
    memory_bandwidth_usage: float
    memory_bandwidth_unit: str = "Gbps"
    networking_bandwith_usage: float
    networking_bandwith_unit: str = "Gbps"

class TotalResources(BaseModel):
    cpu_total: int
    cpu_unit: str = "CPU cores"
    ram_total: int
    ram_unit: str = "GB"
    disk_total: int
    disk_unit: str = "GB"
    memory_bandwidth_total: int
    memory_bandwidth_unit: str = "Gbps"
    networking_bandwith_total: int
    networking_bandwith_unit: str = "Gbps"

class TotalSandboxResources(BaseModel):
    cpu_allocated: int
    cpu_unit: str = "CPU cores"
    ram_allocated: int
    ram_unit: str = "GB"
    disk_allocated: int
    disk_unit: str = "GB"
    memory_bandwidth_allocated: int
    memory_bandwidth_unit: str = "Gbps"
    networking_bandwith_allocated: int
    networking_bandwith_unit: str = "Gbps"

class SandboxComputeResourceStats(BaseModel):
    sandbox_name: str
    sandbox_id: str
    cpu_usage: float
    cpu_unit: str = "CPU %"
    ram_usage: float
    ram_unit: str = "GB"
    disk_usage: float
    disk_unit: str = "GB"
    memory_bandwidth_usage: float
    memory_bandwidth_unit: str = "Gbps"
    networking_bandwith_usage: float
    networking_bandwith_unit: str = "Gbps"

class TotalComputeResourceStats(BaseModel):
    total_resource_usage: "TotalResourceUsage"
    total_resources: "TotalResources"
    total_sandbox_resources: "TotalSandboxResources"
    sandbox_resource_usage: Dict[str, SandboxResourceUsage]

class ComputeResourceStats(BaseModel): # Represents resource stats for a single sandbox
    sandbox_resource_usage: SandboxResourceUsage

class ToolAPIReference(BaseModel):
    function_name: str
    signature: str
    description: str

class SandboxCapabilities(BaseModel):
    available_tools: List[ToolAPIReference]

class SandboxError(Exception):
    pass

class DatabaseError(SandboxError):
    pass

class ResourceError(SandboxError):
    pass

class ToolError(SandboxError):
    pass