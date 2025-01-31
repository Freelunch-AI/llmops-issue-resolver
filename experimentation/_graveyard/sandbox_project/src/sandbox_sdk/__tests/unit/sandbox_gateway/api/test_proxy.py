import pytest
from unittest.mock import AsyncMock, Mock, patch
from fastapi import Request, Response, HTTPException
import httpx
from sandbox_sdk.sandbox_gateway.api.proxy import RequestProxy
from sandbox_sdk.sandbox_gateway.api.models import ProxyConfig

@pytest.fixture
def proxy_config():
    return ProxyConfig(
        max_request_size=1024 * 1024,
        allowed_url_patterns=["api.example.com"],
        filtered_headers=["host"],
        max_retries=3,
        connect_timeout=5.0,
        read_timeout=30.0,
        total_timeout=60.0
    )

@pytest.fixture
def mock_request():
    request = Mock(spec=Request)
    request.method = "GET"
    request.headers = {"content-length": "100", "host": "test.com", "x-custom": "value"}
    request.stream = AsyncMock(return_value=iter([b"test data"]))
    return request

@pytest.fixture
async def proxy(proxy_config):
    async with RequestProxy(config=proxy_config) as proxy:
        yield proxy

@pytest.mark.asyncio
async def test_successful_request_forwarding(proxy, mock_request):
    mock_response = Mock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.headers = {"content-type": "application/json"}
    mock_response.aiter_bytes = AsyncMock(return_value=iter([b"response data"]))
    
    with patch.object(proxy.client, 'request', AsyncMock(return_value=mock_response)):
        response = await proxy.forward_request(
            "https://api.example.com/test",
            mock_request
        )
        
        assert isinstance(response, Response)
        assert response.status_code == 200

@pytest.mark.asyncio
async def test_url_validation(proxy, mock_request):
    with pytest.raises(HTTPException) as exc_info:
        await proxy.forward_request(
            "https://malicious.com/test",
            mock_request
        )
    assert exc_info.value.status_code == 403

@pytest.mark.asyncio
async def test_request_size_limit(proxy, mock_request):
    mock_request.headers = {"content-length": str(proxy.config.max_request_size + 1)}
    
    with pytest.raises(HTTPException) as exc_info:
        await proxy.forward_request(
            "https://api.example.com/test",
            mock_request
        )
    assert exc_info.value.status_code == 413

@pytest.mark.asyncio
async def test_header_sanitization(proxy, mock_request):
    mock_request.headers = {"x-custom": "value\r\ninjection"}
    mock_response = Mock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.headers = {}
    mock_response.aiter_bytes = AsyncMock(return_value=iter([b""]))
    
    with patch.object(proxy.client, 'request', AsyncMock(return_value=mock_response)) as mock_request_call:
        await proxy.forward_request(
            "https://api.example.com/test",
            mock_request
        )
        
        called_headers = mock_request_call.call_args[1]['headers']
        assert called_headers['x-custom'] == "valueinjection"

@pytest.mark.asyncio
async def test_retry_on_timeout(proxy, mock_request):
    mock_response = Mock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.headers = {}
    mock_response.aiter_bytes = AsyncMock(return_value=iter([b""]))
    
    side_effect = [
        httpx.TimeoutException("Timeout"),
        mock_response
    ]
    
    with patch.object(proxy.client, 'request', AsyncMock(side_effect=side_effect)):
        response = await proxy.forward_request(
            "https://api.example.com/test",
            mock_request
        )
        assert isinstance(response, Response)
        assert response.status_code == 200

@pytest.mark.asyncio
async def test_retry_on_connection_error(proxy, mock_request):
    mock_response = Mock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.headers = {}
    mock_response.aiter_bytes = AsyncMock(return_value=iter([b""]))
    
    side_effect = [
        httpx.ConnectError("Connection failed"),
        mock_response
    ]
    
    with patch.object(proxy.client, 'request', AsyncMock(side_effect=side_effect)):
        response = await proxy.forward_request(
            "https://api.example.com/test",
            mock_request
        )
        assert isinstance(response, Response)
        assert response.status_code == 200

@pytest.mark.asyncio
async def test_max_retries_exceeded(proxy, mock_request):
    with patch.object(proxy.client, 'request', 
                     AsyncMock(side_effect=httpx.TimeoutException("Timeout"))):
        with pytest.raises(HTTPException) as exc_info:
            await proxy.forward_request(
                "https://api.example.com/test",
                mock_request
            )
        assert exc_info.value.status_code == 504

@pytest.mark.asyncio
async def test_server_error_handling(proxy, mock_request):
    mock_response = Mock(spec=httpx.Response)
    mock_response.status_code = 500
    mock_response.headers = {}
    mock_response.aiter_bytes = AsyncMock(return_value=iter([b"server error"]))
    
    with patch.object(proxy.client, 'request', AsyncMock(return_value=mock_response)):
        response = await proxy.forward_request(
            "https://api.example.com/test",
            mock_request
        )
        assert response.status_code == 500

@pytest.mark.asyncio
async def test_client_error_handling(proxy, mock_request):
    mock_response = Mock(spec=httpx.Response)
    mock_response.status_code = 404
    mock_response.headers = {}
    mock_response.aiter_bytes = AsyncMock(return_value=iter([b"not found"]))
    
    with patch.object(proxy.client, 'request', AsyncMock(return_value=mock_response)):
        response = await proxy.forward_request(
            "https://api.example.com/test",
            mock_request
        )
        assert response.status_code == 404