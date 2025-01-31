class SandboxError(Exception):
    """Base exception class for Sandbox Toolkit."""
    pass

class DatabaseError(SandboxError):
    """Database-related errors."""
    pass

class ResourceError(SandboxError):
    """Resource allocation errors."""
    pass

class ToolError(SandboxError):
    """Tool execution errors."""
    pass