import io
import shutil
import tarfile
from pathlib import Path

import docker
import psutil

from sandbox_toolkit.helpers.exceptions.exceptions import ResourceError, SandboxError
from sandbox_toolkit.helpers.schema_models.internal_schemas import DatabaseType
from sandbox_toolkit.helpers.schema_models.networking_schemas import (
    ResourceAdjustmentRequest,
    ResourceAdjustmentResponse,
    SandboxCreateRequest,
    SandboxCreateResponse,
    SandboxGetUrlRequest,
    SandboxGetUrlResponse,
    SandboxStartRequest,
    SandboxStartResponse,
    SandboxStatusRequest,
    SandboxStatusResponse,
    SandboxStopRequest,
    SandboxStopResponse,
)
from sandbox_toolkit.logs.logging import logger


def get_host_resources():
    """
    Returns a dictionary containing host resource information (CPU, RAM, disk, memory_bandwidth, networking_bandwidth).
    """
    cpu_count = psutil.cpu_count()
    ram_total = psutil.virtual_memory().total / (1024 ** 3)  # Convert to GB
    disk_total = psutil.disk_usage('/').total / (1024 ** 3)  # Convert to GB
    memory_bandwidth = 0  # Placeholder value
    networking_bandwidth = 0  # Placeholder value
    return {
        "cpu_total": cpu_count,
        "ram_total": ram_total,
        "disk_total": disk_total,
        "memory_bandwidth": memory_bandwidth,
        "networking_bandwidth": networking_bandwidth
    }

def get_host_resource_usage():
    """
    Returns a dictionary containing host resource usage information (CPU, RAM, disk, memory_bandwidth, networking_bandwidth).
    """
    cpu_usage = psutil.cpu_percent()
    ram_usage = psutil.virtual_memory().percent
    disk_usage = psutil.disk_usage('/').percent
    memory_bandwidth_usage = 0  # Placeholder value
    networking_bandwidth_usage = 0  # Placeholder value
    return {
        "cpu_usage": cpu_usage,
        "ram_usage": ram_usage,
        "disk_usage": disk_usage,
        "memory_bandwidth_usage": memory_bandwidth_usage,
        "networking_bandwidth_usage": networking_bandwidth_usage
    }

class SandboxOrchestrator:
    def __init__(self):
        self.created_sandboxes = {}
        self.started_sandboxes = {}
        self.docker_client = docker.from_env() # Initialize docker_client
        self.sandbox_resource_measurements = {} # {sandbox_id: [{timestamp: , usage: {cpu: , ram: , disk: , memory_bandwidth: , networking_bandwidth: }}]}

    async def _take_resource_measurements(self, n=5):
        logger.info("SandboxOrchestrator: Taking resource measurements")
        for sandbox_id in self.started_sandboxes:
            container_name = f"sandbox_container_{sandbox_id}"
            try:
                container = self.docker_client.containers.get(container_name)
                stats = container.stats(
                    stream=False
                )
                
                cpu_usage = stats["cpu_stats"]["cpu_usage"]["total_usage"]
                ram_usage = stats["memory_stats"]["usage"]
                disk_usage = 0 # TODO: implement disk usage
                memory_bandwidth_usage = 0 # TODO: implement memory bandwidth usage
                networking_bandwidth_usage = 0 # TODO: implement networking bandwidth usage

                timestamp = stats["read"]
                usage = {
                    "cpu": cpu_usage,
                    "ram": ram_usage,
                    "disk": disk_usage,
                    "memory_bandwidth": memory_bandwidth_usage,
                    "networking_bandwidth": networking_bandwidth_usage
                }
                if sandbox_id not in self.sandbox_resource_measurements:
                    self.sandbox_resource_measurements[sandbox_id] = []
                self.sandbox_resource_measurements[sandbox_id].append({"timestamp": timestamp, "usage": usage})
                if len(self.sandbox_resource_measurements[sandbox_id]) > n:
                    self.sandbox_resource_measurements[sandbox_id].pop(0)
            except docker.errors.NotFound:
                logger.warning(f"Container {container_name} not found, skipping resource measurement")
            except Exception as e:
                logger.error(f"Error taking resource measurements for container {container_name}: {e}")
        logger.info("SandboxOrchestrator: Resource measurements taken")

    def _get_max_last_used_resources(self, sandbox_id):
        logger.info(f"SandboxOrchestrator: Getting max last used resources for sandbox {sandbox_id}")
        if sandbox_id not in self.sandbox_resource_measurements:
            logger.warning(f"No resource measurements found for sandbox {sandbox_id}")
            return None
        measurements = self.sandbox_resource_measurements[sandbox_id]
        if not measurements:
            logger.warning(f"No resource measurements found for sandbox {sandbox_id}")
            return None
        max_cpu = 0
        max_ram = 0
        max_disk = 0
        max_memory_bandwidth = 0
        max_networking_bandwidth = 0
        for measurement in measurements:
            usage = measurement["usage"]
            max_cpu = max(max_cpu, usage["cpu"])
            max_ram = max(max_ram, usage["ram"])
            max_disk = max(max_disk, usage["disk"])
            max_memory_bandwidth = max(max_memory_bandwidth, usage["memory_bandwidth"])
            max_networking_bandwidth = max(max_networking_bandwidth, usage["networking_bandwidth"])
        max_resources = {
            "cpu": max_cpu,
            "ram": max_ram,
            "disk": max_disk,
            "memory_bandwidth": max_memory_bandwidth,
            "networking_bandwidth": max_networking_bandwidth
        }
        logger.debug(f"Max last used resources for sandbox {sandbox_id}: {max_resources}")
        return max_resources

    async def create_sandbox(self, request: SandboxCreateRequest) -> SandboxCreateResponse:
        logger.info("SandboxOrchestrator: Creating sandbox")
        logger.debug(f"Inputs: {request}")

        sandbox_config = request.sandbox.sandbox_config
        user_knowledge_compressed_content = request.user_knowledge_compressed_content
        sandbox_id = f"sandbox_{len(self.created_sandboxes) + 1}"

        host_resources = get_host_resources()
        host_resources_used = get_host_resource_usage()
        requested_resources = sandbox_config.compute_config

        if requested_resources.cpu > host_resources["cpu_total"] - host_resources_used["'cpu_usage"]:
            raise ResourceError(f"Requested CPU ({requested_resources.cpu}) exceeds available CPU ({host_resources['cpu_total']})")
        if requested_resources.ram > host_resources["ram_total"] - host_resources_used["ram_usage"]:
            raise ResourceError(f"Requested RAM ({requested_resources.ram}) exceeds available RAM ({host_resources['ram_total']})")
        if requested_resources.disk > host_resources["disk_total"] - host_resources_used["disk_usage"]:
            raise ResourceError(f"Requested disk space ({requested_resources.disk}) exceeds available disk space ({host_resources['disk_total']})")
        if requested_resources.memory_bandwidth > host_resources["memory_bandwidth"] - host_resources_used["memory_bandwidth_usage"]:
            raise ResourceError(f"Requested memory bandwidth ({requested_resources.memory_bandwidth}) exceeds available memory bandwidth ({host_resources['memory_bandwidth']})")
        if requested_resources.networking_bandwidth > host_resources["networking_bandwidth"] - host_resources_used["networking_bandwidth_usage"]:
            raise ResourceError(f"Requested networking bandwidth ({requested_resources.networking_bandwidth}) exceeds available networking bandwidth ({host_resources['networking_bandwidth']})")
        
        self.created_sandboxes[sandbox_id] = {
            "sandbox_config": sandbox_config, 
            "sandbox_url": None, 
            "sandbox_network_id": None,
            "user_knowledge_compressed_content": user_knowledge_compressed_content
        } 
        
        logger.info(f"Sandbox created with id {sandbox_id}")
        logger.debug(f"Outputs: {sandbox_id}")
        return SandboxCreateResponse(sandbox_id=sandbox_id) 

    async def start_sandbox(self, request: SandboxStartRequest) -> SandboxStartResponse:
        logger.info(f"SandboxOrchestrator: Starting sandbox {sandbox_id}")
        logger.debug(f"Inputs: {request}")

        sandbox_id = request.sandbox_id
       
        if sandbox_id not in self.created_sandboxes:
            raise SandboxError(f"Sandbox with id '{sandbox_id}' not found.")
        
        sandbox_config = self.created_sandboxes[sandbox_id]["sandbox_config"]

        # 1. Recreate tool modules under tmp/tools directory
        # 1.1. Create tmp/tools directory
        # For each tool in sandbox_config.tools.tools: (1) extract module directory, (2) create module directory if it does not exist, (3) add function code
        # to the module directory 
        tools_dir = Path("/tmp/tools") # Create tmp/tools directory
        tools_dir.mkdir(parents=True, exist_ok=True)
        if sandbox_config.tools and sandbox_config.tools.tools:
            # tool is a Tool object with attributes: function_name, function_code and module_name
            for tool in sandbox_config.tools.tools:
                # join tools_dir with module_name to get the module directory path
                module_file = tools_dir / f"{tool.module_name}.py"
                # create file path if it does not exist
                module_file.touch(exist_ok=True)
                # apend function code to the python module file
                with open(module_file, "a") as f:
                    f.write(tool.function_code)

        # 2. Dynamically modify the Dockerfile of sandbox base to add user's tool and user's knowledge files
        dockerfile_path = Path("/workspace/src/sandbox_toolkit/infra/sandbox_base/Dockerfile.sandboxbase") # Placeholder path
        dockerfile_content = dockerfile_path.read_text()
        # user_knowledge_compressed_content was compresses like this:
        # with io.BytesIO() as byte_stream:
        #     with tarfile.open(fileobj=byte_stream, mode='w:gz') as tar:
        #         tar.add(directory, arcname=os.path.basename(directory))
        user_knowledge_compressed_content = self.created_sandboxes[sandbox_id]["user_knowledge_compressed_content"]

        # uncompress user_knowledge_compressed_content to /tmp/knowledge_files directory
        knowledge_files_dir = Path("/tmp/knowledge_files") # Create tmp/knowledge_files directory
        knowledge_files_dir.mkdir(parents=True, exist_ok=True)
        with io.BytesIO(user_knowledge_compressed_content) as byte_stream:
            with tarfile.open(fileobj=byte_stream, mode='r:gz') as tar:
                tar.extractall(knowledge_files_dir)

        tools_code = ""
        knowledge_files_code = ""

        tools_code.append("COPY /tools /tools") # Copy tools to /tools directory in the container
        knowledge_files_code.append("COPY /knowledge_files /knowledge_files") # Copy knowledge files to /knowledge_files directory in the container

        modified_dockerfile_content = dockerfile_content + "\n" + tools_code + "\n" + knowledge_files_code

        temp_dockerfile_path = Path(f"/tmp/Dockerfile.sandbox_{sandbox_id}") # Create temp Dockerfile
        temp_dockerfile_path.write_text(modified_dockerfile_content)
        dockerfile_path = temp_dockerfile_path # Use temp Dockerfile for build
        image_name = f"sandbox_image_{sandbox_id}" # Example image name

        # copies all directories and files from /workspace/src/sandbox_toolkit/infra/sandbox_base to /tmp
        source_dir = Path("/workspace/src/sandbox_toolkit/infra/sandbox_base")
        destination_dir = Path("/tmp")
        if source_dir.exists() and source_dir.is_dir():
            for item in source_dir.iterdir():
                s = source_dir / item.name
                d = destination_dir / item.name
                if s.is_dir():
                    shutil.copytree(s, d, dirs_exist_ok=True)
                else:
                    shutil.copy2(s, d)

        # 2. Build sandbox image (actual docker build)
        dockerfile = dockerfile_path.read_text() # Read Dockerfile content
        build_context = "tmp" # Assuming build context is the current directory
        try:
            image, logs = self.docker_client.images.build(
                dockerfile=dockerfile,
                path=build_context,
                tag=image_name,
                nocache=True # Disable cache for development, remove in production
            )
            for log in logs: # Print build logs
                logger.debug(log)
            sandbox_image_id = image.id
            logger.debug(f"Orchestrator: Docker image built: {sandbox_image_id}")
        except docker.errors.BuildError as e:
            logger.error(f"Docker build failed: {e}")
            raise SandboxError(f"Docker build failed: {e}")

        # 3. Create sandbox network (actual docker network creation)
        network_name = f"sandbox_network_{sandbox_id}"
        try:
            sandbox_network = self.docker_client.networks.create(network_name)
            sandbox_network_id = sandbox_network.id
            logger.debug(f"Orchestrator: Docker network created: {network_name}, id: {sandbox_network_id}")
        except docker.errors.APIError as e:
            logger.error(f"Docker network creation failed: {e}")
            raise SandboxError(f"Docker network creation failed: {e}")

        # 4. Deploy sandbox service 
        container_name = f"sandbox_container_{sandbox_id}" # Example container name
        ports_mapping = {5000: 51379} # Example port mapping, mapping container port 5000 to host port 51379
        container_run_kwargs = { # Define keyword arguments for container run
            'image': image_name, # Use image_name instead of image_id
            'name': container_name,
            'ports': ports_mapping, # Use 'ports' instead of 'ports_mapping'
            'network': sandbox_network_id, # Use 'network' instead of 'network_name'
            'detach': True,
            'labels': {"sandbox.id": sandbox_id} # Add label for filtering
        }
        try:
            container = self.docker_client.containers.run(**container_run_kwargs)
            sandbox_container_id = container.id
            sandbox_url = f"http://localhost:{ports_mapping[5000]}" # Construct sandbox URL
            logger.debug(f"Orchestrator: Running Docker container: {container_name}, container_id: {sandbox_container_id}, url: {sandbox_url}")
        except docker.errors.ContainerError as e:
            logger.error(f"Docker container run failed: {e}")
            raise SandboxError(f"Docker container run failed: {e}")

        self.started_sandboxes[sandbox_id]["sandbox_url"] = sandbox_url # Store sandbox_url in sandboxes dictionary
        self.started_sandboxes[sandbox_id]["sandbox_network_id"] = sandbox_network_id # Store sandbox_network_id in sandboxes dictionary

        # 5. Attach databases to sandbox network
        database_containers = []
        if sandbox_config.database_config and sandbox_config.database_config.database_type: # Check if database_config and database_type are not None
            if sandbox_config.database_config.database_type == DatabaseType.VECTOR:
                vector_db_container_name = "qdrant_db" # Assuming vector database container name is qdrant_db
                database_containers.append(vector_db_container_name)
            elif sandbox_config.database_config.database_type == DatabaseType.GRAPH:
                graph_db_container_name = "neo4j_db" # Assuming graph database container name is neo4j_db
                database_containers.append(graph_db_container_name)

        response = SandboxStartResponse(sandbox_url=sandbox_url)
        logger.info(f"SandboxOrchestrator: Sandbox {sandbox_id} started ")
        logger.debug(f"Outputs: {response}")
        return response

    async def stop_sandbox(self, sandbox_id) -> SandboxStopResponse:
        logger.info(f"SandboxOrchestrator: Sandbox stopping ")
        logger.debug(f"Inputs: {sandbox_id}")

        logger.debug(f"SandboxOrchestrator: Stopping sandbox {sandbox_id}") # Added logging
        if sandbox_id not in self.started_sandboxes:
            raise SandboxError(f"Sandbox with id '{sandbox_id}' not found.")
        sandbox_info = self.started_sandboxes[sandbox_id]
        sandbox_network_id = sandbox_info["sandbox_network_id"]

        # 1. Stop sandbox container (actual docker container stop)
        container_name = f"sandbox_container_{sandbox_id}" # Construct container name
        try:
            container = self.docker_client.containers.get(container_name)
            container.stop()
            logger.debug(f"Orchestrator: Stopped Docker container: {container_name}")
        except docker.errors.NotFound:
            logger.warning(f"Docker container {container_name} not found, assuming already stopped.")
        except docker.errors.APIError as e:
            logger.error(f"Error stopping Docker container {container_name}: {e}")
            raise SandboxError(f"Error stopping Docker container {container_name}: {e}")

        # 2. Delete sandbox network (actual docker network delete)
        network_name = f"sandbox_network_{sandbox_id}" # Construct network name
        try:
            sandbox_network = self.docker_client.networks.get(network_name)
            sandbox_network.remove()
            logger.debug(f"Orchestrator: Deleted Docker network: {network_name}, id: {sandbox_network_id}")
        except docker.errors.NotFound:
            logger.warning(f"Docker network {network_name} not found, assuming already deleted.")
        except docker.errors.APIError as e:
            logger.error(f"Error deleting Docker network {network_name}: {e}")
            raise SandboxError(f"Error deleting Docker network {network_name}: {e}")

        del self.started_sandboxes[sandbox_id]

        response = SandboxStopResponse()

        logger.info(f"SandboxOrchestrator: Sandbox {sandbox_id} stopped ")
        logger.debug(f"Outputs: {response}")
        return response

    async def get_sandbox_url(self, request: SandboxGetUrlRequest) -> SandboxGetUrlResponse:
        logger.info(f"SandboxOrchestrator: Getting sandbox URL ")
        logger.debug(f"Inputs: {request}")

        sandbox_id = request.sandbox_id
        if sandbox_id not in self.started_sandboxes:
            raise SandboxError(f"Sandbox with id '{sandbox_id}' not found.")
        sandbox_url = self.started_sandboxes[sandbox_id]["sandbox_url"] # Retrieve sandbox_url from sandboxes dictionary

        logger.info(f"SandboxOrchestrator: Sandbox URL retrieved ")
        logger.debug(f"Outputs: {sandbox_url}")
        return SandboxGetUrlResponse(sandbox_url=sandbox_url)

    async def adjust_allocated_resources(self, request: ResourceAdjustmentRequest) -> ResourceAdjustmentResponse:
        logger.info("SandboxOrchestrator: Adjusting allocated resources")
        logger.debug(f"Inputs: {request}")
        multiplier = request.multiplier
        for sandbox_id in self.created_sandboxes:
            if sandbox_id not in self.started_sandboxes:
                logger.warning(f"Sandbox with id '{sandbox_id}' not found in started sandboxes, skipping resource adjustment")
                continue
            sandbox_config = self.created_sandboxes[sandbox_id]["sandbox_config"]
            previous_allocated_resources = sandbox_config.compute_config
            
            max_last_used_resources = self._get_max_last_used_resources(sandbox_id)
            if not max_last_used_resources:
                logger.warning(f"Could not get max last used resources for sandbox {sandbox_id}, skipping resource adjustment")
                continue
            new_allocated_resources = previous_allocated_resources
            new_allocated_resources.cpu = min(int(max_last_used_resources["cpu"] * multiplier), previous_allocated_resources.cpu)
            new_allocated_resources.ram = min(int(max_last_used_resources["ram"] * multiplier), previous_allocated_resources.ram)
            new_allocated_resources.disk = min(int(max_last_used_resources["disk"] * multiplier), previous_allocated_resources.disk)
            new_allocated_resources.memory_bandwidth = min(int(max_last_used_resources["memory_bandwidth"] * multiplier), previous_allocated_resources.memory_bandwidth)
            new_allocated_resources.networking_bandwidth = min(int(max_last_used_resources["networking_bandwidth"] * multiplier), previous_allocated_resources.networking_bandwidth)
            
            await self.stop_sandbox(sandbox_id)
            sandbox_config.compute_config = new_allocated_resources
            await self.start_sandbox(sandbox_id)
            logger.debug(f"Sandbox {sandbox_id} resources adjusted to {new_allocated_resources}")
        response = ResourceAdjustmentResponse()
        logger.info("SandboxOrchestrator: Allocated resources adjusted")
        logger.debug(f"Outputs: {response}")
        return response

    async def get_sandbox_status(self, request: SandboxStatusRequest) -> SandboxStatusResponse:
        logger.info("SandboxOrchestrator: Getting sandbox status")
        logger.debug(f"Inputs: {request}")
        sandbox_id = request.sandbox_id
        if sandbox_id not in self.started_sandboxes:
            raise SandboxError(f"Sandbox with id '{sandbox_id}' not found.")
        container_name = f"sandbox_container_{sandbox_id}"
        try:
            container = self.docker_client.containers.get(container_name)
            container_status = container.status
        except docker.errors.NotFound:
            container_status = "not found"
        sandbox_info = self.started_sandboxes[sandbox_id]
        sandbox_url = sandbox_info["sandbox_url"]
        response = SandboxStatusResponse(
            container_status=container_status,
            id=sandbox_id,
            name=container_name,
            endpoint=sandbox_url,
            last_activity="now" # TODO: implement last activity
        )
        logger.info("SandboxOrchestrator: Sandbox status retrieved")
        logger.debug(f"Outputs: {response}")
        return response
