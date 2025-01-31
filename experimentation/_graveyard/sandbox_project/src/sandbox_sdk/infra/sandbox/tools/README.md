# Sandbox Tools Documentation

This directory contains various utility tools and modules that provide essential functionality for the Sandbox SDK. Each tool module is designed to handle specific operations and can be used independently or in combination with other modules.

## Available Tools

### 1. Filesystem Tools (`filesystem_tools.py`)

A collection of utilities for file system operations and management.

#### Key Functions:
- `create_directory(path: str) -> bool`: Creates a new directory at the specified path
- `delete_directory(path: str) -> bool`: Removes a directory and its contents
- `list_files(directory: str, pattern: str = None) -> List[str]`: Lists files in a directory with optional pattern matching
- `copy_file(source: str, destination: str) -> bool`: Copies a file from source to destination

**Usage Example:**
```python
from sandbox.tools.filesystem_tools import create_directory, list_files

# Create a new directory
create_directory("/path/to/new/directory")

# List all Python files in a directory
python_files = list_files("/path/to/directory", "*.py")
```

### 2. Web Tools (`web_tools.py`)

Utilities for handling HTTP requests, API interactions, and web-related operations.

#### Key Functions:
- `make_request(url: str, method: str = "GET", headers: dict = None) -> Response`: Makes HTTP requests
- `download_file(url: str, destination: str) -> bool`: Downloads a file from a URL
- `validate_url(url: str) -> bool`: Checks if a URL is valid and accessible

**Usage Example:**
```python
from sandbox.tools.web_tools import make_request, download_file

# Make an API request
response = make_request("https://api.example.com/data")

# Download a file
download_file("https://example.com/file.pdf", "local_file.pdf")
```

### 3. Database Tools (`database_tools.py`)

Tools for database operations, connections, and query management.

#### Key Functions:
- `connect(connection_string: str) -> Connection`: Establishes database connection
- `execute_query(connection: Connection, query: str) -> Result`: Executes SQL queries
- `backup_database(connection: Connection, backup_path: str) -> bool`: Creates database backup

**Usage Example:**
```python
from sandbox.tools.database_tools import connect, execute_query

# Connect to database
conn = connect("postgresql://user:password@localhost:5432/dbname")

# Execute a query
results = execute_query(conn, "SELECT * FROM users")
```

### 4. Terminal Tools (`terminal_tools.py`)

Utilities for terminal operations and command-line interface interactions.

#### Key Functions:
- `run_command(command: str) -> Tuple[str, str]`: Executes shell commands
- `get_terminal_size() -> Tuple[int, int]`: Returns terminal dimensions
- `clear_screen() -> None`: Clears the terminal screen

**Usage Example:**
```python
from sandbox.tools.terminal_tools import run_command, clear_screen

# Execute a shell command
output, error = run_command("ls -la")

# Clear the terminal screen
clear_screen()
```

## Installation

The tools are part of the Sandbox SDK and are automatically installed with the package. No additional installation steps are required.

```bash
pip install sandbox-sdk
```

## Contributing

When adding new tools or modifying existing ones:

1. Follow the established naming conventions
2. Add comprehensive docstrings
3. Include unit tests
4. Update this documentation with new functions and examples
5. Ensure backward compatibility

## License

This project is licensed under the MIT License - see the LICENSE file for details.