import asyncio
from typing import Dict, List, Optional, AsyncIterator, Callable, Union
from pydantic import ValidationError
import httpx
import inspect
import textwrap
from pathlib import Path
from contextlib import asynccontextmanager
import psutil
from asyncio import Lock

from .exceptions import (
    SandboxError,
    SandboxNotStartedError,
    SandboxStartError,
    SandboxStopError,
    ActionExecutionError
)
from .logging import logger

from .models import (
    DatabaseAccess,
    ComputeResources,
    AttachedDatabases,
    ActionObservation,
    SandboxEndpoint,
    SandboxGroupEndpoints
)

class Sandbox:
    @asynccontextmanager
    async def session(self) -> AsyncIterator["Sandbox"]:
        """Context manager for sandbox lifecycle.
        
        Example:
            async with sandbox.session() as sb:
                observations = await sb.send_actions(actions)
        """
        try:
            await self.start()
            yield self
        finally:
            await self.end()

    @staticmethod
    def _process_tools(tools: List[Callable]) -> List[str]:
        """Convert function objects to their source code strings."""
        processed_tools = []
        for tool in tools:
            # Get function source code
            source = inspect.getsource(tool)
            # Get the module name where the function is defined
            module_name = tool.__module__.split('.')[-1]
            # Create a string that includes both module name and function code
            tool_str = f"# Module: {module_name}\n{source}"
            processed_tools.append(tool_str)
        return processed_tools

    def __init__(
        self,
        id: str,
        tools: List[str],  # Now expects pre-processed tool strings
        compute_resources: ComputeResources,
        attached_databases: AttachedDatabases,
        orchestrator_url: str,
        sandbox_url: Optional[str] = None,
        action_timeout: int = 300  # 5 minutes default timeout
    ):
        try:
            # Validate input using SandboxCreateRequest
            create_request = SandboxCreateRequest(
                name=f"Sandbox {id}",
                compute_resources=compute_resources,
                attached_databases=attached_databases,
                environment_variables={}
            )
            
            self.id = id
            self.tools = tools  # Already processed tool strings
            self.compute_resources = create_request.compute_resources
            self.attached_databases = create_request.attached_databases
            self.orchestrator_url = orchestrator_url
            self.sandbox_url = sandbox_url
            self.action_timeout = action_timeout
            self._execution_lock = Lock()
            self._client = httpx.AsyncClient()
            self._monitor_task = None
            self._resource_window_size = 5  # Size of sliding window for measurements
            self._monitoring_interval = 0.5  # Monitor every 500ms
            self._measurements_lock = Lock()  # Lock for thread-safe access to measurements
            self._cpu_measurements = []
            self._memory_measurements = []
            self._disk_measurements = []
            self._is_monitoring = False
        except ValidationError as e:
            raise SandboxError(f"Invalid sandbox configuration: {str(e)}")

    async def start(self) -> SandboxEndpoint:
        """Start the sandbox container and return its endpoint information."""
        response = await self._client.post(
            f"{self.orchestrator_url}/sandbox/start",
            json={
                "id": self.id,
                "tools": self.tools,  # Already strings, no conversion needed
                "compute_resources": self.compute_resources.dict(),
                "attached_databases": self.attached_databases.dict()
            }
        )
        response.raise_for_status()
        data = response.json()
        
        # Store URL for internal use
        self.sandbox_url = data["endpoint"]
        
        # Return endpoint information
        return SandboxEndpoint(
            id=self.id,
            name=data.get("name", f"Sandbox {self.id}"),
            endpoint=data["endpoint"],
            auth_info=data.get("auth_info")
        )

    async def send_actions(self, actions: Dict) -> List[ActionObservation]:
        """Send actions to be executed in the sandbox"""
        if not self.sandbox_url:
            raise RuntimeError("Sandbox not started")
        
        async def monitor_resources():
            process = psutil.Process()

            try:
                self._is_monitoring = True
                while self._is_monitoring:
                    cpu_percent = process.cpu_percent()
                    memory_info = process.memory_info()
                    memory_mb = memory_info.rss / (1024 * 1024)  # Convert to MB
                    disk_usage = psutil.disk_usage('/').percent

                    async with self._measurements_lock:
                        # Update sliding windows
                        self._cpu_measurements.append(cpu_percent)
                        self._memory_measurements.append(memory_mb)
                        self._disk_measurements.append(disk_usage)

                        # Keep only the last window_size measurements
                        if len(self._cpu_measurements) > self._resource_window_size:
                            self._cpu_measurements.pop(0)
                            self._memory_measurements.pop(0)
                            self._disk_measurements.pop(0)

                        # Calculate averages
                        avg_cpu = sum(self._cpu_measurements) / len(self._cpu_measurements)
                        avg_memory = sum(self._memory_measurements) / len(self._memory_measurements)
                        avg_disk = sum(self._disk_measurements) / len(self._disk_measurements)

                        # Check against limits
                        if avg_cpu > self.compute_resources.cpu_limit:
                            raise ActionExecutionError(f"CPU usage exceeded limit: {avg_cpu:.1f}%")

                        # Convert memory limit from percentage to MB
                        total_memory = psutil.virtual_memory().total / (1024 * 1024)  # Total memory in MB
                        memory_limit_mb = (self.compute_resources.memory_limit / 100) * total_memory

                        if avg_memory > memory_limit_mb:
                            raise ActionExecutionError(f"Memory usage exceeded limit: {avg_memory:.1f}MB/{memory_limit_mb:.1f}MB")

                        if avg_disk > 90:  # 90% disk usage threshold
                            raise ActionExecutionError(f"Disk usage too high: {avg_disk:.1f}%")

                    await asyncio.sleep(self._monitoring_interval)
            finally:
                self._is_monitoring = False
                async with self._measurements_lock:
                    self._cpu_measurements.clear()
                    self._memory_measurements.clear()
                    self._disk_measurements.clear()
        
        try:
            async with self._execution_lock:  # Ensure thread safety
                # Validate each action in the actions dictionary
                for action_name, action_data in actions.items():
                    ActionExecuteRequest(**action_data)
                
                # Start resource monitoring task
                if self._monitor_task is not None:
                    if not self._monitor_task.done():
                        self._monitor_task.cancel()
                        try:
                            await self._monitor_task
                        except asyncio.CancelledError:
                            pass

                self._monitor_task = asyncio.create_task(monitor_resources())
                
                try:
                    # Execute actions with timeout
                    response = await asyncio.wait_for(
                        self._client.post(
                            f"{self.sandbox_url}/execute",
                            json={"actions": actions}
                        ),
                        timeout=self.action_timeout
                    )
                    
                    response.raise_for_status()
                    data = response.json()
                    return [ActionObservation(**obs) for obs in data["observations"]]
                
                except asyncio.TimeoutError:
                    raise ActionExecutionError(
                        f"Action execution timed out after {self.action_timeout} seconds"
                    )
                finally:
                    # Cancel resource monitoring
                    if self._monitor_task and not self._monitor_task.done():
                        self._is_monitoring = False
                        self._monitor_task.cancel()
                        try:
                            await self._monitor_task
                        except asyncio.CancelledError:
                            pass
                    self._monitor_task = None
            
        except ValidationError as e:
            raise ActionExecutionError(f"Invalid action configuration: {str(e)}")
    def send_actions_sync(self, actions: Dict) -> List[ActionObservation]:
        """Synchronous version of send_actions"""
        return asyncio.run(self.send_actions(actions))

    async def end(self):
        """Stop and remove the sandbox container"""
        if self.sandbox_url:
            response = await self._client.post(
                f"{self.orchestrator_url}/sandbox/stop",
                json={"id": self.id}
            )
            response.raise_for_status()
            self.sandbox_url = None
        await self._client.aclose()

class SandboxGroup:
    def __init__(
        self,
        database_access: DatabaseAccess,
        compute_resources: ComputeResources,
        tools: List[Callable],
        initial_database_population_config: Path,
        orchestrator_url: str = "http://localhost:8000"
    ):
        self.database_access = database_access
        self.compute_resources = compute_resources
        self.tools = Sandbox._process_tools(tools)  # Convert functions to strings
        self.initial_database_population_config = initial_database_population_config
        self.orchestrator_url = orchestrator_url
        self._client = httpx.AsyncClient()
        self.sandboxes: Dict[str, Sandbox] = {}

    async def start_sandbox_group(self) -> SandboxGroupEndpoints:
        """Start the sandbox group and initialize databases.
        Returns information about all sandbox endpoints in the group."""
        response = await self._client.post(
            f"{self.orchestrator_url}/group/start",
            json={
                "database_access": self.database_access.model_dump(),
                "initial_database_population_config": str(self.initial_database_population_config)
            }
        )
        response.raise_for_status()
        data = response.json()
        
        return SandboxGroupEndpoints(
            group_id=data["group_id"],
            sandboxes=[
                SandboxEndpoint(**sandbox_data)
                for sandbox_data in data["sandboxes"]
            ]
        )

    async def create_sandbox(
        self,
        id: str,
        tools: Optional[List[Callable]] = None,
        compute_resources: Optional[ComputeResources] = None,
        attached_databases: Optional[AttachedDatabases] = None
    ) -> Sandbox:
        """Create a new sandbox in the group"""
        try:
            # Validate input using SandboxCreateRequest
            create_request = SandboxCreateRequest(
                name=f"Sandbox {id}",
                compute_resources=compute_resources or self.compute_resources,
                attached_databases=attached_databases or AttachedDatabases(),
                environment_variables={}
            )
            
            # Convert tools to strings if provided, otherwise use group's tools
            tool_strings = Sandbox._process_tools(tools) if tools else self.tools
            
            sandbox = Sandbox(
                id=id,
                tools=tool_strings,
                compute_resources=create_request.compute_resources,
                attached_databases=create_request.attached_databases,
                orchestrator_url=self.orchestrator_url
            )
            self.sandboxes[id] = sandbox
            return sandbox
        except ValidationError as e:
            raise SandboxError(f"Invalid sandbox configuration: {str(e)}")

    def create_sandbox_sync(
        self,
        id: str,
        tools: Optional[List[Callable]] = None,
        compute_resources: Optional[ComputeResources] = None,
        attached_databases: Optional[AttachedDatabases] = None
    ) -> Sandbox:
        """Synchronous version of create_sandbox"""
        return asyncio.run(self.create_sandbox(
            id, tools, compute_resources, attached_databases
        ))

    async def end_group(self):
        """Stop all sandboxes and cleanup resources"""
        for sandbox in self.sandboxes.values():
            await sandbox.end()
        response = await self._client.post(f"{self.orchestrator_url}/group/stop")
        response.raise_for_status()
        await self._client.aclose()