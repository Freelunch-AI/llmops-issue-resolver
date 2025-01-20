import asyncio
import inspect
import logging
from typing import Any, Dict, Optional
from functools import partial
import traceback

from .security import SecurityContext, SecurityError

logger = logging.getLogger(__name__)

class ToolExecutionError(Exception):
    """Raised when tool execution fails."""
    def __init__(self, message: str, tool_name: str, details: Optional[str] = None):
        self.tool_name = tool_name
        self.details = details
        super().__init__(message)

class ToolExecutor:
    def __init__(
        self,
        memory_limit_mb: int = 100,
        cpu_time_limit_sec: int = 10,
        max_processes: int = 5
    ):
        self.security_context = SecurityContext(
            memory_limit_mb=memory_limit_mb,
            cpu_time_limit_sec=cpu_time_limit_sec,
            max_processes=max_processes
        )
        self.tools: Dict[str, Any] = {}

    def register_tool(self, tool_name: str, tool_func: Any):
        """Register a tool function."""
        if not asyncio.iscoroutinefunction(tool_func):
            # Convert sync functions to async using to_thread
            async def wrapper(*args, **kwargs):
                return await asyncio.to_thread(tool_func, *args, **kwargs)
            tool_func = wrapper
        self.tools[tool_name] = tool_func

    async def execute_tool(
        self,
        tool_name: str,
        params: Dict[str, Any],
        timeout: float = 30.0
    ) -> Dict[str, Any]:
        """Execute a tool with security constraints and timeout."""
        # Validate tool existence first
        if tool_name not in self.tools:
            raise ToolExecutionError(
                f"Tool '{tool_name}' not found",
                tool_name
            )

        tool_func = self.tools[tool_name]
        
        # Validate parameters before entering security context
        try:
            sig = inspect.signature(tool_func)
            bound_args = sig.bind(**params)
            bound_args.apply_defaults()
        except TypeError as e:
            raise ToolExecutionError(
                f"Invalid parameters: {str(e)}",
                tool_name
            )
        
        task = None

        try:
            with self.security_context.secure_execution():
                # Run tool with timeout
                task = asyncio.create_task(
                    tool_func(*bound_args.args, **bound_args.kwargs)
                )
                result = await asyncio.wait_for(task, timeout=timeout)
                return {"success": True, "result": result}

        except asyncio.TimeoutError:
            if task and not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            raise ToolExecutionError(
                f"Tool execution timed out after {timeout} seconds",
                tool_name
            )
        except SecurityError as e:
            if task and not task.done():
                task.cancel()
            raise ToolExecutionError(
                f"Security violation: {str(e)}",
                tool_name
            )
        except Exception as e:
            if task and not task.done():
                task.cancel()
            logger.error(f"Tool execution failed: {traceback.format_exc()}")
            raise ToolExecutionError(
                f"Tool execution failed: {str(e)}",
                tool_name,
                traceback.format_exc()
            )

    async def _run_tool(self, tool_func: Any, params: Dict[str, Any]) -> Any:
        """Execute the tool function with parameter validation."""