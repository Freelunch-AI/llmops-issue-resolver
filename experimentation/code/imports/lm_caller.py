import json
import os
import sys
from contextlib import contextmanager
from typing import Optional

from dotenv import load_dotenv
from litellm import completion
from openai import OpenAI
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

with temporary_sys_path(os.path.abspath(os.path.join(os.path.dirname(__file__), 
                                                     '..', '..', '..'))):

    from experimentation.code.imports.helpers.pydantic import (
        create_tools_use_pydantic_model,
    )
    from experimentation.code.imports.lm_tracker import lm_caller_extensor
    from experimentation.code.imports.prompt_templates.sde import (
        prompt_template_default,
    )
    from experimentation.code.imports.schemas.schema_models import (
        CompletionFormat,
        FloatModel,
        LmChatResponse,
        LmChatResponse_Choice,
        LmChatResponse_Message,
        LmChatResponse_Usage,
        LmChatResponse_Usage_CompletionTokensDetails,
        StringModel,
        Tools,
    )

@lm_caller_extensor(cost_threshold=3)
class LmCaller:
    
    def call_lm (self, model_name: str,
                instruction: str, tips: str, constraints: str,
                completion_format_description: str,
                completion_format: CompletionFormat = StringModel,
                tools: Optional[Tools] = None,
                temperature: float = 0, 
                mode: str = "single") -> LmChatResponse:
        
        try:
            CompletionFormat(completion_format=completion_format)
            StringModel(items=model_name)
            StringModel(items=instruction)
            StringModel(items=tips)
            StringModel(items=constraints)
            FloatModel(items=temperature)
            StringModel(items=mode)
        except ValidationError as e:
            print(f"Validation error: {e}")
            raise TypeError

        # need to set api keys as environment variables
        # example:
        # export OPENAI_API_KEY="your-openai-api-key"
        # export ANTHROPIC_API_KEY="your-anthropic-api-key"
        # set environment variables based on .env file
        load_dotenv()

        messages = prompt_template_default(
            instruction=instruction,
            tips=tips,
            constraints=constraints,
            tools=tools,
            completion_format=completion_format,
            completion_format_description=completion_format_description
        )

        dict_messages = [message.dict() for message in messages]

        client = OpenAI()

        if tools:
            ToolsUse = create_tools_use_pydantic_model(tools)
            completion_format = ToolsUse

        response = client.beta.chat.completions.parse(
            model=model_name,
            messages=dict_messages,
            response_format=completion_format,
            )

        # Response object:
        # {
        #     "id": "chatcmpl-9nYAG9LPNonX8DAyrkwYfemr3C8HC",
        #     "object": "chat.completion",
        #     "created": 1721596428,
        #     "model": "gpt-4o-2024-08-06",
        #     "choices": [
            #     {
                #     "index": 0,
                #     "message": {
                #             "role": "assistant",
                #             "content": "Hi, how can i help you?"
                #     },
                #     "logprobs": null,
                #     "finish_reason": "stop"
#                 }
        #     ],
        #     "usage": {
        #         "prompt_tokens": 81,
        #         "completion_tokens": 11,
        #         "total_tokens": 92,
        #         "completion_tokens_details": {
            #         "reasoning_tokens": 0,
            #         "accepted_prediction_tokens": 0,
            #         "rejected_prediction_tokens": 0
        #         }
        #     },
        #     "system_fingerprint": "fp_3407719c7f"
        # }

        print("response = ", response)

        my_response = LmChatResponse(
            created=response.created,
            model=response.model,
            object=response.object,
            choices=[LmChatResponse_Choice(
                index = response.choices[0].index,
                message = LmChatResponse_Message(
                    role = response.choices[0].message.role,
                    parsed = response.choices[0].message.parsed,
                    completion_format = completion_format,
                ),
                finish_reason = response.choices[0].
                finish_reason
        )   ],
            usage=LmChatResponse_Usage(
                prompt_tokens = response.usage.prompt_tokens,
                completion_tokens = response.usage.
                completion_tokens,
                total_tokens = response.usage.total_tokens,
                completion_tokens_details = 
                LmChatResponse_Usage_CompletionTokensDetails(
                    reasoning_tokens=response.usage.completion_tokens_details.reasoning_tokens,
                    accepted_prediction_tokens=response.usage.completion_tokens_details.accepted_prediction_tokens,
                    rejected_prediction_tokens=response.usage.completion_tokens_details.rejected_prediction_tokens,
                )
            )
        )

        content = my_response.choices[0].message.parsed
        return (content, my_response)