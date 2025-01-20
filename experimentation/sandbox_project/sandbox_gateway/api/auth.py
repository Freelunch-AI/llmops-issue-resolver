from datetime import datetime, timedelta
import secrets
from typing import Optional, Tuple, Pattern
import redis
import re
from pydantic import BaseModel, SecretStr, validator
from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN, HTTP_429_TOO_MANY_REQUESTS

SANDBOX_ID_PATTERN: Pattern = re.compile(r'^[a-zA-Z0-9-_]{4,32}$')

class APIKey(BaseModel):
    """API key with metadata."""
    key: SecretStr
    sandbox_id: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    
    @validator('sandbox_id')
    def validate_sandbox_id(cls, v):
        if not SANDBOX_ID_PATTERN.match(v):
            raise ValueError('Invalid sandbox ID format')
        return v

class AuthManager:
    def __init__(
        self,
        redis_client: redis.Redis,
        key_ttl: int = 3600 * 24,  # 24 hours
        rate_limit_attempts: int = 100,  # requests per window
        rate_limit_window: int = 3600  # 1 hour window
    ):
        self.redis = redis_client
        self.key_ttl = key_ttl
        self.api_key_header = APIKeyHeader(name="X-API-Key")
        self.rate_limit_attempts = rate_limit_attempts
        self.rate_limit_window = rate_limit_window
        
        # Lua script for atomic key validation and TTL extension
        self.validate_script = self.redis.register_script('''
            local key = KEYS[1]
            local ttl = ARGV[1]
            
            local sandbox_id = redis.call('GET', key)
            if not sandbox_id then
                return nil
            end
            
            redis.call('EXPIRE', key, ttl)
            return sandbox_id
        ''')

    def generate_api_key(self, sandbox_id: str) -> APIKey:
        """Generate a new API key for a sandbox."""
        if not SANDBOX_ID_PATTERN.match(sandbox_id):
            raise ValueError('Invalid sandbox ID format')
            
        key = secrets.token_urlsafe(32)
        created_at = datetime.utcnow()
        expires_at = created_at + timedelta(seconds=self.key_ttl)

        api_key = APIKey(
            key=key,
            sandbox_id=sandbox_id,
            created_at=created_at,
            expires_at=expires_at
        )

        with self.redis.pipeline() as pipe:
            try:
                pipe.watch(f"apikey:{key}")
                pipe.multi()
                pipe.setex(
                    f"apikey:{key}",
                    self.key_ttl,
                    sandbox_id
                )
                pipe.execute()
            except redis.WatchError:
                raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Key generation failed")

        return api_key

    async def validate_api_key(
        self,
        api_key: str = Security(APIKeyHeader(name="X-API-Key"))
    ) -> str:
        """Validate API key and return sandbox ID."""
        
        # Check rate limit
        rate_limit_key = f"ratelimit:auth:{api_key}"
        current_count = self.redis.incr(rate_limit_key)
        
        # Set expiry on first request
        if current_count == 1:
            self.redis.expire(rate_limit_key, self.rate_limit_window)
        
        if current_count > self.rate_limit_attempts:
            raise HTTPException(
                status_code=HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded"
            )
        
        # Atomic validation and TTL extension using Lua script
        key = f"apikey:{api_key}"
        sandbox_id = self.validate_script(keys=[key], args=[self.key_ttl])
        
        if not sandbox_id:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail="Invalid or expired API key"
            )
        
        return sandbox_id.decode()

    def revoke_api_key(self, api_key: str):
        """Revoke an API key."""
        self.redis.delete(f"apikey:{api_key}")

    def rotate_api_key(self, old_key: str) -> Optional[APIKey]:
        """Rotate an API key while maintaining the same sandbox access."""
        old_key_name = f"apikey:{old_key}"

        with self.redis.pipeline() as pipe:
            try:
                # Watch the old key to ensure atomic operation
                pipe.watch(old_key_name)
                
                # Get sandbox ID from old key
                sandbox_id = pipe.get(old_key_name)
                if not sandbox_id:
                    return None
                
                sandbox_id = sandbox_id.decode()
                
                # Start transaction
                pipe.multi()
                
                # Generate new key and store it
                new_api_key = self.generate_api_key(sandbox_id)
                
                # Delete old key in the same transaction
                pipe.delete(old_key_name)
                pipe.execute()
                
                return new_api_key
            except redis.WatchError:
                return None