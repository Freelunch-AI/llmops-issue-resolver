import os
import sys
from contextlib import contextmanager

from pydantic import ValidationError


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
    from experimentation.code.imports.utils.schema_models import IntModel

def calculate_percentage_resolved(resolved_instances: int, submitted_instances: int) \
    -> float:
    """Calculates the percentage of resolved instances.

    Args:
        resolved_instances (int): The number of instances that have been resolved.
        submitted_instances (int): The total number of instances that were submitted.

    Returns:
        float: The percentage of resolved instances.
    """

    try:
        IntModel(items=resolved_instances)
        IntModel(items=submitted_instances)
    except ValidationError as e:
        print(f"Validation error: {e}")
        raise e
    
    percentage_resolved = resolved_instances / submitted_instances

    return percentage_resolved

def calculate_kowinski_score(resolved_instances: int, submitted_instances: int, \
                             skipped_instances: int) -> float:
    """
    Calculate the Kowinski score based on the number of resolved, submitted, 
    and skipped instances.

    The Kowinski score is calculated using the formula:
    
        kowinski_score = (resolved_instances - submitted_instances) / 
        (resolved_instances + submitted_instances + skipped_instances)
        
    This metric incentivizes skipping an issue over submitting a bad patch.

    Args:
        resolved_instances (int): The number of instances that have been resolved.
        submitted_instances (int): The total number of instances that were submitted.
        skipped_instances (int): The number of instances that were skipped.

    Returns:
        float: The calculated Kowinski score.
    """

    try:
        IntModel(items=resolved_instances)
        IntModel(items=submitted_instances)
        IntModel(items=skipped_instances)
    except ValidationError as e:
        print(f"Validation error: {e}")
        raise e
    
    kowinski_score = (resolved_instances - submitted_instances) / \
        (resolved_instances + submitted_instances + skipped_instances)

    return kowinski_score