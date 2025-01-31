# Getting Started with Sandbox SDK

This tutorial will show you how to use the Sandbox SDK to create and manage sandboxed environments for executing actions.

## Prerequisites

Before getting started, ensure you have the following installed:

- Python 3.9 or higher
- Docker Desktop or Docker Engine
- Git
- uv package manager (recommended)
- At least 8GB RAM and 20GB free disk space
- Linux or macOS (Windows support via WSL2)

## Installation

### Environment Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/your-org/sandbox-sdk.git
   cd sandbox-sdk
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Linux/macOS
   # or
   .venv\Scripts\activate  # On Windows
   ```

```bash
pip install sandbox-sdk
```

## Basic Usage

Here's a simple example of how to use the SDK:

```python
from sandbox import SandboxGroup
from sandbox.models import DatabaseAccess, ComputeResources, DatabaseType, DatabaseAccessType, ResourceUnit
from pathlib import Path

# Configure database access
```

## Running the Sandbox

1. Start the sandbox services:
   ```bash
   sandbox-cli start
   ```

2. Verify the sandbox is running:
   ```bash
   sandbox-cli status
   ```

The sandbox should show all services (database, compute, etc.) as running.

db_access = DatabaseAccess(
    database_type=DatabaseType.VECTOR,
    access_type=DatabaseAccessType.READ_WRITE,
    namespaces=["default"]
)

# Configure compute resources
compute = ComputeResources(
    cpu_cores=2,
    ram_gb=4,
    disk_gb=10,
    memory_bandwidth_gbps=10,
    unit=ResourceUnit.ABSOLUTE
)

# Create sandbox group
group = SandboxGroup(
    database_access=db_access,
    compute_resources=compute,
    tools=[
        Path("my_tools/filesystem_tools.py"),
        Path("my_tools/terminal_tools.py")
    ],
    initial_database_population_config=Path("config/db_init.yml")
)

# Start the group (initializes databases)
await group.start_sandbox_group()

# Create a sandbox
sandbox = await group.create_sandbox("sandbox1")
await sandbox.start()

# Execute actions
observations = await sandbox.send_actions({
    "filesystem_tools.read_file": {
        "description": "Read content of test.txt",
        "args": {
            "path": "test.txt"
        }
    },
    "terminal_tools.execute_command": {
        "description": "List directory contents",
        "args": {
            "command": "ls -la"
        }
    }
})

# Process observations
for obs in observations:
    print(f"stdout: {obs.stdout}")
    print(f"stderr: {obs.stderr}")
    print(f"terminal running: {obs.terminal_still_running}")

# Cleanup
await sandbox.end()
await group.end_group()
```

## Available Tools

The SDK comes with several built-in tools:

### Filesystem Tools
- read_file
- create_file
- delete_file
- append_to_file
- overwrite_file
- edit_file_line_range
- move_file
- copy_file
- list_directory
- create_directory

### Terminal Tools
- change_directory
- execute_command
- uv_add_package
- uv_remove_package
- run_python_script
- get_current_directory
- install_system_package
- get_system_info
- monitor_process

### Web Tools
- scrape_website
- web_search
- extract_data_from_website

### Database Tools
- Vector Database (Qdrant)
  - create_collection
  - insert_points
  - search
- Graph Database (Neo4j)
  - execute_query
  - create_node
  - create_relationship

## Adding Custom Tools

You can add your own tools by creating Python files with functions and passing their paths to the SandboxGroup constructor. The functions should follow these guidelines:

1. Use type hints for parameters
2. Return strings for output or tuples of (stdout, stderr, terminal_running) for terminal commands
3. Use async functions if they perform I/O operations

Example custom tool:

```python
from typing import Tuple

def my_custom_tool(param1: str, param2: int) -> Tuple[str, str, bool]:
    try:
        result = do_something(param1, param2)
        return result, "", False
    except Exception as e:
        return "", str(e), False
## Security Considerations

- Sandboxes run in isolated Docker containers
- Database access is controlled per sandbox
- Resource limits are enforced
- Tools run with restricted permissions
- Network access is restricted by default
- Filesystem access is limited to sandbox workspace
- Memory isolation between sandboxes
- Regular security updates and patches
- Audit logging for all operations

## Error Handling

The SDK uses exceptions to indicate errors:

- SandboxError: Base exception class
- DatabaseError: Database-related errors
- ResourceError: Resource allocation errors
- ToolError: Tool execution errors

Always use try-except blocks to handle potential errors in your code.

## Working with Databases

The Sandbox SDK provides built-in support for both vector (Qdrant) and graph (Neo4j) databases. Here's how to work with them:

### Vector Database (Qdrant) Examples

```python
from sandbox import SandboxGroup
from sandbox.models import DatabaseAccess, DatabaseType, DatabaseAccessType
from qdrant_client.models import PointStruct

# Configure database access for vector database
db_access = DatabaseAccess(
    database_type=DatabaseType.VECTOR,
    access_type=DatabaseAccessType.READ_WRITE,
    namespaces=["my_vectors"]
)

# Create and start sandbox group
group = SandboxGroup(database_access=db_access)
await group.start_sandbox_group()

# Create sandbox
sandbox = await group.create_sandbox("vector_db_sandbox")
await sandbox.start()

# Create a collection
await sandbox.send_actions({
    "database_tools.create_collection": {
        "args": {
            "collection_name": "my_vectors",
            "vector_size": 384  # Size depends on your embeddings
        }
    }
})

# Insert vectors
points = [
    PointStruct(id=1, vector=[0.1, 0.2, ...], payload={"text": "example"})
]
await sandbox.send_actions({
    "database_tools.insert_points": {
        "args": {
            "collection_name": "my_vectors",
            "points": points
        }
    }
})
```

### Graph Database (Neo4j) Examples

```python
from sandbox import SandboxGroup
from sandbox.models import DatabaseAccess, DatabaseType, DatabaseAccessType

# Configure database access for graph database
db_access = DatabaseAccess(
    database_type=DatabaseType.GRAPH,
    access_type=DatabaseAccessType.READ_WRITE,
    namespaces=["default"]
)

# Create and start sandbox group
group = SandboxGroup(database_access=db_access)
await group.start_sandbox_group()

# Create sandbox
sandbox = await group.create_sandbox("graph_db_sandbox")
await sandbox.start()

# Create nodes
person = await sandbox.send_actions({
    "database_tools.create_node": {
        "args": {
            "label": "Person",
            "properties": {"name": "John", "age": 30}
        }
    }
})

# Execute custom query
results = await sandbox.send_actions({
    "database_tools.execute_query": {
        "args": {
            "query": "MATCH (p:Person) WHERE p.age > $age RETURN p",
            "parameters": {"age": 25}
        }
    }
})

## Resource Management

The Sandbox SDK provides features to monitor and manage resource usage effectively. Here's how to work with resource management:

### Checking Available Resources

Before creating new sandboxes, you can check the current resource availability:

```python
from sandbox import SandboxGroup

# Get current resource status
resources = await SandboxGroup.get_current_resources()

# Check specific resource availability
print(f"Available RAM: {resources.available_ram_gb} GB")
print(f"Available CPU cores: {resources.available_cpu_cores}")
print(f"Available disk space: {resources.available_disk_gb} GB")
print(f"Available network bandwidth: {resources.available_network_gbps} Gbps")
```

### Handling Resource Constraints

When creating sandboxes, handle potential resource constraints:

```python
from sandbox import SandboxGroup, ResourceError
from sandbox.models import ComputeResources

compute = ComputeResources(
    cpu_cores=2,
    ram_gb=4,
    disk_gb=10,
    memory_bandwidth_gbps=10
)

try:
    group = SandboxGroup(compute_resources=compute)
    await group.start_sandbox_group()
    sandbox = await group.create_sandbox("my_sandbox")
except ResourceError as e:
    print(f"Insufficient resources: {e}")
    # Handle the error (e.g., wait and retry, use fewer resources)
```

### Adjusting Resource Limits

You can dynamically adjust resource limits based on usage patterns:

```python
# Adjust resource limits to 1.3x the maximum usage from last 5 measurements
await sandbox.adjust_resource_limits()

# Or specify a custom multiplier
await sandbox.adjust_resource_limits(x_percentage=1.5)  # 1.5x the maximum usage
```

### Best Practices for Resource Management

1. **Monitor Resource Usage**:
   - Regularly check resource availability before creating new sandboxes
   - Set up monitoring for long-running sandboxes

2. **Resource Allocation Strategy**:
   - Start with conservative resource limits
   - Use `adjust_resource_limits()` to optimize resource allocation
   - Consider implementing retry mechanisms with exponential backoff

3. **Error Handling**:
   - Always handle `ResourceError` exceptions
   - Implement graceful degradation when resources are constrained
   - Consider resource cleanup in error scenarios

4. **Resource Cleanup**:
   - Always call `end()` on sandboxes when done
   - Use try-finally blocks to ensure proper cleanup
   - Monitor for leaked resources
```