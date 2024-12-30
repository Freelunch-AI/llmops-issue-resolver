import os
import typer
from agent import graph

app = typer.Typer()

@app.command()
def resolve_issue():
    """git
    Resolve issue located in issue.txt
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
    Prints commit message related to last issue resolution
    """
    with open('commit_message.txt', 'r', encoding='utf-8') as file:
        commit_message = file.read()

    typer.echo(commit_message)
