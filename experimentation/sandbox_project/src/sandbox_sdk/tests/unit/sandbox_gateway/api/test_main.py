import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import redis
from sandbox_sdk.sandbox_gateway.api.main import app, redis_client

@pytest.fixture
def test_client():
    return TestClient(app)

@pytest.fixture
def mock_redis():
    with patch('sandbox_sdk.sandbox_gateway.api.main.redis_client') as mock:
        yield mock

def test_register_sandbox_success(test_client, mock_redis):
    test_data = {
        "sandbox_id": "test-sandbox",
        "name": "Test Sandbox",
        "endpoint": "http://test-sandbox:8000"
    }
    
    response = test_client.post("/api/v1/sandboxes/register", json=test_data)
    
    assert response.status_code == 200
    assert response.json()["id"] == test_data["sandbox_id"]
    assert response.json()["name"] == test_data["name"]
    assert response.json()["endpoint"] == test_data["endpoint"]
    assert "api_key" in response.json()

def test_register_sandbox_redis_failure(test_client, mock_redis):
    mock_redis.set.side_effect = redis.RedisError("Connection failed")
    
    test_data = {
        "sandbox_id": "test-sandbox",
        "name": "Test Sandbox",
        "endpoint": "http://test-sandbox:8000"
    }
    
    response = test_client.post("/api/v1/sandboxes/register", json=test_data)
    
    assert response.status_code == 500
    assert "Connection failed" in response.json()["detail"]

def test_unregister_sandbox_success(test_client, mock_redis):
    mock_redis.get.return_value = b"http://test-sandbox:8000"
    mock_redis.eval.return_value = True
    
    response = test_client.delete("/api/v1/sandboxes/test-sandbox")
    
    assert response.status_code == 200
    assert response.json() == {"status": "unregistered"}

def test_unregister_sandbox_not_found(test_client, mock_redis):
    mock_redis.get.return_value = None
    
    response = test_client.delete("/api/v1/sandboxes/nonexistent-sandbox")
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

def test_proxy_request_unauthorized(test_client):
    response = test_client.get("/api/v1/sandbox/test-sandbox/some/path")
    
    assert response.status_code == 403
    assert "Invalid API key" in response.json()["detail"]

@patch('httpx.AsyncClient.request')
def test_proxy_request_success(mock_request, test_client, mock_redis):
    # Mock API key validation
    mock_redis.get.side_effect = [
        b"test-sandbox",  # For API key validation
        b"http://test-sandbox:8000"  # For endpoint lookup
    ]
    
    # Mock the proxied response
    mock_response = Mock()
    mock_response.content = b"test response"
    mock_response.status_code = 200
    mock_response.headers = {"Content-Type": "application/json"}
    mock_request.return_value = mock_response
    
    response = test_client.get(
        "/api/v1/sandbox/test-sandbox/some/path",
        headers={"X-API-Key": "test-key"}
    )
    
    assert response.status_code == 200
    assert response.content == b"test response"

def test_proxy_request_mismatched_sandbox(test_client, mock_redis):
    # Mock API key validation to return different sandbox_id
    mock_redis.get.return_value = b"different-sandbox"
    
    response = test_client.get(
        "/api/v1/sandbox/test-sandbox/some/path",
        headers={"X-API-Key": "test-key"}
    )
    
    assert response.status_code == 403
    assert "Not authorized for this sandbox" in response.json()["detail"]

@patch('httpx.AsyncClient.request')
def test_proxy_request_sandbox_error(mock_request, test_client, mock_redis):
    # Mock API key validation and endpoint lookup
    mock_redis.get.side_effect = [
        b"test-sandbox",
        b"http://test-sandbox:8000"
    ]
    
    # Mock the proxied request to fail
    mock_request.side_effect = Exception("Connection failed")
    
    response = test_client.get(
        "/api/v1/sandbox/test-sandbox/some/path",
        headers={"X-API-Key": "test-key"}
    )
    
    assert response.status_code == 503
    assert "Connection failed" in response.json()["detail"]

def test_proxy_request_different_methods(test_client, mock_redis):
    # Mock API key validation and endpoint lookup
    mock_redis.get.side_effect = [
        b"test-sandbox",  # For API key validation
        b"http://test-sandbox:8000"  # For endpoint lookup
    ]
    
    methods = ["POST", "PUT", "DELETE", "PATCH"]
    for method in methods:
        with patch('httpx.AsyncClient.request') as mock_request:
            mock_response = Mock()
            mock_response.content = b"test response"
            mock_response.status_code = 200
            mock_response.headers = {"Content-Type": "application/json"}
            mock_request.return_value = mock_response
            
            response = test_client.request(
                method,
                "/api/v1/sandbox/test-sandbox/some/path",
                headers={"X-API-Key": "test-key"}
            )
            
            assert response.status_code == 200
            assert response.content == b"test response"