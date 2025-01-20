#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper function for printing status messages
print_status() {
    echo -e "${2}${1}${NC}"
}

# Helper function to check if a container is running
check_container() {
    local container_name=$1
    if docker ps --format '{{.Names}}' | grep -q "^.*${container_name}.*$"; then
        return 0
    else
        return 1
    fi
}

# Helper function to wait for container health
wait_for_container() {
    local container_name=$1
    local max_attempts=30
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        if check_container "$container_name"; then
            print_status "✓ $container_name is running" "$GREEN"
            return 0
        fi
        print_status "Waiting for $container_name to start (attempt $attempt/$max_attempts)..." "$YELLOW"
        sleep 2
        attempt=$((attempt + 1))
    done

    print_status "✗ Failed to start $container_name after $max_attempts attempts" "$RED"
    return 1
}

# Check Qdrant health
check_qdrant_health() {
    local max_attempts=30
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        if curl -s http://localhost:6333/health > /dev/null; then
            print_status "✓ Qdrant is healthy" "$GREEN"
            return 0
        fi
        print_status "Waiting for Qdrant to be healthy (attempt $attempt/$max_attempts)..." "$YELLOW"
        sleep 2
        attempt=$((attempt + 1))
    done

    print_status "✗ Qdrant health check failed" "$RED"
    return 1
}

# Check Neo4j health
check_neo4j_health() {
    local max_attempts=30
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        if curl -s http://localhost:7474 > /dev/null; then
            print_status "✓ Neo4j is healthy" "$GREEN"
            return 0
        fi
        print_status "Waiting for Neo4j to be healthy (attempt $attempt/$max_attempts)..." "$YELLOW"
        sleep 2
        attempt=$((attempt + 1))
    done

    print_status "✗ Neo4j health check failed" "$RED"
    return 1
}

# Setup function
setup() {
    print_status "Starting test environment setup..." "$YELLOW"

    # Start Docker containers
    print_status "Starting Docker containers..." "$YELLOW"
    docker-compose up -d qdrant neo4j

    # Wait for containers to start
    wait_for_container "qdrant" || return 1
    wait_for_container "neo4j" || return 1

    # Check container health
    check_qdrant_health || return 1
    check_neo4j_health || return 1

    print_status "Test environment setup completed successfully!" "$GREEN"
    return 0
}

# Cleanup function
cleanup() {
    print_status "\nCleaning up test environment..." "$YELLOW"
    docker-compose down
    print_status "Cleanup completed!" "$GREEN"
    exit 0
}

# Trap Ctrl+C and call cleanup
trap cleanup INT

# Main execution
setup
if [ $? -ne 0 ]; then
    print_status "Failed to set up test environment" "$RED"
    cleanup
    exit 1
fi

# Keep script running to maintain containers
print_status "\nPress Ctrl+C to stop and cleanup the test environment" "$YELLOW"
while true; do
    sleep 1
done