"""Common utilities for the Sandbox SDK.

This package provides shared functionality used across the SDK, including:
- HTTP client utilities
- Authentication helpers
- Custom exceptions
"""

from sandbox_sdk.sdk.utils.http_client import HTTPClient
from sandbox_sdk.sdk.utils.auth import Auth
from sandbox_sdk.sdk.utils.exceptions import (
    SandboxError,
    AuthenticationError,
    NetworkError,
    SandboxOperationError,
    ValidationError,
    ResourceNotFoundError,
    ConfigurationError,
    RateLimitError,
    TimeoutError,
    InvalidRequestError
)

__all__ = [
    'HTTPClient',
    'Auth',
    'SandboxError',
    'AuthenticationError',
    'NetworkError',
    'SandboxOperationError',
    'ValidationError',
    'ResourceNotFoundError',
    'ConfigurationError',
    'RateLimitError',
    'TimeoutError',
    'InvalidRequestError'
]