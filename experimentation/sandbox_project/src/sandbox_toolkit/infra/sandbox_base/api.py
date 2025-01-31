import io
import tarfile
from pathlib import Path
from typing import List

from core.executor import ActionExecutor
from core.history_manager import get_history
from core.resource_manager import get_resource_usage
from core.stats_manager import (
    get_stats,
    stats_manager,
)
from core.tools_manager import get_tools
from fastapi import FastAPI, HTTPException
from logs.logging import logger

from sandbox_toolkit.helpers.schema_models.internal_schemas import (
    ActionsObservationsPair,
    Compute,
    SandboxStats,
    SandboxTools,
)
from sandbox_toolkit.helpers.schema_models.networking_schemas import (
    Observation,
    SendActionsRequest,
    SendActionsResponse,
)

app = FastAPI(title="Sandbox API")
# Create global executor
executor = ActionExecutor()

@app.post("/actions", response_model=SendActionsResponse)
async def execute_actions(request: SendActionsRequest):
    try:
        actions_dict = request.actions["actions"]
        file_content = request.file_content

        # Handle file content for store_directory_of_files action
        if file_content and "store_directory_of_files" in actions_dict:

            knowledge_files_dir = Path("/knowledge_files")
            knowledge_files_dir.mkdir(parents=True, exist_ok=True)
            with io.BytesIO(file_content) as byte_stream:
                with tarfile.open(fileobj=byte_stream, mode='r:gz') as tar:
                    tar.extractall(knowledge_files_dir)

        # Execute actions
        results = await executor.execute_actions(actions_dict) # Pass actions dict to executor
        
        # Convert results to response model
        observations = [
            Observation(
                function_name=function_name, # Use Observation model from schema
                function_output=result.function_output, # Use Observation model from schema, use result.terminal_output
                process_still_running=False # Assuming process finishes immediately in simulation
            )
            for function_name, result in results.items()
        ]
        
        return SendActionsResponse(observations=observations)
        
    except Exception as e:
        logger.error(f"Error executing actions: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error executing actions: {str(e)}"
        )

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.on_event("startup")
async def startup_event():
    stats_manager.set_container_start_time()

@app.post("/get_tools", response_model=SandboxTools)
async def get_available_tools():
    try:
        tools = await get_tools()
        return tools
    except Exception as e:
        logger.error(f"Error getting tools: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting tools: {str(e)}"
        )

@app.post("/get_resource_usage", response_model=Compute)
async def get_sandbox_resource_usage():
    try:
        resource_usage = await get_resource_usage()
        return resource_usage
    except Exception as e:
        logger.error(f"Error getting resource usage: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting resource usage: {str(e)}"
        )

@app.post("/get_stats", response_model=SandboxStats)
async def get_sandbox_stats():
    try:
        stats = await get_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting stats: {str(e)}"
        )

@app.post("/get_history", response_model=List[ActionsObservationsPair])
async def get_sandbox_history():
    try:
        history = await get_history()
        return history
    except Exception as e:
        logger.error(f"Error getting history: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting history: {str(e)}"
        )
