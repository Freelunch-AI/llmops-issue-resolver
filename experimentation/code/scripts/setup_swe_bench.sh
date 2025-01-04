#!/usr/bin/env bash

# Sets up SWE-bench

set -o errexit
set -o nounset
set -o pipefail
if [[ "${TRACE-0}" == "1" ]]; then 
    set -o xtrace; 
fi

main() {
    # -- Setup SWE-bench --
    if [ ! -d "SWE-bench" ]; then
        git clone https://github.com/swe-bench/SWE-bench.git
    else
        echo "SWE-bench directory already exists. Skipping clone."
    fi
    
    sudo chmod -R 777 .
    uv venv
    source .venv/bin/activate
    uv pip install "./SWE-bench" # -e flag requires elevated privileges
}

main "$@"    

    