import datetime
import logging
import time

from logs.logging import logger
from schema_models.internal_schemas import SandboxStats


class StatsManager:
    def __init__(self):
        self._container_start_time = None
        self._successful_actions = 0
        self._failed_actions = 0

    def set_container_start_time(self):
        self._container_start_time = datetime.datetime.now()

    def increment_successful_actions(self):
        self._successful_actions += 1

    def increment_failed_actions(self):
        self._failed_actions += 1

    async def get_stats(self) -> SandboxStats:
        logger.info("Getting sandbox stats...")
        logger.debug("Inputs: None")

        if self._container_start_time is None:
            start_time = datetime.datetime.now()
        else:
            start_time = self._container_start_time
        
        uptime = time.time() - self._container_start_time.timestamp() if self._container_start_time else 0
        
        stats_data = {
            "sandbox_running_duration": uptime,
            "actions_sent_count": self._successful_actions + self._failed_actions,
            "start_time": start_time.isoformat(),
            "uptime": str(datetime.timedelta(seconds=uptime)),
            "total_actions_executed": self._successful_actions + self._failed_actions,
            "successful_actions": self._successful_actions,
            "failed_actions": self._failed_actions
        }
        
        logger.info("Sandbox stats retrieved successfully.")
        logger.debug(f"Outputs: {stats_data}")
        
        return SandboxStats(**stats_data)

stats_manager = StatsManager()
