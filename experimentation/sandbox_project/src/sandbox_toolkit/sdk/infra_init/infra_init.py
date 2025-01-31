import os
import subprocess
from pathlib import Path

import docker
import yaml

from sandbox_toolkit.helpers.exceptions import SandboxError
from sandbox_toolkit.logs.logging import logger

PACKAGE_PATH = Path(__file__).parent.parent


class InfraInitializer:
    def __init__(self) -> None:
        pass

    def start_infra(self) -> None:
        """
        Starts the infrastructure using Docker Compose.
        This method initializes the Docker client from the environment, reads the 
        Docker Compose configuration file, and brings up the services defined in 
        the configuration file in detached mode.
        Raises:
            SandboxError: If there is an error starting the infrastructure.
        """
        logger.info("Starting infrastructure...")
        logger.debug("Inputs: None")
        try:
            client = docker.from_env()

            compose_file_path = os.path.join(PACKAGE_PATH, "docker-compose.yml")
            with open(compose_file_path, 'r') as file:
                compose_content = yaml.safe_load(file)
            client.compose.up(detach=True, config=compose_content)
            
            print("Infrastructure started successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error starting infrastructure: {e}")
            raise SandboxError(f"Failed to start infrastructure: {e}")
        
        logger.info("Infrastructure started successfully.")
        logger.debug("Outputs: None")
        return

    def stop_infra(self) -> None:
        """
        Stops the infrastructure by bringing down the Docker Compose services.
        This method logs the process of stopping the infrastructure, reads the Docker Compose
        configuration file, and uses the Docker client to bring down the services defined in the
        configuration. If an error occurs during this process, it raises a SandboxError.
        Raises:
            SandboxError: If there is an error stopping the infrastructure.
        """
        logger.info("Stopping infrastructure...")
        logger.debug("Inputs: None")
        try:
            client = docker.from_env()
            compose_file_path = os.path.join(PACKAGE_PATH, "docker-compose.yml")
            with open(compose_file_path, 'r') as file:
                compose_content = yaml.safe_load(file)
            client.compose.down(config=compose_content)
            
            print("Infrastructure stopped successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error stopping infrastructure: {e}")
            raise SandboxError(f"Failed to stop infrastructure: {e}")
        
        logger.info("Infrastructure stopped successfully.")
        logger.debug("Outputs: None")
        return