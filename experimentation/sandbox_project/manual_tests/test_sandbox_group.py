import asyncio
import logging

from sandbox_toolkit.helpers.schema_models.internal_schemas import (
    ComputeConfig,
    DatabaseConfig,
    ResourceUnit,
    Tools,
)
from sandbox_toolkit.logs.logging import setup_logging
from sandbox_toolkit.sdk.core.core import SandboxConfig, SandboxGroup

logger = setup_logging()

async def main():
    logger.debug("Starting manual test: test_sandbox_group.py")
    sandbox_config = SandboxConfig(
        compute_config=ComputeConfig(cpu=1, ram=1, disk=10, memory_bandwidth=10, networking_bandwith=100, unit=ResourceUnit.ABSOLUTE),
        database_config=DatabaseConfig(),
        tools=Tools()
    )

    async with SandboxGroup(sandbox_config=sandbox_config) as sandbox_group:
        logger.debug("SandboxGroup started.")

        sandbox1 = await sandbox_group.create_sandbox(sandbox_name="sandbox1")
        logger.debug(f"Sandbox 1 created: {sandbox1.sandbox_id}")
        sandbox2 = await sandbox_group.create_sandbox(sandbox_name="sandbox2")
        logger.debug(f"Sandbox 2 created: {sandbox2.sandbox_id}")

        await sandbox_group.start_sandbox(sandbox_name="sandbox1")
        logger.debug("Sandbox 1 started.")
        await sandbox_group.start_sandbox(sandbox_name="sandbox2")
        logger.debug("Sandbox 2 started.")

        resource_stats = await sandbox_group.get_resource_stats()
        logger.debug(f"Sandbox Group Resource Stats: {resource_stats}")

        

        await sandbox_group.end_sandbox(sandbox_name="sandbox1")
        logger.debug("Sandbox 1 ended.")
        await sandbox_group.end_sandbox(sandbox_name="sandbox2")
        logger.debug("Sandbox 2 ended.")

    logger.debug("SandboxGroup context finished.")

if __name__ == "__main__":
    asyncio.run(main())
