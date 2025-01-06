#!.venv/bin/python3.9
# usage: uv run main.py [-h] --dataset-name DATASET_NAME --number-of-instances 
# NUMBER_OF_INSTANCES --random-sampling RANDOM_SAMPLING
# Example: 
# source .venv/bin/activate
# uv run main.py --dataset-name swe_bench_verified --number-of-instances 5 --random-sampling 0

import argparse
import os
import subprocess
import sys


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Sets up docker and SWE-bench, \
                                    generates SWE_Verified metrics \
                                    for the AI solution.")
    parser.add_argument('--dataset-name', required=True, help='Name of the dataset')
    parser.add_argument('--number-of-instances', required=True, \
                        help='Number of instances (number)')
    parser.add_argument('--random-sampling', required=True, \
                        help='Random sampling (0 or 1)')
    args = parser.parse_args()

    # Ensure the script is run from its directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if os.getcwd() != script_dir:
        print("Please run this script from the directory it is in")
        sys.exit(1)

    # Source setup_docker.sh
    print("---------------Sourcing setup_docker.sh---------------")
    setup_docker_script = os.path.join(script_dir, 'code', 'scripts', \
                                'setup_docker.sh')
    subprocess.run(['sudo', '-E', 'bash', '-c', \
                    f'source {setup_docker_script}'], check=True)

    # Source setup_swe_bench.sh
    print("---------------Sourcing setup_swe_bench.sh---------------")
    setup_swe_script_script = os.path.join(script_dir, 'code', 'scripts', \
                                'setup_swe_bench.sh')
    subprocess.run(['bash', '-c', f'source {setup_swe_script_script}'], check=True)

    # Run generate_inferences.py
    print("--------------Running generate_inferences.py--------------")
    generate_inferences_cmd = [
        'uv', 'run', 'python', 
        os.path.join('code', 'scripts', 'generate_inferences.py'),
        '--dataset-name', args.dataset_name,
        '--number-of-instances', args.number_of_instances,
        '--random-sampling', args.random_sampling,
    ]
    result = subprocess.run(generate_inferences_cmd, capture_output=True, text=True, \
                            check=True)
    num_skipped_instances = result.stdout.strip()

    # Source generate_results.sh
    print("--------------Sourcing generate_results.sh----------------")
    generate_results_script = os.path.join(script_dir, 'code', 'scripts', \
                                           'generate_results.sh')
    subprocess.run(['bash', '-c', f'source {generate_results_script}', 
                    '--dataset_name', args.dataset_name], check=True)

    # Run generate_metrics.py
    print("------------Running generate_metrics.py----------------")
    generate_metrics_cmd = [
        'uv', 'run', 'python', os.path.join('code', 'scripts', 'generate_metrics.py'),
        '--num-skipped-instances', num_skipped_instances
    ]
    subprocess.run(generate_metrics_cmd, check=True)

if __name__ == "__main__":
    main()