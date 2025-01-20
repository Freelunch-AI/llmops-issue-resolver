import os
import asyncio
import logging
import subprocess
import time
from datetime import datetime, timedelta
from typing import Optional, Dict
from pathlib import Path

logger = logging.getLogger(__name__)

class ServiceManager:
    def __init__(self, compose_file_path: str, inactivity_timeout: int = 1800):
        """
        Initialize the ServiceManager with Docker Compose configuration.
        
        Args:
            compose_file_path (str): Path to the docker-compose.yml file
            inactivity_timeout (int): Timeout in seconds before shutting down services (default: 30 minutes)
        """
        self.compose_file_path = Path(compose_file_path)
        self.inactivity_timeout = inactivity_timeout
        self.last_activity_time: Dict[str, float] = {}
        self.shutdown_tasks: Dict[str, asyncio.Task] = {}
        self._ensure_compose_file()

    def _ensure_compose_file(self) -> None:
        """Ensure the Docker Compose file exists at the specified location."""
        if not self.compose_file_path.exists():
            raise FileNotFoundError(f"Docker Compose file not found at {self.compose_file_path}")

    def start_services(self, services: Optional[list] = None) -> bool:
        """
        Start specified services or all services if none specified.
        
        Args:
            services (Optional[list]): List of service names to start
        
        Returns:
            bool: True if services started successfully, False otherwise
        """
        try:
            cmd = ["docker-compose", "-f", str(self.compose_file_path), "up", "-d"]
            if services:
                cmd.extend(services)
            
            subprocess.run(cmd, check=True)
            
            # Update last activity time for started services
            current_time = time.time()
            if services:
                for service in services:
                    self.last_activity_time[service] = current_time
            else:
                # Get all services from docker-compose
                running_services = self.get_running_services()
                for service in running_services:
                    self.last_activity_time[service] = current_time
            
            # Start inactivity monitoring
            self._start_inactivity_monitoring()
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to start services: {e}")
            return False

    def stop_services(self, services: Optional[list] = None) -> bool:
        """
        Stop specified services or all services if none specified.
        
        Args:
            services (Optional[list]): List of service names to stop
        
        Returns:
            bool: True if services stopped successfully, False otherwise
        """
        try:
            cmd = ["docker-compose", "-f", str(self.compose_file_path), "down"]
            if services:
                cmd = ["docker-compose", "-f", str(self.compose_file_path), "stop"] + services
            
            subprocess.run(cmd, check=True)
            
            # Clean up activity tracking
            if services:
                for service in services:
                    self.last_activity_time.pop(service, None)
                    if service in self.shutdown_tasks:
                        self.shutdown_tasks[service].cancel()
                        self.shutdown_tasks.pop(service)
            else:
                self.last_activity_time.clear()
                for task in self.shutdown_tasks.values():
                    task.cancel()
                self.shutdown_tasks.clear()
            
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to stop services: {e}")
            return False

    def get_running_services(self) -> list:
        """
        Get list of currently running services.
        
        Returns:
            list: List of running service names
        """
        try:
            result = subprocess.run(
                ["docker-compose", "-f", str(self.compose_file_path), "ps", "--services"],
                check=True,
                capture_output=True,
                text=True
            )
            return [service for service in result.stdout.split('\n') if service]
        except subprocess.CalledProcessError:
            return []

    def update_activity(self, service: str) -> None:
        """
        Update the last activity time for a service.
        
        Args:
            service (str): Name of the service
        """
        self.last_activity_time[service] = time.time()

    def _start_inactivity_monitoring(self) -> None:
        """Start monitoring for service inactivity."""
        for service in self.get_running_services():
            if service not in self.shutdown_tasks:
                task = asyncio.create_task(self._monitor_inactivity(service))
                self.shutdown_tasks[service] = task

    async def _monitor_inactivity(self, service: str) -> None:
        """
        Monitor service for inactivity and shut down if inactive.
        
        Args:
            service (str): Name of the service to monitor
        """
        while True:
            try:
                current_time = time.time()
                last_activity = self.last_activity_time.get(service, current_time)
                
                if current_time - last_activity > self.inactivity_timeout:
                    logger.info(f"Service {service} inactive for {self.inactivity_timeout} seconds, shutting down")
                    self.stop_services([service])
                    break
                
                await asyncio.sleep(60)  # Check every minute
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error monitoring service {service}: {e}")
                await asyncio.sleep(60)  # Continue monitoring despite errors

    def is_service_running(self, service: str) -> bool:
        """
        Check if a specific service is running.
        
        Args:
            service (str): Name of the service to check
        
        Returns:
            bool: True if service is running, False otherwise
        """
        return service in self.get_running_services()