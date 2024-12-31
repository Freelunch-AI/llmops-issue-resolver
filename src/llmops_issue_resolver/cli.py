import os
import sys
from contextlib import contextmanager

import typer

from llmops_issue_resolver.agent import graph


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

# with temporary_sys_path(os.path.dirname(__file__)):
#    <package_based_imports>

app = typer.Typer()

@app.command()
def resolve_issue():
    """
        1. Run Graph
        2. Makes changes to resolve the issue
        3. Writes commit message to commit_message.txt
    """
    typer.echo("Started Issue Resolution Attempt")

    events = graph.stream(
        {"messages": [("user", "Solve the Issue")]},
        {"configurable": {"thread_id": "42"}},
        stream_mode="values"
    )
    for event in events:
        event["messages"][-1].pretty_print()
    
    commit_message = "commit_message_goes_here"  # placeholder
    
    with open('commit_message.txt', 'w', encoding='utf-8') as file:
        file.write(commit_message)

    typer.echo("Finished Issue Resolution Attempt")


@app.command()
def get_commit_message():
    """
        1. Reads commit message (related to last issue resolution) from 
        commit_message.txt
        2. Prints commit message
        3. Deletes commit_message.txt
    """
    # print commit message
    with open('commit_message.txt', 'r', encoding='utf-8') as file:
        commit_message = file.read()

    # print commit message
    typer.echo(commit_message)

    # delete commit_message.txt
    os.remove('commit_message.txt')
