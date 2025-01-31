from enum import Enum
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, SecretStr, Field, constr, conint, confloat, \
    HttpUrl, validator
from sandbox_sdk.sdk.schema_models.resources import ComputeResources
from sandbox_sdk.helpers.models import AuthenticationConfig, ApiKeyInfo, SandboxAuthInfo

class DatabaseType(str, Enum):
    VECTOR = "vector"
    GRAPH = "graph"

class DatabaseAccessType(str, Enum):
    READ = "read"
    WRITE = "write"
    READ_WRITE = "read_write"

class DatabaseAccess(BaseModel):
    database_type: DatabaseType
    access_type: DatabaseAccessType
    namespaces: List[str] = Field(default_factory=list)

class ResourceUnit(str, Enum):
    ABSOLUTE = "absolute"
    RELATIVE = "relative"

class AttachedDatabases(BaseModel):
    vector_db: Optional[DatabaseAccess] = Field(
        default_factory=lambda: DatabaseAccess(
            database_type=DatabaseType.VECTOR,
            access_type=DatabaseAccessType.READ,
            namespaces=["default"]
        ),
        description="Vector database access configuration"
    )
    graph_db: Optional[DatabaseAccess] = Field(
        default_factory=lambda: DatabaseAccess(
            database_type=DatabaseType.GRAPH,
            access_type=DatabaseAccessType.READ,
            namespaces=["default"]
        ),
        description="Graph database access configuration"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "vector_db": {
                    "database_type": "vector",
                    "access_type": "read_write",
                    "namespaces": ["default", "custom"]
                },
                "graph_db": {
                    "database_type": "graph",
                    "access_type": "read",
                    "namespaces": ["default"]
                }
            }
        }

class AuthenticationResponse(BaseModel):
    """Response model for successful authentication."""
    auth_info: SandboxAuthInfo
    config: AuthenticationConfig

    class Config:
        json_schema_extra = {
            "example": {
                "auth_info": SandboxAuthInfo.Config.json_schema_extra["example"],
                "config": {
                    "public_key": "-----BEGIN PUBLIC KEY-----\n...",
                    "key_algorithm": "RSA",
                    "key_size": 2048
                }
            }
        }

class ActionObservation(BaseModel):
    stdout: str = ""
    stderr: str = ""
    terminal_still_running: bool = False

# SDK Operation Models
class SandboxCreateRequest(BaseModel):
    """Model for creating a new sandbox instance."""
    name: constr(min_length=1, max_length=64) = Field(..., description="Name of the sandbox")
    compute_resources: ComputeResources = Field(default_factory=ComputeResources)
    attached_databases: AttachedDatabases = Field(default_factory=AttachedDatabases)
    environment_variables: Dict[str, str] = Field(default_factory=dict)
    class Config:
        json_schema_extra = {
            "example": {
                "name": "data-processing-sandbox",
                "compute_resources": {
                    "cpu_cores": 2,
                    "ram_gb": 4,
                    "disk_gb": 20,
                    "memory_bandwidth_gbps": 10.0
                },
                "attached_databases": AttachedDatabases().dict(), 
                "environment_variables": {"DEBUG": "true"} 
            }
        }

class SandboxUpdateRequest(BaseModel):
    """Model for updating an existing sandbox configuration."""
    name: Optional[constr(min_length=1, max_length=64)] = None
    compute_resources: Optional[ComputeResources] = None
    attached_databases: Optional[AttachedDatabases] = None
    environment_variables: Optional[Dict[str, str]] = None

class ActionExecuteRequest(BaseModel):
    """Model for executing an action in a sandbox."""
    command: constr(min_length=1) = Field(..., description="Command to execute")
    working_directory: Optional[str] = Field(default="/", description="Working directory for command execution")
    environment_variables: Dict[str, str] = Field(default_factory=dict)
    timeout_seconds: Optional[conint(ge=1)] = Field(default=3600, description="Timeout in seconds")

    class Config:
        json_schema_extra = {
            "example": {
                "command": "python process_data.py",
                "working_directory": "/app",
                "environment_variables": {"DEBUG": "true"},
                "timeout_seconds": 3600
            }
        }

class FileUploadRequest(BaseModel):
    """Model for file upload operations."""
    source_path: str = Field(..., description="Local path of the file to upload")
    destination_path: str = Field(..., description="Destination path in the sandbox")
    overwrite: bool = Field(default=False, description="Whether to overwrite existing files")

    @validator('source_path', 'destination_path')
    def validate_paths(cls, v):
        if not v or v.isspace():
            raise ValueError("Path cannot be empty")
        return v

class FileDownloadRequest(BaseModel):
    """Model for file download operations."""
    source_path: str = Field(..., description="Path of the file in the sandbox")
    destination_path: str = Field(..., description="Local destination path")
    overwrite: bool = Field(default=False, description="Whether to overwrite existing files")

    @validator('source_path', 'destination_path')
    def validate_paths(cls, v):
        if not v or v.isspace():
            raise ValueError("Path cannot be empty")
        return v

class DatabaseQueryRequest(BaseModel):
    """Model for database query operations."""
    database_type: DatabaseType
    namespace: str = Field(..., description="Database namespace to query")
    query: str = Field(..., description="Query string")
    parameters: Dict[str, Union[str, int, float, bool, List, Dict]] = Field(
        default_factory=dict,
        description="Query parameters"
    )

    @validator('namespace')
    def validate_namespace(cls, v):
        if not v or v.isspace():
            raise ValueError("Namespace cannot be empty")
        return v

    @validator('query')
    def validate_query(cls, v):
        if not v or v.isspace():
            raise ValueError("Query cannot be empty")
        return v