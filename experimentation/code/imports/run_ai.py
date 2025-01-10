# Runs the AI solution that first reads issue.md, tips.txt and fail_to_pass.txt; then 
# modifies the repo to fix the issue.

import os
import sys
from contextlib import contextmanager
from typing import Tuple, Type

from pydantic import BaseModel
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
                                                     '..', '..', '..'))):    
    from experimentation.code.imports.lm_caller import LmCaller
    from experimentation.code.imports.prompt_templates.sde import (
        MARKDOWN_DESCRIPTION,
        TOOLS_USE_DESCRIPTION,
        prompt_template_default,
    )
    from experimentation.code.imports.schemas.schema_models import (
        CompletionFormatDescription,
        StringModel,
        ToolsUse,
    )
    from experimentation.code.imports.tool_builder import tool_builder

def completion_format_description_builder(completion_format: Type[BaseModel], description: str) -> CompletionFormatDescription:
    """
    Builds a CompletionFormatDescription object from the given completion_format and description.
    Args:
        completion_format (Type[BaseModel]): The completion format to be used.
        description (str): The description to be used.
    Returns:
        CompletionFormatDescription: The built CompletionFormatDescription object.
    """
    return 


def run_ai() -> Tuple[str, bool, str]:
    """
    Runs the AI solution at ./repo that first reads issue.md, 
    tips.txt and fail_to_pass.txt; then
    modifies the repo, locally, to fix the issue.

    Returns:
        experiment_name (str): The name of the experiment.
    """

    lm_caller = LmCaller()

    # reason ----------------------------------------------------
   
    completion_format = StringModel

    messages = prompt_template_default(
        instruction="Respond user questions",
        tips="Some tips",
        constraints="Some constraints",
        completion_format_description=CompletionFormatDescription(
            completion_format=completion_format, description=MARKDOWN_DESCRIPTION),
    )

    result = lm_caller.call_lm(completion_format=completion_format, 
                                                model_name="gpt-4o-mini",
                                                messages=messages)
    if result is None:
        raise ValueError("LLM service returned an error")
    elif result[0] is None:
        raise ValueError("LLM service refused to provide a completion")
    else:
        completion_reason, response_reason = result

    # -------------------------------------------

    # act

    tools = tool_builder.get_tools(['tool1', 'tool2'])

    completion_format = ToolsUse

    messages = prompt_template_default(
        tools=tools,
        instruction="Respond user questions",
        tips="Some tips",
        constraints="Some constraints",
        completion_format_description=CompletionFormatDescription(
            completion_format=completion_format, description=TOOLS_USE_DESCRIPTION),
    )
    
    result = lm_caller.call_lm(completion_format=completion_format , 
                                                model_name="gpt-4o-mini",
                                                messages=messages)
    
    if result is None:
        raise ValueError("LLM service returned an error")
    elif result[0] is None:
        raise ValueError("LLM service refused to provide a completion")
    else:
        completion_act, response_act = result

    # placeholder: ai solution goes here
    if os.path.exists("toy.txt"):
        os.remove("toy.txt")
    else:
        with open("toy.txt", "w") as f:
            f.write("This is a placeholder file.")

    # experiment_name should follow this schema: "<static-workflow OR dynamic-workflow>
    # __<dynamic-subworkflows-true OR false>__<additional_inference-time-data-available>
    # __<tools-used>__<explanationid>" 
    # where explanationid is the id of the explanation that the AI solution.
    # solution explanations should be stored in the explanations/ directory.
    # Each explanation should be stored in a file named "id.md"
    # E.g., "static-workflow__dynamic-subworkflows-false__internet-data__langgraph-lite
    # llm-gpt4o__1"
    
    skipped_instance = False # placeholder

    experiment_name = "placeholder__placeholder__placeholder__placeholder__placeholder"
    
    lm_summary = lm_caller.get_summary()

    return (experiment_name, skipped_instance, lm_summary)