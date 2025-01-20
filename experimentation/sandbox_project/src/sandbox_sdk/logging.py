import logging
import sys
from typing import Optional

def setup_logging(
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    log_format: Optional[str] = None
) -> None:
    """Configure logging for the sandbox SDK.
    
    Args:
        level: The logging level (default: INFO)
        log_file: Optional file path to write logs to
        log_format: Optional custom log format string
    """
    if log_format is None:
        log_format = (
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    handlers = [logging.StreamHandler(sys.stdout)]
    if log_file:
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=level,
        format=log_format,
        handlers=handlers
    )

logger = logging.getLogger("sandbox_sdk")