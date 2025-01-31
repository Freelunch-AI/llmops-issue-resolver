import logging
import sys
from typing import Optional

# Store initialized loggers to prevent duplicate configuration
_loggers = {}

def get_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    """
    Get or create a logger with the specified name and configuration.
    
    Args:
        name: The name of the logger
        level: Optional logging level (defaults to INFO if not specified)
    
    Returns:
        logging.Logger: Configured logger instance
    """
    if name in _loggers:
        return _loggers[name]

    logger = logging.getLogger(name)
    
    # Set default level if not specified
    if level is None:
        level = logging.INFO
    logger.setLevel(level)

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Create and configure stream handler
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    
    # Only add handler if logger doesn't already have handlers
    if not logger.handlers:
        logger.addHandler(stream_handler)

    # Prevent propagation to root logger
    logger.propagate = False
    
    # Store logger in cache
    _loggers[name] = logger
    
    return logger