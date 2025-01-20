import unittest
import logging
import os
from unittest.mock import patch, MagicMock, call
from logging.handlers import RotatingFileHandler
from sandbox_sdk.logs.logging import (
    get_log_level,
    SensitiveDataFormatter,
    SENSITIVE_PATTERNS,
    MAX_BYTES,
    BACKUP_COUNT,
    LOG_DIR
)

class TestLogging(unittest.TestCase):
    def setUp(self):
        # Reset logging configuration before each test
        logging.getLogger().handlers = []
        
    def tearDown(self):
        # Clean up logging configuration after each test
        logging.getLogger().handlers = []

    @patch.dict(os.environ, clear=True)
    def test_get_log_level_production(self):
        os.environ['ENV'] = 'production'
        self.assertEqual(get_log_level(), logging.WARNING)

    @patch.dict(os.environ, clear=True)
    def test_get_log_level_staging(self):
        os.environ['ENV'] = 'staging'
        self.assertEqual(get_log_level(), logging.INFO)

    @patch.dict(os.environ, clear=True)
    def test_get_log_level_development(self):
        os.environ['ENV'] = 'development'
        self.assertEqual(get_log_level(), logging.DEBUG)

    @patch.dict(os.environ, clear=True)
    def test_get_log_level_default(self):
        # No ENV set should default to INFO
        self.assertEqual(get_log_level(), logging.INFO)

    def test_sensitive_data_formatter_init(self):
        formatter = SensitiveDataFormatter('%(message)s')
        self.assertIsInstance(formatter, logging.Formatter)

    def test_sensitive_data_masking(self):
        formatter = SensitiveDataFormatter()
        test_cases = [
            ('password="secret123"', 'password="***"'),
            ('api_key: "abcd1234"', 'api_key: "***"'),
            ('secret = "mysecret"', 'secret = "***"'),
            ('token:"bearer123"', 'token:"***"'),
            ('private_key = "key123"', 'private_key = "***"'),
        ]
        
        for input_text, expected_output in test_cases:
            masked = formatter.mask_sensitive_data(input_text)
            self.assertIn('***', masked)
            self.assertNotIn('secret123', masked)
            self.assertNotIn('abcd1234', masked)
            self.assertNotIn('mysecret', masked)
            self.assertNotIn('bearer123', masked)
            self.assertNotIn('key123', masked)

    def test_sensitive_data_case_insensitive(self):
        formatter = SensitiveDataFormatter()
        input_text = 'PASSWORD="secret123" Api_Key="key456"'
        masked = formatter.mask_sensitive_data(input_text)
        self.assertIn('***', masked)
        self.assertNotIn('secret123', masked)
        self.assertNotIn('key456', masked)

    @patch('os.makedirs')
    @patch('logging.getLogger')
    def test_logger_configuration(self, mock_get_logger, mock_makedirs):
        from sandbox_sdk.logs import logging as logging_module
        
        # Verify log directory creation
        mock_makedirs.assert_called_once_with(LOG_DIR, exist_ok=True)
        
        # Get the root logger
        root_logger = logging.getLogger()
        
        # Verify handlers
        handlers = root_logger.handlers
        self.assertTrue(any(isinstance(h, RotatingFileHandler) for h in handlers))
        self.assertTrue(any(isinstance(h, logging.StreamHandler) for h in handlers))

    def test_rotating_file_handler_config(self):
        from sandbox_sdk.logs import logging as logging_module
        
        # Find the RotatingFileHandler
        handler = next(h for h in logging.getLogger().handlers 
                      if isinstance(h, RotatingFileHandler))
        
        # Verify configuration
        self.assertEqual(handler.maxBytes, MAX_BYTES)
        self.assertEqual(handler.backupCount, BACKUP_COUNT)
        self.assertEqual(handler.baseFilename, os.path.join(LOG_DIR, 'app.log'))

    def test_log_formatting(self):
        formatter = SensitiveDataFormatter()
        record = logging.LogRecord(
            name='test',
            level=logging.INFO,
            pathname='test.py',
            lineno=1,
            msg='Test message with password="secret123"',
            args=(),
            exc_info=None
        )
        
        formatted = formatter.format(record)
        self.assertIn('[INFO]', formatted)
        self.assertIn('Test message', formatted)
        self.assertIn('***', formatted)
        self.assertNotIn('secret123', formatted)

if __name__ == '__main__':
    unittest.main()