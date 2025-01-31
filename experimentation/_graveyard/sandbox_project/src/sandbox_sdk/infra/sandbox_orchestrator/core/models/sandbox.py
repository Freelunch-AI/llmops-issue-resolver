from typing import Dict, List, Optional, Union
from pathlib import Path
from pydantic import BaseModel, Field, field_validator, validator

class ResourceConfig(BaseModel):
    """Configuration for sandbox compute resources."""
    cpu_cores: Union[int, float]
    ram_gb: Union[int, float]
    disk_gb: Union[int, float]
    memory_bandwidth_gbps: Union[int, float]
    unit: str = Field("absolute", pattern="^(absolute|relative)$")

    @field_validator("cpu_cores", "ram_gb", "disk_gb", "memory_bandwidth_gbps")
    def validate_positive(cls, v):
        if v <= 0:
            raise ValueError("Resource values must be positive")
        return v

class SecurityConfig(BaseModel):
    """Container-level security configuration for sandboxes."""
    max_processes: Optional[int] = None
    allowed_syscalls: Optional[List[str]] = None
    read_only_root: bool = True
    drop_capabilities: List[str] = Field(
        default_factory=lambda: [
            "NET_ADMIN",
            "SYS_ADMIN",
            "SYS_PTRACE"
        ]
    )

class SandboxConfig(BaseModel):
    """Configuration for a sandbox instance."""
    id: str
    resources: ResourceConfig
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    environment: Dict[str, str] = Field(default_factory=dict)
    tools: List[str]
    working_directory: Path = Field(default=Path("/workspace"))
    
    class Config:
        arbitrary_types_allowed = True