#!/usr/bin/env bash

# Sets up SWE-bench

set -o errexit
set -o nounset
set -o pipefail
if [[ "${TRACE-0}" == "1" ]]; then 
    set -o xtrace; 
fi

main() {
    echo "------------------Started setup_swe_bench.sh>main----------------------"
    # -- Setup SWE-bench --
    if [ ! -d "SWE-bench" ]; then
        git clone https://github.com/swe-bench/SWE-bench.git
    else
        echo "SWE-bench directory already exists. Skipping clone."
    fi
    
    sudo chmod -R 777 .
    uv venv
    deactivate
    source .venv/bin/activate
    # -e flag requires elevated privileges
    uv pip install ./SWE-bench
    echo "----------------Finished setup_swe_bench.sh>main----------------------"
}

main "$@"    

    