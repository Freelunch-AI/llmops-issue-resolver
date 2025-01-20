import os
import subprocess
from typing import Optional, Tuple

def change_directory(path: str) -> None:
    """Change current working directory"""
    os.chdir(path)

def execute_command(command: str, timeout: Optional[int] = None) -> Tuple[str, str, bool]:
    """Execute a shell command and return stdout, stderr and if process is still running"""
    try:
        process = subprocess.run(
            command,
            shell=True,
            text=True,
            capture_output=True,
            timeout=timeout
        )
        return process.stdout, process.stderr, False
    except subprocess.TimeoutExpired as e:
        return e.stdout or "", e.stderr or "", True

def uv_add_package(package: str) -> Tuple[str, str, bool]:
    """Add a package to requirements.txt using uv"""
    return execute_command(f"uv pip install {package}")

def uv_remove_package(package: str) -> Tuple[str, str, bool]:
    """Remove a package using uv"""
    return execute_command(f"uv pip uninstall -y {package}")

def run_python_script(script_path: str) -> Tuple[str, str, bool]:
    """Run a Python script"""
    return execute_command(f"python {script_path}")

def get_current_directory() -> str:
    """Get current working directory"""
    return os.getcwd()