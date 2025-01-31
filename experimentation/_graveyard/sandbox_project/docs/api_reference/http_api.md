# HTTP API Reference

## Sandbox API

### Execute Actions
```http
POST /execute
```

Execute a sequence of actions in the sandbox.

#### Request Body
```json
{
    "actions": {
        "function_name1": {
            "description": "Action description",
            "args": {
                "param1": "value1",
                "param2": "value2"
            }
        },
        "function_name2": {
            "description": "Another action",
            "args": {
                "param1": "value1"
            }
        }
    }
}
```

#### Response
```json
{
    "observations": [
        {
            "stdout": "Output from action 1",
            "stderr": "",
            "terminal_still_running": false
        },
        {
            "stdout": "Output from action 2",
            "stderr": "",
            "terminal_still_running": false
        }
    ]
}
```

### Send Input
```http
POST /input
```

Send input to the terminal.

#### Request Body
```json
{
    "text": "input text"
}
```

#### Response
```json
{
    "status": "success"
}
```

### Get Output
```http
GET /output
```

Get current terminal output.

#### Response
```json
{
    "stdout": "Current output",
    "stderr": "",
    "terminal_still_running": true
}
```

### Health Check
```http
GET /health
```

Check if the sandbox is healthy.

#### Response
```json
{
    "status": "healthy"
}
```

## Orchestrator API

### Start Sandbox Group
```http
POST /group/start
```

Start the sandbox group and initialize databases.

#### Request Body
```json
{
    "database_access": {
        "database_type": "vector",
        "access_type": "read_write",
        "namespaces": ["default"]
    },
    "initial_database_population_config": "/path/to/config.yml"
}
```

#### Response
```json
{
    "status": "started"
}
```

### Start Sandbox
```http
POST /sandbox/start
```

Create and start a new sandbox.

#### Request Body
```json
{
    "id": "sandbox1",
    "tools": ["/path/to/tool1.py", "/path/to/tool2.py"],
    "compute_resources": {
        "cpu_cores": 2,
        "ram_gb": 4.0,
        "disk_gb": 10.0,
        "memory_bandwidth_gbps": 5.0,
        "unit": "absolute"
    },
    "attached_databases": {
        "vector_db": {
            "database_type": "vector",
            "access_type": "read",
            "namespaces": ["default"]
        }
    }
}
```

#### Response
```json
{
    "sandbox_url": "http://localhost:8001"
}
```

### Stop Sandbox
```http
POST /sandbox/stop
```

Stop and remove a sandbox.

#### Request Body
```json
{
    "id": "sandbox1"
}
```

#### Response
```json
{
    "status": "stopped"
}
```

### Stop Group
```http
POST /group/stop
```

Stop all sandboxes and cleanup resources.

#### Response
```json
{
    "status": "stopped"
}
```