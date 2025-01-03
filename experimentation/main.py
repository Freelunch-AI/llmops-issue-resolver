#!/usr/bin/env python3

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
                        help='Random sampling (true or false)')
    parser.add_argument('--experiment-name', required=True, help='Experiment name')
    args = parser.parse_args()

    # Ensure the script is run from its directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if os.getcwd() != script_dir:
        print("Please run this script from the directory it is in")
        sys.exit(1)

    # Source setup_results_generator.sh
    setup_script = os.path.join(script_dir, 'code/scripts/setup_results_generator.sh')
    subprocess.run(['bash', '-c', f'source {setup_script}'], check=True)

    # Run generate_inferences.py
    generate_inferences_cmd = [
        'uv', 'run', 'python', 'code/scripts/generate_inferences.py',
        '--dataset-name', args.dataset_name,
        '--number-of-instances', args.number_of_instances,
        '--random-sampling', args.random_sampling,
        '--experiment-name', args.experiment_name
    ]
    result = subprocess.run(generate_inferences_cmd, capture_output=True, text=True, \
                            check=True)
    num_skipped_instances = result.stdout.strip()

    # Source generate_results.sh
    generate_results_script = os.path.join( \
        script_dir, 'code/scripts/generate_results.sh')
    subprocess.run(['bash', '-c', f'source {generate_results_script} \
                    --dataset-name {args.dataset_name}'], check=True)

    # Run generate_metrics.py
    generate_metrics_cmd = [
        'uv', 'run', 'python', 'code/scripts/generate_metrics.py',
        '--num-skipped-instances', num_skipped_instances
    ]
    subprocess.run(generate_metrics_cmd, check=True)

if __name__ == "__main__":
    main()