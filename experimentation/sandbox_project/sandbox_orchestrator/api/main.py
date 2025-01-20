from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime
import logging
from pathlib import Path

from core.sandbox_manager import SandboxManager
from core.models.database import DatabasesConfig
from core.models.sandbox import SandboxConfig, ResourceConfig, SecurityConfig

app = FastAPI(title="Sandbox Orchestrator")
logger = logging.getLogger(__name__)

# Create global sandbox manager
sandbox_manager = SandboxManager()

class SandboxGroupStartRequest(BaseModel):
    vector_db_config: Path
    graph_db_config: Path

class SandboxGroupStartResponse(BaseModel):
    status: str
    databases: Dict[str, str]  # type -> url

class SandboxCreateRequest(BaseModel):
    id: str
    tools: List[str]
    resources: ResourceConfig
    security: Optional[SecurityConfig] = None
    environment: Dict[str, str] = {}

class SandboxCreateResponse(BaseModel):
    sandbox_url: str

class SandboxStopRequest(BaseModel):
    id: str

class StatusResponse(BaseModel):
    status: str

class ResourceStatusResponse(BaseModel):
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_usage: float
    cpu_available: float
    memory_available: float
    disk_available: float
    network_available: float

class ResourceAdjustmentRequest(BaseModel):
    x_percentage: float = 1.3

class SandboxStatusResponse(BaseModel):
    id: str
    name: str
    endpoint: str
    status: str


@app.post("/group/start", response_model=SandboxGroupStartResponse)
async def start_sandbox_group(request: SandboxGroupStartRequest):
    """Start the sandbox group and initialize databases."""
    try:
        # Load database configs
        db_config = DatabasesConfig.from_yaml(
            request.vector_db_config,
            request.graph_db_config
        )
        
        # Start databases
        await sandbox_manager.start_databases(db_config)
        
        return SandboxGroupStartResponse(
            status="started",
            databases={
                "vector": f"http://{db_config.vector_db.host}:{db_config.vector_db.port}",
                "graph": f"bolt://{db_config.graph_db.host}:{db_config.graph_db.port}"
            }
        )
    except Exception as e:
        logger.error(f"Error starting sandbox group: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/sandbox/start", response_model=SandboxCreateResponse)
async def create_sandbox(request: SandboxCreateRequest):
    """Create and start a new sandbox."""
    try:
        # Create sandbox config
        config = SandboxConfig(
            id=request.id,
            resources=request.resources,
            security=request.security or SecurityConfig(),
            environment=request.environment,
            tools=request.tools
        )
        
        # Create sandbox
        sandbox_url = await sandbox_manager.create_sandbox(
            config.id,
            config.tools,
            config.resources.dict(),
            config.environment
        )
        
        return SandboxCreateResponse(sandbox_url=sandbox_url)
    except Exception as e:
        logger.error(f"Error creating sandbox: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/sandbox/stop", response_model=StatusResponse)
async def stop_sandbox(request: SandboxStopRequest):
    """Stop and remove a sandbox."""
    try:
        await sandbox_manager.stop_sandbox(request.id)
        return StatusResponse(status="stopped")
    except Exception as e:
        logger.error(f"Error stopping sandbox: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/group/stop", response_model=StatusResponse)
async def stop_sandbox_group():
    """Stop all sandboxes and cleanup resources."""
    try:
        await sandbox_manager.cleanup()
        return StatusResponse(status="stopped")
    except Exception as e:
        logger.error(f"Error stopping sandbox group: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sandboxes/status", response_model=List[SandboxStatusResponse])
async def get_sandboxes_status():
    """Get status of all active sandboxes."""
    try:
        active_sandboxes = []
        for sandbox_id, sandbox in sandbox_manager.sandboxes.items():
            status = SandboxStatusResponse(
                id=sandbox_id,
                name=f"Sandbox {sandbox_id}",
                endpoint=f"http://{sandbox_id}:8000",
                status="active",
                last_activity=datetime.now()  # In a real implementation, this would come from the sandbox
            )
            active_sandboxes.append(status)
        return active_sandboxes
    except Exception as e:
        logger.error(f"Error getting sandbox statuses: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/resources", response_model=ResourceStatusResponse)
async def get_resources():
    """Get current resource status including usage and availability."""
    try:
        resource_status = await sandbox_manager.get_resource_status()
        return ResourceStatusResponse(**resource_status)
    except Exception as e:
        logger.error(f"Error getting resource status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/sandboxes/adjust_resources", response_model=StatusResponse)
async def adjust_resources(request: ResourceAdjustmentRequest):
    """Adjust resource limits for all running sandboxes based on their usage."""
    try:
        await sandbox_manager.adjust_sandbox_resources(request.x_percentage)
        return StatusResponse(status="resources adjusted")
    except Exception as e:
        logger.error(f"Error adjusting resource limits: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources when shutting down."""
    await sandbox_manager.cleanup()