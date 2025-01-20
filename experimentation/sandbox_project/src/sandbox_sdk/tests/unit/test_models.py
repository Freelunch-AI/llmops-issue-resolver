import pytest
from sandbox_sdk.helpers.models import DatabaseConfig, ServiceManagementConfig, SandboxConfig

class TestDatabaseConfig:
    def test_valid_database_config(self):
        config = DatabaseConfig(
            username="test_user",
            password="test_pass",
            database_name="test_db"
        )
        assert config.host == "localhost"  # default value
        assert config.port == 5432  # default value
        assert config.username == "test_user"
        assert config.password == "test_pass"
        assert config.database_name == "test_db"

    def test_custom_database_config(self):
        config = DatabaseConfig(
            host="custom_host",
            port=5433,
            username="test_user",
            password="test_pass",
            database_name="test_db"
        )
        assert config.host == "custom_host"
        assert config.port == 5433

    def test_database_config_to_dict(self):
        config = DatabaseConfig(
            username="test_user",
            password="test_pass",
            database_name="test_db"
        )
        config_dict = config.dict()
        assert isinstance(config_dict, dict)
        assert config_dict["username"] == "test_user"
        assert config_dict["password"] == "test_pass"
        assert config_dict["database_name"] == "test_db"

    def test_missing_required_fields(self):
        with pytest.raises(ValueError):
            DatabaseConfig()

class TestServiceManagementConfig:
    def test_valid_service_config(self):
        config = ServiceManagementConfig(
            service_name="test_service",
            port=8080
        )
        assert config.service_name == "test_service"
        assert config.port == 8080
        assert config.host == "localhost"  # default value
        assert config.debug_mode is False  # default value

    def test_custom_service_config(self):
        config = ServiceManagementConfig(
            service_name="test_service",
            port=8080,
            host="custom_host",
            debug_mode=True
        )
        assert config.host == "custom_host"
        assert config.debug_mode is True

    def test_service_config_to_dict(self):
        config = ServiceManagementConfig(
            service_name="test_service",
            port=8080
        )
        config_dict = config.dict()
        assert isinstance(config_dict, dict)
        assert config_dict["service_name"] == "test_service"
        assert config_dict["port"] == 8080

    def test_missing_required_fields(self):
        with pytest.raises(ValueError):
            ServiceManagementConfig()

class TestSandboxConfig:
    def test_valid_sandbox_config(self):
        db_config = DatabaseConfig(
            username="test_user",
            password="test_pass",
            database_name="test_db"
        )
        service_config = ServiceManagementConfig(
            service_name="test_service",
            port=8080
        )
        config = SandboxConfig(
            database=db_config,
            service=service_config
        )
        assert config.environment == "development"  # default value
        assert config.log_level == "INFO"  # default value
        assert config.additional_settings is None  # default value

    def test_custom_sandbox_config(self):
        db_config = DatabaseConfig(
            username="test_user",
            password="test_pass",
            database_name="test_db"
        )
        service_config = ServiceManagementConfig(
            service_name="test_service",
            port=8080
        )
        config = SandboxConfig(
            database=db_config,
            service=service_config,
            environment="production",
            log_level="DEBUG",
            additional_settings={"key": "value"}
        )
        assert config.environment == "production"
        assert config.log_level == "DEBUG"
        assert config.additional_settings == {"key": "value"}

    def test_sandbox_config_to_dict(self):
        db_config = DatabaseConfig(
            username="test_user",
            password="test_pass",
            database_name="test_db"
        )
        service_config = ServiceManagementConfig(
            service_name="test_service",
            port=8080
        )
        config = SandboxConfig(
            database=db_config,
            service=service_config
        )
        config_dict = config.dict()
        assert isinstance(config_dict, dict)
        assert isinstance(config_dict["database"], dict)
        assert isinstance(config_dict["service"], dict)
        assert config_dict["database"]["username"] == "test_user"
        assert config_dict["service"]["service_name"] == "test_service"

    def test_missing_required_fields(self):
        with pytest.raises(ValueError):
            SandboxConfig()

    def test_nested_config_validation(self):
        with pytest.raises(ValueError):
            SandboxConfig(
                database={"invalid": "config"},
                service={"invalid": "config"}
            )