import os
import sys
from contextlib import contextmanager
from typing import List


@contextmanager
def temporary_sys_path(path):
    """
    A context manager to temporarily add a specified path to the system path.
    This context manager appends the given path to `sys.path` and ensures that 
    the original `sys.path` is restored after the context is exited.
    Args:
        path (str): The path to be temporarily added to `sys.path`.
    Yields:
        None: This context manager does not yield any value.
    Example:
        with temporary_sys_path('/some/path'):
            # Perform operations that require the temporary path
    """
    original_sys_path = sys.path.copy()
    sys.path.append(path)
    try:
        yield
    finally:
        sys.path = original_sys_path

# do some imports 'assuming' that the package is installed
# before: 'from agent import ..."
# now: "from llmops_issue_resolver.agent import ..."
# But why do this? 
#     - Because mypy assumes this notation when importing from modules within a package
#     - Because it makes it cleanar for doing imports within modules that are very deep 
#     and want to import from modules that are near surface of the package directory 
#     tree
# All .py modules need to have this line, but with the more general form of the import 

with temporary_sys_path(os.path.abspath(os.path.join(os.path.dirname(__file__), \
                                                     '..', '..', '..', '..'))):    
    from experimentation.code.imports.tool_builder import build_tool
    from experimentation.data.constants import DOCS_ALL

@build_tool(docs=DOCS_ALL["get_directory_tree"]) 
def get_directory_tree(path: str, depth: int = 5, level: int = 0) -> List[str]:
    tree = []
    for root, dirs, files in os.walk(path):
        for file in files:
            tree.append(os.path.join(root, file))
        for directory in dirs:
            if level < depth:
                tree.append(os.path.join(root, directory))
                tree.extend(get_directory_tree(
                    path=os.path.join(root, directory), depth=depth, level=level + 1))
    return tree

        