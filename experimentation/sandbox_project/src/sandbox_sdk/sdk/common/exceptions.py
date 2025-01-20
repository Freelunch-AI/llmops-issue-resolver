"""Exception classes for the Sandbox SDK."""

class SandboxError(Exception):
    """Base exception class for all Sandbox SDK errors."""

    def __init__(self, message: str, *args, **kwargs):
        """Initialize the exception with a message and optional context.

        Args:
            message: The error message.
            *args: Additional positional arguments.
            **kwargs: Additional context as keyword arguments.
        """
        self.message = message
        self.context = kwargs
        super().__init__(message, *args)


class AuthenticationError(SandboxError):
    """Raised when there are authentication or authorization issues."""


class NetworkError(SandboxError):
    """Raised when there are network-related issues (connection, timeout, etc.)."""


class SandboxOperationError(SandboxError):
    """Raised when a sandbox operation fails."""


class ValidationError(SandboxError):
    """Raised when input validation fails."""


class ResourceNotFoundError(SandboxError):
    """Raised when a requested resource is not found."""


class ConfigurationError(SandboxError):
    """Raised when there are issues with the SDK configuration."""


class RateLimitError(SandboxError):
    """Raised when API rate limits are exceeded."""


class TimeoutError(NetworkError):
    """Raised when an operation times out."""


class InvalidRequestError(ValidationError):
    """Raised when the request is malformed or contains invalid parameters."""