import os
import typer

app = typer.Typer()

commit_message = "placeholder"

@app.callback()
def callback():
    """
    LLMOps Issue Resolver
    """

@app.command()
def resolve_issue():
    """
    Resolve issue located in issue.txt
    """
    typer.echo("Started Issue Resolution Attempt")

    # placeholder
    os.rename('toy.py', 'renamed-toy.py')

    global commit_message
    commit_message = "commit_message_goes_here"

    typer.echo("Finished Issue Resolution Attempt")

@app.command()
def get_commit_message():
    """
    Prints commit message related to last issue resolution
    """
    typer.echo(commit_message)