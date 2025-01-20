from pydantic import BaseModel
from typing import Dict, List


class ActionRequest(BaseModel):
    actions: Dict[str, Dict]


class ObservationModel(BaseModel):
    stdout: str
    stderr: str
    terminal_still_running: bool


class ActionResponse(BaseModel):
    observations: List[ObservationModel]