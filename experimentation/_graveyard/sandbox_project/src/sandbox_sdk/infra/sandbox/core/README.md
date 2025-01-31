# Sandbox Core Components

The `sandbox/core` package contains essential components that form the foundation of the sandbox execution environment. This directory houses critical modules for security enforcement and tool execution management.

## Security Module (`security.py`)

The `SecurityContext` class in `security.py` implements robust security mechanisms to ensure safe execution of tools within the sandbox environment:

- **Permission Management**: Controls access to system resources and operations
- **Resource Isolation**: Ensures tools run in isolated environments
- **Access Control**: Manages what operations and resources tools can access
- **Security Policies**: Enforces configurable security policies and restrictions

Example usage:
```python
from sandbox.core.security import SecurityContext

security_context = SecurityContext(
    allowed_operations=['read_file', 'write_file'],
    restricted_paths=['/system', '/network'],
    memory_limit='512MB'
)
```

## Executor Module (`executor.py`)

The `ToolExecutor` class in `executor.py` manages the lifecycle and execution of tools:

- **Tool Lifecycle Management**: Handles tool initialization, execution, and cleanup
- **Error Handling**: Provides robust error handling and recovery mechanisms
- **Resource Management**: Manages system resources during tool execution
- **Execution Monitoring**: Monitors tool execution and enforces timeouts

Example usage:
```python
from sandbox.core.executor import ToolExecutor

executor = ToolExecutor(security_context=security_context)
result = executor.execute_tool(
    tool_name="sample_tool",
    parameters={"input": "data"},
    timeout=30
)
```

## Key Features

### Security Features
- Configurable permission sets
- Resource usage limits
- Network access control
- File system restrictions
- Process isolation

### Execution Features
- Asynchronous execution support
- Timeout management
- Resource cleanup
- Error recovery
- Execution logging

## Best Practices

1. **Security Context Configuration**
   - Always define explicit permissions
   - Use minimal required access
   - Configure resource limits appropriately

2. **Tool Execution**
   - Set reasonable timeouts
   - Handle execution errors
   - Clean up resources after execution
   - Monitor resource usage

## Integration Example

```python
from sandbox.core.security import SecurityContext
from sandbox.core.executor import ToolExecutor

# Configure security context
security_context = SecurityContext(
    allowed_operations=['read_file'],
    memory_limit='256MB',
    timeout=60
)

# Initialize executor
executor = ToolExecutor(security_context=security_context)

try:
    # Execute tool
    result = executor.execute_tool(
        tool_name="analysis_tool",
        parameters={"input_file": "data.txt"}
    )
except Exception as e:
    # Handle execution errors
    print(f"Execution failed: {e}")
```

## Error Handling

The core components provide comprehensive error handling:

- `SecurityViolationError`: Raised when security policies are violated
- `ExecutionTimeoutError`: Raised when tool execution exceeds timeout
- `ResourceExhaustionError`: Raised when resource limits are exceeded
- `ToolExecutionError`: Generic error for execution failures

## Contributing

When extending core components:

1. Maintain security-first approach
2. Add comprehensive tests
3. Document security implications
4. Follow existing patterns
5. Update documentation