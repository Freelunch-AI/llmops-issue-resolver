# Generates results/subsresults/inferences.jsonl file
# E.g., uv run code/scripts/generate_inferences.py --dataset-name \
# princeton-nlp/SWE-bench_Verified --number-of-instances 1 --random-sampling 0

import json
import os
import shutil
import sys
from contextlib import contextmanager

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
                                                     '..', '..', '..'))):
    from experimentation.code.imports.run_ai import run_ai
    from experimentation.code.imports.schemas.schema_models import (
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

def setup_instance(dataset_name:str, instance: pd.Series) -> None:
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

    os.chdir("tmp")

    os.system(f"git clone https://github.com/{repo_path}.git")
    
    os.chdir(f"{repo_name}")
    os.system(f"git reset --hard {base_commit}")

    # Build helper files
    with open("issue.md", "w") as f:
        f.write(instance["problem_statement"])

    with open("tips.txt", "w") as f:
        f.write(instance["hints_text"])

    with open("fail_to_pass.txt", "w") as f:
        f.write(instance["FAIL_TO_PASS"])

    os.system(f"git add . && git commit -m 'instance setup'")

    os.chdir("../../")

    return

def append_to_inferences(inferences_path: str, instance: pd.Series, \
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
        PandasSeriesModel(series=instance)
        StringModel(items=experiment_name)  
    except ValidationError as e:
        print(f"Validation error: {e}")
        raise

    repo_name = get_repo_name(instance=instance)
    os.chdir(os.path.join("tmp", repo_name))
    os.system("git branch")
    patch = os.popen("git diff --patch HEAD~1 HEAD").read()
    os.chdir("../../")

    inference_instance = {
        "instance_id": instance["instance_id"],
        "model_patch": patch,
        "model_name_or_path": experiment_name
    }

    with open(inferences_path, "a") as f:
        f.write(json.dumps(inference_instance) + "\n")

    return

def generate_inferences(dataset_name: str, number_of_instances: int, random_sampling: 
                        bool) -> None:

    print("-----------------Started generate_inferences.py>main---------------")

    #empty inferences.jsonl file
    with open("results/subresults/inferences.jsonl", "w") as f:
        f.write("")

    try:
        StringModel(items=dataset_name)
        IntModel(items=number_of_instances)
        BoolModel(items=random_sampling)
    except ValidationError as e:
        print(f"Validation error: {e}")
        raise

    df = load_dataset(dataset_name)["test"].to_pandas()
    dataset_path = get_dataset_path(dataset_name)
    os.makedirs(os.path.dirname(dataset_path), exist_ok=True)
    df.to_parquet(dataset_path)

    # get only <number_of_instances> from df. Two options: random or not
    df_sampled = df.sample(n=number_of_instances, random_state=DEFAULT_SEED) \
        if random_sampling \
        else df.head(number_of_instances)

    skipped_instances = 0
    # if tmp directory exists, delete contents of it, else create the tmp directory
    if os.path.exists("tmp"):
        shutil.rmtree("tmp")
    os.makedirs("tmp")
    for _, instance in df_sampled.iterrows():
        # Find the instance by instance_id 

        setup_instance(dataset_name=dataset_name, instance=instance)
        repo_name = get_repo_name(instance=instance)

        os.chdir(os.path.join("tmp", repo_name))
        experiment_name, skipped_instance, summary = run_ai()
        os.system(f"git add . && git commit -m 'AI solution run'")
        os.chdir("../../")

        if not skipped_instance:
            append_to_inferences(inferences_path=os.path.join("results", 
                                os.path.join("subresults", "inferences.jsonl")), 
                                instance = instance, \
                                experiment_name=experiment_name)
        else:
            skipped_instances += 1

        shutil.rmtree(os.path.join("tmp", repo_name))
    shutil.rmtree("tmp")       
    print(skipped_instances)
    print("-----------------Finished generate_inferences.py>main---------------")
    return skipped_instances, summary