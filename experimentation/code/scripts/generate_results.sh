#!/usr/bin/env bash

# Generates results given already generated results/subresults/inferences.jsonl file

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
    --predictions_path results/subresults/inferences.jsonl \
    --max_workers 5 \
    --run_id summary

    # move fie ending with .summary.json from . to results/subresults as summary.json
    mv *.summary.json results/subresults/summary.json
}

main "$@"