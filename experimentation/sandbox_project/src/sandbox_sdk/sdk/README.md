# Sandbox SDK

A Python SDK for managing and interacting with sandbox environments for LLM experimentation and testing.

## Overview

The Sandbox SDK provides a simple and intuitive interface for creating, managing, and interacting with isolated sandbox environments. These environments are designed for safe experimentation with Large Language Models (LLMs) and their associated tools.

## Installation

```bash
pip install sandbox-sdk
```

## Quick Start

```python
from sandbox_sdk import SandboxClient

# Initialize the client
client = SandboxClient()

# Create a new sandbox
sandbox = client.create_sandbox(name="my-experiment")

# Use the sandbox
sandbox.setup()
sandbox.run_experiment(...)
```

## Main Components

### SandboxClient

The `SandboxClient` class is the main entry point for interacting with the SDK. It provides methods for:

- Creating new sandboxes
- Managing existing sandboxes
- Configuring global settings
- Handling authentication and resources

Key methods:
- `create_sandbox(name: str, **kwargs)`: Create a new sandbox environment
- `get_sandbox(id: str)`: Retrieve an existing sandbox
- `list_sandboxes()`: List all available sandboxes
- `delete_sandbox(id: str)`: Remove a sandbox environment

### Sandbox

The `Sandbox` class represents an isolated environment for running experiments. Key features include:

- Environment isolation
- Resource management
- Experiment tracking
- State persistence

Key methods:
- `setup()`: Initialize the sandbox environment
- `run_experiment(config: dict)`: Execute an experiment
- `cleanup()`: Clean up resources
- `export_results(path: str)`: Export experiment results

## Usage Examples

### Creating and Managing Sandboxes

```python
from sandbox_sdk import SandboxClient

# Initialize client
client = SandboxClient()

# Create a sandbox with custom configuration
sandbox = client.create_sandbox(
    name="llm-experiment-1",
    resources={"memory": "2GB", "cpu": 1},
    timeout=3600
)

# List all sandboxes
sandboxes = client.list_sandboxes()

# Get a specific sandbox
sandbox = client.get_sandbox("sandbox-id")

# Delete a sandbox
client.delete_sandbox("sandbox-id")
```

### Running Experiments

```python
# Configure and run an experiment
sandbox.setup()

experiment_config = {
    "model": "gpt-3.5-turbo",
    "prompt": "Test prompt",
    "parameters": {
        "temperature": 0.7,
        "max_tokens": 100
    }
}

results = sandbox.run_experiment(experiment_config)

# Export results
sandbox.export_results("./results")

# Clean up
sandbox.cleanup()
```

## API Reference

### SandboxClient

| Method | Description | Parameters |
|--------|-------------|------------|
| `create_sandbox()` | Creates a new sandbox | `name: str`, `resources: dict (optional)` |
| `get_sandbox()` | Retrieves a sandbox | `id: str` |
| `list_sandboxes()` | Lists all sandboxes | None |
| `delete_sandbox()` | Deletes a sandbox | `id: str` |

### Sandbox

| Method | Description | Parameters |
|--------|-------------|------------|
| `setup()` | Sets up the environment | None |
| `run_experiment()` | Runs an experiment | `config: dict` |
| `cleanup()` | Cleans up resources | None |
| `export_results()` | Exports results | `path: str` |

## Configuration

The SDK can be configured using environment variables or a configuration file:

```bash
SANDBOX_API_KEY=your-api-key
SANDBOX_ENDPOINT=https://api.sandbox.example.com
```

Or using a `config.yaml`:

```yaml
api_key: your-api-key
endpoint: https://api.sandbox.example.com
default_resources:
  memory: 1GB
  cpu: 1
```

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for more information.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.