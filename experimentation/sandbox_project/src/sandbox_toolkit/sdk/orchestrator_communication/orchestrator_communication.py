import io
import os
import tarfile

import httpx

from sandbox_toolkit.helpers.exceptions import SandboxError
from sandbox_toolkit.helpers.schema_models.internal_schemas import (
    Compute,
)
from sandbox_toolkit.helpers.schema_models.networking_schemas import *
from sandbox_toolkit.logs.logging import logger
from sandbox_toolkit.sdk.core.core import Sandbox


class OrchestratorClient:
    """
    A client for interacting with the orchestrator service.
    Methods
    -------
    __init__(orchestrator_url: str)
        Initializes the OrchestratorClient with the given URL.
    _compress_directory_(directory: str) -> bytes
        Compresses the specified directory into a gzip tarball and returns the compressed bytes.
    async create_sandbox(sandbox: Sandbox) -> str
        Creates a new sandbox with the given configuration and returns the sandbox ID.
    async start_sandbox(sandbox_id: str) -> None
        Starts the sandbox with the specified sandbox ID.
    async stop_sandbox(sandbox_id: str) -> None
        Stops the sandbox with the specified sandbox ID.
    async get_host_resources() -> Compute
        Retrieves the total resources available on the host.
    async get_host_resource_usage() -> Compute
        Retrieves the current resource usage statistics of the host.
    async close() -> None
        Closes the OrchestratorClient and releases any resources.
    """
    def __init__(self, orchestrator_url: str):
        """
        Initializes the OrchestratorClient.

        Args:
            orchestrator_url (str): The URL of the orchestrator service.

        Logs:
            - Info: Initializing OrchestratorClient with URL.
            - Debug: Inputs: orchestrator_url.
            - Info: OrchestratorClient initialized successfully.
            - Debug: Outputs: None.
        """
        logger.info(f"Initializing OrchestratorClient with URL: {orchestrator_url}")
        logger.debug("Inputs: orchestrator_url")

        self.orchestrator_url = orchestrator_url
        self.client = httpx.AsyncClient()

        logger.info("OrchestratorClient initialized successfully.")
        logger.debug("Outputs: None")


    def _compress_directory_(self, directory: str) -> bytes:
        """
        Compresses the specified directory into a gzip-compressed tar archive.

        Args:
            directory (str): The path to the directory to be compressed.

        Returns:
            bytes: The compressed directory as a byte stream.
        """
        # check if directory exists, raise error if not
        if not os.path.exists(directory):
            raise FileNotFoundError(f"Directory not found: {directory}")

        logger.info(f"Compressing directory: {directory}")
        logger.debug(f"Inputs: directory={directory}")

        with io.BytesIO() as byte_stream:
            with tarfile.open(fileobj=byte_stream, mode='w:gz') as tar:
                tar.add(directory, arcname=os.path.basename(directory))

        logger.info("Directory compressed successfully.")
        logger.debug("Outputs: bytes")
        return byte_stream.getvalue()

    async def create_sandbox(self, sandbox: Sandbox) -> str: # Returns sandbox_id
        """
        Asynchronously creates a sandbox environment.
        This method compresses the user knowledge files, sends a request to the orchestrator
        to create a sandbox, and returns the sandbox ID upon successful creation.
        Args:
            sandbox (Sandbox): The sandbox object containing the necessary information 
                               to create the sandbox environment.
        Returns:
            str: The ID of the created sandbox.
        Raises:
            SandboxError: If the sandbox creation fails due to an HTTP error.
        """
        logger.info("Creating sandbox...")
        logger.debug("Inputs: sandbox")

        # Compress user knowledge files
        knowledge_files_directory = sandbox.knowledge

        try:
            user_knowledge_files_compressed_content = \
                self._compress_directory_(knowledge_files_directory)
        except FileNotFoundError as e:
            user_knowledge_files_compressed_content = None
        
        request = SandboxCreateRequest(sandbox=sandbox, 
                                       user_knowledge_files_compressed_content=user_knowledge_files_compressed_content)
        try:
            response = await self.client.post(
                f"{self.orchestrator_url}/create_sandbox", 
                json=request.dict()
            )

            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            create_response = SandboxCreateResponse(**response.json())

            logger.info("Sandbox created successfully.")
            logger.debug("Outputs: sandbox_id")
            return create_response.sandbox_id
        except httpx.HTTPError as e:
            raise SandboxError(f"Failed to create sandbox: {e}")

    async def start_sandbox(self, sandbox_id: str) -> None:
        """
        Asynchronously starts a sandbox with the given sandbox ID.

        Args:
            sandbox_id (str): The ID of the sandbox to start.

        Returns:
            None

        Raises:
            SandboxError: If there is an error starting the sandbox.
        """
        logger.info(f"Starting sandbox {sandbox_id}...")
        logger.debug("Inputs: sandbox_id")
        request = SandboxStartRequest(sandbox_id=sandbox_id)
        try:
            response = await self.client.post(
                f"{self.orchestrator_url}/start_sandbox", 
                json=request.dict()
            )
            response.raise_for_status()

            logger.info(f"Sandbox {sandbox_id} started successfully.")
            logger.debug("Outputs: None")
            return
        except httpx.HTTPError as e:
            raise SandboxError(f"Failed to start sandbox {sandbox_id}: {e}")

    async def stop_sandbox(self, sandbox_id: str) -> None:
        """
        Asynchronously stops a sandbox with the given sandbox ID.
        Args:
            sandbox_id (str): The ID of the sandbox to stop.
        Returns:
            None
        Raises:
            SandboxError: If there is an error stopping the sandbox.
        Logs:
            Info: When the sandbox stop process starts and completes successfully.
            Debug: The inputs and outputs of the function.
        """
        logger.info(f"Stopping sandbox {sandbox_id}...")
        logger.debug("Inputs: sandbox_id")
        
        request = SandboxStopRequest(sandbox_id=sandbox_id)
        try:
            response = await self.client.post(
                f"{self.orchestrator_url}/stop_sandbox", 
                json=request.dict()
            )
            response.raise_for_status()

            logger.info(f"Sandbox {sandbox_id} stopped successfully.")
            logger.debug("Outputs: None")
            return
        
        except httpx.HTTPError as e:
            raise SandboxError(f"Failed to stop sandbox {sandbox_id}: {e}")

    async def get_host_resources(self) -> Compute:
        """
        Asynchronously retrieves the total compute resources from the orchestrator.

        This method sends a request to the orchestrator to get the total available
        compute resources and returns the response.

        Returns:
            Compute: An object representing the total compute resources.

        Raises:
            SandboxError: If there is an error while fetching the resources from the orchestrator.
        """
        logger.info("Getting total resources...")
        logger.debug("Inputs: None")

        request = HostGetResourcesRequest()
        try:
            response = await self.client.post(
                f"{self.orchestrator_url}/get_total_resources", 
                json=request.dict()
            )
            response.raise_for_status()
            host_resources_response = HostGetResourcesResponse(**response.json())

            logger.info("Total resources retrieved successfully.")
            logger.debug("Outputs: Compute")
            return host_resources_response.host_resources
        except httpx.HTTPError as e:
            raise SandboxError(f"Failed to get total resources: {e}")

    async def get_host_resource_usage(self) -> Compute:
        """
        Asynchronously retrieves the total resource usage statistics from the host.

        This method sends a request to the orchestrator to get the total resource 
        usage statistics and returns the response as a Compute object.

        Returns:
            Compute: An object containing the total resource usage statistics.

        Raises:
            SandboxError: If the request to get the total resource stats fails.
        """
        logger.info("Getting total resource stats...")
        logger.debug("Inputs: None")

        request = HostGetResourceUsageRequest()
        try:
            response = await self.client.post(
                f"{self.orchestrator_url}/get_total_resource_stats", 
                json=request.dict() # Request body is empty, but still send json
            )
            response.raise_for_status()
            host_resource_usage_response = Compute(**response.json())

            logger.info("Total resource stats retrieved successfully.")
            logger.debug("Outputs: Compute")
            return host_resource_usage_response.host_resource_usage
        except httpx.HTTPError as e:
            raise SandboxError(f"Failed to get total resource stats: {e}")

    async def close(self) -> None:
        """
        Asynchronously closes the OrchestratorClient connection.

        This method logs the process of closing the OrchestratorClient, including
        debug information about the inputs and outputs. It then calls the `aclose`
        method on the client to close the connection.

        Returns:
            None
        """
        logger.info("Closing OrchestratorClient...")
        logger.debug("Inputs: None")
        await self.client.aclose()

        logger.info("OrchestratorClient closed successfully.")
        logger.debug("Outputs: None")
        return
