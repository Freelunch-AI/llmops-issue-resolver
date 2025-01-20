import os
import shutil
from pathlib import Path
from typing import Optional

def read_file(path: str) -> str:
    """Read and return the content of a file.

    Args:
        path (str): The path to the file to be read.

    Returns:
        str: The content of the file as a string.

    Raises:
        FileNotFoundError: If the file does not exist.
        IOError: If there are issues reading the file."""
    with open(path, 'r') as f:
        return f.read()

def create_file(path: str, content: str) -> None:
    """Create a new file with the specified content.

    Args:
        path (str): The path where the new file should be created.
        content (str): The content to write to the file.

    Returns:
        None

    Raises:
        IOError: If the file cannot be created or written to.
        FileExistsError: If the file already exists."""
    with open(path, 'w') as f:
        f.write(content)

def delete_file(path: str) -> None:
    """Delete the specified file.

    Args:
        path (str): The path to the file to be deleted.

    Returns:
        None

    Raises:
        FileNotFoundError: If the file does not exist.
        PermissionError: If the user lacks permission to delete the file."""
    os.remove(path)

def append_to_file(path: str, content: str) -> None:
    """Append content to the end of an existing file.

    Args:
        path (str): The path to the file to append to.
        content (str): The content to append to the file.

    Returns:
        None

    Raises:
        FileNotFoundError: If the file does not exist.
        IOError: If there are issues writing to the file."""
    with open(path, 'a') as f:
        f.write(content)

def overwrite_file(path: str, content: str) -> None:
    """Overwrite the entire content of an existing file.

    Args:
        path (str): The path to the file to overwrite.
        content (str): The new content to write to the file.

    Returns:
        None

    Raises:
        FileNotFoundError: If the file does not exist.
        IOError: If there are issues writing to the file."""
    with open(path, 'w') as f:
        f.write(content)

def move_file(src: str, dst: str) -> None:
    """Move a file from the source path to the destination path.

    Args:
        src (str): The source path of the file to be moved.
        dst (str): The destination path where the file should be moved to.

    Returns:
        None

    Raises:
        FileNotFoundError: If the source file does not exist.
        PermissionError: If there are permission issues.
        OSError: If there are issues during the move operation."""
    shutil.move(src, dst)

def copy_file(src: str, dst: str) -> None:
    """Copy a file from the source path to the destination path.

    Args:
        src (str): The source path of the file to be copied.
        dst (str): The destination path where the file should be copied to.

    Returns:
        None

    Raises:
        FileNotFoundError: If the source file does not exist.
        PermissionError: If there are permission issues.
        OSError: If there are issues during the copy operation."""
    shutil.copy2(src, dst)

def list_directory(path: str, pattern: Optional[str] = None) -> list[str]:
    """List the contents of a directory, optionally filtered by a glob pattern.

    Args:
        path (str): The path to the directory to list.
        pattern (Optional[str], optional): A glob pattern to filter the results.
            If None, all contents are returned. Defaults to None.

    Returns:
        list[str]: A list of paths as strings matching the pattern (if provided)
            or all contents if no pattern is specified.

    Raises:
        FileNotFoundError: If the directory does not exist.
        NotADirectoryError: If the path is not a directory."""
    p = Path(path)
    if pattern:
        return [str(f) for f in p.glob(pattern)]
    return [str(f) for f in p.iterdir()]

def create_directory(path: str, exist_ok: bool = True) -> None:
    """Create a directory and its parent directories if they don't exist.

    Args:
        path (str): The path of the directory to create.
        exist_ok (bool, optional): If True, don't raise an error if the directory
            already exists. Defaults to True.

    Returns:
        None

    Raises:
        FileExistsError: If the directory exists and exist_ok is False.
        PermissionError: If there are permission issues creating the directory."""
    os.makedirs(path, exist_ok=exist_ok)