#!/usr/bin/env bash

# Sets up docker and SWE-bench
# Generates SWE_Verified metrics for the AI solution in experimentation/code/imports/run.py

set -o errexit
set -o nounset
set -o pipefail
if [[ "${TRACE-0}" == "1" ]]; then 
    set -o xtrace; 
fi

main() {
    echo "Started main.sh>main"

    # shellcheck source=code/scripts/setup_results_generator.sh
    source code/scripts/setup_results_generator.sh

    uv run python code/scripts/generate_inferences.py \
    --output-inferences-path results/subresults/inferences.jsonl

    # shellcheck source=code/scripts/generate_results.sh
    source /code/scripts/generate_results.sh \
    --input-inferences-path results/subresults/inferences.jsonl \
    --output-report-path results/subresults/report.jsonl \
    --output-summary-path results/subresults/summary.jsonl
    
    uv run python code/scripts/generate_metrics.py \
    --input-report-path results/subresults/report.jsonl \
    --input-summary-path results/subresults/summary.jsonl \
    --output-metrics-path results/metrics.yml
}

main "$@"
