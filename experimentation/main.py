#!.venv/bin/python3.9
# usage: uv run main.py [-h] --dataset-name DATASET_NAME --number-of-instances 
# NUMBER_OF_INSTANCES --random-sampling RANDOM_SAMPLING
# Example: 
# source .venv/bin/activate
# uv run main.py --dataset-name princeton-nlp/SWE-bench_Verified --number-of-instances 1 --random-sampling 0 # noqa

import argparse
import os
import subprocess
import sys
import time
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

with temporary_sys_path(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))):
    from experimentation.code.imports.generate_inferences import generate_inferences
    from experimentation.code.imports.generate_metrics import generate_metrics

# to deal with apt lock problems
def is_apt_get_running():
    result = subprocess.run(['pgrep', 'apt-get'], stdout=subprocess.PIPE)
    return result.returncode == 0

# to deal with apt lock problems
def run_apt_script(script_path: str):
    max_retries = 5
    retry_delay = 10  # seconds

    for _ in range(max_retries):
        if not is_apt_get_running():
            try:
                subprocess.run(['bash', '-c', f'source {script_path}'], 
                                check=True)
                print("Apt script executed successfully.")
                return
            except subprocess.CalledProcessError as e:
                print(f"Error executing setup script: {e}")
                return
        else:
            print(f"apt-get is running. Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)

    print("Max retries reached. Could not execute setup script due to apt-get lock.")
    

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Sets up docker and SWE-bench, \
                                    generates SWE_Verified metrics \
                                    for the AI solution.")
    parser.add_argument('--dataset-name', required=True, help='Name of the dataset')
    parser.add_argument('--number-of-instances', required=True, 
                        help='Number of instances (number)')
    parser.add_argument('--random-sampling', required=True, 
                        help='Random sampling (0 or 1)')
    args = parser.parse_args()

    dataset_name = args.dataset_name
    number_of_instances = int(args.number_of_instances)
    random_sampling = bool(args.random_sampling)

    # Ensure the script is run from its directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if os.getcwd() != script_dir:
        print("Please run this script from the directory it is in")
        sys.exit(1)

    # Source setup_docker.sh
    print("---------------Sourcing setup_docker.sh---------------")
    setup_docker_script = os.path.join(script_dir, 'code', 'scripts', 
                                'setup_docker.sh')
    run_apt_script(setup_docker_script)

    # Source setup_swe_bench.sh
    print("---------------Sourcing setup_swe_bench.sh---------------")
    setup_swe_script = os.path.join(script_dir, 'code', 'scripts', 
                                'setup_swe_bench.sh')
    subprocess.run(['bash', '-c', f'source {setup_swe_script}'], check=True)

    # install litellm pythin package (dont know why but something seems 
    # to be uninstallling litellm before this)
    print("---------------Installing litellm python package---------------")
    subprocess.run(['uv', 'add', 'litellm'], check=True)

    # Run generate_inferences.py
    print("--------------Running generate_inferences.py--------------")
    num_skipped_instances, summary = generate_inferences(dataset_name=dataset_name, 
                                            number_of_instances=number_of_instances, 
                                            random_sampling=random_sampling)

    # Source generate_results.sh
    print("--------------Sourcing generate_results.sh----------------")
    generate_results_script = os.path.join(script_dir, 'code', 'scripts', 
                                           'generate_results.sh')
    subprocess.run(['bash', '-c', f'source {generate_results_script} \
                    --dataset-name {dataset_name}'], check=True)

    # Run generate_metrics.py
    print("------------Running generate_metrics.py----------------")
    generate_metrics(num_skipped_instances=num_skipped_instances, summary=summary)

if __name__ == "__main__":
    main()