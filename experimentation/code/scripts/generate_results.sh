#!/usr/bin/env bash

# Generates results for SWE-bench-Verified, 
# given already generated results/subresults/inferences.jsonl file

set -o errexit
set -o nounset
set -o pipefail
if [[ "${TRACE-0}" == "1" ]]; then 
    set -o xtrace; 
fi

main() {
    echo "------------------Started generate_results.sh>main----------------------"

    local DATASET_NAME=$2

    uv run python -m swebench.harness.run_evaluation \
    --dataset_name "${DATASET_NAME}" \
    --predictions_path results/subresults/inference.jsonl \
    --max_workers 5 \
    --run_id summary

    # move summary file name from ./summary.summary_verified.json to results/subresults/summary.json
    mv summary.summary_verified.json results/subresults/summary.json

    # move report file from logs/run_evaluation/validate-summary/summary/sympy__sympy-20590/report.json
    # to results/subresults/report.json
    mv logs/run_evaluation/validate-summary/summary/sympy__sympy-20590/report.json results/subresults/report.json
    echo "----------------Finished generate_results.sh>main----------------------"
}

main "$@"