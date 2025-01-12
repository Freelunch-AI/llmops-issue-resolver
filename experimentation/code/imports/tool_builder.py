import inspect
import os
import sys
from contextlib import contextmanager
from functools import wraps
from typing import Dict, List

from pydantic import ValidationError


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
                                                     '..', '..', '..'))):    
    from experimentation.code.imports.schemas.schema_models import (
        BoolModel,
        StringListModel,
        StringModel,
        Tool,
        Tools,
    )

class ToolBuilder:
    def __init__(self):
        self._tools: Dict[str, Tool] = {'fs': {}, 'terminal': {}, 'web': {}}

    def register_tool(self, name: str, description: str, function_signature: str, 
                      group: str):
        
        try:
            StringModel(items=name)
            StringModel(items=description)
            StringModel(items=function_signature)
            StringModel(items=group)
        except ValidationError as e:
            print(f"Validation error: {e}")
            raise TypeError("Invalid input")

        tool = Tool(name=name, description=description, 
                    function_signature=function_signature)
        self._tools[group][name] = tool
        print(f"Tool registered: {tool}")

    def get_tools(self, names: List[str], tool_groups: bool = False) -> Tools:

        try:
            StringListModel(items=names)
            BoolModel(items=tool_groups)
        except ValidationError as e:
            print(f"Validation error: {e}")
            raise TypeError("Invalid input")
        
        if not tool_groups:
            tools = [self._tools[group][name] for group in self._tools.keys() 
                                for name in names if name in self._tools[group]]
            print(f"Retrieved tools: {tools}")
            return Tools(tools=tools)
        else:
            tools = [tool for tool in self._tools[name].values() 
                                for name in names if name in self._tools]
            print(f"Retrieved tools: {tools}")
            return Tools(tools=tools)

tool_builder = ToolBuilder()

def build_tool(description: str):

    try:
        StringModel(items=description)
    except ValidationError as e:
        print(f"Validation error: {e}")
        raise TypeError("Invalid input")

    def decorator(func):
        sig = inspect.signature(func)
        
        for arg_name, param in sig.parameters.items():

            arg_type = getattr(param.annotation, '__name__', str(param.annotation))
            args = ', '.join([
                f"{arg_name}: {arg_type}" 
            ])

        return_type = (
            getattr(sig.return_annotation, '__name__', str(sig.return_annotation)) 
            if sig.return_annotation != inspect.Signature.empty 
            else 'Any'
        )

        function_signature = f"{func.__name__}({args}) -> {return_type}"
        
        # group should be the name of the python file from where the function is defined
        group = os.path.basename(inspect.getfile(func)).split('.')[0]
        
        print(f"Registering tool: {func.__name__}, Group: {group}, Description: \
              {description}, Signature: {function_signature}")
        tool_builder.register_tool(name=func.__name__, description=description, 
                                   function_signature=function_signature, group=group)


        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        return wrapper
    return decorator

