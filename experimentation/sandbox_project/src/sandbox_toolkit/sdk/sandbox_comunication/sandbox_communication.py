import os
import tarfile
from typing import List

import httpx

from sandbox_toolkit.helpers.exceptions import SandboxError
from sandbox_toolkit.helpers.schema_models.networking_schemas import *
from sandbox_toolkit.helpers.schema_models.internal_schemas import (
    ActionExecutionRequest,
    ActionsObservationsPair,
    Compute,
    Observation,
    SandboxStats,
    SandboxTools,
)
from sandbox_toolkit.logs.logging import logger


class SandboxClient:
    """
    A client for interacting with the sandbox environment.
    Attributes:
        sandbox_url (str): The URL of the sandbox environment.
        client (httpx.AsyncClient): The HTTP client for making asynchronous requests.
    Methods:
        __init__(sandbox_url: str):
            Initializes the SandboxClient with the given sandbox URL.
        _compress_directory_(directory: str) -> bytes:
            Compresses the specified directory into a tar.gz file and returns its content as bytes.
        send_actions(actions: ActionExecutionRequest) -> List[Observation]:
            Sends actions to the sandbox and returns a list of observations.
        get_tools() -> SandboxTools:
            Retrieves the available tools from the sandbox.
        get_resource_usage() -> Compute:
            Retrieves the resource usage information from the sandbox.
        get_stats() -> SandboxStats:
            Retrieves the statistics of the sandbox.
        get_history() -> List[ActionsObservationsPair]:
            Retrieves the history of actions and observations from the sandbox.
        close():
            Closes the sandbox client.
    """
    def __init__(self, sandbox_url: str):

        self.sandbox_url = sandbox_url
        self.client = httpx.AsyncClient()

    async def _compress_directory_(self, directory: str) -> bytes:
        """
        Compresses the specified directory into a gzip tarball and returns its content as bytes.
        Args:
            directory (str): The path to the directory to be compressed.
        Returns:
            bytes: The compressed tarball content as bytes.
        Raises:
            FileNotFoundError: If the specified directory does not exist.
            PermissionError: If there are permission issues accessing the directory or creating the tarball.
            Exception: For any other exceptions that may occur during compression.
        Logs:
            Info: Logs the start and successful completion of the compression process.
            Debug: Logs the input directory path.
        """
        logger.info(f"Compressing directory: {directory}")
        logger.debug(f"Inputs: directory={directory}")

        file_content = None
        with tarfile.open("directory.tar.gz", "w:gz") as tar:
            tar.add(directory, arcname=os.path.basename(directory))
        with open("directory.tar.gz", "rb") as file:
            file_content = file.read()

        logger.info("Directory compressed successfully.")
        
        return file_content
    
    async def send_actions(self, actions: Actions) -> List[Observation]:
        """
        Sends a set of actions to the sandbox environment.

        Args:
            actions (ActionExecutionRequest): The actions to be executed in the sandbox.

        Returns:
            List[Observation]: A list of observations resulting from the execution of the actions.

        Raises:
            SandboxError: If there is an error sending the actions to the sandbox.

        Example:
            actions = ActionExecutionRequest(actions={"store_directory_of_files": {"args": {"directory_path": "/path/to/dir"}}})
            observations = await send_actions(actions)
        """
        logger.info("Sending actions to sandbox...")
        logger.debug(f"Inputs: actions={actions.dict()}")

        file_content = None
        for function_name, action_details in actions.actions.items():
            if function_name == "store_directory_of_files":
                directory_path = action_details.get("args", {}).get("directory_path")
                file_content = self._compress_directory_(directory_path)

        request = SendActionsRequest(actions=actions, file_content=file_content)
        try:
            response = await self.client.post(
                f"{self.sandbox_url}/send_actions",
                json=request.dict()
            )
            response.raise_for_status()
            send_actions_response = SendActionsResponse(**response.json())

            logger.info("Actions sent successfully.")
            logger.debug("Outputs: List[Observation]")
            return send_actions_response.observations
        except httpx.HTTPError as e:
            raise SandboxError(f"Failed to send actions to sandbox: {e}")

    async def get_tools(self) -> SandboxTools:
        """
        Asynchronously retrieves sandbox tools from the sandbox service.

        This method sends a request to the sandbox service to get the available tools.
        It logs the process and handles any HTTP errors that may occur during the request.

        Returns:
            SandboxTools: An instance of SandboxTools containing the retrieved tools.

        Raises:
            SandboxError: If there is an error while making the request to the sandbox service.
        """
        logger.info("Getting sandbox tools...")
        logger.debug("Inputs: None")

        request = GetToolsRequest()
        try:
            response = await self.client.post(
                f"{self.sandbox_url}/get_tools",
                json=request.dict()
            )
            response.raise_for_status()
            tools_response = GetToolsResponse(**response.json())

            logger.info("Sandbox tools retrieved successfully.")
            logger.debug("Outputs: SandboxTools")
            return tools_response
        except httpx.HTTPError as e:
            raise SandboxError(f"Failed to get sandbox tools: {e}")

    async def get_resource_usage(self) -> Compute:
        """
        Asynchronously retrieves the resource usage of the sandbox.

        This method sends a request to the sandbox to get the current resource usage
        and returns the response as a Compute object.

        Returns:
            Compute: An object containing the resource usage information.

        Raises:
            SandboxError: If there is an error while trying to get the resource usage.
        """
        logger.info("Getting sandbox resource usage...")
        logger.debug("Inputs: None")

        request = GetResourceUsageRequest()
        try:
            response = await self.client.post(
                f"{self.sandbox_url}/get_resource_usage",
                json=request.dict()
            )
            response.raise_for_status()
            resource_usage_response = GetResourceUsageResponse(**response.json())

            logger.info("Sandbox resource usage retrieved successfully.")
            logger.debug("Outputs: Compute")
            return resource_usage_response
        except httpx.HTTPError as e:
            raise SandboxError(f"Failed to get sandbox resource usage: {e}")

    async def get_stats(self) -> SandboxStats:
        """
        Asynchronously retrieves sandbox statistics.

        This method sends a POST request to the sandbox URL to fetch the statistics.
        If the request is successful, it returns a `SandboxStats` object containing
        the retrieved statistics. If the request fails, it raises a `SandboxError`.

        Returns:
            SandboxStats: An object containing the sandbox statistics.

        Raises:
            SandboxError: If the request to get sandbox stats fails.
        """
        logger.info("Getting sandbox stats...")
        logger.debug("Inputs: None")

        request = GetStatsRequest()
        try:
            response = await self.client.post(
                f"{self.sandbox_url}/get_stats",
                json=request.dict()
            )
            response.raise_for_status()
            stats_response = GetStatsResponse(**response.json())

            logger.info("Sandbox stats retrieved successfully.")
            logger.debug("Outputs: SandboxStats")
            return stats_response
        except httpx.HTTPError as e:
            raise SandboxError(f"Failed to get sandbox stats: {e}")

    async def get_history(self) -> List[ActionsObservationsPair]:
        """
        Asynchronously retrieves the history of actions and observations from the sandbox.

        Returns:
            List[ActionsObservationsPair]: A list of action-observation pairs representing the sandbox history.

        Raises:
            SandboxError: If there is an error while attempting to retrieve the sandbox history.

        Logs:
            - Info: When the history retrieval process starts and completes successfully.
            - Debug: The inputs (None) and outputs (List[ActionsObservationsPair]) of the method.
        """
        logger.info("Getting sandbox history...")
        logger.debug("Inputs: None")
        request = GetHistoryRequest()
        try:
            response = await self.client.post(
                f"{self.sandbox_url}/get_history",
                json=request.dict()
            )
            response.raise_for_status()
            history_response = GetHistoryResponse(**response.json())

            logger.info("Sandbox history retrieved successfully.")
            logger.debug("Outputs: List[ActionsObservationsPair]")
            return history_response.history
        except httpx.HTTPError as e:
            raise SandboxError(f"Failed to get sandbox history: {e}")

    async def close(self):
        """
        Asynchronously closes the sandbox client.
        This method logs the process of closing the sandbox client, including
        both the start and successful completion of the operation.
        Returns:
            None
        """
        logger.info("Closing sandbox client...")
        logger.debug("Inputs: None")

        self.client.close()
        
        logger.info("Sandbox client closed successfully.")
        logger.debug("Outputs: None")
        return