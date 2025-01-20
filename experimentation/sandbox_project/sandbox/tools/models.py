from typing import Dict, List, Optional, Union
from pathlib import Path
from pydantic import BaseModel, Field, HttpUrl, validator
import os

# Filesystem Tools Models
class FilePathModel(BaseModel):
    path: str
    
    @validator("path")
    def validate_path(cls, v):
        if not v:
            raise ValueError("Path cannot be empty")
        return v

class FileContentModel(FilePathModel):
    content: str = Field(..., description="Content to write to the file")

class FileMoveModel(BaseModel):
    src: str
    dst: str
    
    @validator("src", "dst")
    def validate_paths(cls, v):
        if not v:
            raise ValueError("Paths cannot be empty")
        return v

class DirectoryListModel(BaseModel):
    path: str
    pattern: Optional[str] = None

# Terminal Tools Models
class CommandModel(BaseModel):
    command: str = Field(..., description="Command to execute")
    timeout: Optional[float] = Field(None, description="Command timeout in seconds")

class PackageModel(BaseModel):
    package: str = Field(..., description="Package name and version (optional)")
    extras: Optional[List[str]] = Field(default_factory=list)

class PythonScriptModel(BaseModel):
    script_path: str
    args: Optional[List[str]] = Field(default_factory=list)

# Web Tools Models
class WebsiteModel(BaseModel):
    url: HttpUrl
    max_depth: Optional[int] = Field(3, ge=1)
    timeout: Optional[float] = Field(30.0, gt=0)

class WebSearchModel(BaseModel):
    query: str
    api_key: str
    max_results: Optional[int] = Field(10, ge=1, le=100)

class WebScrapingModel(BaseModel):
    url: HttpUrl
    selectors: Dict[str, str]
    wait_time: Optional[float] = Field(5.0, ge=0)

# Database Tools Models
class VectorCollectionModel(BaseModel):
    collection_name: str
    vector_size: int = Field(..., gt=0)
    distance: str = Field("cosine", regex="^(cosine|euclidean|dot)$")

class VectorPointModel(BaseModel):
    collection_name: str
    points: List[Dict[str, Union[List[float], Dict]]]
    batch_size: Optional[int] = Field(100, gt=0)

class VectorSearchModel(BaseModel):
    collection_name: str
    query_vector: List[float]
    limit: Optional[int] = Field(10, gt=0)
    filter: Optional[Dict] = None

class GraphQueryModel(BaseModel):
    query: str
    parameters: Optional[Dict] = Field(default_factory=dict)

class GraphNodeModel(BaseModel):
    label: str
    properties: Dict[str, Any]

class GraphRelationshipModel(BaseModel):
    from_node_id: int
    to_node_id: int
    relationship_type: str
    properties: Optional[Dict] = Field(default_factory=dict)