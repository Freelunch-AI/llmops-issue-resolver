from pydantic import BaseModel
from typing import Dict, List


class ActionRequest(BaseModel):
    """Request model for sending actions to the sandbox."""
    actions: Dict[str, Dict]


class ObservationModel(BaseModel):
    """Model representing an observation from the sandbox execution."""
    stdout: str
    stderr: str
    terminal_still_running: bool


class ActionResponse(BaseModel):
    """Response model containing a list of observations from the sandbox."""
    observations: List[ObservationModel]