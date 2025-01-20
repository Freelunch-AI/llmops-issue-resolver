"""HTTP client utility for making requests to sandbox services."""

import logging
from typing import Any, Dict, Optional, Union
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from sandbox_sdk.sdk.utils.exceptions import (
    SandboxAPIError,
    SandboxConnectionError,
    SandboxTimeoutError,
)

logger = logging.getLogger(__name__)

class HTTPClient:
    """Base HTTP client for making requests to sandbox services."""

    def __init__(
        self,
        base_url: str,
        timeout: int = 30,
        max_retries: int = 3,
        pool_connections: int = 10,
        pool_maxsize: int = 10,
        default_headers: Optional[Dict[str, str]] = None,
    ):
        """Initialize HTTP client with configuration.

        Args:
            base_url: Base URL for the API endpoints
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
            pool_connections: Number of connection pools to cache
            pool_maxsize: Maximum size of the connection pool
            default_headers: Default headers to include in all requests
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.default_headers = default_headers or {}
        self.session = self._create_session(max_retries, pool_connections, pool_maxsize)

    def _create_session(self, max_retries: int, pool_connections: int, pool_maxsize: int) -> requests.Session:
        """Create and configure requests session with retry and pooling settings.

        Args:
            max_retries: Maximum number of retries for failed requests
            pool_connections: Number of connection pools to cache
            pool_maxsize: Maximum size of the connection pool

        Returns:
            Configured requests.Session object
        """
        session = requests.Session()
        
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504],
        )

        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=pool_connections,
            pool_maxsize=pool_maxsize
        )
        
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> requests.Response:
        """Make HTTP request with error handling.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            params: URL parameters
            data: Form data to send
            json: JSON data to send
            headers: Additional headers
            **kwargs: Additional arguments to pass to requests

        Returns:
            Response object

        Raises:
            SandboxConnectionError: For connection-related errors
            SandboxTimeoutError: For timeout errors
            SandboxAPIError: For API errors
        """
        url = urljoin(self.base_url, endpoint)
        request_headers = {**self.default_headers, **(headers or {})}

        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                data=data,
                json=json,
                headers=request_headers,
                timeout=self.timeout,
                **kwargs,
            )
            response.raise_for_status()
            return response

        except requests.ConnectionError as e:
            logger.error(f"Connection error for {method} {url}: {str(e)}")
            raise SandboxConnectionError(f"Failed to connect to {url}") from e

        except requests.Timeout as e:
            logger.error(f"Timeout error for {method} {url}: {str(e)}")
            raise SandboxTimeoutError(f"Request to {url} timed out") from e

        except requests.HTTPError as e:
            logger.error(f"HTTP error for {method} {url}: {str(e)}")
            raise SandboxAPIError(
                f"API request failed: {e.response.status_code} - {e.response.text}"
            ) from e

        except Exception as e:
            logger.error(f"Unexpected error for {method} {url}: {str(e)}")
            raise SandboxAPIError(f"Unexpected error: {str(e)}") from e

    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> requests.Response:
        """Send GET request.

        Args:
            endpoint: API endpoint path
            params: URL parameters
            **kwargs: Additional arguments to pass to requests

        Returns:
            Response object
        """
        return self._make_request("GET", endpoint, params=params, **kwargs)

    def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> requests.Response:
        """Send POST request.

        Args:
            endpoint: API endpoint path
            data: Form data to send
            json: JSON data to send
            **kwargs: Additional arguments to pass to requests

        Returns:
            Response object
        """
        return self._make_request("POST", endpoint, data=data, json=json, **kwargs)

    def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> requests.Response:
        """Send PUT request.

        Args:
            endpoint: API endpoint path
            data: Form data to send
            json: JSON data to send
            **kwargs: Additional arguments to pass to requests

        Returns:
            Response object
        """
        return self._make_request("PUT", endpoint, data=data, json=json, **kwargs)

    def delete(
        self,
        endpoint: str,
        **kwargs: Any,
    ) -> requests.Response:
        """Send DELETE request.

        Args:
            endpoint: API endpoint path
            **kwargs: Additional arguments to pass to requests

        Returns:
            Response object
        """
        return self._make_request("DELETE", endpoint, **kwargs)

    def close(self) -> None:
        """Close the session and cleanup resources."""
        if self.session:
            self.session.close()

    def __enter__(self) -> 'HTTPClient':
        """Context manager enter."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()