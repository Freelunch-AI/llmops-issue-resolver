import asyncio
import logging
import unittest # Import unittest
from sandbox_toolkit.sdk.core.core import SandboxConfig, SandboxGroup, Sandbox, ComputeConfig, DatabaseConfig, ResourceUnit, ActionExecutionRequest

logging.basicConfig(level=logging.DEBUG)

class TestSandbox(unittest.TestCase): # Create a TestCase class

    async def asyncSetUp(self): # Use asyncSetUp for async setup
        self.sandbox_config = SandboxConfig(
            compute_config=ComputeConfig(cpu=1, ram=1, disk=10, memory_bandwith=10, networkng_bandwith=100, unit=ResourceUnit.ABSOLUTE),
            database_config=DatabaseConfig(),
            tools=None
        )
        self.sandbox_group = SandboxGroup(sandbox_config=self.sandbox_config)
        await self.sandbox_group.start()
        self.sandbox = await self.sandbox_group.create_sandbox("test_sandbox")
        await self.sandbox.start()

    async def asyncTearDown(self): # Use asyncTearDown for async teardown
        await self.sandbox.end()
        await self.sandbox_group.end_group()

    async def test_send_actions_execute_command(self): # Add unit test method for send_actions
        actions = ActionExecutionRequest(actions={
            "execute_command": {
                "function_call_explanation": "List files in the sandbox",
                "args": {
                    "command": "ls -la"
                }
            }
        })
        observations = await self.sandbox.send_actions(actions)
        self.assertIsNotNone(observations) # Add assertion to check if observations is not None
        self.assertGreater(len(observations), 0) # Add assertion to check if observations is not empty
        self.assertEqual(observations[0].function_name, "execute_command") # Add assertion to check function_name

    def setUp(self):
        asyncio.run(self.asyncSetUp())

    def tearDown(self):
        asyncio.run(self.asyncTearDown())

    def test_send_actions_execute_command_sync(self): # Wrapper for async test
        asyncio.run(self.test_send_actions_execute_command())

if __name__ == "__main__":
    unittest.main()