# Sandbox Gateway

The Sandbox Gateway serves as the central entry point for managing and routing requests to isolated sandbox environments. It provides a secure and controlled interface for external clients to interact with sandbox instances while handling authentication, request validation, and load balancing.

## Architecture Overview

The Sandbox Gateway implements a proxy-based architecture that:
- Intercepts incoming requests from clients
- Validates authentication credentials
- Routes requests to appropriate sandbox instances
- Manages sandbox lifecycle and health checks
- Handles response aggregation and error handling

```
Client Request → Authentication → Request Validation → Sandbox Routing → Sandbox Instance
```

## Authentication Flow

The authentication system (`auth.py`) implements:
- Token-based authentication for API requests
- Role-based access control (RBAC)
- Session management
- Rate limiting
- IP whitelisting capabilities

Authentication flow:
1. Client sends request with authentication token
2. Gateway validates token and permissions
3. If valid, request proceeds to routing
4. If invalid, returns 401/403 error response

## Request Proxying

The proxy system (`proxy.py`) handles:
- Dynamic routing to sandbox instances
- Load balancing across multiple sandboxes
- Request/response transformation
- Error handling and retries
- Timeout management
- Health checking of sandbox instances

## Key Components

### auth.py
- Handles all authentication and authorization logic
- Manages token validation and session state
- Implements security policies and access controls
- Provides audit logging of authentication events

### proxy.py
- Manages sandbox instance routing
- Implements load balancing algorithms
- Handles request/response lifecycle
- Monitors sandbox health and availability
- Provides circuit breaking for failed instances

## Usage Examples

### Authenticating Requests
```python
# Include authentication token in headers
headers = {
    'Authorization': 'Bearer <your-token-here>',
    'Content-Type': 'application/json'
}
```

### Making Sandbox Requests
```python
# Example request to sandbox endpoint
POST /api/v1/sandbox/execute
Host: gateway.example.com
Authorization: Bearer <token>
Content-Type: application/json

{
    "sandbox_id": "sandbox-123",
    "operation": "run_code",
    "payload": {
        "code": "print('Hello World')",
        "language": "python"
    }
}
```

## Configuration

The gateway can be configured through environment variables or configuration files:

```ini
# Gateway Configuration
GATEWAY_PORT=8080
AUTH_TOKEN_EXPIRY=3600
MAX_CONCURRENT_REQUESTS=100

# Authentication Configuration
AUTH_ENABLED=true
AUTH_PROVIDER=jwt
TOKEN_SECRET=<secret-key>

# Proxy Configuration
PROXY_TIMEOUT=30
MAX_RETRIES=3
LOAD_BALANCER_STRATEGY=round-robin
```

## Health Checks

The gateway provides health check endpoints:

- `/health` - Overall gateway health
- `/health/auth` - Authentication service status
- `/health/proxy` - Proxy service status
- `/health/sandboxes` - Status of sandbox instances

## Error Handling

The gateway implements standardized error responses:

```json
{
    "error": {
        "code": "AUTH_001",
        "message": "Invalid authentication token",
        "details": "Token has expired"
    }
}
```

## Monitoring and Metrics

Key metrics tracked by the gateway:
- Request latency
- Authentication success/failure rates
- Proxy routing performance
- Sandbox instance health
- Error rates and types

## Security Considerations

The gateway implements several security measures:
- TLS encryption for all connections
- Token encryption and secure storage
- Request payload validation
- Rate limiting and DDoS protection
- Audit logging of all operations