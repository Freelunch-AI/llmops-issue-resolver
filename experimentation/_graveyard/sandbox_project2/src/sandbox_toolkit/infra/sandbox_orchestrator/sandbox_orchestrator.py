from sandbox_toolkit.helpers.schema_models.schema import SandboxConfig, ComputeConfig, DatabaseConfig, ResourceUnit, Tools, DatabaseType
from sandbox_toolkit.helpers.exceptions.exceptions import SandboxError
from sandbox_toolkit.infra.sandbox_orchestrator.schema import *
from sandbox_toolkit.infra.sandbox_orchestrator.docker_simulator import *
import docker
import logging

logger = logging.getLogger(__name__)

class SandboxOrchestrator:
    def __init__(self):
        self.sandboxes = {} # Dictionary to store created sandboxes, key: sandbox_id, value: {"sandbox_config": SandboxConfig, "sandbox_url": str, "sandbox_network_id": str}
        self.docker_client = docker.from_env() # Initialize docker_client

    async def create_sandbox(self, request: CreateSandboxRequest) -> CreateSandboxResponse:
        sandbox_config = request.sandbox_config
        sandbox_id = f"sandbox_{len(self.sandboxes) + 1}" # Generate sandbox_id
        logger.debug(f"Orchestrator: Creating sandbox with id {sandbox_id}")
        self.sandboxes[sandbox_id] = {"sandbox_config": sandbox_config, "sandbox_url": None, "sandbox_network_id": None} # Store sandbox_config and sandbox info in sandboxes dictionary
        return CreateSandboxResponse(sandbox_id=sandbox_id, sandbox_url="") # Sandbox URL is empty string for now

    async def start_sandbox(self, request: StartSandboxRequest) -> StartSandboxResponse:
        sandbox_id = request.sandbox_id
        logger.debug(f"SandboxOrchestrator: Starting sandbox {sandbox_id}") # Added logging
        if sandbox_id not in self.sandboxes:
            raise SandboxError(f"Sandbox with id '{sandbox_id}' not found.")
        
        sandbox_config = self.sandboxes[sandbox_id]["sandbox_config"] # Retrieve sandbox config from sandboxes dictionary

        # 1. Dynamically modify the Dockerfile of sandbox base to add user's tool (skipped in simulation)
        dockerfile_path = Path("/workspace/src/sandbox_toolkit/infra/sandbox_base/Dockerfile.sandboxbase") # Placeholder path
        image_name = f"sandbox_image_{sandbox_id}" # Example image name

        # 2. Build sandbox image (simulated)
        build_request = DockerImageBuildRequest(dockerfile_path=dockerfile_path, image_name=image_name)
        build_response = await build_docker_image(build_request)
        sandbox_image_id = build_response.image_id
        logger.debug(f"Orchestrator: Docker image built: {sandbox_image_id}")

        # 3. Create sandbox network (simulated)
        network_name = f"sandbox_network_{sandbox_image_id}"
        network_create_request = DockerNetworkCreateRequest(network_name=network_name)
        network_create_response = await create_docker_network(network_create_request)
        sandbox_network_id = network_create_response.network_id
        logger.debug(f"Orchestrator: Docker network created: {network_name}, id: {sandbox_network_id}")

        # 4. Dynamically write sandbox docker-compose file (skipped in simulation)

        # 5. Deploy sandbox service using docker-compose (simulated)
        container_name = f"sandbox_container_{sandbox_image_id}" # Example container name
        ports_mapping = {5000: 51379} # Example port mapping, mapping container port 5000 to host port 51379
        container_run_kwargs = { # Define keyword arguments for container run
            'image_name': image_name,
            'container_name': container_name,
            'ports_mapping': ports_mapping,
            'network_name': sandbox_network_id,
            'detach': True,
            'labels': {"sandbox.id": sandbox_id} # Add label for filtering
        }
        container_run_request = DockerContainerRunRequest(**container_run_kwargs)
        container_run_response = await run_docker_container(container_run_request)
        sandbox_container_id = container_run_response.container_id
        sandbox_url = container_run_response.container_url
        logger.debug(f"Orchestrator: Running Docker container: {container_name}, container_id: {sandbox_container_id}, url: {sandbox_url}")

        self.sandboxes[sandbox_id]["sandbox_url"] = sandbox_url # Store sandbox_url in sandboxes dictionary
        self.sandboxes[sandbox_id]["sandbox_network_id"] = sandbox_network_id # Store sandbox_network_id in sandboxes dictionary

        # 7. Attach databases to sandbox network (simulated)
        database_containers = []
        if sandbox_config.database_config and sandbox_config.database_config.database_type: # Check if database_config and database_type are not None
            if sandbox_config.database_config.database_type == DatabaseType.VECTOR:
                vector_db_container_name = "qdrant_db" # Assuming vector database container name is qdrant_db
                database_containers.append(vector_db_container_name)
            elif sandbox_config.database_config.database_type == DatabaseType.GRAPH:
                graph_db_container_name = "neo4j_db" # Assuming graph database container name is neo4j_db
                database_containers.append(graph_db_container_name)

        for db_container_name in database_containers:
            db_container = self.docker_client.containers.get(db_container_name)
            network = self.docker_client.networks.get(sandbox_network_id)
            network.connect(db_container)
            logger.debug(f"Orchestrator: Attached database container {db_container_name} to sandbox network {sandbox_network_id}")

        return StartSandboxResponse()

    async def stop_sandbox(self, request: StopSandboxRequest) -> StopSandboxResponse:
        sandbox_id = request.sandbox_id
        logger.debug(f"SandboxOrchestrator: Stopping sandbox {sandbox_id}") # Added logging
        if sandbox_id not in self.sandboxes:
            raise SandboxError(f"Sandbox with id '{sandbox_id}' not found.")
        # 1. Simulate stopping sandbox container
        container_stop_request = DockerContainerStopRequest(container_id=sandbox_id)
        container_stop_response = await stop_docker_container(container_stop_request)

        # 2. Simulate deleting sandbox network
        sandbox_network_id = self.sandboxes[sandbox_id]["sandbox_network_id"] # Retrieve sandbox_network_id from sandboxes dictionary
        network_delete_request = DockerNetworkDeleteRequest(network_id=sandbox_network_id)
        network_delete_response = await delete_docker_network(network_delete_request)
        logger.debug(f"SandboxOrchestrator: Deleting Docker network: {sandbox_id}")

        del self.sandboxes[sandbox_id] # Remove sandbox from sandboxes dictionary
        return StopSandboxResponse()

    async def get_sandbox_url(self, request: GetSandboxUrlRequest) -> GetSandboxUrlResponse:
        sandbox_id = request.sandbox_id
        if sandbox_id not in self.sandboxes:
            raise SandboxError(f"Sandbox with id '{sandbox_id}' not found.")
        sandbox_url = self.sandboxes[sandbox_id]["sandbox_url"] # Retrieve sandbox_url from sandboxes dictionary
        return GetSandboxUrlResponse(sandbox_url=sandbox_url)

    async def close(self):
        await self.client.aclose()
