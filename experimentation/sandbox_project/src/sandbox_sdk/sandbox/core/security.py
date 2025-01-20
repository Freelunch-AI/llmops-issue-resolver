import resource
import contextlib
import os
from typing import Optional
import signal
from functools import partial
import tempfile
import uuid
import shutil

class SecurityError(Exception):
    """Raised when security constraints are violated."""
    pass

class ResourceLimiter:
    def __init__(
        self,
        max_memory_mb: int,
        max_cpu_time_sec: int,
        max_processes: Optional[int] = None
    ):
        self.max_memory_mb = max_memory_mb
        self.max_cpu_time_sec = max_cpu_time_sec
        self.max_processes = max_processes

    def _timeout_handler(self, signum, frame):
        # Restore original handler before raising the exception
        if hasattr(self, '_original_handler'):
            signal.signal(signal.SIGXCPU, self._original_handler)

        raise SecurityError("CPU time limit exceeded")

    @contextlib.contextmanager
    def apply_limits(self):
        """Apply resource limits to the current process."""
        try:
            # Set memory limit
            memory_bytes = self.max_memory_mb * 1024 * 1024
            # Set multiple memory limits to cover both parent and child processes
            resource.setrlimit(resource.RLIMIT_DATA, (memory_bytes, memory_bytes))
            resource.setrlimit(resource.RLIMIT_RSS, (memory_bytes, memory_bytes))
            resource.setrlimit(resource.RLIMIT_AS, (memory_bytes * 2, memory_bytes * 2))  # Virtual memory

            # Set CPU time limit
            self._original_handler = signal.getsignal(signal.SIGXCPU)
            signal.signal(signal.SIGXCPU, self._timeout_handler)
            
            # Set both CPU time limits - process and children
            resource.setrlimit(resource.RLIMIT_CPU, (self.max_cpu_time_sec, self.max_cpu_time_sec))
            resource.setrlimit(resource.RLIMIT_RTTIME, (self.max_cpu_time_sec * 1000000, self.max_cpu_time_sec * 1000000))  # microseconds

            # Set process limit if specified
            if self.max_processes:
                resource.setrlimit(
                    resource.RLIMIT_NPROC,
                    (self.max_processes, self.max_processes)
                )

            yield

        finally:
            # Reset signal handler
            if hasattr(self, '_original_handler'):
                signal.signal(signal.SIGXCPU, self._original_handler)

class SecurityContext:
    """Manages security context for tool execution."""
    
    def __init__(
        self,
        memory_limit_mb: int = 100,
        cpu_time_limit_sec: int = 10,
        max_processes: int = 5,
        read_only: bool = True,
        workspace_root: str = "/workspace"
    ):
        self.resource_limiter = ResourceLimiter(
            memory_limit_mb,
            cpu_time_limit_sec,
            max_processes
        )
        self.read_only = read_only
        self.workspace_root = workspace_root

    @contextlib.contextmanager
    def secure_execution(self):
        """Create a secure execution environment."""
        # Create process-specific workspace
        process_workspace = os.path.join(
            self.workspace_root,
            f"proc_{os.getpid()}_{uuid.uuid4().hex}"
        )
        
        original_umask = os.umask(0o077)  # Restrictive file permissions
        
        try:
            # Create isolated workspace directory
            os.makedirs(process_workspace, exist_ok=True)
            
            if self.read_only:
                # Make process workspace read-only
                os.chmod(process_workspace, 0o555)

            with self.resource_limiter.apply_limits():
                # Set environment variable for child processes
                os.environ['SANDBOX_WORKSPACE'] = process_workspace
                yield

        finally:
            # Clean up environment
            os.environ.pop('SANDBOX_WORKSPACE', None)
            
            if self.read_only:
                # Restore permissions before cleanup
                os.chmod(process_workspace, 0o755)
            
            # Clean up process workspace
            shutil.rmtree(process_workspace, ignore_errors=True)
            os.umask(original_umask)