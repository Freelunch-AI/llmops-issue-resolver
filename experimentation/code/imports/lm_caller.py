import os
import sys
from contextlib import contextmanager
from typing import List

import aisuite
from pydantic import BaseModel, ValidationError


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
    from experimentation.code.imports.lm_tracker import LmTracker
    from experimentation.code.imports.utils.schema_models import (
        FloatModel,
        LmChatResponse,
        MessageModel,
        StringModel,
        ValidateBaseModel,
        ValidateMessageModel,
    )

lm_tracker = LmTracker(cost_treshold=3)

@lm_tracker.call_llm()
def call_lm(output_format: BaseModel, 
             provider: str, model_name: str, messages: List[MessageModel], 
             temperature: float = 0.75, mode: str = None, ) -> LmChatResponse:
    # Placeholder for the actual call to the LLM provider
    # Return a response object compatible with OpenAI

    try:
        ValidateBaseModel(output_format)
        StringModel(provider)
        StringModel(model_name)
        FloatModel(temperature)
        ValidateMessageModel(messages)
        if mode:
            StringModel(mode)
    except ValidationError as e:
        print(f"Validation error: {e}")
        raise

    # Call aisuite to get the response

    lm_client = aisuite.Client()
    provider_model = [f"{provider}:{model_name}"]
    dict_messages = [message.dict() for message in messages]

    open_ai_standard_response = lm_client.chat.completions.create(
        model=provider_model,
        messages=dict_messages,
        temperature=temperature
    )

    # Example OpenAI-compatible chat response object
    # response = LmChatResponse(
    #     id="chatcmpl-123456",
    #     object="chat.completion",
    #     created=1728933352,
    #     model="gpt-4o-2024-08-06",
    #     choices=[
    #         {
    #             "index": 0,
    #             "message": {
    #                 "role": "assistant",
    #                 "content": "Hi there! How can I assist you today?",
    #                 "refusal": None,
    #                 "output_format": "text"  # I added this line. 
    #                 If no structured outputs: 
    #                 # format="text", else 
    #                 format="name_of_pydantic_model_passed_in_the_req"
    #             },
    #             "logprobs": None,
    #             "finish_reason": "stop"
    #         }
    #     ],
    #     usage={
    #         "prompt_tokens": 19,
    #         "completion_tokens": 10,
    #         "total_tokens": 29,
    #         "prompt_tokens_details": {
    #             "cached_tokens": 0
    #         },
    #         "completion_tokens_details": {
    #             "reasoning_tokens": 0,
    #             "accepted_prediction_tokens": 0,
    #             "rejected_prediction_tokens": 0
    #         }
    #     },
    #     system_fingerprint="fp_6b68a8204b"
    # )

    my_response = LmChatResponse(
        id=open_ai_standard_response.id,
        object=open_ai_standard_response.object,
        created=open_ai_standard_response.created,
        model=open_ai_standard_response.model,
        choices=[
            {
                "index": open_ai_standard_response.choices[0].index,
                "message": {
                    "role": open_ai_standard_response.choices[0].message.role,
                    "content": open_ai_standard_response.choices[0].message.content,
                    "refusal": open_ai_standard_response.choices[0].message.refusal,
                    "output_format": output_format
                },
                "logprobs": open_ai_standard_response.choices[0].logprobs,
                "finish_reason": open_ai_standard_response.choices[0].finish_reason
            }
        ],
        usage={
            "prompt_tokens": open_ai_standard_response.usage.prompt_tokens,
            "completion_tokens": open_ai_standard_response.usage.completion_tokens,
            "total_tokens": open_ai_standard_response.usage.total_tokens,
            "prompt_tokens_details": {
                "cached_tokens": open_ai_standard_response.usage.prompt_tokens_details.
                cached_tokens
            },
            "completion_tokens_details": {
                "reasoning_tokens": 
                open_ai_standard_response.usage.completion_tokens_details.reasoning_tokens,
                "accepted_prediction_tokens": 
                open_ai_standard_response.usage.completion_tokens_details.accepted_prediction_tokens,
                "rejected_prediction_tokens": 
                open_ai_standard_response.usage.completion_tokens_details.rejected_prediction_tokens
            }
        },
        system_fingerprint=open_ai_standard_response.system_fingerprint
    )

    return (my_response.choices[0].message.content, my_response)