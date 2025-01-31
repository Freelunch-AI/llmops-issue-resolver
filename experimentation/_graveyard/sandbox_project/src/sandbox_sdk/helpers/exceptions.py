class SandboxError(Exception):
    """Base exception for all sandbox-related errors."""

class SandboxNotStartedError(SandboxError):
    """Raised when trying to use a sandbox that hasn't been started."""

class SandboxStartError(SandboxError):
    """Raised when there's an error starting a sandbox."""

class SandboxStopError(SandboxError):
    """Raised when there's an error stopping a sandbox."""

class ActionExecutionError(SandboxError):
    """Raised when there's an error executing an action in the sandbox."""

class ResourceError(SandboxError):
    """Raised when there's an error with resource allocation."""

class DatabaseError(SandboxError):
    """Raised when there's an error with database operations."""

class ConfigurationError(SandboxError):
    """Raised when there's an error in the configuration."""
class ToolError(SandboxError):
    """Raised when there's an error with sandbox tools."""


class AuthenticationError(SandboxError):
    """Raised when there's an authentication-related error."""


class SignatureError(AuthenticationError):
    """Raised when there's an error signing data with private key."""


class APIError(SandboxError):
    """Base exception for API-related errors."""


class RequestError(APIError):
    """Raised when there's an error making an API request."""


class InvalidResponseError(APIError):
    """Raised when receiving an invalid or unexpected API response."""