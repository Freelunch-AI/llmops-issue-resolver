# Generates results/metrics.yml file

import json
import os
import sys
from contextlib import contextmanager

import yaml
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
                                                     '..', '..', '..'))):
    from experimentation.code.imports.utils.calculate_metrics import (
        calculate_kowinski_score,
        calculate_percentage_resolved,
    )
    from experimentation.code.imports.utils.schema_models import (
        IntModel,
        Metrics,
        RelevantSubResults,
        StringModel,
        ValidateMetrics,
        ValidateRelevantSubResults,
    )


def get_relevant_subresults(num_skipped_instances: int) -> RelevantSubResults:
    """
    Retrieve the relevant subresults data from results/subresults/summary.json file.

    E.g., of summary.json:

    {

        "total_instances": 500,
        "submitted_instances": 3,
        "completed_instances": 1,
        "resolved_instances": 0,
        "unresolved_instances": 1,
        "empty_patch_instances": 0,
        "error_instances": 2,
        "unstopped_instances": 0,
        "completed_ids": [
            "sympy__sympy-15599"
        ],
        "incomplete_ids": [
            "astropy__astropy-12907",
            "astropy__astropy-13033",
            "astropy__astropy-13236",
        ],
        "empty_patch_ids": [],
        "submitted_ids": [
            "sympy__sympy-12419",
            "sympy__sympy-15599",
            "sympy__sympy-18698"
        ],
        "resolved_ids": [],
        "unresolved_ids": [
            "sympy__sympy-15599"
        ],
        "error_ids": [
            "sympy__sympy-12419",
            "sympy__sympy-18698"
        ],
        "unstopped_containers": [],
        "unremoved_images": [],
        "schema_version": 2
    }

    Steps:
        1. Load summary.json file as data strcutures easy to work with.
        2. Put the key, value pairs of the following keys in the 
        RelevantSubresults pydantic model
            - "submitted_instances"
            - "resolved_instances"
            - "num_skipped_instances"

    Returns:
        relevant_subresults (RelevantSubresults): data structure containing 
        relevant data for later calculating metrics.
    """

    try:
        # validate num_skipped_instances
        IntModel(items=num_skipped_instances)
    except ValidationError as e:
        print(f"Validation error: {e}")
        raise e

    summary_file_path = os.path.join("results", "subresults", "summary.json")
    with open(summary_file_path, "r") as file:
        summary_data = json.load(file)

    relevant_subresults = RelevantSubResults(
        num_submitted_instances=summary_data["submitted_instances"],
        num_resolved_instances=summary_data["resolved_instances"],
        num_skipped_instances=num_skipped_instances
    )
    
    return relevant_subresults

def build_metrics(relevant_subresults: RelevantSubResults) -> Metrics:
    """
    Builds and returns metrics (as Metrics Pydantic model) 
    based on the provided relevant subresults data.

    Metrics to be calculated:

    - Percentage of resolved instances == resolved_instances / submitted_instances * 100
    - Kowinski score == (resolved_instances - b)/ (resolved_instances + b + 
    num_skipped_instances) 
    where b == submitted_instances - resolved_instances - num_skipped_instances

    Calls the following functions from calculate_metrics.py:
    - calculate_percentage_resolved
    - calculate_kowinski_score

    Args:
        relevant_subresults (RelevantSubresults): The data from which metrics will
        be generated.

    Returns:
        metrics (Metrics): pydantic model containing the calculated metrics.
    """

    try:
        ValidateRelevantSubResults(relevant_subresults=relevant_subresults)
    except ValidationError as e:
        print(f"Validation error: {e}")
        raise e

    percentage_resolved = calculate_percentage_resolved(
        relevant_subresults.num_resolved_instances,
        relevant_subresults.num_submitted_instances
    )

    kowinski_score = calculate_kowinski_score(
        relevant_subresults.num_resolved_instances,
        relevant_subresults.num_submitted_instances,
        relevant_subresults.num_skipped_instances
    )

    metrics = Metrics(
        percentage_resolved=percentage_resolved,
        kowinski_score=kowinski_score
    )

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
       ValidateMetrics(metrics=metrics)
       StringModel(items=path)
    except ValidationError as e:
        print(f"Validation error: {e}")
        raise e

    with open(path, "w") as file:
        yaml.dump(metrics.model_dump(), file)

    print(f"Metrics written to {path}")

def generate_metrics(num_skipped_instances: int) -> None:
    print("-----------------Started generate_metric.py>main---------------")
    relevant_subresults = get_relevant_subresults(
        num_skipped_instances=num_skipped_instances)
    metrics = build_metrics(relevant_subresults)
    write_metrics(metrics)
    print("-----------------Finished generate_metric.py>main---------------")

    return