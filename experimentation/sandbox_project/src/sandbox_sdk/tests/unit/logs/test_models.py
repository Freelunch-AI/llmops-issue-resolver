import pytest
from sandbox_sdk.logs.models import LogConfig

def test_log_config_default_values():
    """Test the default values of LogConfig model."""
    config = LogConfig()
    assert config.level == "INFO"
    assert config.format == "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    assert config.version == 1
    assert config.disable_existing_loggers is False
    assert config.filters is None

def test_log_config_default_handlers():
    """Test the default handlers configuration."""
    config = LogConfig()
    assert "console" in config.handlers
    console_handler = config.handlers["console"]
    assert console_handler["class"] == "logging.StreamHandler"
    assert console_handler["formatter"] == "default"
    assert console_handler["stream"] == "ext://sys.stdout"

def test_log_config_default_formatters():
    """Test the default formatters configuration."""
    config = LogConfig()
    assert "default" in config.formatters
    default_formatter = config.formatters["default"]
    assert default_formatter["format"] == "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

def test_log_config_custom_values():
    """Test LogConfig with custom values."""
    custom_config = LogConfig(
        level="DEBUG",
        format="%(levelname)s: %(message)s",
        disable_existing_loggers=True,
        version=2
    )
    assert custom_config.level == "DEBUG"
    assert custom_config.format == "%(levelname)s: %(message)s"
    assert custom_config.disable_existing_loggers is True
    assert custom_config.version == 2

def test_log_config_custom_handlers():
    """Test LogConfig with custom handlers."""
    custom_handlers = {
        "file": {
            "class": "logging.FileHandler",
            "formatter": "custom",
            "filename": "test.log"
        }
    }
    config = LogConfig(handlers=custom_handlers)
    assert "file" in config.handlers
    file_handler = config.handlers["file"]
    assert file_handler["class"] == "logging.FileHandler"
    assert file_handler["formatter"] == "custom"
    assert file_handler["filename"] == "test.log"

def test_log_config_custom_formatters():
    """Test LogConfig with custom formatters."""
    custom_formatters = {
        "custom": {
            "format": "%(levelname)s - %(message)s"
        }
    }
    config = LogConfig(formatters=custom_formatters)
    assert "custom" in config.formatters
    custom_formatter = config.formatters["custom"]
    assert custom_formatter["format"] == "%(levelname)s - %(message)s"

def test_log_config_custom_filters():
    """Test LogConfig with custom filters."""
    custom_filters = {
        "only_debug": {
            "name": "debug_filter"
        }
    }
    config = LogConfig(filters=custom_filters)
    assert config.filters == custom_filters

def test_log_config_model_serialization():
    """Test serialization of LogConfig model."""
    config = LogConfig(level="DEBUG")
    config_dict = config.model_dump()
    assert isinstance(config_dict, dict)
    assert config_dict["level"] == "DEBUG"
    assert "handlers" in config_dict
    assert "formatters" in config_dict

def test_log_config_model_deserialization():
    """Test deserialization of LogConfig model."""
    config_data = {
        "level": "WARNING",
        "format": "%(message)s",
        "version": 1,
        "disable_existing_loggers": True,
        "handlers": {"file": {"class": "logging.FileHandler", "filename": "app.log"}},
        "formatters": {"simple": {"format": "%(message)s"}},
        "filters": {"custom": {"name": "test_filter"}}
    }
    config = LogConfig(**config_data)
    assert config.level == "WARNING"
    assert config.format == "%(message)s"
    assert config.handlers["file"]["filename"] == "app.log"
    assert config.formatters["simple"]["format"] == "%(message)s"
    assert config.filters["custom"]["name"] == "test_filter"