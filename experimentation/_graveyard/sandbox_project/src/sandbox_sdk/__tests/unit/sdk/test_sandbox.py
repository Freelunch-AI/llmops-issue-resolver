import pytest
from unittest.mock import Mock, patch
from sandbox_sdk.sdk.sdk_sandbox.client import Sandbox
from sandbox_sdk.helpers.exceptions import SandboxError, ConfigurationError, ExecutionError
from sandbox_sdk.helpers.models import SandboxConfig
from pydantic import ValidationError

@pytest.fixture
def basic_config():
    return {
        "allowed_operations": ["analyze", "transform", "validate", "export"],
        "max_size": 1024,
        "timeout": 30
    }

@pytest.fixture
def sandbox(basic_config):
    return Sandbox(config=basic_config)

def test_sandbox_initialization():
    # Test default initialization
    sandbox = Sandbox()
    assert isinstance(sandbox.config, SandboxConfig)
    assert sandbox.custom_handlers == {}
    assert sandbox._resources == {}

    # Test initialization with config
    config = {"max_size": 2048}
    sandbox = Sandbox(config=config)
    assert sandbox.config.max_size == 2048

    # Test initialization with custom handlers
    custom_handler = Mock()
    handlers = {"custom_op": custom_handler}
    sandbox = Sandbox(custom_handlers=handlers)
    assert "custom_op" in sandbox.custom_handlers

def test_execute_operation(sandbox):
    data = {"test": "data"}
    result = sandbox.execute("analyze", data)
    assert result["status"] == "analyzed"
    assert "metadata" in result
    assert "results" in result

def test_analyze_data(sandbox):
    test_data = {"key": "value", "nested": {"inner": "data"}}
    result = sandbox._analyze_data(test_data)
    
    assert result["status"] == "analyzed"
    assert result["metadata"]["type"] == str(type(test_data))
    assert "size" in result["metadata"]
    assert result["metadata"]["structure"]["type"] == "dict"
    assert "key" in result["metadata"]["structure"]["keys"]

def test_transform_data(sandbox):
    test_data = {"input": "data"}
    result = sandbox._transform_data(test_data)
    
    assert result["status"] == "transformed"
    assert "results" in result

def test_validate_data(sandbox):
    valid_data = {"test": "data"}
    result = sandbox._validate_data(valid_data)
    
    assert result["is_valid"] is True
    assert result["errors"] == []

@patch('sandbox_sdk.models.SandboxConfig.validate_schema')
def test_validate_data_with_errors(mock_validate, sandbox):
    mock_validate.side_effect = ValidationError(errors=[], model=None)
    invalid_data = {"invalid": "data"}
    result = sandbox._validate_data(invalid_data)
    
    assert result["is_valid"] is False
    assert isinstance(result["errors"], list)

def test_export_data(sandbox):
    test_data = {
        "content": {"data": "test"},
        "format": "json",
        "destination": "memory"
    }
    result = sandbox._export_data(test_data)
    
    assert result["status"] == "exported"
    assert result["location"] == "memory"
    assert "exported_data" in sandbox._resources

def test_custom_handler_execution(basic_config):
    custom_handler = Mock(return_value={"status": "success"})
    handlers = {"custom_op": custom_handler}
    sandbox = Sandbox(config=basic_config, custom_handlers=handlers)
    
    result = sandbox._process_operation("custom_op", {"test": "data"})
    assert result["status"] == "success"
    custom_handler.assert_called_once()

def test_invalid_operation(sandbox):
    with pytest.raises(ExecutionError):
        sandbox.execute("invalid_operation", {})

def test_cleanup(sandbox):
    # Add some mock resources
    mock_resource = Mock()
    mock_resource.close = Mock()
    sandbox._resources["test_resource"] = mock_resource
    
    sandbox.cleanup()
    
    assert sandbox._resources == {}
    mock_resource.close.assert_called_once()

@patch('sandbox_sdk.models.SandboxConfig.validate_environment')
def test_environment_validation_failure(mock_validate):
    mock_validate.return_value = False
    with pytest.raises(ConfigurationError):
        Sandbox()

def test_analyze_structure(sandbox):
    # Test dict structure
    dict_data = {"key1": "value1", "key2": "value2"}
    result = sandbox._analyze_structure(dict_data)
    assert result["type"] == "dict"
    assert "key1" in result["keys"]
    assert "key2" in result["keys"]
    
    # Test list structure
    list_data = [1, 2, 3]
    result = sandbox._analyze_structure(list_data)
    assert result["type"] == "list"
    assert result["length"] == 3
    
    # Test primitive type
    string_data = "test"
    result = sandbox._analyze_structure(string_data)
    assert result["type"] == str(type(string_data))

def test_cleanup_error_handling():
    sandbox = Sandbox()
    mock_resource = Mock()
    mock_resource.close = Mock(side_effect=Exception("Cleanup error"))
    sandbox._resources["test_resource"] = mock_resource
    
    with pytest.raises(SandboxError):
        sandbox.cleanup()