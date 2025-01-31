from typing import Dict, List, Optional, Union
from pathlib import Path
from pydantic import BaseModel, Field, field_validator
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

class VectorDBConfig(DatabaseConfig):
    """Configuration for vector database."""
    collections: List[Dict[str, Union[str, int, List]]] = Field(default_factory=list)
    initial_data: Optional[List[Dict]] = Field(default_factory=list)

    @field_validator("collections")
    @classmethod
    def validate_collections(cls, v):
        for collection in v:
            if "name" not in collection:
                raise ValueError("Each collection must have a 'name'")
        return v

    @field_validator("collections")
    @classmethod
    def validate_collections(cls, v):
        for collection in v:
            if "name" not in collection or "vector_size" not in collection:
                raise ValueError("Each collection must have 'name' and 'vector_size'")
        return v

class GraphDBConfig(DatabaseConfig):
    """Configuration for graph database."""
    initial_data: Dict[str, List[Dict]] = Field(
        default_factory=lambda: {"nodes": [], "relationships": []}
    )
    backup: Dict[str, Union[bool, str, int]] = Field(
        default_factory=lambda: {
            "enabled": False,
            "schedule": "0 0 * * *",
            "retention_days": 7
        }
    )

    @field_validator("initial_data")
    @classmethod
    def validate_initial_data(cls, v):
        if "nodes" not in v or "relationships" not in v:
            raise ValueError("initial_data must contain 'nodes' and 'relationships'")
        return v

class DatabasesConfig(BaseModel):
    """Combined configuration for all databases."""
    vector_db: VectorDBConfig
    graph_db: GraphDBConfig

    @classmethod
    def from_yaml(cls, vector_config_path: Path, graph_config_path: Path) -> "DatabasesConfig":
        """Load configuration from YAML files."""
        with open(vector_config_path) as f:
            vector_config = yaml.safe_load(f)
        
        with open(graph_config_path) as f:
            graph_config = yaml.safe_load(f)
        
        return cls(
            vector_db=VectorDBConfig(**vector_config),
            graph_db=GraphDBConfig(**graph_config)
        )