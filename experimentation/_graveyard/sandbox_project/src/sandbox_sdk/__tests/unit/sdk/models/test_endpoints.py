import pytest
from pydantic import ValidationError

from sandbox_sdk.sdk.models.endpoints import SandboxEndpoint, SandboxGroupEndpoints


class TestSandboxEndpoint:
    def test_valid_sandbox_endpoint_creation(self):
        endpoint_data = {
            "id": "sandbox-123",
            "name": "Test Sandbox",
            "endpoint": "https://api.sandbox.test/endpoint"
        }
        endpoint = SandboxEndpoint(**endpoint_data)
        
        assert endpoint.id == endpoint_data["id"]
        assert endpoint.name == endpoint_data["name"]
        assert endpoint.endpoint == endpoint_data["endpoint"]

    def test_sandbox_endpoint_missing_fields(self):
        incomplete_data = {
            "id": "sandbox-123",
            "name": "Test Sandbox"
        }
        
        with pytest.raises(ValidationError):
            SandboxEndpoint(**incomplete_data)

    def test_sandbox_endpoint_invalid_types(self):
        invalid_data = {
            "id": 123,  # Should be string
            "name": "Test Sandbox",
            "endpoint": "https://api.sandbox.test/endpoint"
        }
        
        with pytest.raises(ValidationError):
            SandboxEndpoint(**invalid_data)


class TestSandboxGroupEndpoints:
    def test_valid_sandbox_group_endpoints_creation(self):
        group_data = {
            "group_id": "group-123",
            "sandboxes": [
                {
                    "id": "sandbox-1",
                    "name": "Test Sandbox 1",
                    "endpoint": "https://api.sandbox.test/endpoint1"
                },
                {
                    "id": "sandbox-2",
                    "name": "Test Sandbox 2",
                    "endpoint": "https://api.sandbox.test/endpoint2"
                }
            ]
        }
        
        group = SandboxGroupEndpoints(**group_data)
        
        assert group.group_id == group_data["group_id"]
        assert len(group.sandboxes) == 2
        assert isinstance(group.sandboxes[0], SandboxEndpoint)
        assert group.sandboxes[0].id == "sandbox-1"
        assert group.sandboxes[1].id == "sandbox-2"

    def test_sandbox_group_endpoints_empty_sandboxes(self):
        group_data = {
            "group_id": "group-123",
            "sandboxes": []
        }
        
        group = SandboxGroupEndpoints(**group_data)
        assert len(group.sandboxes) == 0

    def test_sandbox_group_endpoints_missing_fields(self):
        incomplete_data = {
            "group_id": "group-123"
        }
        
        with pytest.raises(ValidationError):
            SandboxGroupEndpoints(**incomplete_data)

    def test_sandbox_group_endpoints_invalid_sandbox_data(self):
        invalid_data = {
            "group_id": "group-123",
            "sandboxes": [
                {
                    "id": "sandbox-1",
                    "name": "Test Sandbox 1"
                    # Missing endpoint field
                }
            ]
        }
        
        with pytest.raises(ValidationError):
            SandboxGroupEndpoints(**invalid_data)