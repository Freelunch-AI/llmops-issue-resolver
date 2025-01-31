"""Sandbox SDK Core components."""
import logging
from typing import List, Optional, Union, Callable, Dict
from pathlib import Path
from sandbox_toolkit.helpers.schema_models.schema import SandboxConfig, ActionExecutionRequest, Observation, ActionsObservationsPair, SandboxResourceUsage, SandboxStats, ComputeResourceStats, ToolAPIReference, SandboxCapabilities, TotalComputeResourceStats, SandboxComputeResourceStats
from sandbox_toolkit.helpers.exceptions.exceptions import SandboxError
from sandbox_toolkit.sdk.infra_init.infra_init import InfraInitializer
from sandbox_toolkit.sdk.orchestrator_communication.orchestrator_communication import OrchestratorClient
from sandbox_toolkit.sdk.sandbox_comunication.sandbox_communication import SandboxClient

logging.basicConfig(level=logging.DEBUG)

ORCHESTRATOR_URL = "http://localhost:8000" # TODO: Make configurable

class SandboxGroup:
    """Manages a group of sandboxes."""
    def __init__(self, sandbox_config: SandboxConfig, tools: Optional[Union[List[Callable], List[Path]]] = None):
        """Initializes a SandboxGroup."""
        self.sandbox_config = sandbox_config
        self.tools = tools
        self.sandboxes = {}
        self.infra_initializer = InfraInitializer()
        self.orchestrator_client = OrchestratorClient(ORCHESTRATOR_URL)
        self.infra_started = False

    async def start(self):
        """Starts the infrastructure if it's not already started."""
        logging.debug("SandboxGroup start called") # More concise logging
        if not self.infra_started:
            self.infra_initializer.start_infra()
            self.infra_started = True
        logging.debug("SandboxGroup start finished") # More concise logging

    async def create_sandbox(self, sandbox_name: str) -> "Sandbox":
        """Creates a new sandbox in the group."""
        logging.debug(f"SandboxGroup.create_sandbox called with sandbox_name: {sandbox_name}") # More concise logging
        logging.debug(f"SandboxGroup.create_sandbox - infra_started: {self.infra_started}")
        if not self.infra_started:
            await self.start()
        logging.debug("SandboxGroup create_sandbox - Creating sandbox via orchestrator client...") # More concise logging
        sandbox_id = await self.orchestrator_client.create_sandbox(self.sandbox_config)
        sandbox = Sandbox(sandbox_id, self)
        self.sandboxes[sandbox_name] = sandbox
        return sandbox

    async def get_sandbox(self, sandbox_id: str) -> "Sandbox":
        """Returns a sandbox from the group by its ID."""
        if sandbox_id not in self.sandboxes:
            raise SandboxError(f"Sandbox with id '{sandbox_id}' not found in this group.")
        return self.sandboxes[sandbox_id]

    async def start_sandbox(self, sandbox_id: str):
        """Starts a specific sandbox in the group."""
        logging.debug(f"SandboxGroup start_sandbox called: {sandbox_id}") # More concise logging
        if sandbox_id not in self.sandboxes:
            raise SandboxError(f"Sandbox with id '{sandbox_id}' not found in this group.")
        await self.orchestrator_client.start_sandbox(sandbox_id)

    async def send_actions(self, sandbox_id: str, actions: ActionExecutionRequest) -> List[Observation]:
        """Sends actions to a specific sandbox in the group."""
        sandbox = await self.get_sandbox(sandbox_id)
        return await sandbox.send_actions(actions)

    async def end_sandbox(self, sandbox_id: str):
        """Stops and removes a specific sandbox from the group."""
        logging.debug(f"SandboxGroup end_sandbox called: {sandbox_id}") # More concise logging
        if sandbox_id not in self.sandboxes:
            raise SandboxError(f"Sandbox with id '{sandbox_id}' not found in this group.")
        await self.orchestrator_client.stop_sandbox(sandbox_id)
        del self.sandboxes[sandbox_id]

    async def end_group(self):
        """Stops and removes all sandboxes in the group and stops the infrastructure."""
        logging.debug("SandboxGroup end_group called") # More concise logging
        for sandbox_id in list(self.sandboxes.keys()): # Iterate over a copy of keys to avoid RuntimeError during deletion
            await self.end_sandbox(sandbox_id)
        if self.infra_started:
            self.infra_initializer.stop_infra()
            self.infra_started = False
        logging.debug("SandboxGroup end_group finished") # More concise logging

    async def get_sandbox_resource_stats(self, sandbox_id: str) -> SandboxComputeResourceStats: # Renamed from get_compute_resource_stats
        """Returns the compute resource stats for a specific sandbox in the group."""
        if sandbox_id not in self.sandboxes:
            raise SandboxError(f"Sandbox with id '{sandbox_id}' not found in this group.")
        return await self.orchestrator_client.get_sandbox_resource_usage(sandbox_id) # Call get_sandbox_resource_usage

    async def get_total_resource_stats(self) -> TotalComputeResourceStats:
        """Returns the total compute resource stats for the machine."""
        return await self.orchestrator_client.get_total_resource_stats()

    async def get_resource_stats(self) -> Dict[str, SandboxComputeResourceStats]:
        """Returns the resource stats for all sandboxes in the group."""
        resource_stats = {}
        for sandbox_id in self.sandboxes:
            resource_stats[sandbox_id] = await self.get_sandbox_resource_stats(sandbox_id)
        return resource_stats

    async def __aenter__(self):
        """Asynchronous context manager enter method."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Asynchronous context manager exit method."""
        await self.end_group()

class Sandbox:
    """Represents a single sandbox."""
    def __init__(self, sandbox_id: str, sandbox_group: SandboxGroup):
        """Initializes a Sandbox."""
        self.sandbox_id = sandbox_id
        self.sandbox_group = sandbox_group
        self.sandbox_url = None
        self.sandbox_client = None

    async def start(self):
        """Starts the sandbox."""
        logging.debug(f"Sandbox.start called with sandbox_id: {self.sandbox_id}") # Log Sandbox.start call
        logging.debug(f"Sandbox.start - sandbox_group: {self.sandbox_group}") # Log sandbox_group value
        logging.debug(f"Sandbox.start - sandbox_url: {self.sandbox_url}") # Log sandbox_url
        if not self.sandbox_url:
            self.sandbox_url = await self.sandbox_group.orchestrator_client.get_sandbox_url(self.sandbox_id)
            self.sandbox_client = SandboxClient(self.sandbox_url)
        if self.sandbox_group:
            await self.sandbox_group.start_sandbox(self.sandbox_id)
        else:
            raise NotImplementedError("Starting standalone sandboxes is not yet implemented.") # Raise NotImplementedError for standalone sandboxes

    async def send_actions(self, actions: ActionExecutionRequest) -> List[Observation]:
        """Sends actions to the sandbox and returns observations."""
        if not self.sandbox_client:
            await self.start()
        return await self.sandbox_client.send_actions(actions)

    async def end(self):
        """Stops and removes the sandbox."""
        if self.sandbox_client:
            await self.sandbox_client.close()
            self.sandbox_client = None
            self.sandbox_url = None
        await self.sandbox_group.end_sandbox(self.sandbox_id)

    async def get_history(self) -> List[ActionsObservationsPair]:
        """Returns the action history of the sandbox."""
        if not self.sandbox_client:
            await self.start()
        return await self.sandbox_client.get_history()

    async def get_tools_api_reference(self) -> SandboxCapabilities:
        """Returns the API reference for the tools available in the sandbox."""
        if not self.sandbox_client:
            await self.start()
        return await self.sandbox_client.get_capabilities()

    async def get_resource_stats(self) -> SandboxComputeResourceStats: # Renamed from get_resource_usage
        """Returns the resource usage of the sandbox."""
        if not self.sandbox_client:
            await self.start()
        return await self.sandbox_client.get_resource_usage()

    async def get_stats(self) -> SandboxStats:
        """Returns the stats of the sandbox."""
        if not self.sandbox_client:
            await self.start()
        return await self.sandbox_client.get_stats()
EOF