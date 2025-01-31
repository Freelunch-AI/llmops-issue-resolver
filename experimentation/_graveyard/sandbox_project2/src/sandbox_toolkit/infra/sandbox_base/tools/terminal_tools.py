import subprocess
import os
import json

def execute_command(command: str) -> str:
    """Executes a terminal command and returns the output."""
    try:
        process = subprocess.run(command, capture_output=True, text=True, shell=True, timeout=10)
        if process.returncode == 0:
            return f"Command executed successfully.\\nStdout:\\n{process.stdout}\\nStderr:\\n{process.stderr}"
        else:
            return f"Command failed with exit code {process.returncode}.\\nStdout:\\n{process.stdout}\\nStderr:\\n{process.stderr}"
    except subprocess.TimeoutExpired:
        return "Error: Command timed out."
    except Exception as e:
        return f"Error executing command: {e}"

def change_directory(path: str) -> str:
    """Changes the current working directory to the given path."""
    try:
        os.chdir(path)
        return f"Current directory changed to '{path}'"
    except FileNotFoundError:
        return f"Error: Directory not found at path '{path}'"
    except NotADirectoryError:
        return f"Error: Not a directory at path '{path}'"
    except Exception as e:
        return f"Error changing directory: {e}"

def get_current_directory() -> str:
    """Returns the current working directory."""
    return os.getcwd()

def uv_add_package(package_name: str) -> str:
    """Adds a Python package using uv package manager."""
    try:
        process = subprocess.run(["uv", "pip", "install", package_name], capture_output=True, text=True, timeout=60)
        if process.returncode == 0:
            return f"Package '{package_name}' installed successfully.\\nStdout:\\n{process.stdout}\\nStderr:\\n{process.stderr}"
        else:
            return f"Error installing package '{package_name}' with uv. Exit code {process.returncode}.\\nStdout:\\n{process.stdout}\\nStderr:\\n{process.stderr}"
    except subprocess.TimeoutExpired:
        return f"Error: Installing package '{package_name}' timed out."
    except FileNotFoundError:
        return "Error: uv package manager not found. Please ensure uv is installed in the sandbox."
    except Exception as e:
        return f"Error installing package '{package_name}': {e}"

def uv_remove_package(package_name: str) -> str:
    """Removes a Python package using uv package manager."""
    try:
        process = subprocess.run(["uv", "pip", "uninstall", package_name, "-y"], capture_output=True, text=True, timeout=60)
        if process.returncode == 0:
            return f"Package '{package_name}' removed successfully.\\nStdout:\\n{process.stdout}\\nStderr:\\n{process.stderr}"
        else:
            return f"Error removing package '{package_name}' with uv. Exit code {process.returncode}.\\nStdout:\\n{process.stdout}\\nStderr:\\n{process.stderr}"
    except subprocess.TimeoutExpired:
        return f"Error: Removing package '{package_name}' timed out."
    except FileNotFoundError:
        return "Error: uv package manager not found. Please ensure uv is installed in the sandbox."
    except Exception as e:
        return f"Error removing package '{package_name}': {e}"

def uv_sync_packages() -> str:
    """Syncs Python packages using uv package manager based on requirements.txt."""
    try:
        process = subprocess.run(["uv", "pip", "sync", "requirements.txt"], capture_output=True, text=True, timeout=120)
        if process.returncode == 0:
            return f"Packages synced successfully using requirements.txt.\\nStdout:\\n{process.stdout}\\nStderr:\\n{process.stderr}"
        else:
            return f"Error syncing packages with uv. Exit code {process.returncode}.\\nStdout:\\n{process.stdout}\\nStderr:\\n{process.stderr}"
    except subprocess.TimeoutExpired:
        return "Error: Syncing packages timed out."
    except FileNotFoundError:
        return "Error: requirements.txt file not found."
    except FileNotFoundError:
        return "Error: uv package manager not found. Please ensure uv is installed in the sandbox."
    except Exception as e:
        return f"Error syncing packages: {e}"

def uv_run_python_script(script_path: str) -> str:
    """Runs a Python script using uv package manager."""
    try:
        process = subprocess.run(["uv", "run", "python", script_path], capture_output=True, text=True, timeout=60)
        if process.returncode == 0:
            return f"Python script '{script_path}' executed successfully.\\nStdout:\\n{process.stdout}\\nStderr:\\n{process.stderr}"
        else:
            return f"Error running python script '{script_path}' with uv. Exit code {process.returncode}.\\nStdout:\\n{process.stdout}\\nStderr:\\n{process.stderr}"
    except subprocess.TimeoutExpired:
        return f"Error: Running python script '{script_path}' timed out."
    except FileNotFoundError:
        return f"Error: Python script not found at path '{script_path}'"
    except FileNotFoundError:
        return "Error: uv package manager not found. Please ensure uv is installed in the sandbox."
    except Exception as e:
        return f"Error running python script '{script_path}': {e}"

def install_system_package(package_name: str) -> str:
    """Installs a system package using apt-get."""
    try:
        process = subprocess.run(["apt-get", "install", "-y", package_name], capture_output=True, text=True, shell=True, timeout=120, check=True)
        if process.returncode == 0:
            return f"System package '{package_name}' installed successfully.\\nStdout:\\n{process.stdout}\\nStderr:\\n{process.stderr}"
        else:
            return f"Error installing system package '{package_name}' using apt-get. Exit code {process.returncode}.\\nStdout:\\n{process.stdout}\\nStderr:\\n{process.stderr}"
    except subprocess.TimeoutExpired:
        return f"Error: Installing system package '{package_name}' timed out."
    except subprocess.CalledProcessError as e:
        return f"Error installing system package '{package_name}' using apt-get. Exit code {e.returncode}.\\nStdout:\\n{e.stdout}\\nStderr:\\n{e.stderr}"
    except FileNotFoundError:
        return "Error: apt-get command not found. Please ensure apt-get is available in the sandbox."
    except Exception as e:
        return f"Error installing system package '{package_name}': {e}"

def get_total_available_and_used_compute_resources() -> str:
    """
    Retrieves total available and used compute resources (CPU, RAM, Disk) using system commands.
    Returns a JSON string containing the resource information.
    """
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
            "total_cpu_cores": total_cpu,
            "total_ram_gb": total_ram,
            "total_disk_space_gb": disk_total,
            # Add used resources if possible to retrieve from system commands
        }

        return json.dumps(resource_data)
    except subprocess.CalledProcessError as e:
        return f"Error retrieving resource info: Command failed with exit code {e.returncode} - {e.stderr}"
    except Exception as e:
        return f"Error retrieving resource info: {e}"