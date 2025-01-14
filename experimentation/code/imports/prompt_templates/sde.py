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
    sys.path.extend(path)
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
        DictOptionalModel,
        Examples,
        Message,
        MessageImage,
        Messages,
        StringModel,
        StringOptionalModel,
        Tools,
        ToolsOptional,
    )

def get_message_image(image: str, instruction: str) -> MessageImage:
    return MessageImage( 
                        role="user", content=[
                            {"type": "text", "text": f"Instruction: {instruction}"},
                            {  
                                "type": "image_url", 
                                "image_url": { 
                                    "url": image
                                } 
                            }
                        ]    
            )
    

def get_message_image_example(image_example: Dict[str, str]) -> MessageImage:
    return MessageImage(
                        role="user", content=[
                            {
                                "type": "text", 
                                "text": f" Instruction: {image_example['instruction']}",
                            },
                            {
                                "type": "image_url", 
                                "image_url": { 
                                    "url": image_example['image']

                                } 
                            },
                            {
                                "type": "text",
                                "text": f"Response: {image_example['response']}"
                            },
                        ]
            )


def prompt_template_default(instruction: str,
                            backstory: str,
                            image: Optional[str] = None,
                            image_format: Optional[Dict[str, str]] = None,
                            tips: Optional[str] = None, 
                            completion_format: Type[BaseModel] = StringModel, 
                            constraints: Optional[str] = None, 
                            completion_format_description: Optional[str] = None,
                            examples: Optional[List[Dict[str, str]]] = None,
                            image_examples: Optional[List[Dict[str, str]]] = None,
                            tools: Optional[Tools] = None) -> Messages:
    
    if tools and not completion_format_description:
        raise ValueError("completion_format_description is required when tools are \
                         provided")
    if image_examples:
        if image_examples and not (image and image_format):
            raise ValueError("image is required when image_examples are provided")
        # validate that the image_examples variable 
        # is a list of dictionaries in which each
        # dictionary must have only "instruction", "image" and "response" keys
        for example in image_examples:
            if not all(key in example for key in ("instruction", "image", "response")):
                raise ValueError("Each example must have 'instruction', 'image' \
                                 and 'response' keys")
    if image_format:
        if image_format and not image:
            raise ValueError("image is required when image_format is provided")
        # validate that the image variable has "payload" and "examples" keys
        if not all(key in image_format for key in ("payload", "examples")):
            raise ValueError("image_format must have 'payload' and 'examples' keys")
    if examples:
        if examples and image_examples:
                raise ValueError("You can't provide both text and image examples")
        # validate that the examples variable is a list of dictionaries in which each 
        # dictionary must have only "instruction" and "response" keys
        for example in examples:
            if not all(key in example for key in ("instruction", "response")):
                raise ValueError("Each example must have 'instruction' and 'response' \
                                 keys")

    try:
        ToolsOptional(tools=tools)
        CompletionFormat(completion_format=completion_format)
        Examples(items=examples)
        Examples(items=image_examples)
        StringModel(items=backstory)
        StringModel(items=instruction)
        StringOptionalModel(items=image)
        StringOptionalModel(items=tips)
        DictOptionalModel(items=image_format)
        StringOptionalModel(items=constraints)
        StringOptionalModel(items=completion_format_description)
    except ValidationError as e:
        print(f"Validation error: {e}")
        raise TypeError

    # create JSONSCHEMA from the completion_format_description pydantic class
    completion_format_dict = completion_format.schema()

    completion_format_json = json.dumps(completion_format_dict, indent=4)

    if image:
        if tools and tips and constraints and completion_format_description \
        and image_examples:

            messages = [
                Message(
                        role="system", 
                        content=f"{backstory}.\nTools you can use: {tools.json()}\n \
                        Usefull Tips to consider when following the \
                        instruction: {tips}\n \
                        Constraints you must follow: {constraints}\n \
                        Your response should obey this format: \
                        {completion_format_json} where \
                        the values of the json object are the types of the keys\n \
                        Description of the format that your response should obey: \
                        {completion_format_description}."
                ),

                get_message_image(image=image, instruction=instruction),

                Message(
                        role="user", content=f"Examples of this instruction \
                        being followed:"
                ),
            ]

            for image_example in image_examples:
                messages.extend([
                    
                    Message(
                        role="user", content=f"{image_example['instruction']}"
                    ),

                    get_message_image_example(image_example=image_example),
                ])

            return messages
        
        if tools and tips and constraints:
            return [
                Message(
                    role="system", 
                    content=f"{backstory}.\nTools you can use: {tools.json()}\n \
                    Useful Tips to consider when following the instruction: {tips}\n \
                    Constraints you must follow: {constraints} \
                    Your response should obey this format: \
                    {completion_format_json} where \
                    the values of the json object are the types of the keys\n \
                    Description of the format that your response should obey: \
                    {completion_format_description}."
                ),

                get_message_image(image=image, instruction=instruction),
            ]

        # <TODO> alter all of the other like this one
        if tips and constraints and image_examples and completion_format_description:

            messages = [
                Message(
                        role="system", 
                        content=f"{backstory}.\n \
                        Usefull Tips to consider when following the instruction: \
                        {tips}\n \
                        Constraints you must follow: {constraints}\n \
                        Your response should obey this format: \
                        {completion_format_json} where \
                        the values of the json object are the types of the keys\n \
                        Description of the format that your response should obey: \
                        {completion_format_description}."
                ),

                get_message_image(image=image, instruction=instruction),

                Message(
                        role="user", content=f"Examples of this instruction \
                        being followed:"
                ),
            ]

            for image_example in image_examples:
                messages.extend([
                    
                    Message(
                        role="user", content=f"{image_example['instruction']}"
                    ),

                   get_message_image_example(image_example=image_example),
                ])

            return messages

        if tools and tips and image_examples:
            messages = [
                Message(
                        role="system", 
                        content=f"{backstory}.\nTools you can use: {tools.json()}\n \
                        Usefull Tips to consider when following the \
                        instruction: {tips} \
                        Your response should obey this format: \
                        {completion_format_json} where \
                        the values of the json object are the types of the keys\n \
                        Description of the format that your response should obey: \
                        {completion_format_description}."
                ),

                get_message_image(image=image, instruction=instruction),

                Message(
                        role="user", content=f"Examples of this instruction \
                        being followed:"
                ),
            ]

            for image_example in image_examples:
                messages.extend([
                    
                    Message(
                        role="user", content=f"{image_example['instruction']}"
                    ),

                   get_message_image_example(image_example=image_example),
                ])

            return messages
 
        # without tips
        if tools and constraints and image_examples:
            messages = [
                Message(
                        role="system", 
                        content=f"{backstory}.\nTools you can use: {tools.json()}\n \
                        Constraints you must follow: {constraints}"
                ),

                get_message_image(image=image, instruction=instruction),

                Message(
                        role="user", content=f"Examples of this instruction \
                        being followed:"
                ),
            ]

            for image_example in image_examples:
                messages.extend([
                    
                    Message(
                        role="user", content=f"{image_example['instruction']}"
                    ),

                    get_message_image_example(image_example=image_example),
                ])

            return messages

        # without compelteion_format_description
        if tips and constraints and image_examples:
            messages = [
                Message(
                        role="system", 
                        content=f"{backstory}.\n \
                        Usefull Tips to consider when following the \
                        instruction: {tips}\n \
                        Constraints you must follow: {constraints}"
                ),

                get_message_image(image=image, instruction=instruction),

                Message(
                        role="user", content=f"Examples of this instruction \
                        being followed:"
                ),
            ]

            for image_example in image_examples:
                messages.extend([
                    
                    Message(
                        role="user", content=f"{image_example['instruction']}"
                    ),

                    get_message_image_example(image_example=image_example),
                ])

            return messages

        # without tips and tools
        if constraints and image_examples and completion_format_description:
            messages = [
                Message(
                        role="system", 
                        content=f"{backstory}.\n \
                        Constraints you must follow: {constraints}\n \
                        Your response should obey this format: \
                        {completion_format_json} where \
                        the values of the json object are the types of the keys\n \
                        Description of the format that your response should obey: \
                        {completion_format_description}."
                ),

                get_message_image(image=image, instruction=instruction),

                Message(
                        role="user", content=f"Examples of this instruction \
                        being followed:"
                ),
            ]

            for image_example in image_examples:
                messages.extend([
                    
                    Message(
                        role="user", content=f"{image_example['instruction']}"
                    ),

                   get_message_image_example(image_example=image_example),
                ])

            return messages

        # without tools and image_examples
        if constraints and tips and completion_format_description:
            messages = [
                Message(
                        role="system", 
                        content=f"{backstory}.\n \
                        Usefull Tips to consider when following the \
                        instruction: {tips}\n \
                        Constraints you must follow: {constraints}\n \
                        Your response should obey this format: \
                        {completion_format_json} where \
                        the values of the json object are the types of the keys\n \
                        Description of the format that your response should obey: \
                        {completion_format_description}."
                ),

                get_message_image(image=image, instruction=instruction),
            ]

            return messages

        # without tools and constraints:
        if tips and image_examples and completion_format_description:
            messages = [
                Message(
                        role="system", 
                        content=f"{backstory}.\n \
                        Usefull Tips to consider when following the \
                        instruction: {tips}\n \
                        Your response should obey this format: \
                        {completion_format_json} where \
                        the values of the json object are the types of the keys\n \
                        Description of the format that your response should obey: \
                        {completion_format_description}."
                ),

                get_message_image(image=image, instruction=instruction),

                Message(
                        role="user", content=f"Examples of this instruction \
                        being followed:"
                ),
            ]

            for image_example in image_examples:
                messages.extend([
                    
                    Message(
                        role="user", content=f"{image_example['instruction']}"
                    ),

                    get_message_image_example(image_example=image_example),
                ])

            return messages
        
        # without tips and constraints
        if tools and image_examples:
            messages = [
                Message(
                        role="system", 
                        content=f"{backstory}.\nTools you can use: {tools.json()}\n \
                        Your response should obey this format: \
                        {completion_format_json} where \
                        the values of the json object are the types of the keys\n \
                        Description of the format that your response should obey: \
                        {completion_format_description}."
                ),

                get_message_image(image=image, instruction=instruction),

                Message(
                        role="user", content=f"Examples of this instruction \
                        being followed:"
                ),
            ]

            for image_example in image_examples:
                messages.extend([
                    
                    Message(
                        role="user", content=f"{image_example['instruction']}"
                    ),

                    get_message_image_example(image_example=image_example),
                ])

            return messages

        # without image_examples and constraints
        if tools and tips:
            messages = [
                Message(
                        role="system", 
                        content=f"{backstory}.\nTools you can use: {tools.json()}\n \
                        Usefull Tips to consider when following the \
                        instruction: {tips}\n \
                        Your response should obey this format: \
                        {completion_format_json} where \
                        the values of the json object are the types of the keys\n \
                        Description of the format that your response should obey: \
                        {completion_format_description}."
                ),

                get_message_image(image=image, instruction=instruction),
            ]

            return messages
        
        if constraints and tools:
            messages = [
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

                get_message_image(image=image, instruction=instruction),
            ]

            return messages


        # without tips and tools and completion_format_description
        if constraints and image_examples:
            messages = [
                Message(
                        role="system", 
                        content=f"{backstory}.\n \
                        Constraints you must follow: {constraints}"
                ),

                get_message_image(image=image, instruction=instruction),

                Message(
                        role="user", content=f"Examples of this instruction \
                        being followed:"
                ),
            ]

            for image_example in image_examples:
                messages.extend([
                    
                    Message(
                        role="user", content=f"{image_example['instruction']}"
                    ),

                    get_message_image_example(image_example=image_example),
                ])

            return messages

        # without tools and image_examples and completion_format_description
        if constraints and tips:
            messages = [
                Message(
                        role="system", 
                        content=f"{backstory}.\n \
                        Usefull Tips to consider when following \
                        the instruction: {tips}\n \
                        Constraints you must follow: {constraints}\n"
                ),

                get_message_image(image=image, instruction=instruction),
            ]

            return messages

        # without constraints and tips and image_examples
        if tools:
            messages = [
                Message(
                        role="system", 
                        content=f"{backstory}.\nTools you can use: {tools.json()}\n \
                        Your response should obey this format: \
                        {completion_format_json} where \
                        the values of the json object are the types of the keys\n \
                        Description of the format that your response should obey: \
                        {completion_format_description}."
                ),

                get_message_image(image=image, instruction=instruction),
            ]

            return messages

        # without tips, image_examples and tools
        if constraints and completion_format_description:
            messages = [
                Message(
                        role="system", 
                        content=f"{backstory}.\n \
                        Constraints you must follow: {constraints}\n \
                        Your response should obey this format: \
                        {completion_format_json} where \
                        the values of the json object are the types of the keys\n \
                        Description of the format that your response should obey: \
                        {completion_format_description}."
                ),

                get_message_image(image=image, instruction=instruction),
            ]

            return messages

        # without constraints, tools and tips
        if image_examples and completion_format_description:
            messages = [
                Message(
                        role="system", 
                        content=f"{backstory}.\n \
                        Your response should obey this format: \
                        {completion_format_json} where \
                        the values of the json object are the types of the keys\n \
                        Description of the format that your response should obey: \
                        {completion_format_description}."
                ),

                get_message_image(image=image, instruction=instruction),

                Message(
                        role="user", content=f"Examples of this instruction \
                        being followed:"
                ),
            ]

            for image_example in image_examples:
                messages.extend([
                    
                    Message(
                        role="user", content=f"{image_example['instruction']}"
                    ),

                    get_message_image_example(image_example=image_example),
                ])

            return messages

        # without constraints, tools and image_examples
        if tips and completion_format_description:
            messages = [
                Message(
                        role="system", 
                        content=f"{backstory}.\n \
                        Usefull Tips to consider when following the \
                        instruction: {tips}\n \
                        Your response should obey this format: \
                        {completion_format_json} where \
                        the values of the json object are the types of the keys\n \
                        Description of the format that your response should obey: \
                        {completion_format_description}."
                ),

                get_message_image(image=image, instruction=instruction),
            ]

            return messages

        # without constraints and tools and completion_format_description
        if tips and image_examples:
            messages = [
                Message(
                        role="system", 
                        content=f"{backstory}.\n \
                        Usefull Tips to consider when following the instruction: {tips}"
                ),

                get_message_image(image=image, instruction=instruction),

                Message(
                        role="user", content=f"Examples of this instruction \
                        being followed:"
                ),
            ]

            for image_example in image_examples:
                messages.extend([
                    
                    Message(
                        role="user", content=f"{image_example['instruction']}"
                    ),

                   get_message_image_example(image_example=image_example),
                ])

            return messages

        if completion_format_description:
            messages = [
                Message(
                        role="system", 
                        content=f"{backstory}.\n \
                        Your response should obey this format: \
                        {completion_format_json} where \
                        the values of the json object are the types of the keys\n \
                        Description of the format that your response should obey: \
                        {completion_format_description}."
                ),

                get_message_image(image=image, instruction=instruction),
            ]

            return messages

        # without constraints, image_examples and completion_format_description
        if tips:
            messages = [
                Message(
                        role="system", 
                        content=f"{backstory}.\n \
                        Usefull Tips to consider when following the instruction: {tips}"
                ),

                get_message_image(image=image, instruction=instruction),
            ]

            return messages

        # without tips, contraints and completion_format_description
        if image_examples:
            messages = [
                Message(
                        role="system", 
                        content=f"{backstory}"
                ),

                get_message_image(image=image, instruction=instruction),

                Message(
                        role="user", content=f"Examples of this instruction \
                        being followed:"
                ),
            ]

            for image_example in image_examples:
                messages.extend([
                    
                    Message(
                        role="user", content=f"{image_example['instruction']}"
                    ),

                    get_message_image_example(image_example=image_example),
                ])

            return messages
            
        # without tips, examples and completion_format_description
        if constraints:
            messages = [
                Message(
                        role="system", 
                        content=f"{backstory}.\n \
                        Constraints you must follow: {constraints}"
                ),

                get_message_image(image=image, instruction=instruction),
            ]

            return messages
        
        else:
            messages = [
                Message(
                        role="system", 
                        content=f"{backstory}"
                ),

                get_message_image(image=image, instruction=instruction),
            ]

            return messages

    else:
        if tools and tips and constraints and examples \
        and completion_format_description:
            return [
                Message(
                        role="system", 
                        content=f"{backstory}.\nTools you can use: {tools.json()}\n \
                        Usefull Tips to consider when following \
                        the instruction: {tips}\n \
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
                    role="system", content=f"Examples of this \
                    instruction being followed: \
                    {str(examples)}"
                )
            ]

        # without examples
        if tools and tips and constraints:
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
        if tips and constraints and examples and completion_format_description:
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
                    role="system", content=f"Examples of this \
                    instruction being followed: \
                    {str(examples)}"
                )
            ]

        
        # without constraints
        if tools and tips and examples:
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
                    role="system", content=f"Examples of this \
                    instruction being followed: \
                    {str(examples)}"
                )
            ]
        
        # without tips
        if tools and constraints and examples:
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
                    role="system", content=f"Examples of this \
                    instruction being followed: \
                    {str(examples)}"
                )
            ]
        
        # without compelteion_format_description
        if tips and constraints and examples:
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
                    role="system", content=f"Examples of this \
                    instruction being followed: \
                    {str(examples)}"
                )
            ]
        
        # without tips and tools
        if constraints and examples and completion_format_description:
            return [
                Message(
                    role="system", 
                    content=f"{backstory}.\nConstraints you \
                    must follow: {constraints}\n \
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
                    role="system", content=f"Examples of this \
                    instruction being followed: \
                    {str(examples)}"
                )
            ]

        # without tools and examples
        if constraints and tips and completion_format_description:
            return [
                Message(
                    role="system", 
                    content=f"{backstory}.\nConstraints you must \
                    follow: {constraints}\n \
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
        if tips and examples and completion_format_description:
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
                    role="system", content=f"Examples of this \
                    instruction being followed: \
                    {str(examples)}"
                )
            ]
        
        # without tips and constraints
        if tools and examples:
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
                    role="system", content=f"Examples of this \
                    instruction being followed: \
                    {str(examples)}"
                )
            ]
        
        # without examples and constraints
        if tools and tips:
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
        
        if constraints and tools:
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
        if constraints and examples:
            return [
                Message(
                    role="system", 
                    content=f"{backstory}.\nConstraints \
                    you must follow: {constraints}" \
                ),

                Message(
                    role="user", content=f"Instruction: {instruction}"
                ),

                Message(
                    role="system", content=f"Examples of this \
                    instruction being followed: \
                    {str(examples)}"
                )
            ]
        
        # without tools and examples and completion_format_description
        if constraints and tips:
            return [
                Message(
                    role="system", 
                    content=f"{backstory}.\nConstraints you \
                    must follow: {constraints}\n \
                    Useful Tips to consider when following the instruction: {tips}"
                ),

                Message(
                    role="user", content=f"Instruction: {instruction}"
                )
            ]

        # without constraints and tips and examples
        if tools:
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
        if constraints and completion_format_description:
            return [
                Message(
                    role="system", 
                    content=f"{backstory}.\nConstraints you must \
                    follow: {constraints}\n \
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
        if examples and completion_format_description:
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
                    role="system", content=f"Examples of this \
                    instruction being followed: \
                    {str(examples)}"
                )
            ]

        # without constraints, tools and examples
        if tips and completion_format_description:
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
        if tips and examples:
            return [
                Message(
                    role="system", 
                    content=f"{backstory}.\nUseful Tips to consider \
                    when following the instruction: {tips}"
                ),

                Message(
                    role="user", content=f"Instruction: {instruction}"
                ),

                Message(
                    role="system", content=f"Examples of this \
                    instruction being followed: \
                    {str(examples)}"
                )
            ]

        if completion_format_description:
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
        if tips:
            return [
                Message(
                    role="system", 
                    content=f"{backstory}.\nUseful Tips to consider \
                    when following the instruction: {tips}"
                ),

                Message(
                    role="user", content=f"Instruction: {instruction}"
                )
            ]

        # without tips, contraints and completion_format_description
        if examples:
            return [
                Message(
                    role="system", 
                    content=f"{backstory}"
                ),

                Message(
                    role="user", content=f"Instruction: {instruction}"
                ),

                Message(
                    role="system", content=f"Examples of this \
                    instruction being followed: \
                    {str(examples)}"
                )
            ]
        
        # without tips, examples and completion_format_description
        if constraints:
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