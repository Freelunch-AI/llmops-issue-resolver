# Generates results/subsresults/inferences.jsonl file

import os
import sys
from contextlib import contextmanager
from typing import List

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

with temporary_sys_path(os.abs(os.join("../../../", os.path.dirname(__file__)))):
    from experimentation.code.imports.run_ai import run_ai
    from experimentation.code.imports.utils.schema_models import \
    StringModel, IntModel, BoolModel

def get_instances_ids(dataset_pointer_path: str, dataset_name: str, \
    number_of_instances: int, random_sampling: bool) -> List[str]:
    """
        Gets instance ids from the dataset and puts them in a list.
        Args:
            dataset_pointer_path (str): The path to the dataset pointer.
            dataset_name (str): The name of the dataset.
            number_of_instances (int): The number of instances to retrieve.
            random_sampling (bool): Whether to sample instances randomly.
        Returns:
            List[str]: A list of instance ids.
    """
    try:
        StringModel(items=dataset_pointer_path)
        StringModel(items=dataset_name)
        IntModel(items=number_of_instances)
        BoolModel(items=random_sampling)
    except ValidationError as e:
        print(f"Validation error: {e}")
        raise
    
    return instances_ids

def setup_instance(instance_id: str):
    """
        Sets up an instance with the given instance ID.

        Args:
            instance_id (str): The unique identifier for the instance to be set up.

        Returns:
            None
    """

    try:
        StringModel(items=instance_id)
    except ValidationError as e:
        print(f"Validation error: {e}")
        raise

    return

def append_to_inferences(inferences_path: str):
    """
        Gets local git patch, builds inference json and appends it inferences to 
        inferences.jsonl.

        Args:
            inferences_path (str): The path to the inferences file.

        Returns:
            None
    """

    try:
        StringModel(items=inferences_path)
    except ValidationError as e:
        print(f"Validation error: {e}")
        raise

    return

# <TODO> dataset-name, number_of_instances and random_sampling variabled are passed as 
# command line arguments, 
# example: python generate_inferences.py --dataset-name swe_bench_verified \
# --number-of-instances 10 --random-sampling True
def main() -> None:
    """
    Main function to generate inferences.

    This function retrieves a specified number of instance IDs from a dataset,
    sets up each instance, and appends the results to an inferences file.

    Command line arguments:
    --dataset-name: str
    --number-of-instances: int
        The number of instances to retrieve from the dataset.
    --random-sampling: bool
        Whether to randomly sample the instances or not (if not, then get the first 
        n instances).

    The function performs the following steps:
    1. Retrieves instance IDs from the specified dataset.
    2. Sets up each instance using the retrieved instance IDs.
    3. Runs the AI solution for each instance
    4. Appends the inference results to a specified JSONL file.

    Note:
    - The dataset pointer path is hardcoded in the function.
    - The inferences file path is also hardcoded in the function.
    """

    try:
        StringModel(items=dataset_name)
        IntModel(items=number_of_instances)
        BoolModel(items=random_sampling)
    except ValidationError as e:
        print(f"Validation error: {e}")
        raise

    instances_ids = get_instances_ids(
        dataset_pointer_path="experimentation/datasets/datasets.yml", \
        dataset_name=dataset_name, number_of_instances=number_of_instances, \
        random_sampling=True
        )
    for instance_id in instances_ids:
        setup_instance(instance_id=instance_id)
        run_ai()
        append_to_inferences(inferences_path="src/llmops_issue_resolver/experimentation/results/subresults/inference.jsonl")
    return

if __name__ == '__main__':
    main()