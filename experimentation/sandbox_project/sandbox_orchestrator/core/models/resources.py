from datetime import datetime
from typing import List, Optional, Union
from pydantic import BaseModel, Field

class ResourceUsage(BaseModel):
    """Represents a single resource usage measurement."""
    cpu_cores: Union[int, float]
    ram_gb: Union[int, float]
    disk_gb: Union[int, float]
    memory_bandwidth_gbps: Union[int, float]
    network_bandwidth_gbps: Union[int, float]
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ResourceUsageHistory(BaseModel):
    """Maintains the last five resource usage measurements for a sandbox."""
    sandbox_id: str
    measurements: List[ResourceUsage] = Field(default_factory=list)
    max_measurements: int = Field(default=5)

    class Config:
        arbitrary_types_allowed = True
        allow_mutation = True

    def add_measurement(self, measurement: ResourceUsage) -> None:
        """Add a new measurement and maintain only the last max_measurements."""
        self.measurements.append(measurement)
        if len(self.measurements) > self.max_measurements:
            self.measurements.pop(0)

    def get_max_usage(self) -> Optional[ResourceUsage]:
        """Get the maximum resource usage across all measurements."""
        if not self.measurements:
            return None

        return ResourceUsage(
            cpu_cores=max(m.cpu_cores for m in self.measurements),
            ram_gb=max(m.ram_gb for m in self.measurements),
            disk_gb=max(m.disk_gb for m in self.measurements),
            memory_bandwidth_gbps=max(m.memory_bandwidth_gbps for m in self.measurements),
            network_bandwidth_gbps=max(m.network_bandwidth_gbps for m in self.measurements)
        )

class ResourceStatus(BaseModel):
    """Tracks the total and used resources in the system."""
    total_cpu_cores: Union[int, float] = Field(default=0)
    used_cpu_cores: Union[int, float] = Field(default=0)
    total_ram_gb: Union[int, float] = Field(default=0)
    used_ram_gb: Union[int, float] = Field(default=0)
    total_disk_gb: Union[int, float] = Field(default=0)
    used_disk_gb: Union[int, float] = Field(default=0)
    total_memory_bandwidth_gbps: Union[int, float] = Field(default=0)
    used_memory_bandwidth_gbps: Union[int, float] = Field(default=0)
    total_network_bandwidth_gbps: Union[int, float] = Field(default=0)
    used_network_bandwidth_gbps: Union[int, float] = Field(default=0)

    def has_sufficient_resources(self, required: ResourceUsage) -> bool:
        """Check if there are sufficient resources available."""
        return all([
            self.total_cpu_cores - self.used_cpu_cores >= required.cpu_cores,
            self.total_ram_gb - self.used_ram_gb >= required.ram_gb,
            self.total_disk_gb - self.used_disk_gb >= required.disk_gb,
            self.total_memory_bandwidth_gbps - self.used_memory_bandwidth_gbps >= required.memory_bandwidth_gbps,
            self.total_network_bandwidth_gbps - self.used_network_bandwidth_gbps >= required.network_bandwidth_gbps
        ])

    def get_available_resources(self) -> ResourceUsage:
        """Get the currently available resources."""
        return ResourceUsage(
            cpu_cores=self.total_cpu_cores - self.used_cpu_cores,
            ram_gb=self.total_ram_gb - self.used_ram_gb,
            disk_gb=self.total_disk_gb - self.used_disk_gb,
            memory_bandwidth_gbps=self.total_memory_bandwidth_gbps - self.used_memory_bandwidth_gbps,
            network_bandwidth_gbps=self.total_network_bandwidth_gbps - self.used_network_bandwidth_gbps
        )

    def update_used_resources(self, usage: ResourceUsage) -> None:
        """Update the used resources based on current usage."""
        self.used_cpu_cores = usage.cpu_cores
        self.used_ram_gb = usage.ram_gb
        self.used_disk_gb = usage.disk_gb
        self.used_memory_bandwidth_gbps = usage.memory_bandwidth_gbps
        self.used_network_bandwidth_gbps = usage.network_bandwidth_gbps