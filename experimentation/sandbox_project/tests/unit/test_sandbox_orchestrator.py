import pytest
import asyncio
from pathlib import Path
from sandbox_orchestrator.core.sandbox_manager import SandboxManager
from sandbox_orchestrator.core.models.database import DatabasesConfig
from sandbox_orchestrator.core.models.sandbox import SandboxConfig, ResourceConfig

@pytest.fixture
async def sandbox_manager():
    manager = SandboxManager(
        gateway_url="http://localhost:8000",
        inactivity_threshold=5,  # 5 seconds for testing
        cleanup_interval=1
    )
    yield manager
    await manager.cleanup()

@pytest.fixture
def db_configs(tmp_path):
    # Vector DB config
    vector_config = tmp_path / "vector_db.yml"
    vector_config.write_text("""
host: localhost
port: 6333
credentials:
  user: test
  password: test
initial_data_file: databases/data/vector_db_initial_data.json
""")
    
    # Graph DB config
    graph_config = tmp_path / "graph_db.yml"
    graph_config.write_text("""
host: localhost
port: 7687
credentials:
  user: neo4j
  password: test
initial_data_file: databases/data/graph_db_initial_data.json
""")
    
    return DatabasesConfig.from_yaml(vector_config, graph_config)

@pytest.mark.asyncio
async def test_database_lifecycle(sandbox_manager, db_configs):
    # Start databases
    await sandbox_manager.start_databases(db_configs)
    
    # Verify databases are running
    assert "vector" in sandbox_manager.databases
    assert "graph" in sandbox_manager.databases
    assert sandbox_manager.databases["vector"].status == "running"
    assert sandbox_manager.databases["graph"].status == "running"
    
    # Stop databases
    await sandbox_manager.stop_databases()
    
    # Verify databases are stopped
    assert not sandbox_manager.databases

@pytest.mark.asyncio
async def test_sandbox_lifecycle(sandbox_manager):
    # Create sandbox
    tools = [
        "# Module: test_module\ndef test_func():\n    return 'test'"
    ]
    
    compute_resources = {
        "cpu_cores": 1,
        "ram_gb": 2,
        "disk_gb": 5,
        "memory_bandwidth_gbps": 5
    }
    
    environment = {
        "TEST_VAR": "test_value"
    }
    
    sandbox_url = await sandbox_manager.create_sandbox(
        "test_sandbox",
        tools,
        compute_resources,
        environment
    )
    
    # Verify sandbox is running
    assert "test_sandbox" in sandbox_manager.sandboxes
    assert sandbox_manager.sandboxes["test_sandbox"].status == "running"
    assert sandbox_url.startswith("http://localhost:")
    
    # Stop sandbox
    await sandbox_manager.stop_sandbox("test_sandbox")
    
    # Verify sandbox is stopped
    assert "test_sandbox" not in sandbox_manager.sandboxes

@pytest.mark.asyncio
async def test_sandbox_inactivity_cleanup(sandbox_manager):
    # Create sandbox
    tools = ["# Module: test\ndef test(): pass"]
    compute_resources = {"cpu_cores": 1, "ram_gb": 1}
    
    await sandbox_manager.create_sandbox(
        "test_sandbox",
        tools,
        compute_resources,
        {}
    )
    
    # Wait for inactivity cleanup
    await asyncio.sleep(7)  # > 5 seconds inactivity threshold
    
    # Verify sandbox was cleaned up
    assert "test_sandbox" not in sandbox_manager.sandboxes

@pytest.mark.asyncio
async def test_sandbox_activity_tracking(sandbox_manager):
    # Create sandbox
    tools = ["# Module: test\ndef test(): pass"]
    compute_resources = {"cpu_cores": 1, "ram_gb": 1}
    
    await sandbox_manager.create_sandbox(
        "test_sandbox",
        tools,
        compute_resources,
        {}
    )
    
    # Record activity every 2 seconds
    for _ in range(3):
        sandbox_manager.cleaner.record_activity("test_sandbox")
        await asyncio.sleep(2)
    
    # Verify sandbox is still running after 6 seconds
    assert "test_sandbox" in sandbox_manager.sandboxes
    
    # Wait for inactivity
    await asyncio.sleep(6)
    
    # Verify sandbox was cleaned up
    assert "test_sandbox" not in sandbox_manager.sandboxes

@pytest.mark.asyncio
async def test_error_handling(sandbox_manager):
    # Test invalid compute resources
    with pytest.raises(Exception):
        await sandbox_manager.create_sandbox(
            "test_sandbox",
            [],
            {"cpu_cores": -1},  # Invalid CPU cores
            {}
        )
    
    # Test invalid tool format
    with pytest.raises(ValueError):
        await sandbox_manager.create_sandbox(
            "test_sandbox",
            ["invalid tool format"],  # Missing module comment
            {"cpu_cores": 1, "ram_gb": 1},
            {}
        )
    
    # Test stopping non-existent sandbox
    with pytest.raises(Exception):
        await sandbox_manager.stop_sandbox("nonexistent")