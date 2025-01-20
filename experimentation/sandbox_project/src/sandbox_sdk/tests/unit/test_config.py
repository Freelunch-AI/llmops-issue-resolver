import pytest
import yaml
from pathlib import Path
from pydantic import ValidationError
from sandbox_sdk.sdk.sdk_orchestrator.config import SandboxConfigManager
from sandbox_sdk.helpers.models import ServiceManagementConfig, DatabaseConfig, SandboxConfig

@pytest.fixture
def sample_config_dict():
    return {
        "service_management": {
            "discovery_interval": 30,
            "health_check_timeout": 5,
            "retry_attempts": 3
        },
        "database": {
            "host": "localhost",
            "port": 5432,
            "username": "test_user",
            "password": "test_pass",
            "database": "test_db"
        },
        "environment": "testing",
        "resource_limits": {
            "max_memory": 1024,
            "max_cpu": 2
        },
        "security": {
            "enable_audit": True,
            "log_level": "INFO"
        }
    }

@pytest.fixture
def temp_config_file(tmp_path, sample_config_dict):
    config_file = tmp_path / "test_config.yaml"
    with open(config_file, "w") as f:
        yaml.dump(sample_config_dict, f)
    return config_file

def test_load_config_from_yaml(temp_config_file, sample_config_dict):
    config = SandboxConfigManager.from_yaml(temp_config_file)
    assert isinstance(config, SandboxConfig)
    assert config.environment == "testing"
    assert config.database.host == "localhost"
    assert config.database.port == 5432
    assert config.service_management.discovery_interval == 30

def test_load_config_from_dict(sample_config_dict):
    config = SandboxConfigManager.from_dict(sample_config_dict)
    assert isinstance(config, SandboxConfig)
    assert config.environment == "testing"
    assert config.database.host == "localhost"
    assert config.service_management.health_check_timeout == 5

def test_save_config_to_yaml(tmp_path, sample_config_dict):
    config = SandboxConfigManager.from_dict(sample_config_dict)
    output_file = tmp_path / "output_config.yaml"
    config.to_yaml(output_file)
    
    # Read back and verify
    with open(output_file) as f:
        loaded_data = yaml.safe_load(f)
    
    assert loaded_data["environment"] == "testing"
    assert loaded_data["database"]["host"] == "localhost"
    assert loaded_data["service_management"]["discovery_interval"] == 30

def test_file_not_found_error():
    with pytest.raises(FileNotFoundError):
        SandboxConfigManager.from_yaml("nonexistent_config.yaml")

def test_invalid_yaml_format(tmp_path):
    invalid_yaml = tmp_path / "invalid.yaml"
    with open(invalid_yaml, "w") as f:
        f.write("invalid: yaml: content: {")
    
    with pytest.raises(yaml.YAMLError):
        SandboxConfigManager.from_yaml(invalid_yaml)

def test_invalid_config_structure():
    invalid_config = {
        "service_management": {
            "invalid_field": "value"
        },
        "database": {
            "host": "localhost"
        }
    }
    
    with pytest.raises(ValidationError):
        SandboxConfigManager.from_dict(invalid_config)

def test_config_with_missing_optional_fields(tmp_path):
    minimal_config = {
        "service_management": {
            "discovery_interval": 30
        },
        "database": {
            "host": "localhost",
            "port": 5432,
            "username": "user",
            "password": "pass",
            "database": "db"
        },
        "environment": "testing"
    }
    
    config = SandboxConfigManager.from_dict(minimal_config)
    assert isinstance(config, SandboxConfig)
    assert config.environment == "testing"
    assert config.service_management.discovery_interval == 30

def test_path_object_handling(tmp_path, sample_config_dict):
    config_file = Path(tmp_path) / "config.yaml"
    with open(config_file, "w") as f:
        yaml.dump(sample_config_dict, f)
    
    config = SandboxConfigManager.from_yaml(config_file)
    assert isinstance(config, SandboxConfig)
    
    output_file = Path(tmp_path) / "output.yaml"
    config.to_yaml(output_file)
    assert output_file.exists()