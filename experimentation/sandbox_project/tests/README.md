# Test Suite Documentation

## Overview
This directory contains the test suite for the sandbox project. The tests are designed to verify the functionality of the system components, including database interactions with Qdrant and Neo4j.

## Prerequisites
Before running the tests, ensure you have the following installed:
- Docker (version 20.10.0 or higher)
- Docker Compose (version 2.0.0 or higher)
- Python 3.8 or higher
- pytest

## Environment Setup

### 1. Starting the Test Environment
The project includes a setup script that handles the initialization of required services. To start the test environment:

```bash
./setup_tests.sh
```

This script will:
- Start the required Docker containers (Qdrant and Neo4j)
- Wait for the containers to be fully operational
- Perform health checks on the services
- Keep the containers running until you stop the script

### 2. Service Endpoints
Once the environment is running, the following services will be available:
- Qdrant: http://localhost:6333
- Neo4j: http://localhost:7474

## Running Tests

### Execute Test Suite
To run the complete test suite:
```bash
pytest tests/
```

For verbose output:
```bash
pytest -v tests/
```

To run specific test files:
```bash
pytest tests/test_specific_file.py
```

## Troubleshooting

### Common Issues

1. **Docker Containers Not Starting**
   - Verify Docker daemon is running
   - Check for port conflicts
   - Review Docker logs: `docker logs container_name`

2. **Service Health Checks Failing**
   - Ensure sufficient system resources are available
   - Check service logs for specific errors
   - Verify network connectivity

3. **Test Failures**
   - Confirm all required services are running
   - Check database configurations match test fixtures
   - Review test logs for specific error messages

## Cleanup

The test environment can be cleaned up in two ways:

1. If running `setup_tests.sh`:
   - Press Ctrl+C to stop the script
   - The script will automatically clean up containers

2. Manual cleanup:
   ```bash
   docker-compose down
   ```

## Additional Notes
- The test environment uses isolated Docker containers to prevent interference with local development environments
- All database data is ephemeral and will be cleared when containers are stopped
- The setup script includes automatic health checks to ensure services are ready before tests begin