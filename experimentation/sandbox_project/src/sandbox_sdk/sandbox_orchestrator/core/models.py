from typing import Dict, List, Optional, Union, Deque
from collections import deque
from pydantic import BaseModel, Field, validator, confloat, conint
from pathlib import Path
import yaml

class DatabaseConfig(BaseModel):
    """Base configuration for databases."""
    host: str
    port: int
    credentials: Dict[str, str]
    security: Dict[str, Union[bool, str]] = Field(
        default_factory=lambda: {
            "ssl_enabled": False,
            "ssl_cert_path": "",
            "ssl_key_path": ""
        }
    )
    performance: Dict[str, Union[int, float]] = Field(
        default_factory=dict
    )
    initial_data: Optional[Path] = None

class VectorDBConfig(DatabaseConfig):
    collections: List[Dict[str, Union[str, int, List]]]

class GraphDBConfig(DatabaseConfig):
    initial_nodes: Optional[List[Dict]] = Field(default_factory=list)
    initial_relationships: Optional[List[Dict]] = Field(default_factory=list)

class DatabasesConfig(BaseModel):
    """Combined configuration for all databases."""
    vector_db: VectorDBConfig
    graph_db: GraphDBConfig
    
class ResourceError(Exception):
    """Exception raised for resource allocation and validation errors."""
    pass
class ResourceStatus(BaseModel):
    """Model for tracking resource usage and limits."""
    cpu_cores: confloat(gt=0) = Field(default=0.0, description="Number of CPU cores")
    ram_gb: confloat(gt=0) = Field(default=0.0, description="RAM in gigabytes")
    network_bandwidth_mbps: confloat(gt=0) = Field(default=0.0, description="Network bandwidth in Mbps")
    disk_io_mbps: confloat(gt=0) = Field(default=0.0, description="Disk I/O in Mbps")

    @validator('*')
    def validate_positive(cls, v):
        if v < 0:
            raise ResourceError("Resource values must be positive")
        return v

    def has_sufficient(self, required: 'ResourceStatus') -> bool:
        """Check if current resources are sufficient for the required amount."""
        return all([
            self.cpu_cores >= required.cpu_cores,
            self.ram_gb >= required.ram_gb,
            self.network_bandwidth_mbps >= required.network_bandwidth_mbps,
            self.disk_io_mbps >= required.disk_io_mbps
        ])

    def add(self, other: 'ResourceStatus') -> None:
        """Add resource values from another ResourceStatus object."""
        self.cpu_cores += other.cpu_cores
        self.ram_gb += other.ram_gb
        self.network_bandwidth_mbps += other.network_bandwidth_mbps
        self.disk_io_mbps += other.disk_io_mbps

    def subtract(self, other: 'ResourceStatus') -> None:
        """Subtract resource values from another ResourceStatus object."""
        self.cpu_cores = max(0, self.cpu_cores - other.cpu_cores)
        self.ram_gb = max(0, self.ram_gb - other.ram_gb)
        self.network_bandwidth_mbps = max(0, self.network_bandwidth_mbps - other.network_bandwidth_mbps)
        self.disk_io_mbps = max(0, self.disk_io_mbps - other.disk_io_mbps)

class ResourceUsageHistory:
    """Track resource usage history with a fixed-size deque."""
    def __init__(self, max_history: int = 100):
        self.measurements: Deque[ResourceStatus] = deque(maxlen=max_history)

    def add_measurement(self, usage: ResourceStatus) -> None:
        """Add a new resource usage measurement."""
        self.measurements.append(usage)

    def get_max_usage(self) -> ResourceStatus:
        """Get the maximum resource usage across all measurements."""
        if not self.measurements:
            return ResourceStatus()

        max_usage = ResourceStatus(
            cpu_cores=max(m.cpu_cores for m in self.measurements),
            ram_gb=max(m.ram_gb for m in self.measurements),
            network_bandwidth_mbps=max(m.network_bandwidth_mbps for m in self.measurements),
            disk_io_mbps=max(m.disk_io_mbps for m in self.measurements)
        )
        return max_usage

    def get_average_usage(self) -> ResourceStatus:
        """Get the average resource usage across all measurements."""
        if not self.measurements:
            return ResourceStatus()

        count = len(self.measurements)
        total = ResourceStatus()
        for measurement in self.measurements:
            total.add(measurement)

        avg_usage = ResourceStatus(
            cpu_cores=total.cpu_cores / count,
            ram_gb=total.ram_gb / count,
            network_bandwidth_mbps=total.network_bandwidth_mbps / count,
            disk_io_mbps=total.disk_io_mbps / count
        )
        return avg_usage

    @classmethod
    def from_yaml(cls, path: Union[str, Path]) -> "DatabasesConfig":
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls(**data)