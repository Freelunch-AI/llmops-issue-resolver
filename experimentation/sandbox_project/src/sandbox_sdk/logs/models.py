from pydantic import BaseModel
from typing import Dict, Any, Optional

class LogConfig(BaseModel):
    """Configuration model for logging setup."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    handlers: Dict[str, Any] = {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "stream": "ext://sys.stdout"
        }
    }
    formatters: Dict[str, Dict[str, str]] = {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    }
    filters: Optional[Dict[str, Any]] = None
    disable_existing_loggers: bool = False
    version: int = 1