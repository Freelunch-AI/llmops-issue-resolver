import json
import os
import sys
from contextlib import contextmanager
from typing import Optional

from pydantic import ValidationError
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
    from experimentation.code.imports.schemas.schema_models import (
        CompletionFormatDescriptionDynamic,
        Message,
        StringModel,
        Tools,
        ToolsOptional,
    )

TOOLS_USE_DESCRIPTION = "Here is how you will write your tools use output: ..."
MARKDOWN_DESCRIPTION = "You will write your output as a mardown file ..."

def prompt_template_default(instruction: str, tips: str, 
                           constraints: str, tools: Optional[Tools] = None) -> str:

    try:
        ToolsOptional(tools=tools)
        StringModel(items=instruction)
        StringModel(items=tips)
        StringModel(items=constraints)
    except ValidationError as e:
        print(f"Validation error: {e}")
        raise TypeError
    
    # create JSONSCHEMA from the completion_format_description pydantic class
    completion_format_description_dict = CompletionFormatDescriptionDynamic.schema()
    completion_format_description_json = json.dumps(completion_format_description_dict, 
                                                    indent=4)
    
    print("#########completion_format_description_json", 
          completion_format_description_json)

    if tools is None:
        return [
            Message(
                role="system", 
                content=f"You are a Software Developer Engineer. \
                Usefull Tips to consider when following the instruction: {tips}\n \
                Constraints you must follow: {constraints}\n \
                Description of the format that your response should obey: \
                {completion_format_description_json} where \
                the values of the json object are the types of the keys"
            ),

            Message(
                role="user", content=f"Instruction: {instruction}"
            )
        ]

    else:
        return [
            Message(
                    role="system", 
                    content=f"You are a Software Developer Engineer that \
                    should use one or more tools.\nTools you can use: {tools.json()}\n \
                    Usefull Tips to consider when following the instruction: {tips}\n \
                    Constraints you must follow: {constraints}\n \
                    Description of the format that your response should obey: \
                    {completion_format_description_json} where \
                    the values of the json object are the types of the keys"
            ),

            Message(
                role="user", content=f"Instruction: {instruction}"
            )
        ]