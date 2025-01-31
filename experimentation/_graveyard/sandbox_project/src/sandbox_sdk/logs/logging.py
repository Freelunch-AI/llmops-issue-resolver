import logging
import os
import re
from logging.handlers import RotatingFileHandler
from typing import Any, Dict

# Constants
LOG_DIR = os.path.dirname(os.path.abspath(__file__))
MAX_BYTES = 10 * 1024 * 1024  # 10MB
BACKUP_COUNT = 5

# Patterns for sensitive data
SENSITIVE_PATTERNS = [
    (r'password["\']?\s*[:=]\s*["\']?[^"\',\s]+["\']?', '***'),
    (r'api[_-]?key["\']?\s*[:=]\s*["\']?[^"\',\s]+["\']?', '***'),
    (r'secret["\']?\s*[:=]\s*["\']?[^"\',\s]+["\']?', '***'),
    (r'token["\']?\s*[:=]\s*["\']?[^"\',\s]+["\']?', '***'),
    (r'private[_-]?key["\']?\s*[:=]\s*["\']?[^"\',\s]+["\']?', '***')
]

class SensitiveDataFormatter(logging.Formatter):
    """Custom formatter that masks sensitive information in log messages."""
    
    def __init__(self, fmt: str = None, datefmt: str = None):
        super().__init__(fmt, datefmt)

    def format(self, record: logging.LogRecord) -> str:
        # Format the message first
        formatted_msg = super().format(record)
        
        # Apply masking to the formatted message
        return self.mask_sensitive_data(formatted_msg)
    
    @staticmethod
    def mask_sensitive_data(text: str) -> str:
        """Mask sensitive data in the given text."""
        masked_text = text
        for pattern, mask in SENSITIVE_PATTERNS:
            masked_text = re.sub(pattern, f'\1{mask}', masked_text, flags=re.IGNORECASE)
        return masked_text

def get_log_level() -> int:
    """Get log level based on environment."""
    env = os.getenv('ENV', 'development').lower()
    log_levels = {
        'production': logging.WARNING,
        'staging': logging.INFO,
        'development': logging.DEBUG
    }
    return log_levels.get(env, logging.INFO)

# Create log directory if it doesn't exist
os.makedirs(LOG_DIR, exist_ok=True)

# Configure logging
log_format = '%(asctime)s [%(levelname)s] [%(process)d] [%(threadName)s] '\
            '%(module)s:%(lineno)d - %(message)s'

formatter = SensitiveDataFormatter(log_format)

# File handler with rotation
file_handler = RotatingFileHandler(
    os.path.join(LOG_DIR, 'app.log'),
    maxBytes=MAX_BYTES,
    backupCount=BACKUP_COUNT
)
file_handler.setFormatter(formatter)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# Configure root logger
root_logger = logging.getLogger()
root_logger.setLevel(get_log_level())
root_logger.addHandler(file_handler)
root_logger.addHandler(console_handler)

# Create module logger
logger = logging.getLogger(__name__)