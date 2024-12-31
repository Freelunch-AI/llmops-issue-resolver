import os
import sys

import typer

app = typer.Typer()

# do imports 'assuming' that the package is installed
# before: 'from agent import ..."
# now: "from llmops_issue_resolver.agent import ..."
# But why do this? 
#     - Because mypy assumes this
#     - Because it makes it clenar for doing imports within modules that are very deep 
#     and want to import from modules that are near surface of the package directory 
#     tree
# All .py modules need to have this line, but with the more general form would be:
# sys.path.append(os.join("relative_path_to_llmops_issue_resolver", \
#     os.path.dirname(__file__)))
sys.path.append(os.path.dirname(__file__))

@app.command()
def resolve_issue():
    """
        1. Reads issue in issue.md
        2. Makes changes to resolve the issue
        3. Writes commit message to commit_message.txt
    """
    typer.echo("Started Issue Resolution Attempt")

    # read issue from issue.md

    # resolve issue
    os.rename('toy.py', 'renamed-toy.py')  # placeholder
    commit_message = "commit_message_goes_here"  # placeholder

    # write commit message to commit_message.txt
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
