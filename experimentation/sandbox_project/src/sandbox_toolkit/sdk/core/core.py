"""Sandbox SDK Core components."""

import ast
from pathlib import Path
from typing import Callable, Dict, List, Optional, Union

from sandbox_toolkit.helpers.constants import ORCHESTRATOR_URL
from sandbox_toolkit.helpers.exceptions.exceptions import SandboxError
from sandbox_toolkit.helpers.schema_models.internal_schemas import (
    Actions,
    ActionsObservationsPair,
    Compute,
    GroupResourceSummary,
    HostResourceSummary,
    Observation,
    SandboxConfig,
    SandboxResourceSummary,
    SandboxStats,
    SandboxTools,
    Tool,
)
from sandbox_toolkit.logs.logging import logger
from sandbox_toolkit.sdk.infra_init.infra_init import InfraInitializer
from sandbox_toolkit.sdk.orchestrator_communication.orchestrator_communication import (
    OrchestratorClient,
)
from sandbox_toolkit.sdk.sandbox_comunication.sandbox_communication import SandboxClient


async def get_host_resources() -> Compute:
    """Returns host compute resources for the machine."""
    orchestrator_client = OrchestratorClient(ORCHESTRATOR_URL)
    return await orchestrator_client.get_host_resources()

async def get_host_resource_usage() -> Compute:
    """Returns host compute resource stats for the machine."""
    orchestrator_client = OrchestratorClient(ORCHESTRATOR_URL)
    return await orchestrator_client.get_host_resource_usage()

async def get_host_resource_summary() -> HostResourceSummary:
    """Returns host compute resource summary for the machine."""
    host_resources = await get_host_resources()
    host_resource_usage = await get_host_resource_usage()
    return HostResourceSummary(
        host_resources=host_resources, host_resource_usage=host_resource_usage
    )


class Sandbox:
    """
    Represents a single sandbox.
    Attributes:
        id (str): The unique identifier of the sandbox.
        url (Optional[str]): The URL of the sandbox.
        client (Optional[Client]): The client associated with the sandbox.
        name (str): The name of the sandbox.
        compute (SandboxConfig): The configuration of the sandbox.
        tools (Optional[Union[List[Callable], List[Path]]]): The tools available in the sandbox.
        knowledge (Optional[Path]): The knowledge base associated with the sandbox.
        sandbox_url (HTTPUrl): The URL of the created sandbox.
    Methods:
        __aenter__(): Asynchronous context manager enter method.
        __aexit__(exc_type, exc_val, exc_tb): Asynchronous context manager exit method.
        create() -> HTTPUrl: Creates the sandbox.
        start(): Starts the sandbox.
        send_actions(actions: ActionExecutionRequest) -> List[Observation]: Sends actions to the sandbox and returns observations.
        end(): Stops and removes the sandbox.
        get_history() -> List[ActionsObservationsPair]: Returns the action history of the sandbox.
        get_tools() -> SandboxTools: Returns the API reference for the tools available in the sandbox.
        get_resource_usage() -> Compute: Returns the resource usage of the sandbox.
        get_resource_summary() -> SandboxResourceSummary: Returns the resource summary of the sandbox.
        get_stats() -> SandboxStats: Returns the stats of the sandbox.
    """
    """Represents a single sandbox."""
    def __init__(
            self, 
            sandbox_id: str, 
            sandbox_name: str, 
            sandbox_config: SandboxConfig, 
            sandbox_knowledge: Path = Path("/knowledge"),
            sandbox_tools: Optional[Union[List[Callable], List[Path]]] = None
    ):
        """Initializes a Sandbox."""
        logger.debug(f"Sandbox.__init__ called")
        logger.debug(f"Input: sandbox_id={sandbox_id}, \
                     sandbox_name={sandbox_name}, \
                     sandbox_config={sandbox_config}, \
                     sandbox_knowledge={sandbox_knowledge}, \
                     sandbox_tools={sandbox_tools}")
        
        self.id = sandbox_id
        self.url = None
        self.client = None
        self.name = sandbox_name
        self.compute = sandbox_config
        self.tools = sandbox_tools
        self.knowledge = sandbox_knowledge

        self.sandbox_url = self.create(
            sandbox_name=sandbox_name, 
            sandbox_config=sandbox_config, 
            sandbox_knowledge=sandbox_knowledge, 
            sandbox_tools=sandbox_tools
        )
    
    async def __aenter__(self):
        """
        Asynchronous context manager enter method.
        This method is called when entering the runtime context related to this object.
        It starts the sandbox group and logs the entry and exit points of the method.
        Returns:
            SandboxGroup: The instance of the sandbox group.
        """
        logger.debug(f"SandboxGroup.__aenter__ called")
        logger.debug(f"Input: ") # No input parameters

        await self.start()

        logger.debug(f"SandboxGroup.__aenter__ finished")
        logger.debug(f"Output: self={self}")
        
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Asynchronous context manager exit method.

        This method is called when exiting the context of an asynchronous
        context manager. It logs the entry and exit of the method, as well
        as the exception details if any were raised during the context.

        Args:
            exc_type (Type[BaseException]): The exception type raised, if any.
            exc_val (BaseException): The exception instance raised, if any.
            exc_tb (TracebackType): The traceback object associated with the exception, if any.

        Returns:
            None
        """
        logger.debug(f"SandboxGroup.__aexit__ called")
        logger.debug(f"Input: exc_type={exc_type}, exc_val={exc_val}, exc_tb={exc_tb}")

        await self.end()

        logger.debug(f"SandboxGroup.__aexit__ finished")
        logger.debug(f"Output: None") # No return value

    def _extract_function_code_(self, module_code: str, function_name: str) -> str:
        """
        Extracts the code of a function from a module.
        This method extracts the code of a function from a module by parsing the module code
        and identifying the function code using the function name.
        Args:
            module_code (str): The code of the module containing the function.
            function_name (str): The name of the function to extract.
        Returns:
            str: The code of the function.
        """
        """Extracts the code of a function from a module."""
        logger.debug(f"Sandbox._extract_function_code_ called")
        logger.debug(f"Input: module_code={module_code}, function_name={function_name}")

        module_ast = ast.parse(module_code)
        for node in module_ast.body:
            if isinstance(node, ast.FunctionDef) and node.name == function_name:
                function_ast = node
                function_code = ast.unparse(function_ast)
                break
        else:
            raise SandboxError(f"Function {function_name} not found in module.")

        logger.debug(f"Sandbox._extract_function_code_ finished")
        logger.debug(f"Output: function_code={function_code}")

        return function_code
        

    async def create(self) -> None:
        """
        Creates the sandbox.

        This asynchronous method initializes and creates a sandbox using the provided
        sandbox configuration, name, tools, and knowledge. It communicates with the
        orchestrator client to perform the creation.

        Returns:
            None: The URL of the created sandbox.
        """
        """Creates the sandbox."""
        logger.debug(f"Sandbox.create called")
        logger.debug(f"Input: ") # No input parameters

        if isinstance(self.sandbox_tools, list) and all(callable(tool) for tool in self.sandbox_tools):
            tools_list = []
            for tool in self.sandbox_tools:
                tool_name = tool.__name__
                tool_module = tool.__module__
                tool_path = Path(f"/tools/{tool_module}.py")
                if not tool_path.exists():
                    raise SandboxError(f"Tool {tool_name} not found in /tools")
                with open(tool_path, 'r') as file:
                    module_code = file.read()
                # Extract the function code from the module
                function_code = self._extract_function_code_(module_code, tool_name)
                tools_list.append(Tool(function_name=tool_name, function=function_code, module_name=tool_module))
            self.sandbox_tools = tools_list

        elif isinstance(self.sandbox_tools, list) and all(isinstance(tool, Path) for tool in self.sandbox_tools):
            tools_list = []
            for tool_path in self.sandbox_tools:
                if not tool_path.exists() or not str(tool_path).startswith("/tools"):
                    raise SandboxError(f"Tool path {tool_path} is invalid or not under /tools")
            if tool_path.is_dir():
                module_paths = list(tool_path.glob("*.py"))
            else:
                module_paths = [tool_path]
            for module_path in module_paths:
                with open(module_path, 'r') as file:
                    module_code = file.read()
                    module_ast = ast.parse(module_code)
                    for node in module_ast.body:
                        if isinstance(node, ast.FunctionDef):
                            function_name = node.name
                            function_code = ast.unparse(node)
                            module_name = module_path.stem
                            tools_list.append(Tool(function_name=function_name, function=function_code, module_name=module_name))

            self.sandbox_tools = tools_list
    
        await self.sandbox_group.orchestrator_client.create_sandbox(
            sandbox_config=self.sandbox_config,
            sandbox_name=self.sandbox_name,
            sandbox_tools = self.sandbox_tools,
            sandbox_knowledge = self.sandbox_knowledge
        )

        return

    async def start(self):
        """
        Asynchronously starts the sandbox.

        This method initiates the sandbox by calling the orchestrator client to start the sandbox
        using the provided sandbox ID. It also initializes the sandbox client with the sandbox URL.

        Args:
            None

        Returns:
            None
        """
        """Starts the sandbox."""
        logger.debug(f"Sandbox.start called")
        logger.debug(f"Input: ") # No input parameters

        await self.sandbox_group.orchestrator_client.start_sandbox(self.sandbox_id)

        logger.debug(f"Sandbox.start finished")
        logger.debug(f"Output: None") # No return value

        self.sandbox_client = SandboxClient(self.sandbox_url)

    async def send_actions(self, actions: Actions) -> List[Observation]:
        """
        Sends actions to the sandbox and returns observations.

        Args:
            actions (ActionExecutionRequest): The actions to be sent to the sandbox.

        Returns:
            List[Observation]: A list of observations returned from the sandbox.

        Raises:
            SandboxClientError: If there is an error with the sandbox client.
        """
        """Sends actions to the sandbox and returns observations."""
        logger.debug(f"Sandbox.send_actions called")
        logger.debug(f"Input: actions={actions}")

        if not self.sandbox_client:
            await self.start()

        observations = await self.sandbox_client.send_actions(actions)

        logger.debug(f"Sandbox.send_actions finished")
        logger.debug(f"Output: observations={observations}")

        return observations

    async def end(self):
        """
        Stops and removes the sandbox.

        This method will close the sandbox client if it is running and reset the
        sandbox client and URL attributes to None. If the sandbox client is not
        running, it raises a SandboxError.

        Raises:
            SandboxError: If the sandbox client is not running.

        Returns:
            None
        """
        """Stops and removes the sandbox."""
        logger.debug(f"Sandbox.end called")
        logger.debug(f"Input: ") # No input parameters

        if self.sandbox_client:
            await self.sandbox_client.close()
        else:
            raise SandboxError("Sandbox cannot end without starting first.")

        self.sandbox_client = None
        self.sandbox_url = None

        logger.debug(f"Sandbox.end finished")
        logger.debug(f"Output: None") # No return value

        return

    async def get_history(self) -> List[ActionsObservationsPair]:
        """
        Asynchronously retrieves the action history of the sandbox.

        This method checks if the sandbox client is initialized and starts it if necessary.
        It then fetches the action history from the sandbox client.

        Returns:
            List[ActionsObservationsPair]: A list of action-observation pairs representing the history of actions taken in the sandbox.
        """
        """Returns the action history of the sandbox."""
        logger.debug(f"Sandbox.get_history called")
        logger.debug(f"Input: ")

        if not self.sandbox_client:
            await self.start()

        history = await self.sandbox_client.get_history()

        logger.debug(f"Sandbox.get_history finished")
        logger.debug(f"Output: history={history}")
        return history

    async def get_tools(self) -> SandboxTools:
        """
        Asynchronously retrieves the API reference for the tools available in the sandbox.

        This method ensures that the sandbox client is started if it is not already running,
        and then fetches the available tools from the sandbox client.

        Returns:
            SandboxTools: An object containing the API reference for the tools available in the sandbox.
        """
        logger.debug(f"Sandbox.get_tools_api_reference called")
        logger.debug(f"Input: ") # No input parameters

        if not self.sandbox_client:
            await self.start()

        sandbox_tools = await self.sandbox_client.get_tools()

        logger.debug(f"Sandbox.get_tools_api_reference finished")
        logger.debug(f"Output: sandbox_tools={sandbox_tools}")

        return sandbox_tools

    async def get_resource_usage(self) -> Compute: 
        """
        Asynchronously retrieves the resource usage of the sandbox.
        This method checks if the sandbox client is initialized and starts it if necessary.
        It then fetches the resource usage from the sandbox client.
        Returns:
            Compute: An object representing the resource usage of the sandbox.
        """
        """Returns the resource usage of the sandbox."""
        logger.debug(f"Sandbox.get_resource_usage called")
        logger.debug(f"Input: ")

        if not self.sandbox_client:
            await self.start()

        sandbox_resource_usage = await self.sandbox_client.get_resource_usage()

        logger.debug(f"Sandbox.get_resource_usage finished")
        logger.debug(f"Output: resource_usage={sandbox_resource_usage}")
        
        return sandbox_resource_usage
    
    async def get_resource_summary(self) -> SandboxResourceSummary:
        """
        Asynchronously retrieves and returns the resource summary of the sandbox.
        This method ensures that the sandbox client is started if it is not already running,
        then gathers the current resource usage and allocated resources of the sandbox.
        It combines these details into a `SandboxResourceSummary` object.
        Returns:
            SandboxResourceSummary: An object containing the resource usage and allocated resources of the sandbox.
        """
        """Returns the resource summary of the sandbox."""
        logger.debug(f"Sandbox.get_resource_summary called")
        logger.debug(f"Input: ")

        if not self.sandbox_client:
            await self.start()

        sandbox_resource_usage = await self.get_resource_usage()
        sandbox_allocated_resources = await self.compute
    
        sandbox_resource_summary = SandboxResourceSummary(
            sandbox_resource_usage=sandbox_resource_usage, 
            sandbox_allocated_resources=sandbox_allocated_resources
        )
        logger.debug(f"Sandbox.get_resource_summary finished")
        logger.debug(f"Output: resource_summary={sandbox_resource_summary}")

        return sandbox_resource_summary

    async def get_stats(self) -> SandboxStats:
        """
        Asynchronously retrieves and returns the statistics of the sandbox.

        This method checks if the sandbox client is initialized. If not, it starts the client
        before fetching the sandbox statistics.

        Returns:
            SandboxStats: An object containing the statistics of the sandbox.
        """
        """Returns the stats of the sandbox."""
        logger.debug(f"Sandbox.get_stats called")
        logger.debug(f"Input: ")

        if not self.sandbox_client:
            await self.start()

        sandbox_stats = await self.sandbox_client.get_stats()

        logger.debug(f"Sandbox.get_stats finished")
        logger.debug(f"Output: stats={sandbox_stats}")
        return sandbox_stats
    
class SandboxGroup:
    """
    Manages a group of sandboxes.
    Attributes:
        config (SandboxConfig): Configuration for the sandbox group.
        tools (Optional[Union[List[Callable], List[Path]]]): Tools available for the sandboxes.
        infra_initializer (InfraInitializer): Initializes the infrastructure.
        orchestrator_client (OrchestratorClient): Client to interact with the orchestrator.
        knowledge (Optional[Path]): Knowledge base for the sandboxes.
        name (str): Name of the sandbox group.
        infra_started (bool): Indicates if the infrastructure has been started.
        sandboxes (dict): Dictionary of sandboxes managed by the group.
    Methods:
        start_infra(): Starts the infrastructure if it's not already started.
        create_sandbox(sandbox_name: str) -> Sandbox: Creates a new sandbox in the group.
        get_sandbox(sandbox_id: str) -> Sandbox: Returns a sandbox from the group by its ID.
        start(): Starts all sandboxes in the group.
        end_sandbox(sandbox_id: str): Stops and removes a specific sandbox from the group.
        end(): Stops and removes all sandboxes in the group and stops the infrastructure.
        get_sandbox_resource_usage(sandbox_id: str) -> Compute: Returns the resource usage for a specific sandbox in the group.
        get_resource_usage() -> Compute: Returns the resource usage for all sandboxes in the group.
        get_resource_summary() -> GroupResourceSummary: Returns the resource summary for all sandboxes in the group.
    """

    def __init__(self, group_config: SandboxConfig,
                 group_name: str, 
                 group_knowledge: Optional[Path] = None,
                 group_tools: Optional[Union[List[Callable], List[Path]]] = None
    ) -> None:
        """Initializes a SandboxGroup."""
        self.config = group_config
        self.tools = group_tools
        self.infra_initializer = InfraInitializer()
        self.orchestrator_client = OrchestratorClient(ORCHESTRATOR_URL)
        self.knowledge = group_knowledge
        self.name = group_name

        self.infra_started = False
        self.sandboxes = {}

        return

    async def start_infra(self) -> None:
        """
        Starts the infrastructure if it's not already started.

        This method checks if the infrastructure is already started. If not, it 
        initializes and starts the infrastructure and sets the infra_started flag 
        to True. It also logs the start and end of the process.

        Returns:
            None
        """
        logger.debug(f"SandboxGroup.start_infra called")
        logger.debug(f"Input: sandbox_id=None")
        """Starts the infrastructure if it's not already started."""

        if not self.infra_started:
            self.infra_initializer.start_infra()
            self.infra_started = True

        logger.debug("SandboxGroup start finished")

        return 

    async def create_sandbox(self, sandbox_name: str) -> Sandbox:
        """
        Creates a new sandbox in the group.

        Args:
            sandbox_name (str): The name of the sandbox to be created.

        Returns:
            Sandbox: The created sandbox instance.

        Raises:
            Exception: If the infrastructure fails to start or the sandbox creation fails.

        Logs:
            Debug: Logs the start and end of the sandbox creation process, as well as the input and output details.
        """
        """Creates a new sandbox in the group."""
        logger.debug(f"SandboxGroup.create_sandbox called")
        logger.debug(f"Input: sandbox_name={sandbox_name}")

        if not self.infra_started:
            await self.start_infra()

        sandbox_id = await self.orchestrator_client.create_sandbox(self.sandbox_config)

        sandbox = Sandbox(
            sandbox_name=sandbox_name,
            sandbox_config=self.config,
            sandbox_knowledge=self.knowledge,
            sandbox_tools=self.tools,
            sandbox_id=sandbox_id
        )

        self.sandboxes[sandbox_id] = sandbox

        logger.debug(f"SandboxGroup.create_sandbox finished")
        logger.debug(f"Output: sandbox={sandbox}")

        return sandbox

    async def get_sandbox(self, sandbox_id: str) -> Sandbox:
        """
        Retrieves a sandbox from the group by its ID.

        Args:
            sandbox_id (str): The unique identifier of the sandbox to retrieve.

        Returns:
            Sandbox: The sandbox object corresponding to the provided ID.

        Raises:
            SandboxError: If no sandbox with the given ID is found in the group.

        Logs:
            Debug information about the method call, input, and output.
        """
        """Returns a sandbox from the group by its ID."""

        logger.debug(f"SandboxGroup.get_sandbox called")
        logger.debug(f"Input: sandbox_id={sandbox_id}")

        if sandbox_id not in self.sandboxes:
            raise SandboxError(f"Sandbox with id '{sandbox_id}' \
                               not found in this group.")
        sandbox = self.sandboxes[sandbox_id]

        logger.debug(f"SandboxGroup.get_sandbox finished")
        logger.debug(f"Output: sandbox={sandbox}")

        return sandbox

    async def start(self) -> None:
        """
        Asynchronously starts all sandboxes in the SandboxGroup.
        This method iterates over all sandboxes in the `sandboxes` dictionary and 
        calls their `start` method. It logs the start and end of the process.
        Returns:
            None
        """
        
        logger.debug(f"SandboxGroup.start called")
        logger.debug(f"Input: ") # No input parameters

        for sandbox in self.sandboxes.values():
            await sandbox.start()

        logger.debug(f"SandboxGroup.start finished")
        logger.debug(f"Output: None") # No return value

    async def end_sandbox(self, sandbox_id: str) -> None:
        """
        Ends the sandbox with the given sandbox_id.
        This method stops the sandbox using the orchestrator client and removes it from the sandboxes dictionary.
        Args:
            sandbox_id (str): The unique identifier of the sandbox to be ended.
        Raises:
            SandboxError: If the sandbox with the given id is not found in the group.
        Returns:
            None
        """
        
        logger.debug(f"SandboxGroup.end_sandbox called")
        logger.debug(f"Input: sandbox_id={sandbox_id}")

        if sandbox_id not in self.sandboxes:
            raise SandboxError(f"Sandbox with id '{sandbox_id}' \
                               not found in this group.")
        await self.orchestrator_client.stop_sandbox(sandbox_id)

        del self.sandboxes[sandbox_id]

        logger.debug(f"SandboxGroup.end_sandbox finished")
        logger.debug(f"Output: None") # No return value

        return

    async def end(self) -> None:
        """
        Asynchronously ends the sandbox group by stopping all active sandboxes and infrastructure.
        This method iterates over all active sandboxes, ending each one. If the infrastructure
        was started, it stops the infrastructure and updates the state accordingly.
        Returns:
            None
        """
       
        logger.debug("SandboxGroup end called")
        logger.debug(f"Input: ") # No input parameters

        for sandbox_id in list(self.sandboxes.keys()): # Iterate over a copy of \
            # keys to avoid RuntimeError during deletion
            await self.end_sandbox(sandbox_id)

        logger.debug("SandboxGroup end - Stopping infrastructure...")
        if self.infra_started:
            self.infra_initializer.stop_infra()
            self.infra_started = False

        logger.debug("SandboxGroup endfinished")
        logger.debug(f"Output: None") # No return value

        return

    async def get_sandbox_resource_usage(self, sandbox_id: str) -> Compute:
        """
        Asynchronously retrieves the resource usage of a specified sandbox.
        Args:
            sandbox_id (str): The unique identifier of the sandbox.
        Returns:
            Compute: An object representing the resource usage of the specified sandbox.
        Raises:
            SandboxError: If the sandbox with the given ID is not found in the group.
        """
        
        logger.debug(f"SandboxGroup.get_sandbox_resource_usagecalled")
        logger.debug(f"Input: sandbox_id={sandbox_id}")

        if sandbox_id not in self.sandboxes:
            raise SandboxError(
                f"Sandbox with id '{sandbox_id}' not found in this group.")
        
        sandbox_resource_usage = await \
            self.sandboxes[sandbox_id].get_resource_usage()

        logger.debug(f"SandboxGroup.get_sandbox_resource_usage finished")
        logger.debug(f"Output: resource_usages={sandbox_resource_usage}")

        return sandbox_resource_usage

    async def get_resource_usage(self, sandbox_id: str) -> Compute:
        """
        Asynchronously retrieves the resource usage for all sandboxes in the group.
        Args:
            sandbox_id (str): The ID of the sandbox for which resource usage is to be retrieved.
        Returns:
            Compute: A dictionary containing the resource usage for each sandbox.
        Logs:
            - Debug log indicating the method call.
            - Debug log for input parameters.
            - Debug log indicating the method completion.
            - Debug log for output resource usage.
        """
        
        logger.debug(f"SandboxGroup.get_resource_usage called")
        logger.debug(f"Input: ") # No input parameters

        resource_usage = {}
        for sandbox_id in self.sandboxes:
            resource_usage[sandbox_id] = \
            await self.get_sandbox_resource_usage(sandbox_id)

        logger.debug(f"SandboxGroup.get_resource_usage finished")
        logger.debug(f"Output: resource_usage={resource_usage}")
        return resource_usage
    
    async def get_resource_summary(self) -> GroupResourceSummary:
        """
        Asynchronously retrieves a summary of resources allocated and used by sandboxes in the group.
        This method iterates over all sandboxes in the group, collects their allocated resources and 
        current resource usage, and compiles this information into a GroupResourceSummary object.
        Returns:
            GroupResourceSummary: An object containing the allocated resources and resource usage 
            for each sandbox in the group.
        """
        
        logger.debug(f"SandboxGroup.get_resource_summary called")
        logger.debug(f"Input: ") # No input parameters

        sandboxes_allocated_resources = {}
        sandboxes_resource_usage = {}
        for sandbox_id in self.sandboxes:
            sandbox = self.sandboxes[sandbox_id]
            sandboxes_allocated_resources[sandbox_id] = sandbox.compute
            sandboxes_resource_usage[sandbox_id] = \
            await sandbox.get_resource_usage()

        resource_summary = GroupResourceSummary(
            sandboxes_allocated_resources=sandboxes_allocated_resources,
            sandboxes_resource_usage=sandboxes_resource_usage
        )

        logger.debug(f"SandboxGroup.get_resource_summary finished")
        logger.debug(f"Output: resource_summary={resource_summary}")

        return resource_summary