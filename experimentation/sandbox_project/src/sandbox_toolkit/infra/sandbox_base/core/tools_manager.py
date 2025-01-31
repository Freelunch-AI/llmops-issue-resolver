import inspect
import json
import logging
from pathlib import Path
from typing import Any, Dict, List

from logs.logging import logger
from schema_models.internal_schemas import SandboxTools


def _generate_json_schema(func: callable) -> Dict[str, Any]:
    """Generates a JSON schema for a given function."""
    signature = inspect.signature(func)
    properties = {}
    required = []
    for name, param in signature.parameters.items():
        properties[name] = {
            "type": "string",
            "description": f"Parameter '{name}' of type '{param.annotation}'"
        }
        if param.default == inspect.Parameter.empty:
            required.append(name)
    
    schema = {
        "type": "object",
        "properties": properties,
        "required": required
    }
    return schema

async def get_tools() -> SandboxTools:
    logger.info("Getting sandbox tools...")
    logger.debug("Inputs: None")
    
    tools_dir = Path("src/sandbox_toolkit/infra/sandbox_base/tools/")
    tools = []
    for file_path in tools_dir.glob("*.py"):
        module_name = file_path.stem
        module = __import__(f"sandbox_toolkit.infra.sandbox_base.tools.{module_name}", fromlist=[""])
        for name, obj in inspect.getmembers(module):
            if inspect.isfunction(obj) and not name.startswith("_"):
                schema = _generate_json_schema(obj)
                tools.append({
                    "name": name,
                    "description": obj.__doc__.strip() if obj.__doc__ else "No description provided",
                    "inputSchema": schema
                })
    
    logger.info("Sandbox tools retrieved successfully.")
    logger.debug(f"Outputs: {tools}")
    
    return SandboxTools(tools=tools)
