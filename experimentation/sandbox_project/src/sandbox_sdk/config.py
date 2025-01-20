from pathlib import Path
from typing import Dict, Optional, Union
import yaml
from pydantic import Field
from .models import ServiceManagementConfig, DatabaseConfig, SandboxConfig

class SandboxConfigManager(SandboxConfig):
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