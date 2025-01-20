from datetime import datetime
from typing import Optional, Pattern, Set
import re
from pydantic import BaseModel, SecretStr, validator

# Patterns
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

class ProxyConfig(BaseModel):
    """Configuration for request proxying."""
    max_request_size: int = 10 * 1024 * 1024  # 10MB
    connect_timeout: float = 5.0
    read_timeout: float = 30.0
    total_timeout: float = 60.0  # Total request timeout
    max_retries: int = 3
    initial_backoff: float = 0.1  # Initial backoff in seconds
    max_backoff: float = 10.0     # Maximum backoff in seconds
    backoff_factor: float = 2.0   # Multiplicative factor for backoff
    max_connections: int = 100    # Maximum number of concurrent connections
    allowed_url_patterns: list[str] = []  # List of allowed URL patterns
    chunk_size: int = 8192  # Chunk size for streaming
    filtered_headers: Set[str] = {
        "host",
        "connection",
        "keep-alive",
        "proxy-authenticate",
        "proxy-authorization",
        "te",
        "trailers",
        "transfer-encoding",
        "upgrade"
    }