# Sandbox SDK

A Python library for creating and managing sandboxed environments for executing actions.

## Features

- Create isolated sandbox environments using Docker containers
- Execute filesystem, terminal, web, and database operations safely
- Control resource usage (CPU, RAM, disk, memory bandwidth)
- Manage database access permissions
- Add custom tools dynamically
- Async/await support
- Type hints and validation using Pydantic
- Secure authentication and authorization mechanisms
- Automatic resource scaling and optimization
- Connection pooling for efficient database access
- Real-time resource monitoring and alerts
- Atomic operations for database transactions

## Components

1. SDK (`/src/sandbox_sdk`)
   - Main interface for creating and managing sandboxes
   - Type definitions and models
   - Async client for communicating with sandbox API
   - Authentication and authorization handlers
   - Resource usage tracking and optimization

2. Sandbox (`/sandbox`)
   - Docker container that executes actions
   - Built-in tools for common operations
   - FastAPI server for receiving action requests
   - Resource usage monitoring
   - Real-time metrics collection
   - Automatic resource scaling

3. Sandbox Orchestrator (`/sandbox_orchestrator`)
   - Manages sandbox lifecycle
   - Handles database initialization
   - Controls resource allocation
   - FastAPI server for orchestration
   - Connection pooling and transaction management
   - Resource optimization and load balancing

## Installation

Using `uv`:
```bash
uv pip install sandbox-sdk
```

Using `pip`:
```bash
pip install sandbox-sdk
```

For development:
```bash
git clone https://github.com/yourusername/sandbox-sdk.git
cd sandbox-sdk
uv venv venv
. venv/bin/activate
uv pip install -e ".[dev,test]"
```

## Quick Start

```python
from sandbox import SandboxGroup
from sandbox.models import DatabaseAccess, ComputeResources
from pathlib import Path

# Create sandbox group
group = SandboxGroup(
    database_access=DatabaseAccess(...),
    compute_resources=ComputeResources(...),
    tools=[Path("my_tools.py")],
    initial_database_population_config=Path("db_config.yml"),
    auth_config={
        "auth_type": "jwt",
        "token_expiry": 3600
    },
    resource_limits={
        "max_connections": 100,
        "connection_timeout": 30
    }
)

# Start group and create sandbox
await group.start_sandbox_group()
sandbox = await group.create_sandbox("sandbox1")
await sandbox.start()

# Execute actions
observations = await sandbox.send_actions({
    "my_tools.my_function": {
        "description": "Do something",
        "args": {"param1": "value1"}
    }
})

# Cleanup
await sandbox.end()
await group.end_group()
## Documentation

See the [tutorial](docs/tutorial/getting_started.md) for detailed usage instructions.

## Security

The sandbox environment implements several security measures:

- JWT-based authentication for API access
- Role-based access control for resources
- Encrypted database connections
- Resource isolation between sandboxes
- Automatic session management

## Configuration

### Resource Management
```yaml
resource_limits:
  cpu_limit: 2.0
  memory_limit: "2G"
  max_connections: 100
  connection_timeout: 30
```

### Database Connection
```yaml
database_config:
  pool_size: 20
  max_overflow: 10
  pool_timeout: 30
  pool_recycle: 1800
```

## Development

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Start required Docker containers:
   ```bash
   # Start all required services including Qdrant and Neo4j
   docker-compose up -d
   
   # Verify containers are running
   docker-compose ps
   ```
   
   > **Important**: Ensure that Qdrant and Neo4j containers are running before executing tests.
   > These services are required for the test suite to function properly.
   
   The following services must be running:
   - Qdrant (Vector Database) - Ports 6333, 6334
   - Neo4j (Graph Database) - Ports 7474, 7687

4. Run tests: `pytest tests/`

## License

MIT License
## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request