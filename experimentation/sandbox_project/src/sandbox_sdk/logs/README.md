# Logging System Documentation

This directory contains the logging infrastructure for the sandbox project, providing a standardized approach to system event monitoring, error tracking, and operational insights.

## Overview

The logging system is built around two main components:
- `logging.py`: Handles core logging functionality and configuration
- `models.py`: Defines structured log data models and schemas

## Key Features

- Standardized logging formats across the entire application
- Multiple logging levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Structured log output for better parsing and analysis
- Configurable logging destinations (console, file, external services)
- Thread-safe logging implementation

## Logging Components

### logging.py

The `logging.py` module serves as the central logging configuration hub:

- Initializes logging configuration
- Provides custom formatters and handlers
- Implements context managers for logging scopes
- Handles log rotation and retention policies

### models.py

The `models.py` module defines the structure of log entries:

- Log event schemas and data models
- Validation rules for log fields
- Serialization/deserialization utilities
- Custom log record attributes

## Usage

To use the logging system in your code:

1. Import the logging module:
```python
from sandbox_sdk.logs import logging
```

2. Create a logger instance:
```python
logger = logging.get_logger(__name__)
```

3. Log messages at appropriate levels:
```python
logger.info("Operation completed successfully")
logger.error("An error occurred", exc_info=True)
```

## Log Levels

- **DEBUG**: Detailed information for debugging
- **INFO**: General operational messages
- **WARNING**: Indicate potential issues
- **ERROR**: Error conditions requiring attention
- **CRITICAL**: Critical failures needing immediate action

## Best Practices

1. Use appropriate log levels
2. Include relevant context in log messages
3. Avoid sensitive information in logs
4. Structure log messages for easy parsing
5. Add error tracebacks when logging exceptions

## Configuration

Logging can be configured through:
- Environment variables
- Configuration files
- Programmatic setup

Default configuration is stored in `config/logging.yaml`.

## Log Storage

Logs are stored in:
- Console output (development)
- Log files (production)
- External logging services (optional)

## Monitoring and Analysis

The logging system integrates with:
- Log aggregation tools
- Monitoring systems
- Analytics platforms

## Troubleshooting

Common logging issues and solutions:
1. Missing logs: Check log level configuration
2. Performance issues: Review log rotation settings
3. Storage problems: Monitor log file sizes

## Contributing

When adding new logging functionality:
1. Follow existing logging patterns
2. Update documentation
3. Add appropriate tests
4. Consider backward compatibility