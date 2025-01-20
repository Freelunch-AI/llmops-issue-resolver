import asyncio
import logging
from typing import List, Dict, Optional
import docker
from pathlib import Path
import shutil
import httpx
import time
from functools import wraps

logger = logging.getLogger(__name__)

class CleanupError(Exception):
    """Raised when cleanup fails."""
    def __init__(self, message: str, details: Dict[str, str]):
        self.details = details
        super().__init__(message)

def retry_on_error(max_attempts=3, delay=1):
    """Decorator to retry operations on failure with exponential backoff."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay

            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {str(e)}. Retrying...")
                        await asyncio.sleep(current_delay)
                        current_delay *= 2  # Exponential backoff
                    else:
                        logger.error(f"All {max_attempts} attempts failed for {func.__name__}: {str(e)}")

            raise last_exception
        return wrapper
    return decorator

class ResourceCleaner:
    def __init__(
        self,
        gateway_url: str,
        sandboxes_path: Path,
        sandbox_manager,
        docker_client: Optional[docker.DockerClient] = None
    ):
        self.gateway_url = gateway_url
        self.sandboxes_path = sandboxes_path
        self.sandbox_manager = sandbox_manager
        self.docker_client = docker_client or docker.from_env()
        self.http_client = httpx.AsyncClient()
        self._cleanup_task = None
        self.sandbox_locks = {}
    async def cleanup_sandbox(
        self,
        sandbox_id: str,
        timeout: int = 60  # Increased default timeout
    ) -> None:
        """Clean up all resources associated with a sandbox."""
        errors = {}
        # Get or create lock for this sandbox
        lock = await self._get_sandbox_lock(sandbox_id)
        
        async with lock:
            try:
                # Stop containers
                await asyncio.wait_for(
                    self._stop_containers(sandbox_id),
                    timeout=timeout/2  # Split timeout between operations
                )
                
                # Verify containers are removed
                await self._verify_containers_removed(sandbox_id)

                # Verify networks are cleaned up
                networks = self.docker_client.networks.list(
                    filters={"label": f"sandbox.id={sandbox_id}"}
                )
                if networks:
                    raise RuntimeError(f"Failed to remove all networks for sandbox {sandbox_id}")

                # Double check for any remaining containers
                containers = self.docker_client.containers.list(
                    filters={"label": f"sandbox.id={sandbox_id}"}
                )
                if containers:
                    raise RuntimeError(f"Failed to remove all containers for sandbox {sandbox_id}")
                    
            except Exception as e:
                errors["containers"] = str(e)
            try:
                # Unregister from gateway
                await asyncio.wait_for(
                    self._unregister_from_gateway(sandbox_id),
                    timeout=10
                )
            except Exception as e:
                errors["gateway"] = str(e)

            try:
                # Clean up files
                await self._cleanup_files(sandbox_id)
            except Exception as e:
                errors["files"] = str(e)
            
            # Clean up the lock if cleanup was successful
            if not errors:
                del self.sandbox_locks[sandbox_id]

        if errors:
            raise CleanupError(
                f"Failed to clean up sandbox {sandbox_id}",
                errors
            )

    async def cleanup_group(
        self,
        group_id: str,
        sandbox_ids: List[str],
        database_cleanup: Optional[callable] = None
    ) -> None:
        """Clean up a sandbox group and its databases."""
        sandbox_errors = {}
        failed_sandboxes = []
        successful_sandboxes = []

        # Clean up sandboxes first
        cleanup_tasks = []
        for sandbox_id in sandbox_ids:
            cleanup_tasks.append(self.cleanup_sandbox(sandbox_id))
        
        # Wait for all cleanup tasks to complete
        results = await asyncio.gather(*cleanup_tasks, return_exceptions=True)
        
        # Process results
        for sandbox_id, result in zip(sandbox_ids, results):
            if isinstance(result, Exception):
                sandbox_errors[sandbox_id] = str(result)
                failed_sandboxes.append(sandbox_id)
                logger.error(f"Failed to clean up sandbox {sandbox_id}: {result}")
            else:
                successful_sandboxes.append(sandbox_id)

        # Clean up databases if provided
        database_error = None
        if database_cleanup and not failed_sandboxes:  # Only proceed if all sandboxes were cleaned up
            try:
                await asyncio.wait_for(
                    database_cleanup(),
                    timeout=30
                )
            except Exception as e:
                database_error = str(e)
                logger.error(f"Failed to clean up databases: {e}")

        # Prepare comprehensive error report
        if sandbox_errors or database_error:
            error_details = {
                "failed_sandboxes": sandbox_errors,
                "successful_sandboxes": successful_sandboxes,
                "database_cleanup": database_error if database_error else "not attempted" if failed_sandboxes else "successful"
            }
            raise CleanupError(
                f"Failed to clean up group {group_id}",
                error_details
            )

    async def _stop_containers(self, sandbox_id: str) -> None:
        """Stop and remove containers for a sandbox."""
        failed_containers = []
        containers = self.docker_client.containers.list(
            filters={
                "label": f"sandbox.id={sandbox_id}"
            }
        )
        
        for container in containers:
            try:
                # Try stopping gracefully first
                try:
                    container.stop(timeout=10)
                except Exception as stop_error:
                    logger.warning(f"Failed to stop container {container.id} gracefully: {stop_error}")
                
                # Force remove if needed
                try:
                    container.remove(force=True)
                except Exception as remove_error:
                    logger.error(f"Failed to remove container {container.id}: {remove_error}")
                    failed_containers.append(container.id)
            except Exception as e:
                logger.error(f"Failed to stop container {container.id}: {e}")
                failed_containers.append(container.id)
        
        if failed_containers:
            raise RuntimeError(f"Failed to cleanup containers: {', '.join(failed_containers)}")

    async def _unregister_from_gateway(self, sandbox_id: str) -> None:
        """Unregister sandbox from gateway."""
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                response = await self.http_client.delete(
                    f"{self.gateway_url}/api/v1/sandboxes/{sandbox_id}"
                )
                response.raise_for_status()
                return
            except Exception as e:
                if attempt == max_attempts - 1:
                    raise
                logger.warning(f"Attempt {attempt + 1} failed to unregister sandbox {sandbox_id}: {e}")
                await asyncio.sleep(1 * (2 ** attempt))  # Exponential backoff

    async def _cleanup_files(self, sandbox_id: str) -> None:
        """Clean up sandbox files."""
        sandbox_dir = self.sandboxes_path / sandbox_id
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                if sandbox_dir.exists():
                    shutil.rmtree(sandbox_dir)
                # Verify cleanup
                if sandbox_dir.exists():
                    raise RuntimeError(f"Failed to remove sandbox directory {sandbox_dir}")
                return
            except Exception as e:
                if attempt == max_attempts - 1:
                    raise
                await asyncio.sleep(1 * (2 ** attempt))

    async def cleanup_network(self, network_name: str) -> None:
        """Clean up a Docker network."""
        max_retries = 3
        retry_delay = 1

        try:
            network = self.docker_client.networks.get(network_name)
            
            for attempt in range(max_retries):
                try:
                    # Force disconnect any connected containers
                    if network.attrs.get('Containers'):
                        for container_id in network.attrs['Containers']:
                            try:
                                network.disconnect(container_id, force=True)
                            except Exception as e:
                                logger.warning(f"Failed to disconnect container {container_id}: {e}")
                    
                    network.remove()
                    return
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    logger.warning(f"Attempt {attempt + 1} failed to remove network {network_name}: {e}")
                    await asyncio.sleep(retry_delay * (2 ** attempt))

        except docker.errors.NotFound:
            pass  # Network doesn't exist
        except Exception as e:
            logger.error(f"Failed to remove network {network_name}: {e}")
            raise

    async def __aenter__(self):
        return self
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Clean up any remaining locks
        self.sandbox_locks.clear()
        
        await self.http_client.aclose()
        self.docker_client.close()

    def _is_sandbox_inactive(self, sandbox_id: str) -> bool:
        """Check if a sandbox is inactive based on the inactivity threshold."""
        if sandbox_id not in self.sandbox_manager.sandboxes:
            return True

        last_activity = self.sandbox_manager.sandboxes[sandbox_id].get('last_activity')
        if not last_activity:
            return True

        current_time = asyncio.get_event_loop().time()
        return (current_time - last_activity) > self.sandbox_manager.inactivity_threshold

    async def get_inactive_sandboxes(self) -> List[str]:
        """Get a list of inactive sandbox IDs."""
        return [sandbox_id for sandbox_id in self.sandbox_manager.sandboxes.keys()
                if self._is_sandbox_inactive(sandbox_id)]

    async def _cleanup_inactive_sandboxes(self) -> None:
        """Clean up inactive sandboxes."""
        try:
            # Audit and cleanup obsolete locks first
            await self._audit_locks()
            
            inactive_sandboxes = await self.get_inactive_sandboxes()
            cleanup_tasks = []
            
            for sandbox_id in inactive_sandboxes:
                try:
                    logger.info(f"Cleaning up inactive sandbox {sandbox_id}")
                    cleanup_tasks.append(
                        asyncio.create_task(self.cleanup_sandbox(sandbox_id))
                    )
                except Exception as e:
                    logger.error(f"Error cleaning up sandbox {sandbox_id}: {e}")
                    # Continue with other sandboxes
            
            # Wait for all cleanup tasks to complete
            if cleanup_tasks:
                await asyncio.gather(*cleanup_tasks, return_exceptions=True)
                
        except Exception as e:
            logger.error(f"Error in cleanup task: {e}")

    async def _periodic_cleanup(self) -> None:
        """Periodic cleanup task."""
        while True:
            await self._cleanup_inactive_sandboxes()
            await asyncio.sleep(self.sandbox_manager.cleanup_interval)

    def start_cleanup_task(self) -> None:
        """Start the periodic cleanup task."""
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._periodic_cleanup())
            logger.info("Started periodic cleanup task")

    def stop_cleanup_task(self) -> None:
        """Stop the periodic cleanup task."""
        if self._cleanup_task is not None:
            self._cleanup_task.cancel()
            self._cleanup_task = None
            logger.info("Stopped periodic cleanup task")

    async def _get_sandbox_lock(self, sandbox_id: str) -> asyncio.Lock:
        """Get or create a lock for a sandbox."""
        if sandbox_id not in self.sandbox_locks:
            self.sandbox_locks[sandbox_id] = asyncio.Lock()
        return self.sandbox_locks[sandbox_id]

    async def _verify_containers_removed(self, sandbox_id: str, max_attempts: int = 3) -> None:
        """Verify that all containers for a sandbox are removed with retries."""
        for attempt in range(max_attempts):
            try:
                containers = self.docker_client.containers.list(
                    all=True,  # Include stopped containers
                    filters={"label": f"sandbox.id={sandbox_id}"}
                )
                
                if not containers:
                    return  # Success - no containers found
                
                if attempt < max_attempts - 1:
                    # Force remove any remaining containers
                    for container in containers:
                        try:
                            container.remove(force=True)
                        except Exception as e:
                            logger.warning(f"Error force removing container {container.id}: {e}")
                    
                    await asyncio.sleep(1 * (2 ** attempt))
                    continue
                
                # If we reach here on the last attempt, raise an error
                container_ids = [c.id for c in containers]
                raise RuntimeError(f"Failed to remove containers after {max_attempts} attempts: {container_ids}")
                
            except Exception as e:
                if attempt == max_attempts - 1:
                    raise RuntimeError(f"Error verifying container removal: {str(e)}")

    async def _audit_locks(self) -> None:
        """Audit and remove obsolete locks."""
        try:
            obsolete_locks = []
            for sandbox_id in list(self.sandbox_locks.keys()):
                # Check if sandbox still exists
                if sandbox_id not in self.sandbox_manager.sandboxes:
                    # Try to acquire the lock to ensure it's not in use
                    lock = self.sandbox_locks[sandbox_id]
                    if not lock.locked():
                        obsolete_locks.append(sandbox_id)
                    
            # Remove obsolete locks
            for sandbox_id in obsolete_locks:
                del self.sandbox_locks[sandbox_id]
                logger.debug(f"Removed obsolete lock for sandbox {sandbox_id}")
                
        except Exception as e:
            logger.error(f"Error during lock audit: {e}")