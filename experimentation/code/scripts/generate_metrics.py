# Generates results/metrics.yml file

import os
import sys
from contextlib import contextmanager

from pydantic import ValidationError


@contextmanager
def temporary_sys_path(path: str):
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

    try:
        StringModel(items=path)
    except ValidationError as e:
        print(f"Validation error: {e}")
        raise

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

with temporary_sys_path(os.abs(os.join("../../../", os.path.dirname(__file__)))):
    from experimentation.code.imports.utils.calculate_metrics import (
        calculate_kowinski_score,
        calculate_percentage_resolved,
    )
    from experimentation.code.imports.utils.schema_models import (
        Metrics,
        RelevantSubresults,
        StringModel,
    )


def get_relevant_subresults_data() -> RelevantSubresults:
    """
    Retrieve the relevant subresults data from results/subsresults/report.json and 
    results/subsresults/summary.json files

    Returns:
        relevant_subresults_data (RelevantSubresults): data structure containing 
        relevant data for later calculating metrics.
    """
    
    return relevant_subresults_data

def build_metrics(relevant_subresults_data: RelevantSubresults) -> Metrics:
    """
    Builds and returns metrics based on the provided relevant subresults data.

    Args:
        relevant_subresults_data (RelevantSubresults): The data from which metrics will
        be generated.

    Returns:
        metrics (Metrics): data structure containing the calculated metrics.
    """

    try:
        StringModel(items=relevant_subresults_data)
    except ValidationError as e:
        print(f"Validation error: {e}")
        raise

    return metrics

def write_metrics(metrics: Metrics, path: str ="results/metrics.yml") -> None:
    """
    Writes the given metrics to a specified file in YAML format.

    Args:
        metrics (Metrics): data structure containing the calculated metrics.
        path (str, optional): The file path where the metrics will be saved. 
        Defaults to "results/metrics.yml".

    Returns:
        None
    """

    try:
        Metrics(items=metrics)
        StringModel(items=path)
    except ValidationError as e:
        print(f"Validation error: {e}")
        raise

    return

def main() -> None:
    relevant_subresults_data = get_relevant_subresults_data()
    metrics = build_metrics(relevant_subresults_data)
    write_metrics(metrics)
    return

if __name__ == '__main__':
    main()