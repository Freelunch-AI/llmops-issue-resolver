# Runs the AI solution that first reads issue.md, tips.txt and fail_to_pass.txt; then 
# modifies the repo to fix the issue.

from typing import Tuple


def run_ai() -> Tuple[str, bool]:
    """
    Runs the AI solution at ./repo that first reads issue.md, 
    tips.txt and fail_to_pass.txt; then
    modifies the repo, locally, to fix the issue.

    Returns:
        experiment_name (str): The name of the experiment.
    """

    # experiment_name should follow this schema: "<static-workflow OR dynamic-workflow>
    # __<dynamic-subworkflows-true OR false>__<additional_inference-time-data-available>
    # __<tools-used>__<explanationid>" 
    # where explanationid is the id of the explanation that the AI solution.
    # solution explanations should be stored in the explanations/ directory.
    # Each explanation should be stored in a file named "id.md"
    # E.g., "static-workflow__dynamic-subworkflows-false__internet-data__langgraph-lite
    # llm-gpt4o__1"
    experiment_name = "placeholder__placeholder__placeholder__placeholder__placeholder"
    skipped_instance = False # placeholder
    return (experiment_name, skipped_instance)