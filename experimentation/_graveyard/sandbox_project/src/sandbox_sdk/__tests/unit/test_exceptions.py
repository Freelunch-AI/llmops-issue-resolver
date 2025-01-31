import unittest
from sandbox_sdk.helpers.exceptions import (
    SandboxError,
    SandboxNotStartedError,
    SandboxStartError,
    SandboxStopError,
    ActionExecutionError,
    ResourceError,
    DatabaseError,
    ConfigurationError,
    ToolError,
    AuthenticationError,
    SignatureError,
    APIError,
    RequestError,
    InvalidResponseError,
)

class TestExceptions(unittest.TestCase):
    def test_sandbox_error_base(self):
        error = SandboxError("Test error message")
        self.assertEqual(str(error), "Test error message")
        self.assertIsInstance(error, Exception)

    def test_sandbox_not_started_error(self):
        error = SandboxNotStartedError("Sandbox not initialized")
        self.assertIsInstance(error, SandboxError)
        self.assertEqual(str(error), "Sandbox not initialized")

    def test_sandbox_start_error(self):
        error = SandboxStartError("Failed to start sandbox")
        self.assertIsInstance(error, SandboxError)
        self.assertEqual(str(error), "Failed to start sandbox")

    def test_sandbox_stop_error(self):
        error = SandboxStopError("Failed to stop sandbox")
        self.assertIsInstance(error, SandboxError)
        self.assertEqual(str(error), "Failed to stop sandbox")

    def test_action_execution_error(self):
        error = ActionExecutionError("Action failed")
        self.assertIsInstance(error, SandboxError)
        self.assertEqual(str(error), "Action failed")

    def test_resource_error(self):
        error = ResourceError("Resource allocation failed")
        self.assertIsInstance(error, SandboxError)
        self.assertEqual(str(error), "Resource allocation failed")

    def test_database_error(self):
        error = DatabaseError("Database operation failed")
        self.assertIsInstance(error, SandboxError)
        self.assertEqual(str(error), "Database operation failed")

    def test_configuration_error(self):
        error = ConfigurationError("Invalid configuration")
        self.assertIsInstance(error, SandboxError)
        self.assertEqual(str(error), "Invalid configuration")

    def test_tool_error(self):
        error = ToolError("Tool operation failed")
        self.assertIsInstance(error, SandboxError)
        self.assertEqual(str(error), "Tool operation failed")

    def test_authentication_error(self):
        error = AuthenticationError("Authentication failed")
        self.assertIsInstance(error, SandboxError)
        self.assertEqual(str(error), "Authentication failed")

    def test_signature_error(self):
        error = SignatureError("Signature verification failed")
        self.assertIsInstance(error, AuthenticationError)
        self.assertIsInstance(error, SandboxError)
        self.assertEqual(str(error), "Signature verification failed")

    def test_api_error_base(self):
        error = APIError("API error occurred")
        self.assertIsInstance(error, SandboxError)
        self.assertEqual(str(error), "API error occurred")

    def test_request_error(self):
        error = RequestError("Request failed")
        self.assertIsInstance(error, APIError)
        self.assertIsInstance(error, SandboxError)
        self.assertEqual(str(error), "Request failed")

    def test_invalid_response_error(self):
        error = InvalidResponseError("Invalid response received")
        self.assertIsInstance(error, APIError)
        self.assertIsInstance(error, SandboxError)
        self.assertEqual(str(error), "Invalid response received")

if __name__ == '__main__':
    unittest.main()