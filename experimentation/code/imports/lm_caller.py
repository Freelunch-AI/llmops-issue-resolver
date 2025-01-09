import os
import sys
from contextlib import contextmanager
from typing import Any, List, Optional

import litellm
from dotenv import load_dotenv
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

with temporary_sys_path(os.path.abspath(os.path.join(os.path.dirname(__file__), 
                                                     '..', '..', '..'))):

    from experimentation.code.imports.lm_tracker import lm_caller_extensor
    from experimentation.code.imports.schemas.schema_models import (
        FloatModel,
        LmChatResponse,
        MessageModel,
        StringModel,
        StringOptionalModel,
        ValidateMessagesModel,
        ValidatePydanticModel,
    )

@lm_caller_extensor(cost_threshold=3)
class LmCaller:
    
    def call_lm (self, model_name: str, 
                messages: List[MessageModel], output_format: 
                Optional[Any] = StringModel, 
                temperature: float = 0.75, 
                mode: Optional[str] = None) -> LmChatResponse:
        
        try:
            ValidatePydanticModel(output_format)
            StringModel(items=model_name)
            FloatModel(items=temperature)
            ValidateMessagesModel(messages)
            if mode:
                StringOptionalModel(items=mode)
        except ValidationError as e:
            print(f"Validation error: {e}")
            raise

        dict_messages = [message.dict() for message in messages]

        # need to set api keys as environment variables
        # example:
        # export OPENAI_API_KEY="your-openai-api-key"
        # export ANTHROPIC_API_KEY="your-anthropic-api-key"
        # set environment variables based on .env file
        load_dotenv()

        # need to add support for setting output_format (Pydantic object) 
        # as an input here
        litellm_standard_chat_response = litellm.completion(
            model=model_name,
            messages=dict_messages,
            temperature=temperature #optional
        )

        # LiteLLM OpenAI-compatible 
        # OpenAI native response object has some more fields) 
        # chat response json
        # {
        #     'choices': [
        #         {
        #         'finish_reason': str,     # String: 'stop'
        #         'index': int,             # Integer: 0
        #         'message': {              # Dictionary [str, str]
        #             'role': str,            # String: 'assistant'
        #             'content': str          # String: "default message"
        #         }
        #         }
        #     ],
        #     'created': str,               # String: None
        #     'model': str,                 # String: None
        #     'usage': {                    # Dictionary [str, int]
        #         'prompt_tokens': int,       # Integer
        #         'completion_tokens': int,   # Integer
        #         'total_tokens': int         # Integer
        #     }
        # }

        my_response = LmChatResponse(
            created=litellm_standard_chat_response.created,
            model=litellm_standard_chat_response.model,
            choices=[
                {
                    "index": litellm_standard_chat_response.choices[0].index,
                    "message": {
                        "role": litellm_standard_chat_response.choices[0].message.role,
                        "content": litellm_standard_chat_response.choices[0].
                        message.content,
                        "output_format": output_format
                    },
                    "finish_reason": litellm_standard_chat_response.choices[0].
                    finish_reason
                }
            ],
            usage={
                "prompt_tokens": litellm_standard_chat_response.usage.prompt_tokens,
                "completion_tokens": litellm_standard_chat_response.usage.
                completion_tokens,
                "total_tokens": litellm_standard_chat_response.usage.total_tokens,
            },
        )

        print(my_response)

        return (my_response.choices[0].message.content, my_response)