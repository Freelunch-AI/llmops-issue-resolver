import os
import typer

app = typer.Typer()

commit_message = "placeholder"


@app.command()
def resolve_issue():
    """git
    Resolve issue located in issue.txt
    """
    typer.echo("Started Issue Resolution Attempt")

    os.rename('toy.py', 'renamed-toy.py')  # placeholder
    global commit_message
    commit_message = "commit_message_goes_here"  # placeholder

    typer.echo("Finished Issue Resolution Attempt")


@app.command()
def get_commit_message():
    """
    Prints commit message related to last issue resolution
    """
    typer.echo(commit_message)
