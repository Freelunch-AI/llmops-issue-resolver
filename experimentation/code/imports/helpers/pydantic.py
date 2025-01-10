import os
import sys
from contextlib import contextmanager

from pydantic import create_model
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
                                                     '..', '..', '..', '..'))):    
    import experimentation.code.imports.schemas.schema_models as schema_models

# dynamically create the following pydantic model in 
    # "experimentation.code.imports.schemas.schema_models":
    # class CompletionFormatDescriptionDynamic(BaseModel):
    #     completion_format: {completion_format}
    #     description: str

def create_completion_format_description_dynamic_model(completion_format: type) -> None:
    CompletionFormatDescriptionDynamic = create_model(
        'CompletionFormatDescriptionDynamic',
        completion_format=(completion_format, ...),
        description=(str, ...)
    )
    CompletionFormatDescriptionDynamic.update_forward_refs()
    schema_models.CompletionFormatDescriptionDynamic = CompletionFormatDescriptionDynamic
    return 