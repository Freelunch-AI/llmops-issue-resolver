from pathlib import Path
from typing import Dict, Optional, Union
import yaml
from pydantic import Field
from ...helpers.models import ServiceManagementConfig, DatabaseConfig, SandboxConfig
"""
Configuration management module for the Sandbox environment.

This module provides functionality to manage sandbox configurations through YAML files
or dictionaries. It supports the following configuration sections:

1. Service Management Configuration:
   - Service discovery settings
   - Health check parameters
   - Service lifecycle management

2. Database Configuration:
   - Connection parameters
   - Credentials
   - Pool settings

3. Sandbox Configuration:
   - Environment settings
   - Resource limits
   - Security policies

Typical usage:

    # Load configuration from YAML
    config = SandboxConfigManager.from_yaml('config.yaml')
    
    # Access configuration parameters
    db_host = config.database.host
    service_timeout = config.service_management.timeout
    
    # Modify and save configuration
    config.database.port = 5432
    config.to_yaml('updated_config.yaml')

The configuration file should be in YAML format with sections corresponding to
the different configuration classes (ServiceManagementConfig, DatabaseConfig,
and SandboxConfig).
"""


class SandboxConfigManager(SandboxConfig):
    @classmethod
    def from_yaml(cls, path: Union[str, Path]) -> "SandboxConfig":
        """Load sandbox configuration from a YAML file.

        Args:
            path: Path to the YAML configuration file. Can be a string or Path object.

        Returns:
            SandboxConfig: A configured instance with settings from the YAML file.

        Raises:
            FileNotFoundError: If the configuration file doesn't exist.
            yaml.YAMLError: If the YAML file is malformed.
            ValidationError: If the configuration data doesn't match the expected schema.
        """
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls(**data)

    @classmethod
    def from_dict(cls, data: Dict) -> "SandboxConfig":
        """Load sandbox configuration from a dictionary.

        Args:
            data: Dictionary containing configuration parameters structured according
                 to the expected schema with sections for service_management,
                 database, and general sandbox settings.

        Returns:
            SandboxConfig: A configured instance with the provided settings.

        Raises:
            ValidationError: If the configuration data doesn't match the expected schema.
        """
        return cls(**data)

    def to_yaml(self, path: Union[str, Path]) -> None:
        """Save the current configuration to a YAML file.

        Args:
            path: Destination path for the YAML file. Can be a string or Path object.

        Raises:
            PermissionError: If the process lacks permission to write to the specified path.
            OSError: If there's an error writing to the file.
        """
        with open(path, "w") as f:
            yaml.dump(self.dict(), f)