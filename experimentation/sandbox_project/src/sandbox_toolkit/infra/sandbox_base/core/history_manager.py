import logging
from typing import List

from schema_models.internal_schemas import ActionsObservationsPair, Observation

logger = logging.getLogger(__name__)

async def get_history() -> List[ActionsObservationsPair]:
    logger.info("Getting sandbox history...")
    logger.debug("Inputs: None")

    # Dummy data for now
    history_data = [
        ActionsObservationsPair(
            actions={"action1": {"args": {"arg1": "value1"}}},
            observations=[Observation(function_name="action1", terminal_output="Action 1 output", process_still_running=False)]
        ),
        ActionsObservationsPair(
            actions={"action2": {"args": {"arg2": "value2"}}},
            observations=[Observation(function_name="action2", terminal_output="Action 2 output", process_still_running=False)]
        )
    ]
    
    logger.info("Sandbox history retrieved successfully.")
    logger.debug(f"Outputs: {history_data}")
    
    return history_data
