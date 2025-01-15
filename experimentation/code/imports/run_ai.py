# Runs the AI solution that first reads issue.md, tips.txt and fail_to_pass.txt; then 
# modifies the repo to fix the issue.

import os
import sys
from contextlib import contextmanager
from typing import Tuple

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
    import experimentation.code.imports.tools.filesystem_tools # noqa
    from experimentation.code.imports.lm_caller import LmCaller
    from experimentation.code.imports.schemas.schema_models import (
        CompletionReasoning,
    )
    from experimentation.code.imports.tool_builder import tool_builder
    from experimentation.data.constants import TEXT_TO_CONTEXT_OVERLOAD
    from experimentation.code.imports.helpers.openai import get_ready_openai_image
    from experimentation.code.imports.utils.exceptions import (
        CostThresholdExcededError,
        ContextSizeExcededError,
        LmContentFilterError,
        LmLengthError,
        LmRefusalError
    )
    


my_local_image_path = os.path.join(os.path.dirname(__file__), "..", "..", 
                                   "data", "images", "cat_image.jpeg")

EXAMPLE_REMOTE_IMAGE = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"
EXAMPLE_LOCAL_IMAGE = get_ready_openai_image(image_path=my_local_image_path)

def run_ai() -> Tuple[str, bool, str]:

    lm_caller = LmCaller()

    # reason ----------------------------------------------------

    try:
        result = lm_caller.call_lm(
            model_name = "gpt-4o-mini",
            instruction = TEXT_TO_CONTEXT_OVERLOAD,
            image = EXAMPLE_LOCAL_IMAGE,
            image_format = {
                "payload": "jpeg_base64",
                "examples": "url_http"
            },
            tips = "Some tips to help the model",
            constraints = "Some contraints the model must obey",
            completion_format = CompletionReasoning,
            image_examples = [ 
                                {
                                    "instruction": "Tell me whats in the image", 
                                    "image": EXAMPLE_REMOTE_IMAGE, 
                                    "response": "A boardwalk in a park with a blue sky"
                                },
                            ]
        )
    except Exception as e:
        result = None
        if isinstance(e, ContextSizeExcededError):
            print('Caught ContextSizeExcededError')
        elif isinstance(e, LmContentFilterError):
            print('Caught LmContentFilterError')
        elif isinstance(e, LmLengthError):
            print('Caught LmLengthError')
        elif isinstance(e, LmRefusalError):
            print('Caught LmRefusalError')
        elif isinstance(e, CostThresholdExcededError):
           print('Caught CostThresholdExcededError')
        else:
            raise e
    
    

    # -------------------------------------------

    # act

    tools = tool_builder.get_tools(['get_directory_tree'])
    
    try:
        result = lm_caller.call_lm(
            model_name = "gpt-4o-mini",
            instruction = "Count the r's in the strawberry",
            tips = "Some tips to help the model",
            constraints = "Some contraints the model must obey",
            tools = tools,
            examples = [ {"instruction": "Count the r's in row", "response": "1"} ],
        )
    except Exception as e:
        result = None
        if isinstance(e, ContextSizeExcededError):
            print('Caught ContextSizeExcededError')
        elif isinstance(e, LmContentFilterError):
            print('Caught LmContentFilterError')
        elif isinstance(e, LmLengthError):
            print('Caught LmLengthError')
        elif isinstance(e, LmRefusalError):
            print('Caught LmRefusalError')
        elif isinstance(e, CostThresholdExcededError):
           print('Caught CostThresholdExcededError')
        else:
            raise e

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