import asyncio
import logging
from sandbox_toolkit.sdk.core.core import SandboxConfig, SandboxGroup, Sandbox, ComputeConfig, DatabaseConfig, ResourceUnit, ActionExecutionRequest

logging.basicConfig(level=logging.DEBUG)

async def main():
    logging.debug("Starting manual test: test_sandbox.py")
    sandbox_config = SandboxConfig(
        compute_config=ComputeConfig(cpu=1, ram=1, disk=10, memory_bandwith=10, networkng_bandwith=100, unit=ResourceUnit.ABSOLUTE),
        database_config=DatabaseConfig(),
        tools=None
    )

    async with SandboxGroup(sandbox_config=sandbox_config) as sandbox_group:
        sandbox = await sandbox_group.create_sandbox("test_sandbox")
        logging.debug(f"Sandbox created: {sandbox.sandbox_id}")
        await sandbox.start()
        logging.debug("Sandbox started.")

        actions = ActionExecutionRequest(actions={
            "execute_command": {
                "function_call_explanation": "List files in the sandbox",
                "args": {
                    "command": "ls -la"
                }
            }
        })
        observations = await sandbox.send_actions(actions)
        print("Observations:", observations)

        resource_usage = await sandbox.get_resource_usage()
        print("Resource Usage:", resource_usage)

        stats = await sandbox.get_stats()
        print("Stats:", stats)

        capabilities = await sandbox.get_tools_api_reference()
        print("Capabilities:", capabilities)

        history = await sandbox.get_history()
        print("History:", history)

        await sandbox.end()
        logging.debug("Sandbox ended.")

    logging.debug("SandboxGroup context finished.")

if __name__ == "__main__":
    asyncio.run(main())