from typing import Any, Dict, Optional, Union
from pydantic import ValidationError
from ..logs.logging import logger
from ..exceptions import (
    SandboxError,
    ConfigurationError,
    ExecutionError
)
from ..models import SandboxConfig
from .utils import validate_input, sanitize_output

class Sandbox:
    """Main class for sandbox operations."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None, custom_handlers: Optional[Dict[str, Any]] = None):
        """Initialize sandbox with optional configuration."""
        self.config = SandboxConfig(config) if config else SandboxConfig()
        self.custom_handlers = custom_handlers or {}
        self._resources = {}
        
        # Validate environment on initialization
        self._validate_environment()
        logger.debug("Sandbox initialized with config: %s", self.config)

    def execute(self, operation: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an operation in the sandbox environment."""
        try:
            logger.info("Executing operation: %s", operation)
            validated_data = validate_input(data)
            
            if not self.config.is_operation_allowed(operation):
                raise ValidationError(f"Operation '{operation}' is not allowed")
            
            result = self._process_operation(operation, validated_data)
            sanitized_result = sanitize_output(result)
            
            logger.debug("Operation completed successfully")
            return sanitized_result
            
        except Exception as e:
            logger.error("Error during execution: %s", str(e))
            raise ExecutionError(f"Failed to execute operation: {str(e)}")

    def _process_operation(self, operation: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process the operation with validated data."""
        try:
            # Check for custom handler first
            if operation in self.custom_handlers:
                return self.custom_handlers[operation](data)
            
            # Process built-in operations
            if operation == "analyze":
                return self._analyze_data(data)
            elif operation == "transform":
                return self._transform_data(data)
            elif operation == "validate":
                return self._validate_data(data)
            elif operation == "export":
                return self._export_data(data)
            else:
                raise SandboxError(f"Unknown operation: {operation}")
                
        except Exception as e:
            logger.error("Operation processing failed: %s", str(e))
            raise ExecutionError(f"Operation processing failed: {str(e)}")

    def _analyze_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the input data."""
        logger.debug("Analyzing data")
        analysis_result = {
            "status": "analyzed",
            "metadata": {
                "size": len(str(data)),
                "type": str(type(data)),
                "structure": self._analyze_structure(data)
            },
            "results": data
        }
        
        self._resources["last_analysis"] = analysis_result
        return analysis_result

    def _transform_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform the input data."""
        logger.debug("Transforming data")
        transformed_data = self._apply_transformations(data)
        return {"status": "transformed", "results": transformed_data}

    def _validate_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the input data against defined schemas."""
        logger.debug("Validating data")
        validation_results = {
            "is_valid": True,
            "errors": []
        }
        try:
            self.config.validate_schema(data)
        except ValidationError as e:
            validation_results["is_valid"] = False
            validation_results["errors"] = e.errors()
        return validation_results

    def _export_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Export data with specified format and destination."""
        logger.debug("Exporting data")
        export_format = data.get("format", "json")
        destination = data.get("destination", "memory")
        
        exported_data = self._format_data(data["content"], export_format)
        if destination == "memory":
            self._resources["exported_data"] = exported_data
        return {"status": "exported", "location": destination}

    def _validate_environment(self) -> None:
        """Validate the sandbox environment setup."""
        logger.debug("Validating sandbox environment")
        if not self.config.validate_environment():
            raise ConfigurationError("Invalid sandbox environment configuration")

    def _analyze_structure(self, data: Any) -> Dict[str, Any]:
        """Analyze the structure of input data."""
        if isinstance(data, dict):
            return {"type": "dict", "keys": list(data.keys())}
        elif isinstance(data, list):
            return {"type": "list", "length": len(data)}
        return {"type": str(type(data))}

    def cleanup(self) -> None:
        """Clean up sandbox resources."""
        try:
            # Clean up resources
            logger.info("Cleaning up sandbox resources")
            for resource in self._resources.values():
                if hasattr(resource, 'close'):
                    resource.close()
            self._resources.clear()
            self.config.reset()
        except Exception as e:
            logger.error("Cleanup failed: %s", str(e))
            raise SandboxError(f"Failed to cleanup sandbox: {str(e)}")