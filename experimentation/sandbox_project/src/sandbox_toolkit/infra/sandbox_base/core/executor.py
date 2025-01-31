import importlib
import inspect
import logging
import os
import time
from pathlib import Path
from typing import Any, Callable, Dict, List

from logs.logging import logger

from core.stats_manager import stats_manager


class ActionExecutor:
    def __init__(self):
        self.tools = self._load_tools()

    def _load_tools(self):
        tools = {}
        tools_dir = Path("src/sandbox_toolkit/infra/sandbox_base/tools/")
        for file_path in tools_dir.glob("*.py"):
            module_name = file_path.stem
            module = __import__(f"sandbox_toolkit.infra.sandbox_base.tools.{module_name}", fromlist=[""])
            for name, obj in inspect.getmembers(module):
                if inspect.isfunction(obj) and not name.startswith("_"):
                    tools[name] = obj
        return tools

    def _get_current_files(self):
        files = {}
        for filename in os.listdir("."):
            try:
                file_path = os.path.join(".", filename)
                last_modified = os.path.getmtime(file_path)
                with open(filename, "r") as f:
                    files[filename] = (f.read(), last_modified)
            except Exception:
                files[filename] = None
        return files

    async def _execute_tool(self, tool, args):
        """Execute a tool and return the result."""
        try:
            return tool(**args)
        except Exception as e:
            logger.error(f"Error executing tool {tool.__name__}: {e}")
            raise

    async def execute_actions(self, actions: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Execute a sequence of actions and return results."""
        logger.info(f"Executing actions: {actions}")
        import asyncio
        
        async def execute_single_action(function_name, function_details):
            tool = self.tools.get(function_name)
            if tool:
                start_time = time.time()
                files_before = self._get_current_files()
                try:
                    result = await self._execute_tool(tool, function_details.get("args", {}))
                    stats_manager.increment_successful_actions()
                    end_time = time.time()
                    latency = end_time - start_time
                    files_after = self._get_current_files()
                    created_or_modified_files = []
                    for filename in files_after:
                        if filename not in files_before:
                            created_or_modified_files.append(filename)
                        elif files_before[filename] is not None and files_after[filename] is not None and files_after[filename][1] != files_before[filename][1]:
                             created_or_modified_files.append(filename)
                    return {
                        "latency": latency,
                        "created_or_modified_file": created_or_modified_files,
                        "result": result
                    }
                except Exception as e:
                    error_message = f"Error executing tool '{function_name}': {e}"
                    logger.error(error_message)
                    stats_manager.increment_failed_actions()
                    return {
                        "latency": 0,
                        "created_or_modified_file": [],
                        "error": error_message
                    }
            else:
                error_message = f"Tool '{function_name}' not found."
                logger.error(error_message)
                stats_manager.increment_failed_actions()
                return {
                    "terminal_output": "",
                    "latency": 0,
                    "created_or_modified_file": [],
                    "error": error_message
                }

        tasks = [execute_single_action(function_name, function_details) for function_name, function_details in actions.items()]
        results = await asyncio.gather(*tasks)
        logger.info(f"Finished executing actions, results: {results}")
        return dict(zip(actions.keys(), results))
