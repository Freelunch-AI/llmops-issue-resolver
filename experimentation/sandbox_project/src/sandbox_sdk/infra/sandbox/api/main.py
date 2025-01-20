from fastapi import FastAPI, HTTPException
from typing import List
from .models import ActionRequest, ObservationModel, ActionResponse
import logging
from pathlib import Path

from ..core.executor import ActionExecutor
from ..core.terminal import TerminalOutput

app = FastAPI(title="Sandbox API")
logger = logging.getLogger(__name__)
# Create global executor
executor = ActionExecutor()

@app.post("/execute", response_model=ActionResponse)
async def execute_actions(request: ActionRequest):
    """Execute a sequence of actions in the sandbox."""
    try:
        # Execute actions
        results = await executor.execute_actions(request.actions)
        
        # Convert results to response model
        observations = [
            ObservationModel(
                stdout=result.stdout,
                stderr=result.stderr,
                terminal_still_running=result.still_running
            )
            for result in results
        ]
        
        return ActionResponse(observations=observations)
        
    except Exception as e:
        logger.error(f"Error executing actions: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error executing actions: {str(e)}"
        )



@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources when shutting down."""
    executor.close()