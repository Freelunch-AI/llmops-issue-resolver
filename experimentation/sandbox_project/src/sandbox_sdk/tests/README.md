# Test Suite Documentation

## Overview
This directory contains the comprehensive test suite for the sandbox project. The test suite is designed to ensure reliability, correctness, and maintainability of the codebase through a combination of unit tests, integration tests, and end-to-end tests. The tests verify all system components, with particular focus on database interactions with Qdrant and Neo4j, API functionality, and core business logic.


## Testing Strategy
The project follows a pyramid testing strategy with three main layers:

1. **Unit Tests (70%)**
   - Focus on testing individual components in isolation
   - Mock external dependencies
   - Verify business logic and edge cases
   - Fast execution and high coverage

2. **Integration Tests (20%)**
   - Test interaction between components
   - Verify database operations with Qdrant and Neo4j
   - Test API endpoints and data flow

3. **End-to-End Tests (10%)**
   - Test complete user scenarios
   - Verify system behavior as a whole
   - Include UI/API workflow tests

## Test Organization
Tests are organized by type and functionality:

```
tests/
├── unit/              # Unit tests for individual components
│   ├── vector_store/   # Tests for vector store functionality
│   ├── graph/          # Tests for graph operations
│   ├── data/           # Tests for data processing
│   ├── api/            # Tests for API components
│   └── utils/          # Tests for utility functions
├── integration/       # Integration tests for component interactions
├── e2e/               # End-to-end tests for complete workflows
└── fixtures/          # Shared test fixtures and data
```

## Key Test Files

### Unit Tests
- `unit/vector_store/test_storage.py`: Tests for vector storage and retrieval operations
- `unit/graph/test_operations.py`: Tests for graph database operations
- `unit/data/test_processing.py`: Tests for data processing utilities

### Integration Tests
- `test_db_integration.py`: Tests database interactions and transactions
- `test_api_integration.py`: Tests API endpoints and responses
### End-to-End Tests
- `test_workflows.py`: Tests complete user workflows
- `test_system.py`: Tests system-wide functionality

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

### Test Coverage
The project maintains high test coverage to ensure code quality. To run tests with coverage reporting:

```bash
pytest --cov=src tests/
```

Generate HTML coverage report:
```bash
pytest --cov=src tests/ --cov-report=html
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
## Additional Notes
- The test environment uses isolated Docker containers to prevent interference with local development environments
- All database data is ephemeral and will be cleared when containers are stopped
- The setup script includes automatic health checks to ensure services are ready before tests begin

## Unit Test Organization Guidelines

The unit tests follow a mirrored directory structure that matches the main package:

1. **Directory Structure**
   - Unit tests are organized in directories that mirror the main package structure
   - Each component in `src/sandbox_sdk/` has a corresponding test directory in `tests/unit/`
   - Test files should be placed in the directory corresponding to the module they test

2. **Naming Conventions**
   - Test files should be named `test_*.py`
   - Test directories should match the source directory names
   - Each test file should focus on a specific module or functionality