import json
import logging
import subprocess

from schema_models.internal_schemas import Compute, ResourceUnit

logger = logging.getLogger(__name__)

async def get_resource_usage() -> Compute:
    logger.info("Getting sandbox resource usage...")
    logger.debug("Inputs: None")

    try:
        # Get total CPU cores
        cpu_info = subprocess.run(["nproc"], capture_output=True, text=True, shell=True, check=True)
        total_cpu = int(cpu_info.stdout.strip())

        # Get total RAM in GB
        mem_info = subprocess.run(["free", "-g", "-m"], capture_output=True, text=True, shell=True, check=True)
        mem_lines = mem_info.stdout.splitlines()
        total_ram = int(mem_lines[1].split()[1]) / 1024 # Convert MB to GB

        # Get disk usage in GB for root partition
        disk_info = subprocess.run(["df", "-h", "/"], capture_output=True, text=True, shell=True, check=True)
        disk_lines = disk_info.stdout.splitlines()
        disk_total = disk_lines[1].split()[1] # Total disk space

        resource_data = {
            "cpu": total_cpu,
            "ram": total_ram,
            "disk": int(disk_total.replace("G","")),
            "memory_bandwidth": 0,
            "networking_bandwith": 0,
            "unit": ResourceUnit.ABSOLUTE
        }
    except subprocess.CalledProcessError as e:
        logger.error(f"Error retrieving resource info: Command failed with exit code {e.returncode} - {e.stderr}")
        resource_data = {
            "cpu": 0,
            "ram": 0,
            "disk": 0,
            "memory_bandwidth": 0,
            "networking_bandwith": 0,
            "unit": ResourceUnit.ABSOLUTE
        }
    except Exception as e:
        logger.error(f"Error retrieving resource info: {e}")
        resource_data = {
            "cpu": 0,
            "ram": 0,
            "disk": 0,
            "memory_bandwidth": 0,
            "networking_bandwith": 0,
            "unit": ResourceUnit.ABSOLUTE
        }
    
    logger.info("Sandbox resource usage retrieved successfully.")
    logger.debug(f"Outputs: {resource_data}")
    
    return Compute(**resource_data)
