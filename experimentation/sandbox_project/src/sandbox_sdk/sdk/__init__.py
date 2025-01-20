"""
Sandbox SDK - A Python SDK for interacting with sandbox environments.

This module provides the main interface for the Sandbox SDK, exposing the
SandboxClient class and related utilities for sandbox operations.
"""

from typing import TYPE_CHECKING

from sandbox_sdk.sdk.utils.http_client import HTTPClient
from sandbox_sdk.sdk.utils.auth import generate_auth_headers, AuthenticationError
from sandbox_sdk.sdk.utils.exceptions import (
    SandboxError,
    NetworkError,
    SandboxOperationError,
    ValidationError,
    ResourceNotFoundError,
    ConfigurationError,
    RateLimitError,
    TimeoutError,
    InvalidRequestError,
)

if TYPE_CHECKING:
    from sandbox_sdk.sdk.sdk_sandbox.client import SandboxClient

__version__ = "1.0.0"

__all__ = [
    "SandboxClient",
    "HTTPClient",
    "generate_auth_headers",
    "AuthenticationError",
    "SandboxError",
    "NetworkError",
    "SandboxOperationError",
    "ValidationError",
    "ResourceNotFoundError",
    "ConfigurationError",
    "RateLimitError",
    "TimeoutError",
    "InvalidRequestError",
]

# Lazy import to avoid circular dependencies
def __getattr__(name):
    if name == "SandboxClient":
        from sandbox_sdk.sdk.sdk_sandbox.client import SandboxClient
        return SandboxClient
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")