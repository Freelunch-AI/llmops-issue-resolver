import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Dict

# Constants
LOG_DIR = Path(__file__).parent
LOG_FORMAT = ('%(asctime)s - %(process)d - %(threadName)s - '
             '%(name)s - %(levelname)s - %(message)s')
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
MAX_BYTES = 10 * 1024 * 1024  # 10MB
BACKUP_COUNT = 5

# Default log level based on environment
DEFAULT_LOG_LEVEL = logging.DEBUG if os.getenv('SANDBOX_ENV') == 'development' else logging.INFO

# Component log files
LOG_FILES = {
    'sdk': LOG_DIR / 'sdk.log',
    'infra': LOG_DIR / 'infrastructure.log',
    'sandbox': LOG_DIR / 'sandbox.log'
}

# Ensure log directory exists
CUSTOM_LOG_DIR = os.getenv('SANDBOX_LOG_DIR')
if CUSTOM_LOG_DIR:
    LOG_DIR = Path(CUSTOM_LOG_DIR)

os.makedirs(LOG_DIR, exist_ok=True)

def setup_file_handler(log_file: Path, log_format: str) -> logging.FileHandler:
    """Create and configure a file handler for logging.
    Args:
        log_file (Path): Path to the log file
        log_format (str): Format string for log messages

    Returns:
        logging.FileHandler: Configured file handler
    """
    handler = RotatingFileHandler(
        log_file,
        maxBytes=MAX_BYTES,
        backupCount=BACKUP_COUNT
    )
    handler.setFormatter(logging.Formatter(log_format, DATE_FORMAT))
    return handler

def configure_logger(name: str, log_file: Path, level: int = logging.INFO) -> logging.Logger:
    """Configure a logger with file handler.

    Args:
        name (str): Name of the logger
        log_file (Path): Path to the log file
        level (int): Logging level

    Returns:
        logging.Logger: Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Add file handler
    handler = setup_file_handler(log_file, LOG_FORMAT)
    logger.addHandler(handler)

    # Add console handler for development
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
    logger.addHandler(console_handler)

    return logger

# Configure component loggers
sdk_logger = configure_logger('sandbox_toolkit.sdk', LOG_FILES['sdk'])
infra_logger = configure_logger('sandbox_toolkit.infra', LOG_FILES['infra'])
sandbox_logger = configure_logger('sandbox_toolkit.sandbox', LOG_FILES['sandbox'])

def get_logger(component: str) -> logging.Logger:
    """Get a configured logger for a specific component.

    Args:
        component (str): Component name ('sdk', 'infra', or 'sandbox')

    Returns:
        logging.Logger: Configured logger for the component

    Raises:
        ValueError: If component is not recognized
    """
    loggers = {
        'sdk': sdk_logger,
        'infra': infra_logger,
        'sandbox': sandbox_logger
    }

    if component not in loggers:
        raise ValueError(f"Unknown component: {component}. Valid components are: {list(loggers.keys())}")

    return loggers[component]

def set_log_level(component: str, level: int) -> None:
    """Set the logging level for a specific component.

    Args:
        component (str): Component name ('sdk', 'infra', or 'sandbox')
        level (int): Logging level (e.g., logging.DEBUG, logging.INFO)
    """
    logger = get_logger(component)
    logger.setLevel(level)


def enable_debug_mode() -> None:
    """Enable debug mode for all components."""
    for component in ['sdk', 'infra', 'sandbox']:
        set_log_level(component, logging.DEBUG)
def log_error(logger: logging.Logger, error: Exception, context: Dict = None) -> None:
    """Standardized error logging with context.

    Args:
        logger (logging.Logger): Logger instance
        error (Exception): The error to log
        context (Dict, optional): Additional context information
    """
    # Format the error message with stack trace
    import traceback
    stack_trace = ''.join(traceback.format_tb(error.__traceback__))
    
    error_msg = f"Error: {str(error)}\nStack Trace:\n{stack_trace}"
    if context:
        error_msg += f" | Context: {context}"


def sanitize_log_message(message: str) -> str:
    """Sanitize log messages to prevent log injection.

    Args:
        message (str): Raw log message

    Returns:
        str: Sanitized log message
    """
    # Remove control characters and normalize whitespace
    sanitized = ' '.join(message.split())
    # Escape any remaining special characters
    return sanitized.encode('unicode_escape').decode()


def log_operation(logger: logging.Logger, operation: str, status: str, details: Dict = None) -> None:
    """Standardized operation logging.

    Args:
        logger (logging.Logger): Logger instance
        operation (str): Name of the operation
        status (str): Status of the operation (e.g., 'started', 'completed', 'failed')
        details (Dict, optional): Additional operation details
    """
    msg = f"Operation: {operation} | Status: {status}"
    if details:
        msg += f" | Details: {details}"