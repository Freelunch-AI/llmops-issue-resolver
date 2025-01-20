"""Custom exceptions for the sandbox orchestrator."""

class SandboxOrchestratorError(Exception):
    """Base exception class for sandbox orchestrator."""
    pass

class CleanupError(SandboxOrchestratorError):
    """Raised when cleanup operations fail."""
    def __init__(self, message: str, details: dict[str, str]):
        self.details = details
        super().__init__(message)

class DatabaseError(SandboxOrchestratorError):
    """Raised when database operations fail."""
    pass

class SandboxError(SandboxOrchestratorError):
    """Raised when sandbox operations fail."""
    pass

class NetworkError(SandboxOrchestratorError):
    """Raised when network operations fail."""
    pass

class ResourceAllocationError(SandboxOrchestratorError):
    """Raised when resource allocation fails."""
    pass

class GatewayError(SandboxOrchestratorError):
    """Raised when communication with the gateway fails."""
    pass

class ConfigurationError(SandboxOrchestratorError):
    """Raised when there are configuration-related issues."""
    pass