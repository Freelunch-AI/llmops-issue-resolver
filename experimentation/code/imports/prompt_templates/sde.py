import json
import os
import sys
from contextlib import contextmanager
from typing import Dict, List, Optional, Type, Union

from pydantic import BaseModel, ValidationError
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

with temporary_sys_path(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__), 
                                                     '..', '..', '..', '..'))):
    import experimentation.code.imports.schemas.schema_models as schema_models
    from experimentation.code.imports.schemas.schema_models import (
        CompletionFormat,
        Examples,
        Message,
        StringModel,
        StringOptionalModel,
        Tools,
        ToolsOptional,
    )

def prompt_template_default(instruction: str, backstory: str,
                            tips: Optional[str] = None, 
                            completion_format: 
                            Type[BaseModel] = StringModel, 
                            constraints: Optional[str] = None, 
                            completion_format_description: Optional[str] = None,
                            examples: Optional[List[Dict[str, str]]] = None,
                            tools: Optional[Tools] = None) -> str:
    
    if tools and not completion_format_description:
        raise ValueError("completion_format_description is required when tools are \
                         provided")

    try:
        ToolsOptional(tools=tools)
        CompletionFormat(completion_format=completion_format)
        Examples(examples=examples)
        StringModel(items=backstory)
        StringModel(items=instruction)
        StringOptionalModel(items=tips)
        StringOptionalModel(items=constraints)
        StringOptionalModel(items=completion_format_description)
    except ValidationError as e:
        print(f"Validation error: {e}")
        raise TypeError

    # create JSONSCHEMA from the completion_format_description pydantic class
    completion_format_dict = completion_format.schema()

    completion_format_json = json.dumps(completion_format_dict, indent=4)

    if tools and tips and constraints and examples and completion_format_description:
        return [
            Message(
                    role="system", 
                    content=f"{backstory}.\nTools you can use: {tools.json()}\n \
                    Usefull Tips to consider when following the instruction: {tips}\n \
                    Constraints you must follow: {constraints}\n \
                    Your response should obey this format: \
                    {completion_format_json} where \
                    the values of the json object are the types of the keys\n \
                    Description of the format that your response should obey: \
                    {completion_format_description}."
            ),

            Message(
                role="user", content=f"Instruction: {instruction}"
            ),

            Message(
                role="system", content=f"Examples of this instruction being followed: \
                {str(examples)}"
            )
        ]

    # without examples
    elif tools and tips and constraints:
        return [
            Message(
                role="system", 
                content=f"{backstory}.\nTools you can use: {tools.json()}\n \
                Useful Tips to consider when following the instruction: {tips}\n \
                Constraints you must follow: {constraints}\n \
                Your response should obey this format: \
                {completion_format_json} where \
                the values of the json object are the types of the keys\n \
                Description of the format that your response should obey: \
                {completion_format_description}."
            ),

            Message(
                role="user", content=f"Instruction: {instruction}"
            )
        ]
    
    # without tools
    elif tips and constraints and examples and completion_format_description:
        return [
            Message(
                role="system", 
                content=f"{backstory}. \
                Useful Tips to consider when following the instruction: {tips}\n \
                Constraints you must follow: {constraints}. Your response \
                should obey this format: \
                {completion_format_json} where \
                the values of the json object are the types of the keys\n"
            ),

            Message(
                role="user", content=f"Instruction: {instruction}"
            ),

            Message(
                role="system", content=f"Examples of this instruction being followed: \
                {str(examples)}"
            )
        ]

    
    # without constraints
    elif tools and tips and examples:
        return [
            Message(
                role="system", 
                content=f"{backstory}.\nTools you can use: {tools.json()}\n \
                Useful Tips to consider when following the instruction: {tips}\n \
                Your response should obey this format: \
                {completion_format_json} where \
                the values of the json object are the types of the keys\n \
                Description of the format that your response should obey: \
                {completion_format_description}."
            ),

            Message(
                role="user", content=f"Instruction: {instruction}"
            ),

            Message(
                role="system", content=f"Examples of this instruction being followed: \
                {str(examples)}"
            )
        ]
    
    # without tips
    elif tools and constraints and examples:
        return [
            Message(
                role="system", 
                content=f"{backstory}.\nTools you can use: {tools.json()}\n \
                Constraints you must follow: {constraints}\n \
                Your response should obey this format: \
                {completion_format_json} where \
                the values of the json object are the types of the keys\n \
                Description of the format that your response should obey: \
                {completion_format_description}."
            ),

            Message(
                role="user", content=f"Instruction: {instruction}"
            ),

            Message(
                role="system", content=f"Examples of this instruction being followed: \
                {str(examples)}"
            )
        ]
    
    # without compelteion_format_description
    elif tips and constraints and examples:
        return [
            Message(
                role="system", 
                content=f"{backstory}.\n \
                Useful Tips to consider when following the instruction: {tips}\n \
                Constraints you must follow: {constraints}."
            ),

            Message(
                role="user", content=f"Instruction: {instruction}"
            ),

            Message(
                role="system", content=f"Examples of this instruction being followed: \
                {str(examples)}"
            )
        ]
    
    # without tips and tools
    elif constraints and examples and completion_format_description:
        return [
            Message(
                role="system", 
                content=f"{backstory}.\nConstraints you must follow: {constraints}\n \
                Your response should obey this format: \
                {completion_format_json} where \
                the values of the json object are the types of the keys\n \
                Description of the format that your response should obey: \
                {completion_format_description}."
            ),

            Message(
                role="user", content=f"Instruction: {instruction}"
            ),

            Message(
                role="system", content=f"Examples of this instruction being followed: \
                {str(examples)}"
            )
        ]

    # without tools and examples
    elif constraints and tips and completion_format_description:
        return [
            Message(
                role="system", 
                content=f"{backstory}.\nConstraints you must follow: {constraints}\n \
                Useful Tips to consider when following the instruction: {tips}\n \
                Your response should obey this format: \
                {completion_format_json} where \
                the values of the json object are the types of the keys\n \
                Description of the format that your response should obey: \
                {completion_format_description}."
            ),

            Message(
                role="user", content=f"Instruction: {instruction}"
            )
        ]
    
    # without tools and constraints:
    elif tips and examples and completion_format_description:
        return [
            Message(
                role="system", 
                content=f"{backstory}.\nUseful Tips to consider when following the \
                instruction: {tips}\n \
                Your response should obey this format: \
                {completion_format_json} where \
                the values of the json object are the types of the keys\n \
                Description of the format that your response should obey: \
                {completion_format_description}."
            ),

            Message(
                role="user", content=f"Instruction: {instruction}"
            ),

            Message(
                role="system", content=f"Examples of this instruction being followed: \
                {str(examples)}"
            )
        ]
    
    # without tips and constraints
    elif tools and examples:
        return [
            Message(
                role="system", 
                content=f"{backstory}.\nTools you can use: {tools.json()}\n \
                Your response should obey this format: \
                {completion_format_json} where \
                the values of the json object are the types of the keys\n \
                Description of the format that your response should obey: \
                {completion_format_description}."
            ),

            Message(
                role="user", content=f"Instruction: {instruction}"
            ),

            Message(
                role="system", content=f"Examples of this instruction being followed: \
                {str(examples)}"
            )
        ]
    
    # without examples and constraints
    elif tools and tips:
        return [
            Message(
                role="system", 
                content=f"{backstory}.\nTools you can use: {tools.json()}\n \
                Useful Tips to consider when following the instruction: {tips}\n \
                Your response should obey this format: \
                {completion_format_json} where \
                the values of the json object are the types of the keys\n \
                Description of the format that your response should obey: \
                {completion_format_description}."
            ),

            Message(
                role="user", content=f"Instruction: {instruction}"
            )
        ]
    
    elif constraints and tools:
        return [
            Message(
                role="system", 
                content=f"{backstory}.\nTools you can use: {tools.json()}\n \
                Constraints you must follow: {constraints}"
            ),

            Message(
                role="user", content=f"Instruction: {instruction}"
            )
        ]
    
    # without tips and tools and completion_format_description
    elif constraints and examples:
        return [
            Message(
                role="system", 
                content=f"{backstory}.\nConstraints you must follow: {constraints}" \
            ),

            Message(
                role="user", content=f"Instruction: {instruction}"
            ),

            Message(
                role="system", content=f"Examples of this instruction being followed: \
                {str(examples)}"
            )
        ]
    
    # without tools and examples and completion_format_description
    elif constraints and tips:
        return [
            Message(
                role="system", 
                content=f"{backstory}.\nConstraints you must follow: {constraints}\n \
                Useful Tips to consider when following the instruction: {tips}"
            ),

            Message(
                role="user", content=f"Instruction: {instruction}"
            )
        ]

    # without constraints and tips and examples
    elif tools:
        return [
            Message(
                role="system", 
                content=f"{backstory}.\nTools you can use: {tools.json()}\n \
                Your response should obey this format: \
                {completion_format_json} where \
                the values of the json object are the types of the keys\n \
                Description of the format that your response should obey: \
                {completion_format_description}."
            ),

            Message(
                role="user", content=f"Instruction: {instruction}"
            )
        ]
    
    # without tips, examples and tools
    elif constraints and completion_format_description:
        return [
            Message(
                role="system", 
                content=f"{backstory}.\nConstraints you must follow: {constraints}\n \
                Your response should obey this format: \
                {completion_format_json} where \
                the values of the json object are the types of the keys\n \
                Description of the format that your response should obey: \
                {completion_format_description}."
            ),

            Message(
                role="user", content=f"Instruction: {instruction}"
            )
        ]
    
    # without constraints, tools and tips
    elif examples and completion_format_description:
        return [
            Message(
                role="system", 
                content=f"{backstory}. Your response should obey this format: \
                {completion_format_json} where \
                the values of the json object are the types of the keys"
            ),

            Message(
                role="user", content=f"Instruction: {instruction}"
            ),

            Message(
                role="system", content=f"Examples of this instruction being followed: \
                {str(examples)}"
            )
        ]

    # without constraints, tools and examples
    elif tips and completion_format_description:
        return [
            Message(
                role="system", 
                content=f"{backstory}.\nUseful Tips to consider when following the \
                instruction: {tips}\n \
                Your response should obey this format: \
                {completion_format_json} where \
                the values of the json object are the types of the keys\n \
                Description of the format that your response should obey: \
                {completion_format_description}."
            ),

            Message(
                role="user", content=f"Instruction: {instruction}"
            )
        ]
    
    # without constraints and tools and completion_format_description
    elif tips and examples:
        return [
            Message(
                role="system", 
                content=f"{backstory}.\nUseful Tips to consider when following the instruction: {tips}" #noqa
            ),

            Message(
                role="user", content=f"Instruction: {instruction}"
            ),

            Message(
                role="system", content=f"Examples of this instruction being followed: \
                {str(examples)}"
            )
        ]

    elif completion_format_description:
        return [
            Message(
                role="system", 
                content=f"{backstory}.\nYour response should obey this format: \
                {completion_format_json} where \
                the values of the json object are the types of the keys\n \
                Description of the format that your response should obey: \
                {completion_format_description}."
            ),

            Message(
                role="user", content=f"Instruction: {instruction}"
            )
        ]

    # without constraints, examples and completion_format_description
    elif tips:
        return [
            Message(
                role="system", 
                content=f"{backstory}.\nUseful Tips to consider when following the instruction: {tips}" #noqa
            ),

            Message(
                role="user", content=f"Instruction: {instruction}"
            )
        ]

    # without tips, contraints and completion_format_description
    elif examples:
        return [
            Message(
                role="system", 
                content=f"{backstory}"
            ),

            Message(
                role="user", content=f"Instruction: {instruction}"
            ),

            Message(
                role="system", content=f"Examples of this instruction being followed: \
                {str(examples)}"
            )
        ]
    
     # without tips, examples and completion_format_description
    elif constraints:
        return [
            Message(
                role="system", 
                content=f"{backstory}.\nConstraints you must follow: {constraints}"
            ),

            Message(
                role="user", content=f"Instruction: {instruction}"
            )
        ]
    
    else:
        return [
            Message(
                role="system", 
                content=f"{backstory}."
            ),

            Message(
                role="user", content=f"Instruction: {instruction}"
            )
        ]