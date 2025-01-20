from typing import Dict, Optional, Union
from pydantic import BaseModel, Field

class DatabaseConfig(BaseModel):
    """Configuration for database connections."""
    host: str = Field(default="localhost", description="Database host address")
    port: int = Field(default=5432, description="Database port number")
    username: str = Field(description="Database username")
    password: str = Field(description="Database password")
    database_name: str = Field(description="Name of the database")

class ServiceManagementConfig(BaseModel):
    """Configuration for service management."""
    service_name: str = Field(description="Name of the service")
    port: int = Field(description="Port number for the service")
    host: str = Field(default="localhost", description="Host address for the service")
    debug_mode: bool = Field(default=False, description="Enable debug mode")

class SandboxConfig(BaseModel):
    """Main configuration class for the sandbox environment."""
    database: DatabaseConfig = Field(description="Database configuration settings")
    service: ServiceManagementConfig = Field(description="Service management configuration")
    environment: str = Field(default="development", description="Environment name")
    log_level: str = Field(default="INFO", description="Logging level")
    additional_settings: Optional[Dict] = Field(default=None, description="Additional configuration settings")