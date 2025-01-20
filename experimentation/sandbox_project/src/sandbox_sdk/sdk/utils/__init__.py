"""Common utilities for the Sandbox SDK.

This package provides shared functionality used across the SDK, including:
- HTTP client utilities
- Authentication helpers
- Custom exceptions
"""

from sandbox_sdk.sdk.utils.http_client import HttpClient
from sandbox_sdk.sdk.utils.auth import Auth
from sandbox_sdk.sdk.utils.exceptions import (
    SandboxError,
    AuthenticationError,
    ValidationError,
    ApiError,
    ConnectionError
)

__all__ = [
    'HttpClient',
    'Auth',
    'SandboxError',
    'AuthenticationError',
    'ValidationError',
    'ApiError',
    'ConnectionError'
]