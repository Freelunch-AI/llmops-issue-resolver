import os
import sys
import time
from contextlib import contextmanager
from functools import wraps
from typing import Optional

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
    from experimentation.code.imports.schemas.schema_models import (
        FloatModel,
        LmChatResponse,
        LmSummary,
    )
    from experimentation.code.imports.utils.exceptions import CostThresholdExceededError

# Usage example:
# tracker = TrackLLMCalls()
# @tracker.call_llm_provider
# def some_llm_function(...):
#     ...
# result = some_llm_function(...)
# print(tracker.get_history_and_state())


def lm_caller_extensor(cost_threshold: float = 3) -> type:

    try:
        FloatModel(items=cost_threshold)
    except ValidationError as e:
        print(f"Validation error: {e}")
        raise

    def decorator(cls):

        original_call_lm = cls.call_lm

        cost_mapping_1M_tokens = {
           "gemini/gemini-pro": {
                "input_tokens": 0.075,
                "cached_input_tokens": None,
                "output_tokens": 0.3
           },
            "gpt-4o-mini": {
                "batch": {
                    "input_tokens": 0.075,
                    "cached_input_tokens": None,
                    "output_tokens": 0.3
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
        def calculate_cost(cls, result: LmChatResponse, model_name: str, 
                           mode: Optional[str]) -> float:
            if not hasattr(result[1].usage, 'prompt_token_details') or \
            not hasattr(result[1].usage.prompt_token_details, 'cached_tokens'):
                if mode == None:
                    cost = (
                        cls.cost_mapping_1M_tokens[model_name]
                        ['input_tokens'] * result[1].usage.prompt_tokens + 
                        cls.cost_mapping_1M_tokens[model_name]
                        ['output_tokens'] * result[1].usage.completion_tokens
                    ) / 1e6
                else:
                    cost = (
                        cls.cost_mapping_1M_tokens[model_name][mode]
                        ['input_tokens'] * result[1].usage.prompt_tokens + 
                        cls.cost_mapping_1M_tokens[model_name][mode]
                        ['output_tokens'] * result[1].usage.completion_tokens
                    ) / 1e6
            else:
                if mode == None:
                    cost = (
                        cls.cost_mapping_1M_tokens[model_name]
                        ['input_tokens'] * (result[1].usage.prompt_tokens - 
                                        result[1].usage.prompt_token_details.
                                        cached_tokens) +
                        cls.cost_mapping_1M_tokens[model_name]
                        ['output_tokens'] * result[1].usage.completion_tokens +
                        cls.cost_mapping_1M_tokens[model_name]
                        ['cached_input_tokens'] * result[1].usage.
                        prompt_token_details.cached_tokens
                    ) / 1e6
                else:
                    cost = (
                        cls.cost_mapping_1M_tokens[model_name][mode]
                        ['input_tokens'] * (result[1].usage.prompt_tokens - 
                                        result[1].usage.prompt_token_details.
                                        cached_tokens) +
                        cls.cost_mapping_1M_tokens[model_name][mode]
                        ['output_tokens'] * result[1].usage.completion_tokens +
                        cls.cost_mapping_1M_tokens[model_name][mode]
                        ['cached_input_tokens'] * result[1].usage.
                        prompt_token_details.cached_tokens
                    ) / 1e6

            return cost

        def new_call_lm(self, *args: list, **kwargs: dict) -> LmChatResponse:
            start_time = time.time()
            result = original_call_lm(self, *args, **kwargs)
            end_time = time.time()

            model_name = kwargs.get('model_name')
            mode = kwargs.get('mode')

            cost = self.__class__.calculate_cost(result=result, 
            model_name=model_name, mode=mode)
            
            duration = end_time - start_time

            self.history.append({
                'mode': mode,
                'result': result[1].dict(),
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

            return result
            
        def get_summary(self):
            return LmSummary.parse_obj({
                'history': self.history,
                'state': self.state
            })
            
        cls.__init__ = new_init

        cls.cost_mapping_1M_tokens = cost_mapping_1M_tokens
        cls.calculate_cost = calculate_cost
        cls.call_lm = new_call_lm
        cls.get_summary = get_summary

        return cls
    
    return decorator
