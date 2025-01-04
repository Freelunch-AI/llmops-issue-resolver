#!/usr/bin/env bash

# Sets up docker and SWE-bench

set -o errexit
set -o nounset
set -o pipefail
if [[ "${TRACE-0}" == "1" ]]; then 
    set -o xtrace; 
fi

main() {
    echo "Started setup_results_generator.sh>main"
    # -- Setup Docker -- 

    # Add Docker's official GPG key:
    sudo apt-get update
    sudo apt-get install ca-certificates curl
    sudo install -m 0755 -d /etc/apt/keyrings
    sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
    sudo chmod a+r /etc/apt/keyrings/docker.asc

    # Add the repository to Apt sources:
    echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
    $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
    sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update

    # Install the Docker packages
    sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

    # Create the docker group
    if ! getent group docker > /dev/null; then
        sudo groupadd docker
    fi
    # Add the current user to the docker group
    sudo usermod -aG docker "$USER"
    # Activate new group
    newgrp docker

    # -- Setup SWE-bench --

    # <Todo> These lines are not running, dont know why
    git clone https://github.com/swe-bench/SWE-bench.git
    sudo uv pip install -e SWE-bench
    echo "Finished setup_results_generator.sh>main"
}

main "$@"


