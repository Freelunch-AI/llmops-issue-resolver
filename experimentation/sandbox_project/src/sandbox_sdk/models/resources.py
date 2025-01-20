from datetime import datetime
from pydantic import BaseModel, PositiveInt, PositiveFloat, validator, Field
from typing import Optional, List

class ResourceLimits(BaseModel):
    """System-wide resource limits for sandboxes."""
    max_cpu_cores: PositiveInt = 8
    max_ram_gb: PositiveInt = 32
    max_disk_gb: PositiveInt = 100
    max_sandboxes: PositiveInt = 10

class ComputeResources(BaseModel):
    """Resource configuration for a sandbox."""
    cpu_cores: PositiveFloat
    ram_gb: PositiveInt
    disk_gb: PositiveInt
    memory_bandwidth_gbps: Optional[PositiveFloat] = None
    network_bandwidth_mbps: Optional[PositiveFloat] = None

    @validator("cpu_cores")
    def validate_cpu(cls, v):
        if v > ResourceLimits.max_cpu_cores:
            raise ValueError(f"CPU cores cannot exceed {ResourceLimits.max_cpu_cores}")
        return v

    @validator("ram_gb")
    def validate_ram(cls, v):
        if v > ResourceLimits.max_ram_gb:
            raise ValueError(f"RAM cannot exceed {ResourceLimits.max_ram_gb}GB")
        return v

    @validator("disk_gb")
    def validate_disk(cls, v):
        if v > ResourceLimits.max_disk_gb:
            raise ValueError(f"Disk space cannot exceed {ResourceLimits.max_disk_gb}GB")
        return v


class ResourceUsage(BaseModel):
    """Current resource usage measurements for a sandbox."""
    cpu_usage_percent: PositiveFloat
    ram_usage_gb: PositiveFloat
    disk_usage_gb: PositiveFloat
    memory_bandwidth_usage_gbps: Optional[PositiveFloat] = None
    network_bandwidth_usage_mbps: Optional[PositiveFloat] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ResourceHistory(BaseModel):
    """Historical resource usage data for a sandbox."""
    sandbox_id: str
    measurements: List[ResourceUsage]
    max_cpu_usage: PositiveFloat
    max_ram_usage: PositiveFloat
    max_disk_usage: PositiveFloat
    max_memory_bandwidth_usage: Optional[PositiveFloat] = None
    max_network_bandwidth_usage: Optional[PositiveFloat] = None

    @validator("measurements")
    def validate_measurements_length(cls, v):
        if len(v) > 5:  # Keep only last 5 measurements
            v = v[-5:]
        return v


class ResourceStatus(BaseModel):
    """Overall resource status and availability information."""
    total_cpu_cores: PositiveInt
    total_ram_gb: PositiveInt
    total_disk_gb: PositiveInt
    available_cpu_cores: PositiveFloat
    available_ram_gb: PositiveFloat
    available_disk_gb: PositiveFloat
    total_sandboxes: PositiveInt
    active_sandboxes: PositiveInt
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    @property
    def available_sandboxes(self) -> int:
        return max(0, self.total_sandboxes - self.active_sandboxes)

    @property
    def is_capacity_available(self) -> bool:
        return self.available_sandboxes > 0 and \
               all([self.available_cpu_cores > 0, 
                    self.available_ram_gb > 0, 
                    self.available_disk_gb > 0])