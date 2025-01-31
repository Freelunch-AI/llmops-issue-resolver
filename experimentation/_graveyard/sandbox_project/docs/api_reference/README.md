# API Reference Documentation

This document provides detailed information about the APIs exposed by the sandbox gateway and orchestrator services.

## Table of Contents
- [Authentication](#authentication)
- [Sandbox Gateway API](#sandbox-gateway-api)
- [Orchestrator API](#orchestrator-api)
- [Error Handling](#error-handling)
- [Usage Examples](#usage-examples)

## Authentication

All API endpoints require authentication using JWT (JSON Web Tokens). To authenticate your requests:

1. Obtain a JWT token by calling the authentication endpoint
2. Include the token in the Authorization header:
   ```
   Authorization: Bearer <your_jwt_token>
   ```

### Token Endpoint

```
POST /api/v1/auth/token
```

Request body:
```json
{
    "username": "your_username",
    "password": "your_password"
}
```

## Sandbox Gateway API

### Create Sandbox Environment

```
POST /api/v1/sandbox/environments
```

Creates a new isolated sandbox environment.

Request body:
```json
{
    "name": "test-environment",
    "template": "python-3.9",
    "timeout": 3600
}
```

Response:
```json
{
    "environment_id": "env-123456",
    "status": "creating",
    "creation_time": "2023-01-01T00:00:00Z"
}
```

### List Environments

```
GET /api/v1/sandbox/environments
```

Returns a list of all sandbox environments.

### Delete Environment

```
DELETE /api/v1/sandbox/environments/{environment_id}
```

Terminates and removes a sandbox environment.

### Execute Code

```
POST /api/v1/sandbox/environments/{environment_id}/execute
```

Executes code in the specified environment.

Request body:
```json
{
    "code": "print('Hello, World!')",
    "timeout": 30
}
```

## Orchestrator API

### Create Workflow

```
POST /api/v1/orchestrator/workflows
```

Creates a new workflow definition.

Request body:
```json
{
    "name": "test-workflow",
    "steps": [
        {
            "name": "step1",
            "type": "code_execution",
            "config": {
                "code": "print('Step 1')"
            }
        }
    ]
}
```

### Start Workflow

```
POST /api/v1/orchestrator/workflows/{workflow_id}/start
```

Starts a workflow execution.

### Get Workflow Status

```
GET /api/v1/orchestrator/workflows/{workflow_id}/status
```

Returns the current status of a workflow.

### List Workflows

```
GET /api/v1/orchestrator/workflows
```

Returns a list of all workflows.

## Error Handling

All API endpoints use standard HTTP status codes:

- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error

Error responses follow this format:
```json
{
    "error": {
        "code": "ERROR_CODE",
        "message": "Human-readable error message",
        "details": {}
    }
}
```

## Usage Examples

### Creating and Using a Sandbox Environment

1. Create a new environment:
```bash
curl -X POST \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "test-env", "template": "python-3.9"}' \
  https://api.sandbox.example.com/api/v1/sandbox/environments
```

2. Execute code in the environment:
```bash
curl -X POST \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"code": "print(\"Hello, World!\")"}' \
  https://api.sandbox.example.com/api/v1/sandbox/environments/env-123456/execute
```

### Creating and Running a Workflow

1. Create a workflow:
```bash
curl -X POST \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "example-workflow",
    "steps": [
      {
        "name": "step1",
        "type": "code_execution",
        "config": {
          "code": "print(\"Step 1\")"
        }
      }
    ]
  }' \
  https://api.sandbox.example.com/api/v1/orchestrator/workflows
```

2. Start the workflow:
```bash
curl -X POST \
  -H "Authorization: Bearer <token>" \
  https://api.sandbox.example.com/api/v1/orchestrator/workflows/workflow-123456/start
```

3. Check workflow status:
```bash
curl -X GET \
  -H "Authorization: Bearer <token>" \
  https://api.sandbox.example.com/api/v1/orchestrator/workflows/workflow-123456/status
```