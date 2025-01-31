import logging
import os
import inspect
import re

SENSITIVE_PATTERNS = [
    (r'api[_-]?key["\']?\s*[:=]\s*["\']?[^"\',\s]+["\']?', '***'),
    (r'secret["\']?\s*[:=]\s*["\']?[^"\',\s]+["\']?', '***'),
    (r'token["\']?\s*[:=]\s*["\']?[^"\',\s]+["\']?', '***'),
    (r'private[_-]?key["\']?\s*[:=]\s*["\']?[^"\',\s]+["\']?', '***')
]

LOG_DIR = os.path.join(os.path.dirname(__file__), 'logs')

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

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

def find_project_root(start_path, target_dir='logs'):
    """Find the first upward directory that contains the target_dir."""
    current_dir = os.path.abspath(start_path)
    while True:
        if os.path.isdir(os.path.join(current_dir, target_dir)):
            return current_dir
        parent_dir = os.path.dirname(current_dir)
        if parent_dir == current_dir:
            return start_path  # Reached the filesystem root
        current_dir = parent_dir

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Get the name and path of the file that called the logger
    caller = inspect.stack()[1].filename
    caller_path = os.path.abspath(caller)
    
    # Determine the project root by finding the first directory upwards that contains a 'logs' folder
    project_root = find_project_root(os.path.dirname(caller_path), target_dir='logs')
    relative_path = os.path.relpath(caller_path, project_root)
    
    # Construct the full log file path, mimicking directory structure
    log_file = os.path.join(LOG_DIR, relative_path) # LOG_DIR = 'logs'
    log_file = os.path.splitext(log_file)[0] + '.log' # Replace the file extension with .log
    
    # Ensure the log directory exists
    log_file_dir = os.path.dirname(log_file)
    if not os.path.exists(log_file_dir):
        os.makedirs(log_file_dir)

    handler = logging.FileHandler(log_file)
    handler.setFormatter(SensitiveDataFormatter('%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'))
    logger.addHandler(handler)

    return logger

logger = setup_logging()
