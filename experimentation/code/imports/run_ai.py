# Runs the AI solution that first reads issue.md, tips.txt and fail_to_pass.txt; then 
# modifies the repo to fix the issue.

import os
import sys
from contextlib import contextmanager
from typing import Tuple


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
    from experimentation.code.imports.schemas.schema_models import (
        ExampleOutputModel,
        MessageModel,
    )


def run_ai() -> Tuple[str, bool, str]:
    """
    Runs the AI solution at ./repo that first reads issue.md, 
    tips.txt and fail_to_pass.txt; then
    modifies the repo, locally, to fix the issue.

    Returns:
        experiment_name (str): The name of the experiment.
    """

    lm_caller = LmCaller()

    messages = [
        MessageModel(role="system", content="You are a Software Engineer"),
        MessageModel(role="user", content="Explain the concept of recursion to me.")
    ]

    completion, response = lm_caller.call_lm(output_format=ExampleOutputModel, 
                                                model_name="gemini/gemini-pro",
                                                messages=messages)

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