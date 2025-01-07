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
    if [ ! -d "packages/SWE-bench" ]; then
        git clone https://github.com/swe-bench/SWE-bench.git packages/SWE-bench
    else
        echo "SWE-bench directory already exists. Skipping clone."
    fi
    
    sudo chmod -R 777 .
    uv venv
    echo "---------1---------"
    source .venv/bin/activate
    echo "---------2---------"
    # -e flag requires elevated privileges
    uv pip install ./packages/SWE-bench
    echo "----------------Finished setup_swe_bench.sh>main----------------------"
}

main "$@"    

    