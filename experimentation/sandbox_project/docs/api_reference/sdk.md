# Sandbox SDK API Reference

## Core Classes

### SandboxGroup

The main class for managing groups of sandboxes and their shared resources.

```python
class SandboxGroup:
    def __init__(
        self,
        database_access: DatabaseAccess,
        compute_resources: ComputeResources,
        tools: List[Path],
        initial_database_population_config: Path,
        orchestrator_url: str = "http://localhost:8000"
    )
```

#### Parameters:
- `database_access`: Database access configuration
- `compute_resources`: Default compute resources for sandboxes
- `tools`: List of paths to tool Python files
- `initial_database_population_config`: Path to YAML file with initial database data
- `orchestrator_url`: URL of the sandbox orchestrator service

#### Methods:

##### `async start_sandbox_group()`
Start the sandbox group and initialize databases.

##### `async create_sandbox()`
```python
async def create_sandbox(
    self,
    id: str,
    tools: Optional[List[Path]] = None,
    compute_resources: Optional[ComputeResources] = None,
    attached_databases: Optional[AttachedDatabases] = None
) -> Sandbox
```

##### `create_sandbox_sync()`
Synchronous version of `create_sandbox()`.

##### `async end_group()`
Stop all sandboxes and cleanup resources.

### Sandbox

Individual sandbox instance for executing actions.

```python
class Sandbox:
    def __init__(
        self,
        id: str,
        tools: List[Path],
        compute_resources: ComputeResources,
        attached_databases: AttachedDatabases,
        orchestrator_url: str,
        sandbox_url: Optional[str] = None
    )
```

#### Methods:

##### `async start()`
Start the sandbox container.

##### `async send_actions(actions: Dict) -> List[ActionObservation]`
Send actions to be executed in the sandbox.

##### `send_actions_sync(actions: Dict) -> List[ActionObservation]`
Synchronous version of `send_actions()`.

##### `async end()`
Stop and remove the sandbox container.
##### `async session() -> AsyncContextManager[Sandbox]`
Context manager for sandbox lifecycle.

##### `async get_current_resources() -> Dict[str, float]`
Get the current available resources for the sandbox environment.

Returns a dictionary containing the available resources with keys:
- `cpu_cores`: Available CPU cores
- `ram_gb`: Available RAM in gigabytes
- `disk_gb`: Available disk space in gigabytes
- `memory_bandwidth_gbps`: Available memory bandwidth in GB/s

##### `async adjust_resource_limits(x_percentage: float = 1.3) -> None`
Adjust the sandbox resource limits based on historical usage patterns. The function analyzes the last five resource usage measurements and sets new limits by multiplying the maximum observed usage by the specified percentage.

Parameters:
- `x_percentage`: Multiplier for resource adjustment (default: 1.3). For example, if maximum RAM usage was 2GB and x_percentage is 1.3, the new RAM limit will be set to 2.6GB.

## Data Models

### ComputeResources

```python
class ComputeResources(BaseModel):
    cpu_cores: Union[int, float] = 1
    ram_gb: Union[int, float] = 2.0
    disk_gb: Union[int, float] = 10.0
    memory_bandwidth_gbps: Union[int, float] = 5.0
    unit: ResourceUnit = ResourceUnit.ABSOLUTE
```

### DatabaseAccess

```python
class DatabaseAccess(BaseModel):
    database_type: DatabaseType
    access_type: DatabaseAccessType
    namespaces: List[str] = []
```

### AttachedDatabases

```python
class AttachedDatabases(BaseModel):
    vector_db: Optional[DatabaseAccess] = default_vector_db
    graph_db: Optional[DatabaseAccess] = default_graph_db
```

### ActionObservation

```python
class ActionObservation(BaseModel):
    stdout: str = ""
    stderr: str = ""
    terminal_still_running: bool = False
```

## Enums

### DatabaseType
- `VECTOR`
- `GRAPH`

### DatabaseAccessType
- `READ`
- `WRITE`
- `READ_WRITE`

### ResourceUnit
- `ABSOLUTE`
- `RELATIVE`

## Exceptions

- `SandboxError`: Base exception for all sandbox-related errors
- `SandboxNotStartedError`: Raised when trying to use a sandbox that hasn't been started
- `SandboxStartError`: Raised when there's an error starting a sandbox
- `SandboxStopError`: Raised when there's an error stopping a sandbox
- `ActionExecutionError`: Raised when there's an error executing an action
- `ResourceError`: Raised when there's an error with resource allocation
- `DatabaseError`: Raised when there's an error with database operations
- `ConfigurationError`: Raised when there's an error in the configuration
- `ToolError`: Raised when there's an error with sandbox tools