import os

import typer
from agent import graph

app = typer.Typer()

@app.command()
def resolve_issue():
    """
        1. Reads issue in issue.md
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
