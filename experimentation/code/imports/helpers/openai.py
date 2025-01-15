import os
import sys
from contextlib import contextmanager


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

with temporary_sys_path(os.path.abspath(os.path.join(os.path.dirname(__file__), 
                                                     '..', '..', '..', '..'))):
    from experimentation.code.imports.utils.images import encode_image

def get_ready_openai_image(image_path: str) -> str:
    base64_image = encode_image(image_path=image_path)
    return f"data:image/jpeg;base64,{base64_image}"
