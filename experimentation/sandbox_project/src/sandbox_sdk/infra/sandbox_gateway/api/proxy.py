from typing import Optional, Dict, Any
import httpx
from fastapi import Request, Response, HTTPException
import asyncio
from pydantic import HttpUrl
from .models import ProxyConfig
import logging

logger = logging.getLogger(__name__)

class RequestProxy:
    def __init__(self, config: Optional[ProxyConfig] = None):
        self.config = config or ProxyConfig()
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(
                connect=self.config.connect_timeout,
                read=self.config.read_timeout,
                pool=self.config.total_timeout
            ),
            limits=httpx.Limits(
                max_connections=self.config.max_connections
            )
        )

    def _validate_url(self, url: str) -> bool:
        """Validate URL against allowed patterns."""
        if not self.config.allowed_url_patterns:
            return True
        return any(pattern in url for pattern in self.config.allowed_url_patterns)

    def _sanitize_header_value(self, value: str) -> str:
        """Sanitize header values to prevent injection."""
        return value.replace('\n', '').replace('\r', '')

    async def forward_request(
        self,
        target_url: str,
        request: Request,
        additional_headers: Optional[Dict[str, str]] = None
    ) -> Response:
        """Forward a request to target URL with proper handling."""
        # Validate target URL
        if not self._validate_url(target_url):
            raise HTTPException(
                status_code=403,
                detail="Target URL not allowed"
            )

        # Validate request size
        content_length = request.headers.get("content-length", 0)
        if int(content_length) > self.config.max_request_size:
            raise HTTPException(
                status_code=413,
                detail="Request too large"
            )

        # Prepare headers
        headers = {
            k: self._sanitize_header_value(v) for k, v in request.headers.items()
            if k.lower() not in self.config.filtered_headers
        }
        if additional_headers:
            headers.update({k: self._sanitize_header_value(v) for k, v in additional_headers.items()})

        # Forward request with retries
        for attempt in range(self.config.max_retries):
            try:
                # Calculate exponential backoff delay
                if attempt > 0:
                    backoff = min(
                        self.config.initial_backoff * (self.config.backoff_factor ** (attempt - 1)),
                        self.config.max_backoff
                    )
                    await asyncio.sleep(backoff)

                # Stream the request body
                async def request_stream():
                    async for chunk in request.stream():
                        yield chunk

                response = await self.client.request(
                    method=request.method,
                    url=target_url,
                    content=request_stream(),
                    headers=headers,
                    follow_redirects=True,
                    timeout=self.config.total_timeout
                )

                # Handle different response status codes
                if response.status_code >= 400:
                    if response.status_code >= 500:
                        # Server errors might be retryable
                        if attempt == self.config.max_retries - 1:
                            return await self._stream_response(response)
                        continue
                    else:
                        # Client errors should not be retried
                        return await self._stream_response(response)

                return await self._stream_response(response)

            except httpx.TimeoutException:
                logger.warning(f"Request timeout (attempt {attempt + 1}/{self.config.max_retries})")
                if attempt == self.config.max_retries - 1:
                    raise HTTPException(
                        status_code=504,
                        detail="Target service timeout"
                    )

            except httpx.ConnectError as e:
                logger.warning(f"Connection error (attempt {attempt + 1}/{self.config.max_retries}): {e}")
                if attempt == self.config.max_retries - 1:
                    raise HTTPException(
                        status_code=503,
                        detail="Service temporarily unavailable"
                    )

            except httpx.RequestError as e:
                logger.error(f"Proxy request failed: {e}")
                raise HTTPException(
                    status_code=502,
                    detail="Bad gateway"
                )

    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
        return None

    async def _stream_response(self, response: httpx.Response) -> Response:
        """Stream the response body."""
        async def response_stream():
            async for chunk in response.aiter_bytes(chunk_size=self.config.chunk_size):
                yield chunk

        return Response(
            content=response_stream(),
            status_code=response.status_code,
            headers=dict(response.headers)
        )