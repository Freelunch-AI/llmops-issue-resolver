from pathlib import Path
from typing import Dict, Optional, Union
import yaml
from pydantic import BaseModel, Field

class DatabaseConfig(BaseModel):
    host: str
    port: int
    credentials: Dict[str, str] = Field(default_factory=dict)

class SandboxConfig(BaseModel):
    orchestrator_url: str = "http://localhost:8000"
    default_compute_resources: Dict[str, Union[int, float, str]]
    database_configs: Dict[str, DatabaseConfig]
    tools_directory: Optional[Path] = None
    log_level: str = "INFO"
    log_file: Optional[str] = None

    @classmethod
    def from_yaml(cls, path: Union[str, Path]) -> "SandboxConfig":
        """Load configuration from a YAML file."""
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls(**data)

    @classmethod
    def from_dict(cls, data: Dict) -> "SandboxConfig":
        """Load configuration from a dictionary."""
        return cls(**data)

    def to_yaml(self, path: Union[str, Path]) -> None:
        """Save configuration to a YAML file."""
        with open(path, "w") as f:
            yaml.dump(self.dict(), f)