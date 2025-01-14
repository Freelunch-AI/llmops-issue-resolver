# Runs the AI solution that first reads issue.md, tips.txt and fail_to_pass.txt; then 
# modifies the repo to fix the issue.

import base64
import os
import sys
from contextlib import contextmanager
from typing import Tuple

from rich import print


# Function to encode the image
def encode_image(image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def get_ready_image(base64Image: str) -> str:
    return f"data:image/jpeg;base64,{base64Image}"


my_image_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "images", 
                             "cat_image.jpeg")
my_base64_image = encode_image(my_image_path)
EXAMPLE_LOCAL_IMAGE = get_ready_image(base64Image=my_base64_image)
EXAMPLE_REMOTE_IMAGE = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"

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
    import experimentation.code.imports.tools.fs # noqa
    from experimentation.code.imports.lm_caller import LmCaller
    from experimentation.code.imports.schemas.schema_models import (
        CompletionReasoning,
    )
    from experimentation.code.imports.tool_builder import tool_builder

def run_ai() -> Tuple[str, bool, str]:

    lm_caller = LmCaller()

    # reason ----------------------------------------------------

    result = lm_caller.call_lm(
        model_name = "gpt-4o-mini",
        instruction = "Instruction the model must follow",
        image = EXAMPLE_LOCAL_IMAGE,
        image_format = {
            "payload": "jpeg_base64",
            "examples": "url_http"
        },
        tips = "Some tips to help the model",
        constraints = "Some contraints the model must obey",
        completion_format = CompletionReasoning,
        completion_format_description = "Description of the completion format",
        image_examples = [ 
                            {
                                "instruction": "Tell me whats in the image", 
                                "image": EXAMPLE_REMOTE_IMAGE, 
                                "response": "A boardwalk in a park with a blue sky"
                            },
                        ]
    )

    if result is None:
        raise ValueError("LLM service returned an error")
    elif result[0] is None:
        raise ValueError("LLM service refused to provide a completion")
    else:
        completion_format_object_reason, response_reason = result

    # -------------------------------------------

    # act

    tools = tool_builder.get_tools(['get_directory_tree'])
    
    result = lm_caller.call_lm(
        model_name = "gpt-4o-mini",
        instruction = "Count the r's in the strawberry",
        tips = "Some tips to help the model",
        constraints = "Some contraints the model must obey",
        tools = tools,
        completion_format_description = "Description of the completion format",
        examples = [ {"instruction": "Count the r's in row", "response": "1"} ],
    )
    
    if result is None:
        raise ValueError("LLM service returned an error")
    elif result[0] is None:
        raise ValueError("LLM service refused to provide a completion")
    else:
        completion_format_object_act, response_act = result

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