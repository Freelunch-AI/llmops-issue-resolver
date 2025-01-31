"""Filesystem tools for sandbox."""
import os
import shutil

def read_file(path: str) -> str:
    """Reads and returns the content of a file."""
    try:
        with open(path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: File not found at path '{path}'"
    except Exception as e:
        return f"Error reading file: {e}"

def create_file(path: str, content: str) -> str:
    """Creates a new file with the given path and content."""
    try:
        with open(path, "w") as f:
            f.write(content)
        return f"File created successfully at path '{path}'"
    except Exception as e:
        return f"Error creating file: {e}"

def delete_file(path: str) -> str:
    """Deletes the file at the given path."""
    try:
        os.remove(path)
        return f"File deleted successfully at path '{path}'"
    except FileNotFoundError:
        return f"Error: File not found at path '{path}'"
    except Exception as e:
        return f"Error deleting file: {e}"

def append_to_file(path: str, content: str) -> str:
    """Appends content to the end of the file at the given path."""
    try:
        with open(path, "a") as f:
            f.write(content)
        return f"Content appended successfully to file at path '{path}'"
    except FileNotFoundError:
        return f"Error: File not found at path '{path}'"
    except Exception as e:
        return f"Error appending to file: {e}"

def overwrite_file(path: str, content: str) -> str:
    """Overwrites the file at the given path with the given content."""
    try:
        with open(path, "w") as f:
            f.write(content)
        return f"File overwritten successfully at path '{path}'"
    except Exception as e:
        return f"Error overwriting file: {e}"

def edit_file_line_range(path: str, start_line: int, end_line: int, new_content: str) -> str:
    """Edits a specific range of lines in a file with new content."""
    try:
        with open(path, "r") as f:
            lines = f.readlines()

        if start_line < 1 or start_line > len(lines) + 1 or end_line < start_line or end_line > len(lines) + 1:
            return "Error: Invalid line range specified."

        lines[start_line-1:end_line] = [new_content + '\n']
        with open(path, "w") as f:
            f.writelines(lines)
        return f"File edited successfully at path '{path}', lines {start_line}-{end_line} replaced."
    except FileNotFoundError:
        return f"Error: File not found at path '{path}'"
    except Exception as e:
        return f"Error editing file: {e}"

def move_file(source_path: str, destination_path: str) -> str:
    """Moves a file from source path to destination path."""
    try:
        shutil.move(source_path, destination_path)
        return f"File moved successfully from '{source_path}' to '{destination_path}'"
    except FileNotFoundError:
        return f"Error: Source file not found at path '{source_path}'"
    except Exception as e:
        return f"Error moving file: {e}"

def copy_file(source_path: str, destination_path: str) -> str:
    """Copies a file from source path to destination path."""
    try:
        shutil.copy2(source_path, destination_path)
        return f"File copied successfully from '{source_path}' to '{destination_path}'"
    except FileNotFoundError:
        return f"Error: Source file not found at path '{source_path}'"
    except Exception as e:
        return f"Error copying file: {e}"

def list_directory(path: str) -> str:
    """Lists the content of the directory at the given path."""
    try:
        contents = os.listdir(path)
        return "Directory contents:\n" + '\n'.join(contents)
    except FileNotFoundError:
        return f"Error: Directory not found at path '{path}'"
    except NotADirectoryError:
        return f"Error: Not a directory at path '{path}'"
    except Exception as e:
        return f"Error listing directory: {e}"

def create_directory(path: str) -> str:
    """Creates a new directory at the given path."""
    try:
        os.makedirs(path, exist_ok=True)
        return f"Directory created successfully at path '{path}'"
    except FileExistsError:
        return f"Error: Directory already exists at path '{path}'"
    except Exception as e:
        return f"Error creating directory: {e}"
