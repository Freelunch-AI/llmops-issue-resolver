from fastapi import FastAPI, HTTPException
from typing import List
from sandbox_toolkit.infra.sandbox_base.models import ActionRequest, ObservationModel, ActionResponse
import logging
from pathlib import Path


from sandbox_toolkit.infra.sandbox_base.executor import ActionExecutor



app = FastAPI(title="Sandbox API")
logger = logging.getLogger(__name__)
# Create global executor
executor = ActionExecutor()

@app.post("/actions", response_model=ActionResponse) # Changed endpoint to /actions
async def execute_actions(request: ActionRequest):
    """Execute a sequence of actions in the sandbox."""
    try:
        # Execute actions
        results = await executor.execute_actions(request.actions["actions"]) # Pass actions dict to executor
        
        # Convert results to response model
        observations = [
            ObservationModel(
                stdout=result.terminal_output, # Use Observation model from schema
                stderr="", # Assuming no stderr for now in simulation
                terminal_still_running=False # Assuming process finishes immediately in simulation
            )
            for function_name, result in results.items()
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