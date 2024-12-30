import os

import pytest
from typer.testing import CliRunner

from llmops_issue_resolver.cli import app

runner = CliRunner()

@pytest.fixture
def setup_files():
    # Setup: create a dummy 'toy.py' file
    with open('toy.py', 'w') as f:
        f.write("print('This is a toy file')")
    yield
    # Teardown: remove created files
    if os.path.exists('toy.py'):
        os.remove('toy.py')
    if os.path.exists('renamed-toy.py'):
        os.remove('renamed-toy.py')
    if os.path.exists('commit_message.txt'):
        os.remove('commit_message.txt')

def test_resolve_issue(setup_files):
    result = runner.invoke(app, ["resolve_issue"])
    assert result.exit_code == 0
    assert "Started Issue Resolution Attempt" in result.output
    assert "Finished Issue Resolution Attempt" in result.output
    assert os.path.exists('renamed-toy.py')
    assert os.path.exists('commit_message.txt')
    with open('commit_message.txt', 'r', encoding='utf-8') as file:
        commit_message = file.read()
    assert commit_message == "commit_message_goes_here"