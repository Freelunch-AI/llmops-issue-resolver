import pytest
from pathlib import Path
from ...models import (
    ResourceConfig,
    SecurityConfig,
    SandboxConfig
)

@pytest.fixture
def resource_config():
    return {
        "cpu_cores": 2,
        "ram_gb": 4.0,
        "disk_gb": 10.0,
        "memory_bandwidth_gbps": 5.0,
        "unit": "absolute"
    }

@pytest.fixture
def security_config():
    return {
        "network_isolation": True,
        "max_processes": 50,
        "read_only_root": True,
        "drop_capabilities": ["NET_ADMIN", "SYS_ADMIN"]
    }

def test_resource_config(resource_config):
    config = ResourceConfig(**resource_config)
    assert config.cpu_cores == 2
    assert config.ram_gb == 4.0
    assert config.unit == "absolute"

def test_invalid_resource_config(resource_config):
    # Test negative value
    resource_config["cpu_cores"] = -1
    with pytest.raises(ValueError):
        ResourceConfig(**resource_config)
    
    # Test invalid unit
    resource_config["cpu_cores"] = 1
    resource_config["unit"] = "invalid"
    with pytest.raises(ValueError):
        ResourceConfig(**resource_config)

def test_security_config(security_config):
    config = SecurityConfig(**security_config)
    assert config.network_isolation is True
    assert config.max_processes == 50
    assert len(config.drop_capabilities) == 2

def test_security_config_defaults():
    config = SecurityConfig()
    assert config.network_isolation is True
    assert config.max_processes is None
    assert config.read_only_root is True
    assert len(config.drop_capabilities) == 3

def test_sandbox_config(resource_config, security_config):
    config = SandboxConfig(
        id="test-sandbox",
        resources=ResourceConfig(**resource_config),
        security=SecurityConfig(**security_config),
        tools=["tool1", "tool2"],
        working_directory=Path("/workspace")
    )
    
    assert config.id == "test-sandbox"
    assert isinstance(config.resources, ResourceConfig)
    assert isinstance(config.security, SecurityConfig)
    assert len(config.tools) == 2
    assert config.working_directory == Path("/workspace")