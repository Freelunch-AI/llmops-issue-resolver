import os
import sys
from contextlib import contextmanager
from typing import List, Type

from pydantic import BaseModel, ValidationError, create_model
from rich import print


@contextmanager
def temporary_sys_path(path):
    """
    A context manager to temporarily add a specified path to the system path.
    This context manager appends the given path to `sys.path` and ensures that 
    the original `sys.path` is restored after the context is exited.
    Args:
        path (str): The path to be temporarily added to `sys.path`.
    Yields:
        None: This context manager does not yield any value.
    Example:
        with temporary_sys_path('/some/path'):
            # Perform operations that require the temporary path
    """
    original_sys_path = sys.path.copy()
    sys.path.append(path)
    try:
        yield
    finally:
        sys.path = original_sys_path

# do some imports 'assuming' that the package is installed
# before: 'from agent import ..."
# now: "from llmops_issue_resolver.agent import ..."
# But why do this? 
#     - Because mypy assumes this notation when importing from modules within a package
#     - Because it makes it cleanar for doing imports within modules that are very deep 
#     and want to import from modules that are near surface of the package directory 
#     tree
# All .py modules need to have this line, but with the more general form of the import 

with temporary_sys_path(os.path.abspath(os.path.join(os.path.dirname(__file__), \
                                                     '..', '..', '..', '..'))):
    from experimentation.code.imports.schemas.schema_models import Tools

def create_tools_use_pydantic_model(tools: Tools) -> Type[BaseModel]:

    try:
        Tools(tools=tools.tools)
    except ValidationError as e:
        print(f"Validation error: {e}")
        raise TypeError("tools list is not valid Tools object")

    args_dict = {}
    fields_ToolsUse = {}
    for i, tool in enumerate(tools.tools):
        # function singautre is a string with the format: "func_name(arg1: type1, arg2: type2) -> return_type"

        func_signature = tool.function_signature
        args_part = func_signature.split('->')[0].strip()
        args_list = args_part[args_part.find('(')+1:args_part.find(')')].split(',')

        for arg in args_list:
            arg_name, arg_type = arg.split(':')
            args_dict[arg_name.strip()] = (eval(arg_type.strip()), ...)
        
        # get function name from function signature
        func_name = func_signature.split('(')[0].strip()

        tool_use_args_model = create_model(f"Arguments_of_{func_name}", **args_dict)

        fields_ToolsUse[func_name] = (tool_use_args_model, ...)

    ToolsUse = create_model("ToolsUse", **fields_ToolsUse)

    return ToolsUse