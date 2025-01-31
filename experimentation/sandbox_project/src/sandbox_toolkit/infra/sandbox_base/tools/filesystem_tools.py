import contextlib
import io
import os
import shutil
from pathlib import Path

from sandbox_toolkit.logs.logging import logger
from src.sandbox_toolkit.infra.sandbox_base.schema_models.internal_schemas import (
    ToolReturn,
)


def read_file(path: str) -> ToolReturn:
    """Reads and returns the content of a file."""
    with io.StringIO() as stdout, io.StringIO() as stderr:
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            logger.info(f"Starting read_file with path: {path}")
            with io.StringIO() as stdout, io.StringIO() as stderr:
                with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    return_value = ""
                    try:
                        with open(path, "r") as f:
                            return_value = f.read()
                    except FileNotFoundError:
                        return_value = f"Error: File not found at path '{path}'"
                    except Exception as e:
                        return_value = f"Error reading file: {e}"
                    log_file_path = "src/sandbox_toolkit/infra/sandbox_base/logs/logs/tools/filesystem_tools.log"
                    logs = ""
                    if Path(log_file_path).exists():
                        try:
                            with open(log_file_path, "r") as f:
                                logs = f.read()
                        except FileNotFoundError:
                            logs = ""
                    logger.info(f"Finished read_file with path: {path}, output: {return_value}")
                    return ToolReturn(return_value=return_value, std_out=stdout.getvalue(), std_err=stderr.getvalue(), logs=logs)

def create_file(path: str, content: str) -> ToolReturn:
    """Creates a new file with the given path and content."""
    with io.StringIO() as stdout, io.StringIO() as stderr:
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            logger.info(f"Starting create_file with path: {path}")
            with io.StringIO() as stdout, io.StringIO() as stderr:
                with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    return_value = ""
                    try:
                        with open(path, "w") as f:
                            f.write(content)
                        return_value = f"File created successfully at path '{path}'"
                    except Exception as e:
                        return_value = f"Error creating file: {e}"
                    log_file_path = "../logs/logs/tools/filesystem_tools.log"
                    logs = ""
                    if Path(log_file_path).exists():
                        try:
                            with open(log_file_path, "r") as f:
                                logs = f.read()
                        except FileNotFoundError:
                            logs = ""
                    logger.info(f"Finished create_file with path: {path}, output: {return_value}")
                    return ToolReturn(return_value=return_value, std_out=stdout.getvalue(), std_err=stderr.getvalue(), logs=logs)

def delete_file(path: str) -> ToolReturn:
    """Deletes the file at the given path."""
    with io.StringIO() as stdout, io.StringIO() as stderr:
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            logger.info(f"Starting delete_file with path: {path}")
            with io.StringIO() as stdout, io.StringIO() as stderr:
                with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    return_value = ""
                    try:
                        os.remove(path)
                        return_value = f"File deleted successfully at path '{path}'"
                    except FileNotFoundError:
                        return_value = f"Error: File not found at path '{path}'"
                    except Exception as e:
                        return_value = f"Error deleting file: {e}"
                    log_file_path = "../logs/logs/tools/filesystem_tools.log"
                    logs = ""
                    if Path(log_file_path).exists():
                        try:
                            with open(log_file_path, "r") as f:
                                logs = f.read()
                        except FileNotFoundError:
                            logs = ""
                    logger.info(f"Finished delete_file with path: {path}, output: {return_value}")
                    return ToolReturn(return_value=return_value, std_out=stdout.getvalue(), std_err=stderr.getvalue(), logs=logs)

def append_to_file(path: str, content: str) -> ToolReturn:
    """Appends content to the end of the file at the given path."""
    with io.StringIO() as stdout, io.StringIO() as stderr:
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            logger.info(f"Starting append_to_file with path: {path}")
            with io.StringIO() as stdout, io.StringIO() as stderr:
                with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    return_value = ""
                    try:
                        with open(path, "a") as f:
                            f.write(content)
                        return_value = f"Content appended successfully to file at path '{path}'"
                    except FileNotFoundError:
                        return_value = f"Error: File not found at path '{path}'"
                    except Exception as e:
                        return_value = f"Error appending to file: {e}"
                    log_file_path = "../logs/logs/tools/filesystem_tools.log"
                    logs = ""
                    if Path(log_file_path).exists():
                        try:
                            with open(log_file_path, "r") as f:
                                logs = f.read()
                        except FileNotFoundError:
                            logs = ""
                    logger.info(f"Finished append_to_file with path: {path}, output: {return_value}")
                    return ToolReturn(return_value=return_value, std_out=stdout.getvalue(), std_err=stderr.getvalue(), logs=logs)

def overwrite_file(path: str, content: str) -> ToolReturn:
    """Overwrites the file at the given path with the given content."""
    with io.StringIO() as stdout, io.StringIO() as stderr:
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            logger.info(f"Starting overwrite_file with path: {path}")
            with io.StringIO() as stdout, io.StringIO() as stderr:
                with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    return_value = ""
                    try:
                        with open(path, "w") as f:
                            f.write(content)
                        return_value = f"File overwritten successfully at path '{path}'"
                    except Exception as e:
                        return_value = f"Error overwriting file: {e}"
                    log_file_path = "../logs/logs/tools/filesystem_tools.log"
                    logs = ""
                    if Path(log_file_path).exists():
                        try:
                            with open(log_file_path, "r") as f:
                                logs = f.read()
                        except FileNotFoundError:
                            logs = ""
                    logger.info(f"Finished overwrite_file with path: {path}, output: {return_value}")
                    return ToolReturn(return_value=return_value, std_out=stdout.getvalue(), std_err=stderr.getvalue(), logs=logs)

def edit_file_line_range(path: str, start_line: int, end_line: int, new_content: str) -> ToolReturn:
    """Edits a specific range of lines in a file with new content."""
    with io.StringIO() as stdout, io.StringIO() as stderr:
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            logger.info(f"Starting edit_file_line_range with path: {path}, start_line: {start_line}, end_line: {end_line}")
            with io.StringIO() as stdout, io.StringIO() as stderr:
                with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    return_value = ""
                    try:
                        with open(path, "r") as f:
                            lines = f.readlines()

                        if start_line < 1 or start_line > len(lines) or end_line < start_line or end_line > len(lines) + 1:
                            return_value = "Error: Invalid line range specified."
                        else:
                            lines[start_line-1:end_line] = [new_content + '\\n']
                            with open(path, "w") as f:
                                f.writelines(lines)
                            return_value = f"File edited successfully at path '{path}', lines {start_line}-{end_line} replaced."
                    except FileNotFoundError:
                        return_value = f"Error: File not found at path '{path}'"
                    except Exception as e:
                        return_value = f"Error editing file: {e}"
                    log_file_path = "../logs/logs/tools/filesystem_tools.log"
                    logs = ""
                    if Path(log_file_path).exists():
                        try:
                            with open(log_file_path, "r") as f:
                                logs = f.read()
                        except FileNotFoundError:
                            logs = ""
                    logger.info(f"Finished edit_file_line_range with path: {path}, start_line: {start_line}, end_line: {end_line}, output: {return_value}")
                    return ToolReturn(return_value=return_value, std_out=stdout.getvalue(), std_err=stderr.getvalue(), logs=logs)

def move_file(source_path: str, destination_path: str) -> ToolReturn:
    """Moves a file from source path to destination path."""
    with io.StringIO() as stdout, io.StringIO() as stderr:
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            try:
                shutil.move(source_path, destination_path)
                return ToolReturn(return_value=f"File moved successfully from '{source_path}' to '{destination_path}'", std_out="", std_err="", logs="")
            except FileNotFoundError:
                return ToolReturn(return_value=f"Error: Source file not found at path '{source_path}'", std_out="", std_err="", logs="")
            except Exception as e:
                return ToolReturn(return_value=f"Error moving file: {e}", std_out="", std_err="", logs="")

def copy_file(source_path: str, destination_path: str) -> ToolReturn:
    """Copies a file from source path to destination path."""
    with io.StringIO() as stdout, io.StringIO() as stderr:
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            try:
                shutil.copy2(source_path, destination_path)
                return ToolReturn(return_value=f"File copied successfully from '{source_path}' to '{destination_path}'", std_out="", std_err="", logs="")
            except FileNotFoundError:
                return ToolReturn(return_value=f"Error: Source file not found at path '{source_path}'", std_out="", std_err="", logs="")
            except Exception as e:
                return ToolReturn(return_value=f"Error copying file: {e}", std_out="", std_err="", logs="")

def list_directory(path: str) -> ToolReturn:
    """Lists the content of the directory at the given path."""
    with io.StringIO() as stdout, io.StringIO() as stderr:
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            try:
                contents = os.listdir(path)
                return ToolReturn(return_value="Directory contents:\n" + '\n'.join(contents), std_out="", std_err="", logs="")
            except FileNotFoundError:
                return ToolReturn(return_value=f"Error: Directory not found at path '{path}'", std_out="", std_err="", logs="")
            except NotADirectoryError:
                return ToolReturn(return_value=f"Error: Not a directory at path '{path}'", std_out="", std_err="", logs="")
            except Exception as e:
                return ToolReturn(return_value=f"Error listing directory: {e}", std_out="", std_err="", logs="")
    
def list_directory_recursive(path: str) -> ToolReturn:
    """Lists the content of the directory at the given path recursively."""
    with io.StringIO() as stdout, io.StringIO() as stderr:
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            try:
                contents = []
                for root, dirs, files in os.walk(path):
                    contents.append(f"Directory: {root}")
                    contents.extend([f"  File: {f}" for f in files])
                return ToolReturn(return_value="Directory contents (recursive):\n" + '\n'.join(contents), std_out="", std_err="", logs="")
            except FileNotFoundError:
                return ToolReturn(return_value=f"Error: Directory not found at path '{path}'", std_out="", std_err="", logs="")
            except NotADirectoryError:
                return ToolReturn(return_value=f"Error: Not a directory at path '{path}'", std_out="", std_err="", logs="")
            except Exception as e:
                return ToolReturn(return_value=f"Error listing directory recursively: {e}", std_out="", std_err="", logs="")

def create_directory(path: str) -> ToolReturn:
    """Creates a new directory at the given path."""
    with io.StringIO() as stdout, io.StringIO() as stderr:
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            try:
                os.makedirs(path, exist_ok=True)
                return ToolReturn(return_value=f"Directory created successfully at path '{path}'", std_out="", std_err="", logs="")
            except FileExistsError:
                return ToolReturn(return_value=f"Error: Directory already exists at path '{path}'", std_out="", std_err="", logs="")
            except Exception as e:
                return ToolReturn(return_value=f"Error creating directory: {e}", std_out="", std_err="", logs="")

def replace_python_function_in_file(file_path: str, old_function_name: str, new_function_code: str) -> ToolReturn:
    """Replaces the code of a Python function in a file with new code."""
    with io.StringIO() as stdout, io.StringIO() as stderr:
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            try:
                with open(file_path, "r") as f:
                    lines = f.readlines()

                start_index = None
                end_index = None
                for i, line in enumerate(lines):
                    if old_function_name in line:
                        start_index = i
                    if start_index is not None and line.strip() == "":
                        end_index = i
                        break

                if start_index is None or end_index is None:
                    return ToolReturn(return_value=f"Error: Function '{old_function_name}' not found in file.", std_out="", std_err="", logs="")

                lines[start_index:end_index] = new_function_code.splitlines()

                with open(file_path, "w") as f:
                    f.writelines(lines)

                return ToolReturn(return_value=f"Function '{old_function_name}' replaced successfully in file '{file_path}'", std_out="", std_err="", logs="")
            except FileNotFoundError:
                return ToolReturn(return_value=f"Error: File not found at path '{file_path}'", std_out="", std_err="", logs="")
            except Exception as e:
                return ToolReturn(return_value=f"Error replacing function in file: {e}", std_out="", std_err="", logs="")
    
def replace_python_class_in_file(file_path: str, old_class_name: str, new_class_code: str) -> ToolReturn:
    """Replaces the code of a Python class in a file with new code."""
    with io.StringIO() as stdout, io.StringIO() as stderr:
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            try:
                with open(file_path, "r") as f:
                    lines = f.readlines()

                start_index = None
                end_index = None
                for i, line in enumerate(lines):
                    if old_class_name in line:
                        start_index = i
                    if start_index is not None and line.strip() == "":
                        end_index = i
                        break

                if start_index is None or end_index is None:
                    return ToolReturn(return_value=f"Error: Class '{old_class_name}' not found in file.", std_out="", std_err="", logs="")

                lines[start_index:end_index] = new_class_code.splitlines()

                with open(file_path, "w") as f:
                    f.writelines(lines)

                return ToolReturn(return_value=f"Class '{old_class_name}' replaced successfully in file '{file_path}'", std_out="", std_err="", logs="")
            except FileNotFoundError:
                return ToolReturn(return_value=f"Error: File not found at path '{file_path}'", std_out="", std_err="", logs="")
            except Exception as e:
                return ToolReturn(return_value=f"Error replacing class in file: {e}", std_out="", std_err="", logs="")

def replace_python_method_in_file(file_path: str, class_name: str, old_method_name: str, new_method_code: str) -> ToolReturn:
    """Replaces the code of a Python method in a class in a file with new code."""
    with io.StringIO() as stdout, io.StringIO() as stderr:
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            try:
                with open(file_path, "r") as f:
                    lines = f.readlines()

                class_found = False
                method_found = False
                for i, line in enumerate(lines):
                    if class_name in line:
                        class_found = True
                    if class_found and old_method_name in line:
                        method_found = True
                        start_index = i
                    if method_found and line.strip() == "":
                        end_index = i
                        break

                if not class_found:
                    return ToolReturn(return_value=f"Error: Class '{class_name}' not found in file.", std_out="", std_err="", logs="")
                if not method_found:
                    return ToolReturn(return_value=f"Error: Method '{old_method_name}' not found in class '{class_name}'.", std_out="", std_err="", logs="")

                lines[start_index:end_index] = new_method_code.splitlines()

                with open(file_path, "w") as f:
                    f.writelines(lines)

                return ToolReturn(return_value=f"Method '{old_method_name}' replaced successfully in class '{class_name}' in file '{file_path}'", std_out="", std_err="", logs="")
            except FileNotFoundError:
                return ToolReturn(return_value=f"Error: File not found at path '{file_path}'", std_out="", std_err="", logs="")
            except Exception as e:
                return ToolReturn(return_value=f"Error replacing method in file: {e}", std_out="", std_err="", logs="")
