import asyncio
import logging
from sandbox_toolkit.sdk.core.core import SandboxConfig, SandboxGroup, ActionExecutionRequest
from sandbox_toolkit.helpers.schema_models.schema import ResourceUnit, ComputeConfig, DatabaseConfig, DatabaseType, DatabaseAccessType, Tools
import sys
sys.path.append('.')
from tools.my_tool import greet
from sandbox_toolkit.logs.logging import setup_logging # Import setup_logging

logger = setup_logging() # Call setup_logging to configure logger

async def main():
    logger.debug("Starting manual test: test_user_tools.py") # Use logger.debug
    sandbox_config = SandboxConfig(
        compute_config=ComputeConfig(cpu=1, ram=1, disk=10, memory_bandwidth=10, networking_bandwith=100, unit=ResourceUnit.ABSOLUTE),
        database_config=DatabaseConfig(database_type=DatabaseType.VECTOR, access_type=DatabaseAccessType.READ_WRITE, namespaces=["default"]),
        tools=Tools(tools=[greet]) # Pass user-defined tool here
    )

    async with SandboxGroup(sandbox_config=sandbox_config) as sandbox_group:
        sandbox = await sandbox_group.create_sandbox("test_sandbox_with_tool")
        await sandbox_group.start_sandbox("test_sandbox_with_tool") # Corrected start_sandbox call

        actions = ActionExecutionRequest(actions={
            "greet_tool": {
                "function_call_explanation": "Greet user using user-defined tool",
                "args": {
                    "name": "Tester"
                }
            }
        })
        observations = await sandbox.send_actions(actions)
        print("Observations:", observations)

        await sandbox.end()

if __name__ == "__main__":
    asyncio.run(main())