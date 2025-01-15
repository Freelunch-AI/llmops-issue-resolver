import json
import os
import sys
from contextlib import contextmanager
from typing import Dict, List, Optional

from dotenv import load_dotenv
from openai import OpenAI
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

    import experimentation.code.imports.schemas.schema_models as schema_models
    from experimentation.code.imports.helpers.pydantic import (
        create_tools_use_pydantic_model,
    )
    from experimentation.code.imports.lm_tracker import lm_caller_extensor
    from experimentation.code.imports.prompt_templates.sde import (
        prompt_template_default,
    )
    from experimentation.code.imports.schemas.schema_models import (
        CompletionFormat,
        LmChatResponse,
        LmChatResponse_Choice,
        LmChatResponse_Message,
        LmChatResponse_Usage,
        LmChatResponse_Usage_CompletionTokensDetails,
        StringModel,
        Tools,
    )
    from experimentation.code.imports.utils.exceptions import (
        ContextSizeExcededError,
        LmContentFilterError,
        LmLengthError,
        LmRefusalError,
    )
    from experimentation.code.imports.utils.tokens import calculate_number_of_tokens
    from experimentation.data.constants import (
        COST_MAPPING_1M_TOKENS,
        SWE_BACKSTORY,
    )


@lm_caller_extensor(cost_threshold=3)
class LmCaller:
    
    def call_lm (self, model_name: str,
        instruction: str, 
        tips: Optional[str] = None,
        image: Optional[str] = None,
        image_format: Optional[Dict[str, str]] = None, 
        constraints: Optional[str] = None,
        examples: Optional[List[Dict[str, str]]] = None,
        image_examples: Optional[List[Dict[str, str]]] = None,
        completion_format: CompletionFormat = StringModel,
        tools: Optional[Tools] = None,
        temperature: float = 0, 
        backstory: Optional[str] = SWE_BACKSTORY,
    ) -> LmChatResponse:

        # need to set api keys as environment variables
        # example:
        # export OPENAI_API_KEY="your-openai-api-key"
        # export ANTHROPIC_API_KEY="your-anthropic-api-key"
        # set environment variables based on .env file
        load_dotenv()

        if tools:
            create_tools_use_pydantic_model(tools)
            ToolsUse = schema_models.ToolsUse
            completion_format = ToolsUse

        messages = prompt_template_default(
            instruction=instruction,
            image=image,
            image_format=image_format,
            tips=tips,
            constraints=constraints,
            tools=tools,
            completion_format=completion_format,
            examples=examples,
            image_examples=image_examples,
            backstory=backstory,
        )

        input_tokens = calculate_number_of_tokens(messages=messages, 
                                                  tokenization_method=COST_MAPPING_1M_TOKENS[model_name]["tokenization_method"])

        if input_tokens > COST_MAPPING_1M_TOKENS[model_name]["context_window"]:
            raise ContextSizeExcededError(
                f"""The input tokens are more than the maximum allowed tokens 
                for {model_name}. The context window of {model_name} is 
                {COST_MAPPING_1M_TOKENS[model_name]["context_window"]} tokens.
                """
            )

        dict_messages = [message.dict() for message in messages]

        client = OpenAI()

        response = client.beta.chat.completions.parse(
            model=model_name,
            messages=dict_messages,
            temperature=temperature,
            response_format=completion_format,
            )
        
        if response.choices[0].message.refusal:
            raise LmRefusalError("LLM service refused to provide a completion")
        if response.choices[0].finish_reason == "lenght":
            raise LmLengthError("Completion reached max output tokens limit \
                                without finishing")
        if response.choices[0].finish_reason == "content_filter": 
            raise LmContentFilterError("Completion reached max output tokens limit \
                                       and stopped")

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
                #              "refusal": null
                #     },:
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

        completion = my_response.choices[0].message.parsed
        return (completion, my_response)