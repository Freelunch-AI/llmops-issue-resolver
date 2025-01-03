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
    echo "Started generate_results.sh>main"

    uv run python -m swebench.harness.run_evaluation \
    --dataset_name princeton-nlp/SWE-bench_Verified \
    --predictions_path results/subresults/inference.jsonl \
    --max_workers 5 \
    --run_id summary

    # change generated summary file name from summary.summary_verified.json to summary.json
    mv results/subresults/summary.summary_verified.json results/subresults/summary.json
}

main "$@"