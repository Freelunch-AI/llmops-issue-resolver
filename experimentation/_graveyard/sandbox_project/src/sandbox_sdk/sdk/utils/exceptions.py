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
    def __init__(self, message: str, credentials=None, *args, **kwargs):
        """Initialize authentication error.

        Args:
            message: The error message.
            credentials: Optional credentials context that caused the error.
            *args: Additional positional arguments.
            **kwargs: Additional context as keyword arguments.
        """
        super().__init__(f"Authentication failed: {message}", *args, **kwargs)


class NetworkError(SandboxError):
    """Raised when there are network-related issues (connection, timeout, etc.)."""
    def __init__(self, message: str, endpoint=None, status_code=None, *args, **kwargs):
        """Initialize network error.

        Args:
            message: The error message.
            endpoint: The API endpoint that failed.
            status_code: The HTTP status code if applicable.
            *args: Additional positional arguments.
            **kwargs: Additional context as keyword arguments.
        """
        super().__init__(f"Network error ({status_code if status_code else 'unknown'}): {message}", *args, **kwargs)


class SandboxOperationError(SandboxError):
    """Raised when a sandbox operation fails."""
    def __init__(self, message: str, operation=None, resource_id=None, *args, **kwargs):
        """Initialize sandbox operation error.

        Args:
            message: The error message.
            operation: The operation that failed.
            resource_id: The ID of the resource being operated on.
            *args: Additional positional arguments.
            **kwargs: Additional context as keyword arguments.
        """
        super().__init__(f"Operation failed: {message}", *args, **kwargs)


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

    def __init__(self, message: str, field=None, value=None, *args, **kwargs):
        """Initialize invalid request error.

        Args:
            message: The error message.
            field: The field that failed validation.
            value: The invalid value.
            *args: Additional positional arguments.
            **kwargs: Additional context as keyword arguments.
        """
        super().__init__(f"Invalid request: {message}", *args, **kwargs)


class ResourceConflictError(SandboxError):
    """Raised when there is a conflict with existing resources."""

    def __init__(self, message: str, resource_type=None, resource_id=None, *args, **kwargs):
        """Initialize resource conflict error.

        Args:
            message: The error message.
            resource_type: The type of resource causing the conflict.
            resource_id: The ID of the conflicting resource.
            *args: Additional positional arguments.
        """
        super().__init__(f"Resource conflict: {message}", *args, **kwargs)


class SandboxExecutionError(SandboxError):
    """Raised when execution of an action in a running sandbox fails."""

    def __init__(self, message: str, action=None, sandbox_id=None, *args, **kwargs):
        """Initialize sandbox execution error.

        Args:
            message: The error message.
            action: The action that failed during execution.
            sandbox_id: The ID of the sandbox where execution failed.
            *args: Additional positional arguments.
            **kwargs: Additional context as keyword arguments.
        """
        super().__init__(f"Sandbox execution failed: {message}", *args, **kwargs)
        self.action = action
        self.sandbox_id = sandbox_id


class SandboxConnectionError(SandboxError):
    """Raised when there are connectivity issues with a running sandbox instance."""

    def __init__(self, message: str, sandbox_id=None, endpoint=None, *args, **kwargs):
        """Initialize sandbox connection error.

        Args:
            message: The error message.
            sandbox_id: The ID of the sandbox that had connection issues.
            endpoint: The endpoint that failed to connect.
            *args: Additional positional arguments.
            **kwargs: Additional context as keyword arguments.
        """
        super().__init__(f"Sandbox connection failed: {message}", *args, **kwargs)
        self.sandbox_id = sandbox_id
        self.endpoint = endpoint```