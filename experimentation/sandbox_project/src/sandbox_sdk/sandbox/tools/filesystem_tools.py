import os
import shutil
from pathlib import Path
from typing import Optional

def read_file(path: str) -> str:
    """Read content of a file"""
    with open(path, 'r') as f:
        return f.read()

def create_file(path: str, content: str) -> None:
    """Create a new file with content"""
    with open(path, 'w') as f:
        f.write(content)

def delete_file(path: str) -> None:
    """Delete a file"""
    os.remove(path)

def append_to_file(path: str, content: str) -> None:
    """Append content to a file"""
    with open(path, 'a') as f:
        f.write(content)

def overwrite_file(path: str, content: str) -> None:
    """Overwrite content of a file"""
    with open(path, 'w') as f:
        f.write(content)

def move_file(src: str, dst: str) -> None:
    """Move a file from src to dst"""
    shutil.move(src, dst)

def copy_file(src: str, dst: str) -> None:
    """Copy a file from src to dst"""
    shutil.copy2(src, dst)

def list_directory(path: str, pattern: Optional[str] = None) -> list[str]:
    """List contents of a directory, optionally filtered by pattern"""
    p = Path(path)
    if pattern:
        return [str(f) for f in p.glob(pattern)]
    return [str(f) for f in p.iterdir()]

def create_directory(path: str, exist_ok: bool = True) -> None:
    """Create a directory and its parents if they don't exist"""
    os.makedirs(path, exist_ok=exist_ok)