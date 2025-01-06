# Generates results/subsresults/inferences.jsonl file

import argparse
import json
import os
import shutil
import sys
from contextlib import contextmanager
from typing import List

import pandas as pd
from datasets import load_dataset
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
                                                     "../../../"))):
    from experimentation.code.imports.run_ai import run_ai
    from experimentation.code.imports.utils.schema_models import (
        BoolModel,
        IntModel,
        PandasSeriesModel,
        StringModel,
    )
    from experimentation.code.imports.utils.seeds import DEFAULT_SEED

def get_dataset_path(dataset_name: str) -> str:
        """
        Constructs the local path for the dataset based on its name.

        Args:
            dataset_name (str): The name of the dataset.

        Returns:
            str: The local path to the dataset file.
        """

        try:
            StringModel(items=dataset_name)
        except ValidationError as e:
            print(f"Validation error: {e}")
            raise

        dataset_name_underline = dataset_name.replace("/", "_")
        dataset_path = os.path.join("datasets", f"{dataset_name_underline}", 
                                    f"{dataset_name_underline}.parquet")
        return dataset_path

def get_instances_ids(dataset_name: str, \
    number_of_instances: int, random_sampling: bool, dataset: pd.DataFrame) \
        -> pd.Series:
    """
        Gets instance ids from the dataset and puts them in a list.
        
        Steps:
            1. Use dataset_pointer_path to ge the dataset from hugginface. 
            The http path is the value to the key url which is a property of 
            <dataset_name>.
            2. Store the dataset locally in datasets/swe_bench_verified/
            swe_bench_verified.parquet
            3. Get the instance ids from the dataset and put them in a list.

        Args:
            dataset_pointer_path (str): The path to the dataset pointer .yml file.
            dataset_name (str): The name of the dataset.
            number_of_instances (int): The number of instances to retrieve.
            random_sampling (bool): Whether to sample instances randomly.
        Returns:
            List[str]: A list of instance ids.
    """

    try:
        StringModel(items=dataset_name)
        IntModel(items=number_of_instances)
        BoolModel(items=random_sampling)
    except ValidationError as e:
        print(f"Validation error: {e}")
        raise

    # Get the instance IDs
    if random_sampling:
        instances_ids = \
        dataset.sample(n=number_of_instances, random_state=DEFAULT_SEED) \
        ['instance_id']
    else:
        instances_ids = dataset.head(number_of_instances)['instance_id']

    return instances_ids

def get_repo_name(instance: pd.Series) -> str:
            """
            Retrieves the repository name for a given dataset and instance ID.

            Args:
                dataset_name (str): The name of the dataset.
                instance_id (str): The unique identifier for the instance.

            Returns:
                str: The repository name.
            """

            try:
                PandasSeriesModel(series=instance)
            except ValidationError as e:
                print(f"Validation error: {e}")
                raise

            repo_path = instance["repo"]
            repo_name = repo_path.split("/")[1]

            return repo_name

def setup_instance(dataset_name:str, instance: pd.Series) -> str:
    """
        Sets up the stage for an AI solution to run inference for a specific instance.

        Steps:
            1. Get row of the dataset swe_benc_verified that corresponds to the 
            instance_id.
                1. Get http pointer to the dataset in huggingface 
                (e.g., https://huggingface.co/datasets/princeton-nlp/SWE-bench_Verified), 
                which is in datasets/datasets.yml as the value for the key 
                <dataset_name>
                2. Get the columns ["base_commit" (str), "hints_text" (str), 
                "test_patch" (str), "problem_statement" (str), "FAIL_TO_PASS" (str)], 
                the row that has the instance_id in the column 'instance_id'.
            2. Pull the repo that has the issue at a specific commit of the main branch.
            The specific commit is "base_commit".
            3. Build helper files for the AI solution to run inference.
                1. Build issue.md file with the content of the column 
                "problem_statement".
                2. Build tips.txt file with the content of the column "hints_text".
                3. Build fail_to_pass.txt file with the content of the column 
                "FAIL_TO_PASS".

        Args:
            dataset_name: (str): The name of the dataset.
            instance_id (str): The unique identifier for the instance to be set up.
            
        Returns:
            None
    """

    try:
        PandasSeriesModel(series=instance)
        StringModel(items=dataset_name)
    except ValidationError as e:
        print(f"Validation error: {e}")
        raise

    # Pull the repo at the specific commit
    base_commit = instance["base_commit"]
    # clone the repo
    repo_path = instance['repo']
    repo_name = repo_path.split("/")[1]

    os.makedirs("tmp", exist_ok=True)
    os.chdir("tmp")

    os.system(f"git clone https://github.com/{repo_path}.git")
    
    os.chdir(f"{repo_name}")
    os.system(f"git checkout {base_commit} && git reset --hard {base_commit}")

    # Build helper files
    with open("issue.md", "w") as f:
        f.write(instance["problem_statement"])

    with open("tips.txt", "w") as f:
        f.write(instance["hints_text"])

    with open("fail_to_pass.txt", "w") as f:
        f.write(instance["FAIL_TO_PASS"])

    setup_commit = os.popen("git rev-parse HEAD").read().strip()

    os.chdir("../../")

    return setup_commit

def append_to_inferences(inferences_path: str, instance_id: str, instance: pd.Series, \
                         experiment_name: str) -> None:
    """
        Gets local git patch, builds inference instance json and appends it 
        inferences to inferences.jsonl.

        Inference json looks like this:

        {
            "instance_id": "<Unique task instance ID>",
            "model_patch": "<.patch file content string>",
            "model_name_or_path": "<Model name here (i.e. SWE-Llama-13b)>",
        }

        Args:
            inferences_path (str): The path to the inferences file inferences.jsonl.

        Returns:
            None
    """

    try:
        StringModel(items=inferences_path)
        StringModel(items=instance_id)
        StringModel(items=experiment_name)
    except ValidationError as e:
        print(f"Validation error: {e}")
        raise

    # <TODO: fix> the patch is always returning empty
    repo_name = get_repo_name(instance=instance)
    os.chdir(os.path.join("tmp", repo_name))
    patch = os.popen("git diff --patch").read()
    os.chdir("../../")

    inference_instance = {
        "instance_id": instance_id,
        "model_patch": patch,
        "model_name_or_path": experiment_name
    }

    with open(inferences_path, "a") as f:
        f.write(json.dumps(inference_instance) + "\n")

    return

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
    print("-----------------Started generate_inferences.py>main---------------")

    #empty inferences.jsonl file
    with open("results/subresults/inferences.jsonl", "w") as f:
        f.write("")

    parser = argparse.ArgumentParser(description="Generate inferences")
    parser.add_argument("--dataset-name", type=str, required=True, 
                        help="Name of the dataset")
    parser.add_argument("--number-of-instances", type=int, required=True, 
                        help="Number of instances to retrieve")
    parser.add_argument("--random-sampling", type=bool, required=True, 
                        help="Whether to randomly sample instances")

    args = parser.parse_args()

    dataset_name = args.dataset_name
    number_of_instances = int(args.number_of_instances)
    random_sampling = bool(args.random_sampling)

    try:
        StringModel(items=dataset_name)
        IntModel(items=number_of_instances)
        BoolModel(items=random_sampling)
    except ValidationError as e:
        print(f"Validation error: {e}")
        raise

    dataset = load_dataset(dataset_name)["test"].to_pandas()
    dataset_path = get_dataset_path(dataset_name)
    os.makedirs(os.path.dirname(dataset_path), exist_ok=True)
    dataset.to_parquet(dataset_path)

    instances_ids = get_instances_ids(
        dataset_name=dataset_name, number_of_instances=number_of_instances, 
        random_sampling=True,
        dataset=dataset
    )

    dataset = pd.read_parquet(get_dataset_path(dataset_name))
    
    skipped_instances = 0
    for instance_id in instances_ids:
        # Find the instance by instance_id 
        instance = dataset[dataset["instance_id"] == instance_id].iloc[0]

        setup_commit = setup_instance(dataset_name=dataset_name, instance=instance)
        
        repo_name = get_repo_name(instance=instance)

        os.chdir(os.path.join("tmp", repo_name))
        os.system(f"git reset --hard {setup_commit}")
        experiment_name, skipped_instance = run_ai()
        os.chdir("../../")

        if not skipped_instance:
            append_to_inferences(inferences_path=os.path.join("results", 
                                os.path.join("subresults", "inferences.jsonl")), \
                                instance_id=instance_id, \
                                instance = instance,
                                experiment_name=experiment_name)
        else:
            skipped_instances += 1

        shutil.rmtree(os.path.join("tmp", repo_name))    
    print(skipped_instances)
    print("-----------------Finished generate_inferences.py>main---------------")
    return

if __name__ == '__main__':
    main()