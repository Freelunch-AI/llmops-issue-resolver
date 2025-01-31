import asyncio
import os
import yaml
import httpx
import subprocess
import docker
import logging
import shutil
from datetime import datetime, timedelta
from ..databases.vector_db.vector_db import VectorDatabase
from ..databases.graph_db.graph_db import GraphDatabase
from pathlib import Path
from typing import Dict, List, Optional
from .cleanup import ResourceCleaner
from .models import (
    SandboxConfig,
    SandboxEndpoint,
    SandboxGroupEndpoints,
    DatabasesConfig,
    ResourceStatus,
    ResourceUsageHistory,
    ResourceError)
class SandboxManager:
    def __init__(
        self,
        gateway_url: str,
        inactivity_threshold: int = 3600,  # 1 hour
        cleanup_interval: int = 300  # 5 minutes
    ):
        self.gateway_url = gateway_url
        self.template_path = Path(__file__).parent.parent / "templates" / "sandbox-compose.yml.template"
        self.sandboxes_path = Path(__file__).parent.parent / "sandboxes"
        self.sandboxes_path.mkdir(exist_ok=True)
        self.inactivity_threshold = inactivity_threshold
        self.cleanup_interval = cleanup_interval
        self.sandboxes = {}
        self._sandbox_locks = {}
        self._resource_lock = asyncio.Lock()
        self._locks_lock = asyncio.Lock()
        self.total_resources = ResourceStatus()
        self.used_resources = ResourceStatus()
        self.resource_history = {}
        self._resource_monitor_task = None
        self.logger = logging.getLogger(__name__)
        self.graph_db = None
        self.vector_db = None
        self.docker_client = docker.from_env()
        # Initialize ResourceCleaner for proper cleanup handling
        self.resource_cleaner = ResourceCleaner(gateway_url, self.sandboxes_path, self, self.docker_client)

        # Constants for timeouts
        self.CONTAINER_START_TIMEOUT = 60  # seconds
        self.CONTAINER_HEALTH_CHECK_TIMEOUT = 30  # seconds
        self.CONTAINER_STOP_TIMEOUT = 10  # seconds

    def _create_sandbox_compose(
        self,
        sandbox_id: str,
        config: SandboxConfig,
        api_key: str
    ) -> Path:
        """Create a docker-compose file for a sandbox."""
        # Load template
        with open(self.template_path) as f:
            template = f.read()

        # Replace placeholders
        compose_content = template.format(
            id=sandbox_id,
            api_key=api_key,
            cpu_limit=str(config.compute_resources['cpu_cores']),
            memory_limit=f"{config.compute_resources['ram_gb']}G"
        )

        # Create sandbox directory
        sandbox_dir = self.sandboxes_path / sandbox_id
        sandbox_dir.mkdir(exist_ok=True)

        # Write docker-compose file
        compose_path = sandbox_dir / "docker-compose.yml"
        compose_path.write_text(compose_content)
        return compose_path

    async def _collect_resource_usage(self, sandbox_id: str) -> ResourceStatus:
        """Collect resource usage data for a sandbox using Docker stats."""
        try:
            containers = self.docker_client.containers.list(
                filters={"label": f"sandbox.id={sandbox_id}"}
            )

            total_usage = ResourceStatus()
            for container in containers:
                stats = container.stats(stream=False)

                # Calculate CPU usage
                cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - \
                           stats['precpu_stats']['cpu_usage']['total_usage']
                system_delta = stats['cpu_stats']['system_cpu_usage'] - \
                              stats['precpu_stats']['system_cpu_usage']
                cpu_usage = (cpu_delta / system_delta) * 100.0

                # Calculate memory usage in GB
                memory_usage = stats['memory_stats']['usage'] / (1024 * 1024 * 1024)

                total_usage.cpu_cores += cpu_usage
                total_usage.ram_gb += memory_usage

            return total_usage

        except Exception as e:
            self.logger.error(f"Error collecting resource usage for sandbox {sandbox_id}: {str(e)}")
            return ResourceStatus()

    async def create_sandbox(
        self,
        sandbox_id: str,
        tools: List[str],
        compute_resources: Dict,
        environment: Dict[str, str] = None
    ) -> SandboxEndpoint:
        """Create and start a new sandbox with proper rollback and error handling."""
        # First acquire the resource lock to check and allocate resources atomically
        async with self._resource_lock:
            required_resources = ResourceStatus(
                cpu_cores=compute_resources['cpu_cores'],
                ram_gb=compute_resources['ram_gb']
            )
            
            available_resources = ResourceStatus(
                cpu_cores=self.total_resources.cpu_cores - self.used_resources.cpu_cores,
                ram_gb=self.total_resources.ram_gb - self.used_resources.ram_gb
            )
            
            if not available_resources.has_sufficient(required_resources):
                raise ResourceError("Insufficient resources available")
            
            # Allocate resources
            self.used_resources.cpu_cores += compute_resources['cpu_cores']
            self.used_resources.ram_gb += compute_resources['ram_gb']
            
            self._sandbox_locks[sandbox_id] = asyncio.Lock()
        
        resources_allocated = False
        endpoint_info = None
        compose_path = None
        
        async with self._sandbox_locks[sandbox_id]:
            config = SandboxConfig(
                id=sandbox_id,
                tools=tools,
                compute_resources=compute_resources,
                environment=environment or {}
            )
            
            try:
                # First register with gateway to get API key
                self.logger.info(f"Registering sandbox {sandbox_id} with gateway")
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self.gateway_url}/api/v1/sandboxes/register",
                        json={
                            "sandbox_id": sandbox_id,
                            "name": f"Sandbox {sandbox_id}",
                            "endpoint": f"http://{sandbox_id}:8000"  # Internal docker network endpoint
                        }
                    )
                    response.raise_for_status()
                    endpoint_info = response.json()
                
                # Create docker-compose file
                self.logger.info(f"Creating docker-compose file for sandbox {sandbox_id}")
                compose_path = self._create_sandbox_compose(
                    config.id,
                    config,
                    endpoint_info["api_key"]
                )
                
                # Start sandbox containers
                self.logger.info(f"Starting containers for sandbox {sandbox_id}")
                try:
                    result = subprocess.run(
                        ["docker-compose", "-f", str(compose_path), "up", "-d"],
                        check=True,
                        capture_output=True,
                        timeout=self.CONTAINER_START_TIMEOUT
                    )
                    
                    # Wait for containers to be healthy
                    await self._wait_for_containers_health(sandbox_id)
                    
                except subprocess.TimeoutExpired:
                    raise RuntimeError(f"Timeout while starting sandbox {sandbox_id}")
                except subprocess.CalledProcessError as e:
                    raise RuntimeError(f"Failed to start sandbox {sandbox_id}: {e.stderr.decode()}")
                
                # Verify all containers are running
                containers = self.docker_client.containers.list(
                    filters={"label": f"sandbox.id={sandbox_id}"}
                )
                if not containers:
                    raise RuntimeError(f"No containers found for sandbox {sandbox_id}")
                
                self.logger.info(f"Successfully created sandbox {sandbox_id}")
                
                # Initialize resource history
                self.resource_history[sandbox_id] = ResourceUsageHistory()
                initial_usage = await self._collect_resource_usage(sandbox_id)
                self.resource_history[sandbox_id].add_measurement(initial_usage)
                
                resources_allocated = True
                return SandboxEndpoint(**endpoint_info)
                
            except Exception as e:
                self.logger.error(f"Error creating sandbox {sandbox_id}: {str(e)}")
                
                # Use ResourceCleaner for proper cleanup
                try:
                    await self.resource_cleaner.cleanup_sandbox(sandbox_id)
                except Exception as cleanup_error:
                    self.logger.error(f"Error during cleanup after failed creation: {cleanup_error}")
                
                # Release allocated resources if they were allocated but not successfully used
                if not resources_allocated:
                    async with self._resource_lock:
                        self.used_resources.cpu_cores -= compute_resources['cpu_cores']
                        self.used_resources.ram_gb -= compute_resources['ram_gb']
                
                raise
    
    async def delete_sandbox(self, sandbox_id: str):
        """Stop and remove a sandbox with proper resource cleanup."""
        try:
            # Unregister from gateway first
            async with httpx.AsyncClient() as client:
                try:
                    await client.delete(f"{self.gateway_url}/api/v1/sandboxes/{sandbox_id}")
                except Exception as e:
                    self.logger.error(f"Error unregistering sandbox {sandbox_id} from gateway: {e}")

            # Release resources and clean up tracking
            async with self._resource_lock:
                if sandbox_id in self.sandboxes:
                    config = self.sandboxes[sandbox_id]
                    self.used_resources.cpu_cores -= config.compute_resources['cpu_cores']
                    self.used_resources.ram_gb -= config.compute_resources['ram_gb']
                    del self.sandboxes[sandbox_id]

                # Remove resource history
                if sandbox_id in self.resource_history:
                    del self.resource_history[sandbox_id]

            # Clean up containers and networks
            compose_path = self.sandboxes_path / sandbox_id / "docker-compose.yml"
            if compose_path.exists():
                try:
                    # Stop containers
                    result = subprocess.run(
                        ["docker-compose", "-f", str(compose_path), "down", "--remove-orphans", "--volumes"],
                        check=True,
                        capture_output=True,
                        timeout=self.CONTAINER_STOP_TIMEOUT
                    )
                except subprocess.TimeoutExpired:
                    # Force remove containers if timeout
                    containers = self.docker_client.containers.list(
                        filters={"label": f"sandbox.id={sandbox_id}"}
                    )
                    for container in containers:
                        try:
                            container.remove(force=True)
                        except Exception as e:
                            self.logger.error(f"Error force removing container: {e}")
                except subprocess.CalledProcessError as e:
                    self.logger.error(f"Error stopping sandbox {sandbox_id}: {e.stderr.decode()}")

            # Clean up networks
            try:
                networks = self.docker_client.networks.list(
                    filters={"name": f".*_{sandbox_id}"}
                )
                for network in networks:
                    try:
                        network.remove()
                    except Exception as e:
                        self.logger.error(f"Error removing network {network.name}: {e}")
            except Exception as e:
                self.logger.error(f"Error cleaning up networks for sandbox {sandbox_id}: {e}")

            # Remove the sandbox directory using shutil.rmtree
            sandbox_dir = self.sandboxes_path / sandbox_id
            if sandbox_dir.exists():
                try:
                    shutil.rmtree(sandbox_dir)
                except Exception as e:
                    self.logger.error(f"Error removing sandbox directory {sandbox_dir}: {e}")

            # Clean up sandbox lock
            async with self._locks_lock:
                if sandbox_id in self._sandbox_locks:
                    del self._sandbox_locks[sandbox_id]

        except Exception as e:
            self.logger.error(f"Error during sandbox {sandbox_id} cleanup: {e}")
            raise
    
    async def create_sandbox_group(
        self,
        configs: List[SandboxConfig]
    ) -> SandboxGroupEndpoints:
        """Create and start a group of sandboxes."""
        endpoints = []
        created = []
        
        try:
            for config in configs:
                endpoint = await self.create_sandbox(config)
                endpoints.append(endpoint)
                created.append(config.id)
            
            return SandboxGroupEndpoints(
                sandboxes=endpoints
            )
            
        except Exception as e:
            # Cleanup any created sandboxes
            for sandbox_id in created:
                await self.delete_sandbox(sandbox_id)
            raise
    
    async def delete_sandbox_group(self, sandbox_ids: List[str]):
        """Stop and remove a group of sandboxes."""
        for sandbox_id in sandbox_ids:
            await self.delete_sandbox(sandbox_id)
            
    async def start_databases(self, config: DatabasesConfig):
        """Start and initialize databases."""
        try:
            # Initialize Neo4j connection
            neo4j_uri = f"neo4j://{config.graph_db.host}:{config.graph_db.port}"
            self.graph_db = GraphDatabase(
                uri=neo4j_uri,
                user=config.graph_db.credentials['user'],
                password=config.graph_db.credentials['password']
            )
            
            # Initialize Qdrant connection
            self.vector_db = VectorDatabase(
                host=config.vector_db.host,
                port=config.vector_db.port
            )
            
            # Test connections by executing simple operations
            await self.graph_db.execute_query("RETURN 1")
            await self.vector_db.create_collection(
                collection_name="test_connection",
                vector_size=4
            )
            await self.vector_db.delete_collection("test_connection")
            
        except Exception as e:
            # Clean up any successful connections before re-raising
            await self.stop_databases()
            raise RuntimeError(f"Failed to initialize databases: {str(e)}") from e

    async def stop_databases(self):
        """Stop all databases."""
        try:
            # Close Neo4j connection if it exists
            if self.graph_db is not None:
                self.graph_db.close()
                self.graph_db = None
            
            # Close Qdrant connection if it exists
            if self.vector_db is not None:
                self.vector_db.close()
                self.vector_db = None
                
        except Exception as e:
            # Log error but don't re-raise as this is cleanup code
            logging.error(f"Error while stopping databases: {str(e)}")

    async def cleanup(self):
        """Clean up all resources."""
        # Stop all sandboxes
        for sandbox_id in list(self.sandboxes.keys()):
            await self.delete_sandbox(sandbox_id)
        # Stop all databases
        await self.stop_databases()
    
    async def _wait_for_containers_health(self, sandbox_id: str) -> None:
        """Wait for all containers in a sandbox to be healthy with individual timeouts."""
        start_time = datetime.now()
        global_timeout = timedelta(seconds=self.CONTAINER_HEALTH_CHECK_TIMEOUT)
        container_timeout = timedelta(seconds=10)  # Individual container timeout
        
        while (datetime.now() - start_time) < global_timeout:
            try:
                containers = self.docker_client.containers.list(
                    filters={"label": f"sandbox.id={sandbox_id}"}
                )
                
                if not containers:
                    self.logger.error(f"No containers found for sandbox {sandbox_id}")
                    raise RuntimeError(f"No containers found for sandbox {sandbox_id}")
                
                container_statuses = {}
                all_healthy = True
                
                for container in containers:
                    try:
                        container.reload()  # Refresh container state
                        container_id = container.id[:12]  # Short ID for logging
                        
                        # Check if container is still running
                        if container.status != 'running':
                            self.logger.error(f"Container {container_id} in sandbox {sandbox_id} is not running. Status: {container.status}")
                            raise RuntimeError(f"Container {container_id} is not running")
                        
                        # Check container health status
                        health = container.attrs.get('State', {}).get('Health', {})
                        status = health.get('Status')
                        container_statuses[container_id] = status
                        
                        if status not in ['healthy', None]:  # None means no healthcheck defined
                            all_healthy = False
                            self.logger.warning(f"Container {container_id} in sandbox {sandbox_id} is not healthy. Status: {status}")
                            
                            # Check individual container timeout
                            container_start = datetime.fromtimestamp(container.attrs['State']['StartedAt'])
                            if datetime.now() - container_start > container_timeout:
                                raise RuntimeError(f"Container {container_id} health check timeout exceeded")
                    
                    except Exception as e:
                        self.logger.error(f"Error checking container {container_id} health: {str(e)}")
                        raise
                
                if all_healthy:
                    self.logger.info(f"All containers in sandbox {sandbox_id} are healthy: {container_statuses}")
                    return
                
                await asyncio.sleep(1)
                
            except Exception as e:
                self.logger.error(f"Error during health check for sandbox {sandbox_id}: {str(e)}")
                raise RuntimeError(f"Error checking container health: {str(e)}")
        self.logger.error(f"Global timeout exceeded waiting for containers in sandbox {sandbox_id}")
        raise RuntimeError(f"Timeout waiting for containers to be healthy in sandbox {sandbox_id}")
    
    async def adjust_sandbox_resources(self, x_percentage: float = 1.3):
        """Adjust resource limits of sandboxes based on their usage history with proper thread safety."""
        async with self._resource_lock:
            # Create a copy of sandbox IDs to avoid modification during iteration
            sandbox_ids = list(self.resource_history.keys())

        for sandbox_id in sandbox_ids:
            try:
                # Get sandbox lock
                async with self._locks_lock:
                    if sandbox_id not in self._sandbox_locks:
                        continue
                    sandbox_lock = self._sandbox_locks[sandbox_id]

                async with sandbox_lock:
                    # Check if sandbox still exists
                    if sandbox_id not in self.resource_history:
                        continue

                    history = self.resource_history[sandbox_id]
                    # Get maximum resource usage from history
                    max_usage = history.get_max_usage()

                    # Calculate new limits
                    new_limits = ResourceStatus(
                        cpu_cores=max_usage.cpu_cores * x_percentage,
                        ram_gb=max_usage.ram_gb * x_percentage
                    )

                    # Update container limits
                    containers = self.docker_client.containers.list(
                        filters={"label": f"sandbox.id={sandbox_id}"}
                    )

                    for container in containers:
                        try:
                            container.update(
                                cpu_quota=int(new_limits.cpu_cores * 100000),
                                memory=int(new_limits.ram_gb * 1024 * 1024 * 1024)
                            )
                        except Exception as e:
                            self.logger.error(f"Error updating container {container.id} resources: {e}")
                            continue

                    self.logger.info(f"Adjusted resources for sandbox {sandbox_id} to {new_limits}")

            except Exception as e:
                self.logger.error(f"Error adjusting resources for sandbox {sandbox_id}: {str(e)}")
                continue