import asyncio
import logging
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod
import tenacity

logger = logging.getLogger(__name__)

class DatabaseError(Exception):
    """Base class for database errors."""
    pass

class DatabaseConnectionError(DatabaseError):
    """Raised when database connection fails."""
    pass

class DatabaseInitializationError(DatabaseError):
    """Raised when database initialization fails."""
    pass

class BaseDatabase(ABC):
    def __init__(
        self,
        host: str,
        port: int,
        credentials: Dict[str, str],
        max_retries: int = 5,
        retry_delay: float = 1.0
    ):
        self.host = host
        self.port = port
        self.credentials = credentials
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._client = None

    @abstractmethod
    async def connect(self) -> None:
        """Establish connection to database."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Close database connection."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if database is healthy."""
        pass

    @abstractmethod
    async def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize database with configuration."""
        pass

    async def ensure_connected(self) -> None:
        """Ensure database is connected with retries."""
        retry = tenacity.AsyncRetrying(
            stop=tenacity.stop_after_attempt(self.max_retries),
            wait=tenacity.wait_exponential(multiplier=self.retry_delay),
            retry=tenacity.retry_if_exception_type(DatabaseConnectionError),
            before_sleep=lambda retry_state: logger.warning(
                f"Connection attempt {retry_state.attempt_number} failed, retrying..."
            )
        )

        try:
            await retry(self.connect)
        except tenacity.RetryError as e:
            raise DatabaseConnectionError(
                f"Failed to connect after {self.max_retries} attempts"
            ) from e

    async def ensure_healthy(self, timeout: float = 30.0) -> None:
        """Wait for database to be healthy with timeout."""
        start_time = asyncio.get_event_loop().time()
        
        while True:
            try:
                if await self.health_check():
                    return
            except Exception as e:
                logger.warning(f"Health check failed: {e}")

            if asyncio.get_event_loop().time() - start_time > timeout:
                raise DatabaseError(f"Database not healthy after {timeout} seconds")

            await asyncio.sleep(self.retry_delay)

    async def safe_initialize(self, config: Dict[str, Any]) -> None:
        """Safely initialize database with retries."""
        try:
            await self.ensure_connected()
            await self.ensure_healthy()
            await self.initialize(config)
        except Exception as e:
            await self.disconnect()
            raise DatabaseInitializationError(
                f"Failed to initialize database: {str(e)}"
            ) from e

    async def __aenter__(self):
        await self.ensure_connected()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()