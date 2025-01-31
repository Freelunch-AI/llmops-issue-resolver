import unittest
import sys
import sys
sys.path.append('/workspace/src')
print(sys.path)
from unittest.mock import AsyncMock, MagicMock
from sandbox_toolkit.sdk.core.core import SandboxGroup, Sandbox, SandboxConfig

class TestSandboxGroup(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        from sandbox_toolkit.helpers.schema_models.internal_schemas import ComputeConfig, DatabaseConfig, ResourceUnit, Tools

        self.sandbox_config = SandboxConfig(
            compute_config=ComputeConfig(cpu=1, ram=1, disk=10, memory_bandwidth=10, networking_bandwith=100, unit=ResourceUnit.ABSOLUTE),
            database_config=DatabaseConfig(),
            tools=Tools()
        )
        self.orchestrator_client_mock = AsyncMock()
        self.infra_initializer_mock = MagicMock()
        self.sandbox_group = SandboxGroup(sandbox_config=self.sandbox_config)
        self.sandbox_group.orchestrator_client = self.orchestrator_client_mock
        self.sandbox_group.infra_initializer = self.infra_initializer_mock

    async def test_create_sandbox_async(self):
        sandbox_id = "test_sandbox_id"
        self.orchestrator_client_mock.create_sandbox.return_value = sandbox_id
        sandbox = await self.sandbox_group.create_sandbox("test_sandbox")
        self.assertIsInstance(sandbox, Sandbox)
        self.assertEqual(sandbox.sandbox_id, sandbox_id)
        self.assertEqual(len(self.sandbox_group.sandboxes), 1)
        self.assertIn("test_sandbox", self.sandbox_group.sandboxes)

async def test_start_group(self):
        await self.sandbox_group.start()
        self.infra_initializer_mock.start_infra.assert_called_once()


if __name__ == '__main__':
    unittest.main()