import pytest
import asyncio
import time
from pathlib import Path
from sandbox_sdk import (
    SandboxGroup,
    DatabaseAccess,
    ComputeResources,
    DatabaseType,
    DatabaseAccessType,
    ResourceUnit
)
from sandbox_sdk.exceptions import ActionExecutionError
@pytest.fixture
def test_tools():
    def echo_message(message: str) -> str:
        """Echo the input message."""
        return f"Echo: {message}"
    
    def add_numbers(a: float, b: float) -> float:
        """Add two numbers."""
        return a + b
    
    async def async_operation(delay: float) -> str:
        """Async operation with delay."""
        await asyncio.sleep(delay)
        return f"Completed after {delay}s"
    
    def cpu_intensive_operation(iterations: int) -> str:
        """CPU intensive operation."""
        result = 0
        for i in range(iterations):
            result += sum(i * j for j in range(1000))
        return f"Completed {iterations} iterations"
    
    def memory_intensive_operation(size_mb: int) -> str:
        """Memory intensive operation."""
        # Allocate memory in chunks
        chunk_size = 1024 * 1024  # 1MB
        data = [bytearray(chunk_size) for _ in range(size_mb)]
        return f"Allocated {size_mb}MB memory"
    
    def disk_intensive_operation(size_mb: int, path: Path) -> str:
        """Disk intensive operation."""
        file_path = path / f"test_file_{size_mb}mb"
        with open(file_path, 'wb') as f:
            f.write(b'0' * (size_mb * 1024 * 1024))
        return f"Written {size_mb}MB to disk"
    
    return [
        echo_message,
        add_numbers,
        async_operation,
        cpu_intensive_operation,
        memory_intensive_operation,
        disk_intensive_operation
    ]

@pytest.fixture
def db_access():
    return DatabaseAccess(
        database_type=DatabaseType.VECTOR,
        access_type=DatabaseAccessType.READ_WRITE,
        namespaces=["default"]
    )

@pytest.fixture
def compute_resources():
    return ComputeResources(
        cpu_cores=1,
        ram_gb=2,
        disk_gb=5,
        memory_bandwidth_gbps=5,
        unit=ResourceUnit.ABSOLUTE
    )

@pytest.fixture
def db_config(tmp_path):
    config = tmp_path / "db_config.yml"
    config.write_text("""
vector_db:
  collections:
    - name: test
      vector_size: 128
      initial_data: []
graph_db:
  nodes: []
  relationships: []
""")
    return config

@pytest.mark.asyncio
async def test_sandbox_lifecycle(db_access, compute_resources, test_tools, db_config, mock_gateway):
    group = SandboxGroup(
        database_access=db_access,
        compute_resources=compute_resources,
        tools=test_tools,
        initial_database_population_config=db_config
    )
    
    # Start group
    await group.start_sandbox_group()
    
    # Create sandbox
    sandbox = await group.create_sandbox("test_sandbox")
    await sandbox.start()
    
    # Execute sync actions
    observations = await sandbox.send_actions({
        "test_sandbox.echo_message": {
            "description": "Test echo function",
            "args": {
                "message": "Hello, World!"
            }
        },
        "test_sandbox.add_numbers": {
            "description": "Test addition",
            "args": {
                "a": 2.5,
                "b": 3.5
            }
        }
    })
    
    assert len(observations) == 2
    assert observations[0].stdout == "Echo: Hello, World!"
    assert observations[1].stdout == "6.0"
    
    # Execute async action
    observations = await sandbox.send_actions({
        "test_sandbox.async_operation": {
            "description": "Test async operation",
            "args": {
                "delay": 0.1
            }
        }
    })
    
    assert len(observations) == 1
    assert "Completed after 0.1s" in observations[0].stdout
    
    # Cleanup
    await sandbox.end()
    await group.end_group()

@pytest.mark.asyncio
async def test_sandbox_parallel_execution(db_access, compute_resources, test_tools, db_config, mock_gateway):
    group = SandboxGroup(
        database_access=db_access,
        compute_resources=compute_resources,
        tools=test_tools,
        initial_database_population_config=db_config
    )
    
    await group.start_sandbox_group()
    sandbox = await group.create_sandbox("test_sandbox")
    await sandbox.start()
    
    # Execute multiple async operations in parallel
    start_time = time.time()
    observations = await sandbox.send_actions({
        "test_sandbox.async_operation": {
            "args": {"delay": 0.5}
        },
        "test_sandbox.async_operation": {
            "args": {"delay": 0.5}
        }
    })
    
    execution_time = time.time() - start_time
    assert execution_time < 0.8  # Should take ~0.5s, not ~1s
    assert len(observations) == 2
    
    await sandbox.end()
    await group.end_group()

@pytest.mark.asyncio
async def test_sandbox_resource_limits(db_access, compute_resources, test_tools, db_config, mock_gateway):
    # Set very low resource limits
    compute_resources.ram_gb = 0.1
    
    group = SandboxGroup(
        database_access=db_access,
        compute_resources=compute_resources,
        tools=test_tools,
        initial_database_population_config=db_config
    )
    
    await group.start_sandbox_group()
    
    # Creating sandbox should fail due to insufficient resources
    with pytest.raises(Exception):
        sandbox = await group.create_sandbox("test_sandbox")
        await sandbox.start()
    await group.end_group()

@pytest.mark.asyncio
async def test_sandbox_cpu_exhaustion(db_access, compute_resources, test_tools, db_config, mock_gateway, tmp_path):
    # Set low CPU limit
    compute_resources.cpu_cores = 0.5
    
    group = SandboxGroup(
        database_access=db_access,
        compute_resources=compute_resources,
        tools=test_tools,
        initial_database_population_config=db_config
    )
    
    await group.start_sandbox_group()
    sandbox = await group.create_sandbox("test_sandbox")
    await sandbox.start()
    
    # Execute CPU intensive operation
    with pytest.raises(ActionExecutionError, match="CPU usage exceeded limit"):
        await sandbox.send_actions({
            "test_sandbox.cpu_intensive_operation": {
                "args": {"iterations": 1000000}
            }
        })
    
    await sandbox.end()
    await group.end_group()

@pytest.mark.asyncio
async def test_sandbox_memory_exhaustion(db_access, compute_resources, test_tools, db_config, mock_gateway, tmp_path):
    # Set low memory limit
    compute_resources.ram_gb = 0.1
    
    group = SandboxGroup(
        database_access=db_access,
        compute_resources=compute_resources,
        tools=test_tools,
        initial_database_population_config=db_config
    )
    
    await group.start_sandbox_group()
    sandbox = await group.create_sandbox("test_sandbox")
    await sandbox.start()
    
    # Execute memory intensive operation
    with pytest.raises(ActionExecutionError, match="Memory usage exceeded limit"):
        await sandbox.send_actions({
            "test_sandbox.memory_intensive_operation": {
                "args": {"size_mb": 200}
            }
        })
    
    await sandbox.end()
    await group.end_group()

@pytest.mark.asyncio
async def test_sandbox_disk_exhaustion(db_access, compute_resources, test_tools, db_config, mock_gateway, tmp_path):
    # Set low disk limit
    compute_resources.disk_gb = 0.1
    
    group = SandboxGroup(
        database_access=db_access,
        compute_resources=compute_resources,
        tools=test_tools,
        initial_database_population_config=db_config
    )
    
    await group.start_sandbox_group()
    sandbox = await group.create_sandbox("test_sandbox")
    await sandbox.start()
    
    # Execute disk intensive operation
    with pytest.raises(ActionExecutionError, match="Disk usage too high"):
        await sandbox.send_actions({
            "test_sandbox.disk_intensive_operation": {
                "args": {
                    "size_mb": 200,
                    "path": str(tmp_path)
                }
            }
        })
    
    await sandbox.end()
    await group.end_group()

@pytest.mark.asyncio
async def test_sandbox_concurrent_resource_contention(db_access, compute_resources, test_tools, db_config, mock_gateway, tmp_path):
    # Set moderate resource limits
    compute_resources.cpu_cores = 1
    compute_resources.ram_gb = 0.5
    
    group = SandboxGroup(
        database_access=db_access,
        compute_resources=compute_resources,
        tools=test_tools,
        initial_database_population_config=db_config
    )
    
    await group.start_sandbox_group()
    sandbox = await group.create_sandbox("test_sandbox")
    await sandbox.start()
    
    # Execute multiple resource-intensive operations concurrently
    with pytest.raises(ActionExecutionError):
        await asyncio.gather(
            sandbox.send_actions({
                "test_sandbox.cpu_intensive_operation": {
                    "args": {"iterations": 500000}
                }
            }),
            sandbox.send_actions({
                "test_sandbox.memory_intensive_operation": {
                    "args": {"size_mb": 100}
                }
            }),
            sandbox.send_actions({
                "test_sandbox.disk_intensive_operation": {
                    "args": {
                        "size_mb": 100,
                        "path": str(tmp_path)
                    }
                }
            })
        )
    
    await sandbox.end()
    await group.end_group()

@pytest.mark.asyncio
async def test_sandbox_error_handling(db_access, compute_resources, test_tools, db_config, mock_gateway):
    group = SandboxGroup(
        database_access=db_access,
        compute_resources=compute_resources,
        tools=test_tools,
        initial_database_population_config=db_config
    )
    
    await group.start_sandbox_group()
    sandbox = await group.create_sandbox("test_sandbox")
    await sandbox.start()
    
    # Test invalid function
    observations = await sandbox.send_actions({
        "test_sandbox.nonexistent_function": {
            "args": {}
        }
    })
    
    assert len(observations) == 1
    assert observations[0].stderr != ""
    assert observations[0].stdout == ""
    
    # Test invalid arguments
    observations = await sandbox.send_actions({
        "test_sandbox.add_numbers": {
            "args": {
                "a": "not a number",
                "b": 1
            }
        }
    })
    
    assert len(observations) == 1
    assert observations[0].stderr != ""
    
    await sandbox.end()
    await group.end_group()