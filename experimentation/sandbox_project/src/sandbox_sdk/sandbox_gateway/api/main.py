from fastapi import FastAPI, HTTPException, Security, Depends, Request, Response
from fastapi.security.api_key import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN
import httpx
import redis
import os
import secrets
from typing import Dict, Optional
from pydantic import BaseModel

class SandboxRegistration(BaseModel):
    """Request model for registering a new sandbox."""
    sandbox_id: str
    name: str
    endpoint: str

# Lua script for atomic sandbox unregistration
UNREGISTER_SANDBOX_SCRIPT = """
local sandbox_id = ARGV[1]
local keys = redis.call('keys', 'apikey:*')
local deleted = false
for _, key in ipairs(keys) do
    if redis.call('get', key) == sandbox_id then
        redis.call('del', key)
        deleted = true
    end
end
return deleted"""


class SandboxEndpoint(BaseModel):
    """Response model for sandbox endpoint information."""
    id: str
    name: str
    endpoint: str
    api_key: str

app = FastAPI()

# Redis client for storing API keys and sandbox info
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    db=0
)

# API key header
API_KEY_HEADER = APIKeyHeader(name="X-API-Key")

async def get_sandbox_id(api_key: str = Security(API_KEY_HEADER)) -> str:
    """Validate API key and return sandbox ID."""
    sandbox_id = redis_client.get(f"apikey:{api_key}")
    if not sandbox_id:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Invalid API key"
        )
    return sandbox_id.decode()

@app.post("/api/v1/sandboxes/register", response_model=SandboxEndpoint)
async def register_sandbox(registration: SandboxRegistration) -> SandboxEndpoint:
    """Register a new sandbox and generate API key."""
    # Generate API key
    api_key = secrets.token_urlsafe(32)
    
    try:
        # Store API key -> sandbox ID mapping
        redis_client.set(f"apikey:{api_key}", registration.sandbox_id)
        
        # Store sandbox endpoint
        redis_client.set(
            f"sandbox:{registration.sandbox_id}:endpoint",
            registration.endpoint
        )
        
        return SandboxEndpoint(
            id=registration.sandbox_id,
            name=registration.name,
            endpoint=registration.endpoint,
            api_key=api_key
        )
    
    except Exception as e:
        # Cleanup on failure
        redis_client.delete(f"apikey:{api_key}")
        redis_client.delete(f"sandbox:{registration.sandbox_id}:endpoint")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/v1/sandboxes/{sandbox_id}")
async def unregister_sandbox(sandbox_id: str):
    """Unregister a sandbox and remove all associated API keys atomically.
    
    Args:
        sandbox_id: The ID of the sandbox to unregister
        
    Returns:
        Dict with status message
        
    Raises:
        HTTPException: If Redis operations fail or sandbox not found
    """
    try:
        # First verify sandbox exists
        if redis_client.get(f"sandbox:{sandbox_id}:endpoint") is None:
            raise HTTPException(
                status_code=404,
                detail=f"Sandbox {sandbox_id} not found"
            )

        # Then execute atomic unregistration using Lua script
        deleted = redis_client.eval(
            UNREGISTER_SANDBOX_SCRIPT,
            0,  # number of keys
            sandbox_id.encode()
        )

        if not deleted:
            raise HTTPException(
                status_code=400,
                detail=f"No API keys found for sandbox {sandbox_id}"
            )

        # Finally remove sandbox endpoint
        redis_client.delete(f"sandbox:{sandbox_id}:endpoint")

        return {"status": "unregistered"}
    except redis.RedisError as e:
        raise HTTPException(status_code=500, detail=f"Redis operation failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.api_route("/api/v1/sandbox/{sandbox_id}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_to_sandbox(
    sandbox_id: str,
    path: str,
    request: Request,
    authenticated_sandbox_id: str = Depends(get_sandbox_id)
):
    """Proxy authenticated requests to the appropriate sandbox."""
    # Verify sandbox ID matches the authenticated one
    if sandbox_id != authenticated_sandbox_id:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Not authorized for this sandbox"
        )
    
    # Get sandbox endpoint
    endpoint = redis_client.get(f"sandbox:{sandbox_id}:endpoint")
    if not endpoint:
        raise HTTPException(status_code=404, detail="Sandbox not found")
    
    # Forward request to sandbox
    sandbox_url = endpoint.decode()
    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
                method=request.method,
                url=f"{sandbox_url}/{path}",
                headers={k: v for k, v in request.headers.items() if k.lower() != "host"},
                cookies=request.cookies,
                content=await request.body(),
                follow_redirects=True
            )
            
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers)
            )
        except httpx.RequestError as exc:
            raise HTTPException(status_code=503, detail=str(exc))