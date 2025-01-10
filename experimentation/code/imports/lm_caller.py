import os
import sys
from contextlib import contextmanager
from typing import List, Type

import litellm
from dotenv import load_dotenv
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

with temporary_sys_path(os.path.abspath(os.path.join(os.path.dirname(__file__), 
                                                     '..', '..', '..'))):

    from experimentation.code.imports.lm_tracker import lm_caller_extensor
    from experimentation.code.imports.schemas.schema_models import (
        FloatModel,
        LmChatResponse,
        LmChatResponse_Choice,
        LmChatResponse_Message,
        LmChatResponse_Usage,
        LmChatResponse_Usage_CompletionTokensDetails,
        LmChatResponse_Usage_PromptTokensDetails,
        Message,
        StringModel,
        ValidateMessagesModel,
        ValidatePydanticModel,
    )

@lm_caller_extensor(cost_threshold=3)
class LmCaller:
    
    def call_lm (self, model_name: str,
                messages: List[Message], completion_format: 
                Type[BaseModel] = StringModel, 
                temperature: float = 0.75, 
                mode: str = "single") -> LmChatResponse:
        
        try:
            ValidatePydanticModel(completion_format)
            StringModel(items=model_name)
            FloatModel(items=temperature)
            ValidateMessagesModel(messages)
            StringModel(items=mode)
        except ValidationError as e:
            print(f"Validation error: {e}")
            raise TypeError

        dict_messages = [message.dict() for message in messages]

        # need to set api keys as environment variables
        # example:
        # export OPENAI_API_KEY="your-openai-api-key"
        # export ANTHROPIC_API_KEY="your-anthropic-api-key"
        # set environment variables based on .env file
        load_dotenv()

        # need to add support for setting completion_format (Pydantic object) 
        # as an input here

        try:
            litellm_standard_chat_response = litellm.completion(
                model=model_name,
                messages=dict_messages,
                response_format=completion_format,
                temperature=temperature #optional
            )
        except Exception as e:
            print(f"Error: {e}")
            return None

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
        #             'content': obj         # String: "default message"
        #         }
        #         }
        #     ],
        #     'created': str,               # String: None
        #     'model': str,                 # String: None
        #     'usage': {                    # Dictionary [str, int]
        #         'prompt_tokens': int,       # Integer
        #         'completion_tokens': int,   # Integer
        #         'total_tokens': int         # Integer
                # "prompt_tokens_details": {
                #     "cached_tokens": 1920
                # },
                # "completion_tokens_details": {
                #     "reasoning_tokens": 0
                # }
        #     }
        # }

        response = LmChatResponse(
            created=litellm_standard_chat_response.created,
            model=litellm_standard_chat_response.model,
            choices=[LmChatResponse_Choice(
               index = litellm_standard_chat_response.choices[0].index,
                message = LmChatResponse_Message(
                    role = litellm_standard_chat_response.choices[0].message.role,
                    content = litellm_standard_chat_response.choices[0].
                    message.content,
                    completion_format = completion_format,
                ),
                finish_reason = litellm_standard_chat_response.choices[0].
                finish_reason
        )   ],
            usage=LmChatResponse_Usage(
                prompt_tokens = litellm_standard_chat_response.usage.prompt_tokens,
                completion_tokens = litellm_standard_chat_response.usage.
                completion_tokens,
                total_tokens = litellm_standard_chat_response.usage.total_tokens,
                prompt_tokens_details = LmChatResponse_Usage_PromptTokensDetails(
                    cached_tokens=litellm_standard_chat_response.usage.prompt_tokens_details.cached_tokens
                ),
                completion_tokens_details = LmChatResponse_Usage_CompletionTokensDetails(
                    reasoning_tokens=litellm_standard_chat_response.usage.completion_tokens_details.reasoning_tokens
                )
            ),
        )

        print(response)

        return (response.choices[0].message.content, response)