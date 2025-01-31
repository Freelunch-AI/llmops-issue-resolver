# Source Code Directory (src)

This directory contains the core source code for the LLMOps Issue Resolver sandbox project. The code here demonstrates various patterns and practices for implementing LLM-based operations and issue resolution workflows.

## Directory Structure

```
src/
├── sandbox_sdk/       # Core SDK implementation for sandbox operations
│   ├── client/       # Client-side implementations
│   ├── models/       # Data models and schemas
│   └── utils/        # Utility functions and helpers
```

## Components

### sandbox_sdk

The `sandbox_sdk` directory contains the main SDK implementation that provides:
- Client interfaces for LLM interactions
- Data models for structured information exchange
- Utility functions for common operations
- Testing and validation tools

For detailed implementation specifics, please refer to the [sandbox_sdk documentation](./sandbox_sdk/README.md).

## Usage

To use the components in this directory:

1. Import the required modules from the SDK:
   ```python
   from sandbox_sdk.client import SandboxClient
   from sandbox_sdk.models import IssueModel
   ```

2. Follow the implementation examples in the respective component documentation.

## Documentation

- [SDK Documentation](./sandbox_sdk/README.md)
- [API Reference](../docs/api-reference.md)
- [Implementation Guide](../docs/implementation-guide.md)

## Contributing

When contributing to this codebase:

1. Follow the established project structure
2. Maintain consistent documentation standards
3. Include appropriate unit tests
4. Update relevant documentation when adding new features

For detailed contribution guidelines, please refer to the [Contributing Guide](../CONTRIBUTING.md).