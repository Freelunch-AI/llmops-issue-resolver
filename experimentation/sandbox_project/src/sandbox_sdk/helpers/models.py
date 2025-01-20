from typing import Dict, Optional
from pydantic import BaseModel, Field, SecretStr
from datetime import datetime

class AuthenticationConfig(BaseModel):
    """Configuration for authentication settings."""
    public_key: str = Field(description="Public key for asymmetric encryption")
    private_key: Optional[str] = Field(None, description="Private key for asymmetric encryption")
    key_algorithm: str = Field(default="RSA", description="Encryption algorithm used for keys")
    key_size: int = Field(default=2048, description="Size of the encryption keys")

class ApiKeyInfo(BaseModel):
    """Model for API key information."""
    key: SecretStr = Field(..., description="Secret API key")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = Field(None, description="Expiration timestamp for the API key")
    is_active: bool = Field(default=True, description="Whether the API key is active")

class SandboxAuthInfo(BaseModel):
    """Model for storing sandbox authentication information."""
    sandbox_id: str = Field(..., description="Unique identifier for the sandbox")
    api_key: ApiKeyInfo = Field(..., description="API key information")
    auth_token: Optional[str] = Field(None, description="Authentication token if needed")
    endpoint: str = Field(..., description="Sandbox endpoint URL")
    additional_auth_data: Optional[Dict] = Field(default=None, description="Additional authentication data")

    class Config:
        json_schema_extra = {
            "example": {
                "sandbox_id": "sandbox-123",
                "api_key": {
                    "key": "sk_sandbox_123xyz",
                    "created_at": "2024-01-01T00:00:00Z",
                    "expires_at": "2024-12-31T23:59:59Z",
                    "is_active": True
                },
                "endpoint": "http://localhost:8000/api/v1/sandbox/sandbox-123",
                "additional_auth_data": {}
            }
        }