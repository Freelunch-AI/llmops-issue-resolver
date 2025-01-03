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


def get_relevant_subresults_data(skipped_instances: int) -> RelevantSubresults:
    """
    Retrieve the relevant subresults data from results/subsresults/summary.json file.

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
        RelevantSubsresults pydantic model
            - "submitted_instances"
            - "resolved_instances"
            - "skipped_instances"

    Returns:
        relevant_subresults_data (RelevantSubresults): data structure containing 
        relevant data for later calculating metrics.
    """

    import json

    summary_file_path = os.path.join("results", "subsresults", "summary.json")
    with open(summary_file_path, "r") as file:
        summary_data = json.load(file)

    relevant_subresults_data = RelevantSubresults(
        submitted_instances=summary_data["submitted_instances"],
        resolved_instances=summary_data["resolved_instances"],
        skipped_instances=skipped_instances
    )
    
    return relevant_subresults_data

def build_metrics(relevant_subresults_data: RelevantSubresults) -> Metrics:
    """
    Builds and returns metrics (as Metrics Pydantic model) 
    based on the provided relevant subresults data.

    Metrics to be calculated:

    - Percentage of resolved instances == resolved_instances / submitted_instances * 100
    - Kowinski score == (resolved_instances - b)/ (resolved_instances + b + 
    skipped_instances) 
    where b == submitted_instances - resolved_instances - skipped_instances

    Calls the following functions from calculate_metrics.py:
    - calculate_percentage_resolved
    - calculate_kowinski_score

    Args:
        relevant_subresults_data (RelevantSubresults): The data from which metrics will
        be generated.

    Returns:
        metrics (Metrics): pydantic model containing the calculated metrics.
    """

    try:
        StringModel(items=relevant_subresults_data)
    except ValidationError as e:
        print(f"Validation error: {e}")
        raise

    percentage_resolved = calculate_percentage_resolved(
        relevant_subresults_data.resolved_instances,
        relevant_subresults_data.submitted_instances
    )

    kowinski_score = calculate_kowinski_score(
        relevant_subresults_data.resolved_instances,
        relevant_subresults_data.submitted_instances,
        relevant_subresults_data.skipped_instances
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

    import yaml

    with open(path, "w") as file:
        yaml.dump(metrics.dict(), file)

    print(f"Metrics written to {path}")

def parse_arguments():
    import argparse


    parser = argparse.ArgumentParser( \
        description="Generate metrics from subresults data.")
    parser.add_argument("--num-skipped-instances", type=int, required=True)
    args = parser.parse_args()
    return args.num_skipped_instances

def main() -> None:
    skipped_instances = parse_arguments()
    relevant_subresults_data = get_relevant_subresults_data(
        skipped_instances=skipped_instances)
    metrics = build_metrics(relevant_subresults_data)
    write_metrics(metrics)
    return

if __name__ == '__main__':
    main()