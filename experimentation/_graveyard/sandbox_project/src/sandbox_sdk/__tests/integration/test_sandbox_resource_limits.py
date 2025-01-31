import pytest
import asyncio
import numpy as np
import psutil
import time
from sandbox_sdk.sandbox import Sandbox
from sandbox_sdk.helpers.models import ComputeResources, AttachedDatabases, ResourceUnit
from sandbox_sdk.helpers.exceptions import ActionExecutionError
from sandbox_sdk.helpers.exceptions import ResourceError
from sandbox_sdk.resource_manager import get_current_resources, adjust_resource_limits

@pytest.fixture
async def sandbox():
    """Create a sandbox instance with strict resource limits."""
    compute_resources = ComputeResources(
        cpu_cores=30,  # 30% CPU limit
        ram_gb=20,     # 20% RAM limit
        unit=ResourceUnit.RELATIVE
    )
    
    sandbox = Sandbox(
        id="resource-test",
        tools=[],
        compute_resources=compute_resources,
        attached_databases=AttachedDatabases(),
        orchestrator_url="http://localhost:8000"
    )
    
    async with sandbox.session() as sb:
        yield sb

def generate_cpu_intensive_code():
    """Generate Python code that performs CPU-intensive calculations."""
    return """
import numpy as np
import time

def intensive_calculation():
    size = 1000
    for _ in range(10):
        # Matrix operations
        matrix_a = np.random.rand(size, size)
        matrix_b = np.random.rand(size, size)
        result = np.dot(matrix_a, matrix_b)
        
        # Additional computations
        for i in range(size):
            for j in range(size):
                result[i][j] = np.sin(result[i][j])

intensive_calculation()
"""

def generate_memory_intensive_code():
    """Generate Python code that consumes significant memory."""
    return """
import numpy as np
import time

def consume_memory():
    # Create large arrays
    arrays = []
    for _ in range(20):
        # Each array is approximately 100MB
        arr = np.random.rand(3000, 3000)
        arrays.append(arr)
        time.sleep(0.1)  # Small delay to allow monitoring

consume_memory()
"""

@pytest.mark.asyncio
async def test_cpu_limit_violation(sandbox):
    """Test that CPU limit violations are detected and handled."""
    actions = {
        "cpu_intensive": {
            "command": "python -c '" + generate_cpu_intensive_code() + "'",
            "timeout_seconds": 30
        }
    }
    
    with pytest.raises(ActionExecutionError) as exc_info:
        await sandbox.send_actions(actions)
    
    assert "CPU usage exceeded limit" in str(exc_info.value)

@pytest.mark.asyncio
async def test_memory_limit_violation(sandbox):
    """Test that memory limit violations are detected and handled."""
    actions = {
        "memory_intensive": {
            "command": "python -c '" + generate_memory_intensive_code() + "'",
            "timeout_seconds": 30
        }
    }
    
    with pytest.raises(ActionExecutionError) as exc_info:
        await sandbox.send_actions(actions)
    
    assert "Memory usage exceeded limit" in str(exc_info.value)
@pytest.mark.asyncio
async def test_burst_resource_usage(sandbox):
    """Test system response to burst resource usage patterns."""
    burst_code = """
import numpy as np
import time
import threading

def cpu_burst():
    # CPU-intensive burst
    size = 2000
    for _ in range(3):
        matrix = np.random.rand(size, size)
        np.linalg.svd(matrix)
        time.sleep(0.5)

def memory_burst():
    # Memory-intensive burst
    arrays = []
    for _ in range(3):
        arr = np.random.rand(3000, 3000)
        arrays.append(arr)
        time.sleep(0.5)
        arrays.clear()

def combined_burst():
    threads = []
    for _ in range(2):
        t1 = threading.Thread(target=cpu_burst)
        t2 = threading.Thread(target=memory_burst)
        threads.extend([t1, t2])
        t1.start()
        t2.start()
    
    for t in threads:
        t.join()

combined_burst()
"""
    
    actions = {
        "burst_usage": {
            "command": "python -c '" + burst_code + "'",
            "timeout_seconds": 30
        }
    }
    
    # Execute burst usage test and verify resource monitoring
    with pytest.raises(ActionExecutionError) as exc_info:
        await sandbox.send_actions(actions)
    
    # Verify that the error is related to resource limits
    assert any(msg in str(exc_info.value) for msg in [
        "CPU usage exceeded limit",
        "Memory usage exceeded limit"
    ])

@pytest.mark.asyncio
async def test_resource_cleanup_after_violation(sandbox):
    """Test that resources are properly cleaned up after limit violations."""
    # First, trigger a resource violation
    actions = {
        "memory_intensive": {
            "command": "python -c '" + generate_memory_intensive_code() + "'",
            "timeout_seconds": 30
        }
    }
    
    with pytest.raises(ActionExecutionError):
        await sandbox.send_actions(actions)
    
    # Wait briefly for cleanup
    await asyncio.sleep(2)
    
    # Now run a simple action to verify sandbox is still operational
    simple_action = {
        "simple_task": {
            "command": "echo 'test'",
            "timeout_seconds": 5
        }
    }
    
    result = await sandbox.send_actions(simple_action)
    assert result[0].stdout.strip() == "test"

@pytest.mark.asyncio
async def test_concurrent_resource_limits(sandbox):
    """Test resource limits under concurrent execution."""
    concurrent_code = """
import numpy as np
import threading
import time

def worker():
    size = 500
    for _ in range(5):
        matrix = np.random.rand(size, size)
        result = np.linalg.svd(matrix)
        time.sleep(0.1)

threads = []
for _ in range(4):
    t = threading.Thread(target=worker)
    threads.append(t)
    t.start()

for t in threads:
    t.join()
"""
    
    actions = {
        "concurrent_usage": {
            "command": "python -c '" + concurrent_code + "'",
            "timeout_seconds": 30
        }
    }
    
    with pytest.raises(ActionExecutionError) as exc_info:
        await sandbox.send_actions(actions)
    assert any(msg in str(exc_info.value) for msg in 
              ["CPU usage exceeded limit", "Memory usage exceeded limit"])

@pytest.mark.asyncio
async def test_get_current_resources():
    """Test that get_current_resources returns accurate resource information."""
    # Get current resource status
    resources = await get_current_resources()
    
    # Verify the structure and data types of returned resources
    assert 'cpu_usage' in resources
    assert 'memory_usage' in resources
    assert 'disk_usage' in resources
    assert isinstance(resources['cpu_usage'], float)
    assert isinstance(resources['memory_usage'], float)
    assert isinstance(resources['disk_usage'], float)
    
    # Verify resource values are within reasonable ranges
    assert 0 <= resources['cpu_usage'] <= 100
    assert 0 <= resources['memory_usage'] <= 100
    assert 0 <= resources['disk_usage'] <= 100

@pytest.mark.asyncio
async def test_insufficient_resources_creation():
    """Test that sandbox creation fails when insufficient resources are available."""
    # Create compute resources that exceed system capacity
    excessive_resources = ComputeResources(
        cpu_cores=200,  # 200% CPU
        ram_gb=200,     # 200% RAM
        unit=ResourceUnit.RELATIVE
    )
    
    # Attempt to create sandbox with excessive resources
    with pytest.raises(ResourceError) as exc_info:
        sandbox = Sandbox(
            id="excessive-resource-test",
            tools=[],
            compute_resources=excessive_resources,
            attached_databases=AttachedDatabases(),
            orchestrator_url="http://localhost:8000"
        )
        async with sandbox.session():
            pass
    
    assert "Insufficient resources available" in str(exc_info.value)

@pytest.mark.asyncio
async def test_adjust_resource_limits_default(sandbox):
    """Test that adjust_resource_limits works correctly with default x_percentage."""
    # Generate some resource usage
    simple_action = {
        "simple_task": {
            "command": "python -c 'import numpy as np; a = np.random.rand(1000, 1000); np.dot(a, a)'",
            "timeout_seconds": 5
        }
    }
    await sandbox.send_actions(simple_action)
    
    # Adjust resource limits using default x_percentage (1.3)
    adjusted_limits = await adjust_resource_limits(sandbox.id)
    
    # Verify the adjustments
    assert adjusted_limits is not None
    assert all(isinstance(limit, float) for limit in adjusted_limits.values())
    
    # Verify the sandbox continues to work with new limits
    result = await sandbox.send_actions(simple_action)
    assert result[0].exit_code == 0

@pytest.mark.asyncio
async def test_adjust_resource_limits_custom(sandbox):
    """Test that adjust_resource_limits works correctly with custom x_percentage."""
    # Generate some resource usage
    simple_action = {
        "simple_task": {
            "command": "python -c 'import numpy as np; a = np.random.rand(1000, 1000); np.dot(a, a)'",
            "timeout_seconds": 5
        }
    }
    await sandbox.send_actions(simple_action)
    
    # Adjust resource limits with custom x_percentage
    custom_percentage = 1.5
    adjusted_limits = await adjust_resource_limits(sandbox.id, x_percentage=custom_percentage)
    
    # Verify the adjustments
    assert adjusted_limits is not None
    assert all(isinstance(limit, float) for limit in adjusted_limits.values())
    
    # Verify the sandbox continues to work with new limits
    result = await sandbox.send_actions(simple_action)
    assert result[0].exit_code == 0

@pytest.mark.asyncio
async def test_container_startup_failure():
    """Test handling of container startup failures."""
    # Create sandbox with invalid orchestrator URL to simulate startup failure
    sandbox = Sandbox(
        id="startup-failure-test",
        tools=[],
        compute_resources=ComputeResources(
            cpu_cores=30,
            ram_gb=20,
            unit=ResourceUnit.RELATIVE
        ),
        attached_databases=AttachedDatabases(),
        orchestrator_url="http://invalid-url:8000"
    )
    
    with pytest.raises(SandboxStartError) as exc_info:
        async with sandbox.session():
            pass
    
    assert "Failed to start sandbox container" in str(exc_info.value)

@pytest.mark.asyncio
async def test_resource_allocation_race_condition(sandbox):
    """Test handling of race conditions during resource allocation."""
    # Create multiple concurrent resource-intensive tasks
    actions = {}
    for i in range(5):
        actions[f"concurrent_task_{i}"] = {
            "command": f"python -c '
import numpy as np
import time
matrix = np.random.rand(1000, 1000)
time.sleep({i*0.1})
result = np.dot(matrix, matrix)'",
            "timeout_seconds": 10
        }
    
    # Execute actions concurrently to test race condition handling
    tasks = [sandbox.send_actions({k: v}) for k, v in actions.items()]
    with pytest.raises(ActionExecutionError) as exc_info:
        await asyncio.gather(*tasks)
    
    assert any(msg in str(exc_info.value) for msg in [
        "Resource allocation conflict",
        "Resource limit exceeded",
        "Concurrent resource access violation"
    ])

@pytest.mark.asyncio
async def test_cleanup_after_startup_failure():
    """Test proper cleanup of resources after container startup failure."""
    # Create sandbox with configuration that will cause startup failure
    failed_sandbox = Sandbox(
        id="cleanup-test",
        tools=[],
        compute_resources=ComputeResources(
            cpu_cores=30,
            ram_gb=20,
            unit=ResourceUnit.RELATIVE
        ),
        attached_databases=AttachedDatabases(),
        orchestrator_url="http://invalid-url:8000"
    )
    
    try:
        async with failed_sandbox.session():
            pass
    except SandboxStartError:
        pass
    
    # Verify system resources are properly released
    resources = await get_current_resources()
    assert resources['cpu_usage'] < 90  # System CPU should not be saturated
    assert resources['memory_usage'] < 90  # System memory should not be exhausted
    
    # Verify we can start a new sandbox after failure
    new_sandbox = Sandbox(
        id="post-failure-test",
        tools=[],
        compute_resources=ComputeResources(
            cpu_cores=30,
            ram_gb=20,
            unit=ResourceUnit.RELATIVE
        ),
        attached_databases=AttachedDatabases(),
        orchestrator_url="http://localhost:8000"
    )
    
    async with new_sandbox.session() as sb:
        result = await sb.send_actions({"echo": {"command": "echo 'test'", "timeout_seconds": 5}})
        assert result[0].exit_code == 0