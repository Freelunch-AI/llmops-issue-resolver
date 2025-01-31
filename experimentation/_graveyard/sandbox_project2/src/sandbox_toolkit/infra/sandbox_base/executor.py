import logging
import importlib
from typing import Dict, List, Callable, Any
from sandbox_toolkit.infra.sandbox_base.tools.filesystem_tools.read_file import read_file
from sandbox_toolkit.infra.sandbox_base.tools.filesystem_tools.create_file import create_file
from sandbox_toolkit.infra.sandbox_base.tools.filesystem_tools.delete_file import delete_file
from sandbox_toolkit.infra.sandbox_base.tools.filesystem_tools.append_to_file import append_to_file
from sandbox_toolkit.infra.sandbox_base.tools.filesystem_tools.overwrite_file import overwrite_file
from sandbox_toolkit.infra.sandbox_base.tools.filesystem_tools.edit_file_line_range import edit_file_line_range
from sandbox_toolkit.infra.sandbox_base.tools.filesystem_tools.move_file import move_file
from sandbox_toolkit.infra.sandbox_base.tools.filesystem_tools.copy_file import copy_file
from sandbox_toolkit.infra.sandbox_base.tools.filesystem_tools.list_directory import list_directory
from sandbox_toolkit.infra.sandbox_base.tools.filesystem_tools.create_directory import create_directory
from sandbox_toolkit.infra.sandbox_base.tools.terminal_tools.execute_command import execute_command
from sandbox_toolkit.infra.sandbox_base.tools.terminal_tools.change_directory import change_directory
from sandbox_toolkit.infra.sandbox_base.tools.terminal_tools.get_current_directory import get_current_directory
from sandbox_toolkit.infra.sandbox_base.tools.terminal_tools.uv_add_package import uv_add_package
from sandbox_toolkit.infra.sandbox_base.tools.terminal_tools.uv_remove_package import uv_remove_package
from sandbox_toolkit.infra.sandbox_base.tools.terminal_tools.uv_sync_packages import uv_sync_packages
from sandbox_toolkit.infra.sandbox_base.tools.terminal_tools.uv_run_python_script import uv_run_python_script
from sandbox_toolkit.infra.sandbox_base.tools.terminal_tools.install_system_package import install_system_package
from sandbox_toolkit.infra.sandbox_base.tools.terminal_tools.get_total_available_and_used_compute_resources import get_total_available_and_used_compute_resources
from sandbox_toolkit.infra.sandbox_base.tools.web_tools.scrape_website import scrape_website
from sandbox_toolkit.infra.sandbox_base.tools.web_tools.google_search import google_search
from sandbox_toolkit.infra.sandbox_base.tools.web_tools.get_most_voted_coding_forum_answers_to_similar_problems import get_most_voted_coding_forum_answers_to_similar_problems
from sandbox_toolkit.infra.sandbox_base.tools.database_tools.semantic_search.store_directory_of_files import store_directory_of_files
from sandbox_toolkit.infra.sandbox_base.tools.database_tools.semantic_search.given_a_query_and_dreictory_retrive_relevant_parts_of_files_within_the_directory import given_a_query_and_dreictory_retrive_relevant_parts_of_files_within_the_directory
from sandbox_toolkit.helpers.schema_models.schema import ToolError

logger = logging.getLogger(__name__)

class ActionExecutor:
    def __init__(self):
        self.tools = {
            "read_file": read_file,
            "create_file": create_file,
            "delete_file": delete_file,
            "append_to_file": append_to_file,
            "overwrite_file": overwrite_file,
            "edit_file_line_range": edit_file_line_range,
            "move_file": move_file,
            "copy_file": copy_file,
            "list_directory": list_directory,
            "create_directory": create_directory,
            "execute_command": execute_command,
            "change_directory": change_directory,
            "get_current_directory": get_current_directory,
            "uv_add_package": uv_add_package,
            "uv_remove_package": uv_remove_package,
            "uv_sync_packages": uv_sync_packages,
            "uv_run_python_script": uv_run_python_script,
            "install_system_package": install_system_package,
            "get_total_available_and_used_compute_resources": get_total_available_and_used_compute_resources,
            "scrape_website": scrape_website,
            "google_search": google_search,
            "get_most_voted_coding_forum_answers_to_similar_problems": get_most_voted_coding_forum_answers_to_similar_problems,
            "store_directory_of_files": store_directory_of_files,
            "given_a_query_and_dreictory_retrive_relevant_parts_of_files_within_the_directory": given_a_query_and_dreictory_retrive_relevant_parts_of_files_within_the_directory,
            "execute_query": None, # Placeholder for graph database tools
            "create_node": None, # Placeholder for graph database tools
            "create_relationship": None # Placeholder for graph database tools
            # Add other tools here
        }

    async def execute_actions(self, actions: Dict[str, Dict[str, Any]]) -> List[Any]:
        """Execute a sequence of actions and return results."""
        results = []
        for function_name, action_args in actions.items():
            tool = self.tools.get(function_name)
            if tool:
                try:
                    result = await self._execute_tool(tool, action_args.get("args", {}))
                    results.append(result)
                except Exception as e:
                    error_message = f"Error executing tool '{function_name}': {e}"
                    logger.error(error_message)
                    results.append(ToolError(function_name=function_name, error=error_message)) # Use ToolError exception
            else:
                error_message = f"Tool '{function_name}' not found."
                logger.error(error_message)
                results.append(ToolError(function_name=function_name, error=error_message)) # Use ToolError exception
        return results

    async def _execute_tool(self, tool: Callable, args: Dict[str, Any]) -> Any:
        """Execute a single tool (function) with arguments."""
        return tool(**args)

    def close(self):
        pass # Add any cleanup logic here