from datetime import datetime
from pydantic import BaseModel, PositiveInt, PositiveFloat, validator, Field
from typing import Optional, List, Dict, Union, ClassVar
from pathlib import Path
from ..sdk_orchestrator.config import SandboxConfigManager


class ResourceLimits(BaseModel):
    """System-wide resource limits for sandboxes."""
    max_cpu_cores: PositiveInt = Field(default=8)
    max_ram_gb: PositiveInt = Field(default=32)
    max_disk_gb: PositiveInt = Field(default=100)
    max_sandboxes: PositiveInt = Field(default=10)

    @classmethod
    def from_config(cls, config: SandboxConfigManager) -> 'ResourceLimits':
        """Load resource limits from configuration.

        Args:
            config: SandboxConfigManager instance containing resource limits.

        Returns:
            ResourceLimits: Instance with limits from configuration.
        """
        return cls(
            max_cpu_cores=config.resource_limits.max_cpu_cores,
            max_ram_gb=config.resource_limits.max_ram_gb,
            max_disk_gb=config.resource_limits.max_disk_gb,
            max_sandboxes=config.resource_limits.max_sandboxes
        )

    _instance: ClassVar[Optional['ResourceLimits']] = None


class ComputeResources(BaseModel):
    """Resource configuration for a sandbox."""
    cpu_cores: PositiveFloat
    ram_gb: PositiveInt
    disk_gb: PositiveInt
    memory_bandwidth_gbps: Optional[PositiveFloat] = None
    network_bandwidth_mbps: Optional[PositiveFloat] = None

    @validator("cpu_cores")
    def validate_cpu(cls, v):
        if ResourceLimits._instance is None:
            ResourceLimits._instance = ResourceLimits()
        if v > ResourceLimits._instance.max_cpu_cores:
            raise ValueError(f"CPU cores cannot exceed {ResourceLimits._instance.max_cpu_cores}")
        return v

    @validator("ram_gb")
    def validate_ram(cls, v):
        if ResourceLimits._instance is None:
            ResourceLimits._instance = ResourceLimits()
        if v > ResourceLimits._instance.max_ram_gb:
            raise ValueError(f"RAM cannot exceed {ResourceLimits._instance.max_ram_gb}GB")
        return v

    @validator("disk_gb")
    def validate_disk(cls, v):
        if ResourceLimits._instance is None:
            ResourceLimits._instance = ResourceLimits()
        if v > ResourceLimits._instance.max_disk_gb:
            raise ValueError(f"Disk space cannot exceed {ResourceLimits._instance.max_disk_gb}GB")
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