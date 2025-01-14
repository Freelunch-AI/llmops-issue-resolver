import os
import sys
import time
from contextlib import contextmanager
from typing import Dict, List, Optional

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
    from experimentation.code.imports.constants.constants import SWE_BACKSTORY
    from experimentation.code.imports.schemas.schema_models import (
        CompletionFormat,
        DictOptionalModel,
        Examples,
        FloatModel,
        LmChatResponse,
        LmSummary,
        StringModel,
        StringOptionalModel,
        Tools,
        ValidateLmChatResponse,
    )
    from experimentation.code.imports.utils.exceptions import CostThresholdExceededError

# Usage example:
# tracker = TrackLLMCalls()
# @tracker.call_llm_provider
# def some_llm_function(...):
#     ...
# response = some_llm_function(...)
# print(tracker.get_history_and_state())


def lm_caller_extensor(cost_threshold: float = 3) -> type:

    try:
        FloatModel(items=cost_threshold)
    except ValidationError as e:
        print(f"Validation error: {e}")
        raise TypeError

    def decorator(cls):

        original_call_lm = cls.call_lm
        
        cost_mapping_1M_tokens = {
            "gpt-4o-mini": {
                "batch": {
                    "input_tokens": 1.25,
                    "cached_input_tokens": None,
                    "output_tokens": 5.0
                },
                "single": {
                    "input_tokens": 2.5,
                    "cached_input_tokens": 1.25,
                    "output_tokens": 10.0
                }
            },
            "gpt-4o": { # prices are not real
                "batch": {
                    "input_tokens": 1.25,
                    "cached_input_tokens": None,
                    "output_tokens": 5.0
                },
                "single": {
                    "input_tokens": 2.5,
                    "cached_input_tokens": 1.25,
                    "output_tokens": 10.0
                }
            },
            "gpt-4": { # prices are not real
                "batch": {
                    "input_tokens": 1.25,
                    "cached_input_tokens": None,
                    "output_tokens": 5.0
                },
                "single": {
                    "input_tokens": 2.5,
                    "cached_input_tokens": 1.25,
                    "output_tokens": 10.0
                }
            }
        }

        def new_init(self) -> None:
            self.history = []
            self.state = {
                'number_of_calls_made': 0,
                'total_cost': 0.0,
                'total_time': 0.0,
                'average_cost_per_call': 0.0,
                'average_time_per_call': 0.0
            }

            self.cost_threshold = cost_threshold

        @classmethod
        def calculate_cost(cls, response: LmChatResponse, model_name: str, 
                           mode: str = "single") -> float:
            
            try:
                ValidateLmChatResponse(response)
                print("-------------1-------------")
                StringModel(items=model_name)
                print("-------------2-------------")
                StringModel(items=mode)
            except ValidationError as e:
                print(f"Validation error: {e}")
                raise TypeError

            if not hasattr(response.usage, 'prompt_token_details') or \
            not hasattr(response.usage.prompt_token_details, 'cached_tokens'):
                cost = (
                    cls.cost_mapping_1M_tokens[model_name][mode]
                    ['input_tokens'] * response.usage.prompt_tokens + 
                    cls.cost_mapping_1M_tokens[model_name][mode]
                    ['output_tokens'] * response.usage.completion_tokens
                ) / 1e6
            else:
                cost = (
                    cls.cost_mapping_1M_tokens[model_name][mode]
                    ['input_tokens'] * (response.usage.prompt_tokens - 
                                    response.usage.prompt_token_details.
                                    cached_tokens) +
                    cls.cost_mapping_1M_tokens[model_name][mode]
                    ['output_tokens'] * response.usage.completion_tokens +
                    cls.cost_mapping_1M_tokens[model_name][mode]
                    ['cached_input_tokens'] * response.usage.
                    prompt_token_details.cached_tokens
                ) / 1e6

            return cost

        def new_call_lm(
            self, 
            model_name: str,
            instruction: str, 
            tips: Optional[str] = None,
            image: Optional[str] = None,
            image_format: Optional[Dict[str, str]] = None, 
            constraints: Optional[str] = None,
            completion_format_description: Optional[str] = None,
            examples: Optional[List[Dict[str, str]]] = None,
            image_examples: Optional[List[Dict[str, str]]] = None,
            completion_format: CompletionFormat = StringModel,
            tools: Optional[Tools] = None,
            temperature: float = 0, 
            backstory: Optional[str] = SWE_BACKSTORY,
        ) -> LmChatResponse:
            
            try:
                CompletionFormat(completion_format=completion_format)
                Examples(items=examples)
                Examples(items=image_examples)
                StringOptionalModel(items=completion_format_description)
                StringModel(items=model_name)
                StringModel(items=instruction)
                StringOptionalModel(items=tips)
                StringOptionalModel(items=constraints)
                StringOptionalModel(items=image)
                DictOptionalModel(items=image_format)
                StringModel(items=backstory)
                FloatModel(items=temperature)
            except ValidationError as e:
                print(f"Validation error: {e}")
                raise TypeError

            start_time = time.time()

            result = original_call_lm(self, 
                model_name=model_name, 
                instruction=instruction,
                tips=tips,
                image=image,
                image_format=image_format,
                constraints=constraints,
                completion_format_description=completion_format_description,
                examples=examples,
                image_examples=image_examples,
                completion_format=completion_format,
                tools=tools,
                temperature=temperature,
                backstory=backstory,
            )

            if result is None:
                return None
            else:
                completion, response = result

                end_time = time.time()

                cost = self.__class__.calculate_cost(response=response, 
                model_name=model_name)
                
                duration = end_time - start_time

                print("response = ", response)
                print("response.dict()", response.dict())

                self.history.append({
                    'model_name': model_name,
                    'temperature': temperature,
                    'tools': tools,
                    'completion_format_description': completion_format_description,
                    'completion_format': completion_format,
                    'instruction': instruction,
                    'backstory': backstory,
                    'tips': tips,
                    'image': image,
                    'image_format': image_format,
                    'image_examples': image_examples,
                    'examples': examples,
                    'constraints': constraints,

                    'response': response.dict(),
                    'cost': cost,
                    'duration': duration
                })

                self.state['number_of_calls_made'] += 1
                self.state['total_cost'] += cost
                self.state['total_time'] += duration
                self.state['average_cost_per_call'] = self.state['total_cost'] \
                / self.state['number_of_calls_made']
                self.state['average_time_per_call'] = self.state['total_time'] \
                / self.state['number_of_calls_made']

                if self.state['total_cost'] > self.cost_threshold:
                    raise CostThresholdExceededError(
                        f"Total cost {self.state['total_cost']} \
                        exceeded the threshold of {self.cost_threshold}")

                return completion, response 
            
        def get_summary(self):
            print("lm_summary=", {'history': self.history,'state': self.state})
            try:
                return LmSummary(**{
                    'history': self.history,
                    'state': self.state
                })
            except ValidationError as e:
                print(f"Validation error: {e}")
                raise
            
        cls.__init__ = new_init

        cls.cost_mapping_1M_tokens = cost_mapping_1M_tokens
        cls.calculate_cost = calculate_cost
        cls.call_lm = new_call_lm
        cls.get_summary = get_summary

        return cls
    
    return decorator
