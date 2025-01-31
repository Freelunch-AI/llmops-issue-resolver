import contextlib
import io
import os
import subprocess

from sandbox_toolkit.logs.logging import logger
from src.sandbox_toolkit.infra.sandbox_base.schema_models.internal_schemas import (
    Compute,
    ToolReturn,
)


def execute_command(command: str) -> ToolReturn:
    """Executes a terminal command and returns the output."""
    with io.StringIO() as stdout, io.StringIO() as stderr:
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            try:
                process = subprocess.run(command, capture_output=True, text=True, shell=True, timeout=10)
                if process.returncode == 0:
                    return_value = f"Command executed successfully."
                else:
                    return_value = f"Command failed with exit code {process.returncode}."
                return ToolReturn(return_value=return_value, std_out=process.stdout, std_err=process.stderr, logs="")
            except subprocess.TimeoutExpired:
                return ToolReturn(return_value="Error: Command timed out.", std_out="", std_err="", logs="")
            except Exception as e:
                return ToolReturn(return_value=f"Error executing command: {e}", std_out="", std_err="", logs="")

def change_directory(path: str) -> ToolReturn:
    """Changes the current working directory to the given path."""
    with io.StringIO() as stdout, io.StringIO() as stderr:
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            try:
                os.chdir(path)
                return ToolReturn(return_value=f"Current directory changed to '{path}'", std_out="", std_err="", logs="")
            except FileNotFoundError:
                return ToolReturn(return_value=f"Error: Directory not found at path '{path}'", std_out="", std_err="", logs="")
            except NotADirectoryError:
                return ToolReturn(return_value=f"Error: Not a directory at path '{path}'", std_out="", std_err="", logs="")
            except Exception as e:
                return ToolReturn(return_value=f"Error changing directory: {e}", std_out="", std_err="", logs="")

def get_current_directory() -> ToolReturn:
    """Returns the current working directory."""
    with io.StringIO() as stdout, io.StringIO() as stderr:
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            return ToolReturn(return_value=os.getcwd(), std_out="", std_err="", logs="")

def uv_add_package(package_name: str) -> ToolReturn:
    """Adds a Python package using uv package manager."""
    with io.StringIO() as stdout, io.StringIO() as stderr:
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            try:
                process = subprocess.run(["uv", "add", package_name], capture_output=True, text=True, timeout=60)
                if process.returncode == 0:
                    return_value = f"Package '{package_name}' installed successfully."
                else:
                    return_value = f"Error installing package '{package_name}' with uv. Exit code {process.returncode}."
                return ToolReturn(return_value=return_value, std_out=process.stdout, std_err=process.stderr, logs="")
            except subprocess.TimeoutExpired:
                return ToolReturn(return_value=f"Error: Installing package '{package_name}' timed out.", std_out="", std_err="", logs="")
            except FileNotFoundError:
                return ToolReturn(return_value="Error: uv package manager not found. Please ensure uv is installed in the sandbox.", std_out="", std_err="", logs="")
            except Exception as e:
                return ToolReturn(return_value=f"Error installing package '{package_name}': {e}", std_out="", std_err="", logs="")

def uv_remove_package(package_name: str) -> ToolReturn:
    """Removes a Python package using uv package manager."""
    with io.StringIO() as stdout, io.StringIO() as stderr:
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            try:
                process = subprocess.run(["uv", "remove", package_name, "-y"], capture_output=True, text=True, timeout=60)
                if process.returncode == 0:
                    return_value = f"Package '{package_name}' removed successfully."
                else:
                    return_value = f"Error removing package '{package_name}' with uv. Exit code {process.returncode}."
                return ToolReturn(return_value=return_value, std_out=process.stdout, std_err=process.stderr, logs="")
            except subprocess.TimeoutExpired:
                return ToolReturn(return_value=f"Error: Removing package '{package_name}' timed out.", std_out="", std_err="", logs="")
            except FileNotFoundError:
                return ToolReturn(return_value="Error: uv package manager not found. Please ensure uv is installed in the sandbox.", std_out="", std_err="", logs="")
            except Exception as e:
                return ToolReturn(return_value=f"Error removing package '{package_name}': {e}", std_out="", std_err="", logs="")

def uv_sync_packages() -> ToolReturn:
    """Syncs Python packages using uv package manager based on requirements.txt."""
    with io.StringIO() as stdout, io.StringIO() as stderr:
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            try:
                process = subprocess.run(["uv", "sync"], capture_output=True, text=True, timeout=120)
                if process.returncode == 0:
                    return_value = "Packages synced successfully using requirements.txt."
                else:
                    return_value = f"Error syncing packages with uv. Exit code {process.returncode}."
                return ToolReturn(return_value=return_value, std_out=process.stdout, std_err=process.stderr, logs="")
            except subprocess.TimeoutExpired:
                return ToolReturn(return_value="Error: Syncing packages timed out.", std_out="", std_err="", logs="")
            except FileNotFoundError:
                return ToolReturn(return_value="Error: requirements.txt file not found.", std_out="", std_err="", logs="")
            except FileNotFoundError:
                return ToolReturn(return_value="Error: uv package manager not found. Please ensure uv is installed in the sandbox.", std_out="", std_err="", logs="")
            except Exception as e:
                return ToolReturn(return_value=f"Error syncing packages: {e}", std_out="", std_err="", logs="")

def uv_run_python_script(script_path: str) -> ToolReturn:
    """Runs a Python script using uv package manager."""
    with io.StringIO() as stdout, io.StringIO() as stderr:
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            try:
                process = subprocess.run(["uv", "run", "python", script_path], capture_output=True, text=True, timeout=60)
                if process.returncode == 0:
                    return_value = f"Python script '{script_path}' executed successfully."
                else:
                    return_value = f"Error running python script '{script_path}' with uv. Exit code {process.returncode}."
                return ToolReturn(return_value=return_value, std_out=process.stdout, std_err=process.stderr, logs="")
            except subprocess.TimeoutExpired:
                return ToolReturn(return_value=f"Error: Running python script '{script_path}' timed out.", std_out="", std_err="", logs="")
            except FileNotFoundError:
                return ToolReturn(return_value=f"Error: Python script not found at path '{script_path}'", std_out="", std_err="", logs="")
            except FileNotFoundError:
                return ToolReturn(return_value="Error: uv package manager not found. Please ensure uv is installed in the sandbox.", std_out="", std_err="", logs="")
            except Exception as e:
                return ToolReturn(return_value=f"Error running python script '{script_path}': {e}", std_out="", std_err="", logs="")

def install_system_package(package_name: str) -> ToolReturn:
    """Installs a system package using apt-get."""
    with io.StringIO() as stdout, io.StringIO() as stderr:
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            try:
                process = subprocess.run(["sudo", "apt-get", "install", "-y", package_name], capture_output=True, text=True, shell=True, timeout=120, check=True)
                if process.returncode == 0:
                    return_value = f"System package '{package_name}' installed successfully."
                else:
                    return_value = f"Error installing system package '{package_name}' using apt-get. Exit code {process.returncode}."
                return ToolReturn(return_value=return_value, std_out=process.stdout, std_err=process.stderr, logs="")
            except subprocess.TimeoutExpired:
                return ToolReturn(return_value=f"Error: Installing system package '{package_name}' timed out.", std_out="", std_err="", logs="")
            except subprocess.CalledProcessError as e:
                return ToolReturn(return_value=f"Error installing system package '{package_name}' using apt-get. Exit code {e.returncode}.", std_out=e.stdout, std_err=e.stderr, logs="")
            except FileNotFoundError:
                return ToolReturn(return_value="Error: apt-get command not found. Please ensure apt-get is available in the sandbox.", std_out="", std_err="", logs="")
            except Exception as e:
                return ToolReturn(return_value=f"Error installing system package '{package_name}': {e}", std_out="", std_err="", logs="")

def get_total_available_and_used_compute_resources() -> ToolReturn:
    """
    Retrieves total available and used compute resources (CPU, RAM, Disk) using system commands.
    Returns a Compute object containing the resource information.
    """
    with io.StringIO() as stdout, io.StringIO() as stderr:
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            logger.info(f"Starting get_total_available_and_used_compute_resources")
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
                
                compute_resources = Compute(
                    cpu=total_cpu,
                    ram=total_ram,
                    disk=int(disk_total[:-1]), # Remove 'G' from disk_total and convert to int
                    memory_bandwidth=0,
                    networking_bandwith=0
                )
                logger.info(f"Finished get_total_available_and_used_compute_resources, output: {compute_resources}")
                return ToolReturn(return_value=compute_resources, std_out="", std_err="", logs="")
            except subprocess.CalledProcessError as e:
                logger.error(f"Error retrieving resource info: Command failed with exit code {e.returncode} - {e.stderr}")
                return ToolReturn(return_value=f"Error retrieving resource info: Command failed with exit code {e.returncode} - {e.stderr}", std_out="", std_err="", logs="")
            except Exception as e:
                logger.error(f"Error retrieving resource info: {e}")
                return ToolReturn(return_value=f"Error retrieving resource info: {e}", std_out="", std_err="", logs="")
