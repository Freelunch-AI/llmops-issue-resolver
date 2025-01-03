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

with temporary_sys_path(os.abs(os.join("../../../../", os.path.dirname(__file__)))):
    from experimentation.code.imports.utils.schema_models import RelevantSubresults

def calculate_percentage_resolved(
    relevant_subresults_data: RelevantSubresults) -> float:
    """Calculates the percentage of resolved issues

    Args:
        relevant_subresults_data (RelevantSubresults): relevant data, 
        from results/subsresults/report.json results/subresults/summary.json
        for calculating metrics

    Returns:
        float: percentage of resolved issues
    """

    try:
        RelevantSubresults(items=relevant_subresults_data)
    except ValidationError as e:
        print(f"Validation error: {e}")
        raise

    return

def calculate_kowinski_score(relevant_subresults_data: RelevantSubresults) -> float:
    """
    Calculate the Kowinski score based on the provided relevant subresults data.

    Submissions are scored using a simple metric that incentivizes skipping an issue over 
    submitting a bad patch.
    
        kowinski_score= (a - b)/ (a + b + c)
        
        where a, b, and c are respectively the number of correctly resolved issues, 
        the number of failing issues, and the number of skipped issues.

    Args:
        relevant_subresults_data (RelevantSubresults): 
        A pydantic model containing the relevant subresults data 
        required to calculate the Kowinski score.

    Returns:
        float: The calculated Kowinski score.
    """

    try:
        RelevantSubresults(items=relevant_subresults_data)
    except ValidationError as e:
        print(f"Validation error: {e}")
        raise

    return