import os
import sys
from contextlib import contextmanager

import pytest
from typer.testing import CliRunner


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
# would be:
# sys.path.append(os.join("relative_path_to_llmops_issue_resolver", \
#     os.path.dirname(__file__)))


# with temporary_sys_path(os.path.abspath(os.path.join(os.path.dirname(__file__), 
#     '../../'))):
#     from llmops_issue_resolver.cli import app  # type: ignore
# 
# runner = CliRunner()

# @pytest.fixture 
# def setup_files_for_test_resolve_issue():
#     """
#         Fixture to set up and tear down files for testing.
# 
#         This fixture creates a dummy 'toy.py' file before the test and ensures its 
#         removal, along with any other files created during the test ('renamed-toy.py' 
#         and 'commit_message.txt'), after the test completes.
# 
#         Setup:
#             - Creates a 'toy.py' file with a simple print statement.
# 
#         Teardown:
#             - Removes 'toy.py' if it exists.
#             - Removes 'renamed-toy.py' if it exists.
#             - Removes 'commit_message.txt' if it exists.
#     """
#     # Setup: create a dummy files
#     with open('toy.py', 'w') as f:
#         f.write("print('This is a toy file')")
# 
#     yield
# 
#     # Teardown: remove created files
#     if os.path.exists('toy.py'):
#         os.remove('toy.py')
#     if os.path.exists('renamed-toy.py'):
#         os.remove('renamed-toy.py')
#     if os.path.exists('commit_message.txt'):
#         os.remove('commit_message.txt')

# @pytest.fixture 
# def setup_files_for_get_commit_message():
#     """
#         Fixture to set up and tear down files for testing.
# 
#         This fixture creates a dummy 'commit_message.txt' file before the test and ensures 
#         its removal after the test completes.
# 
#         Setup:
#             - Creates a 'commit_message.txt' file with a placeholder.
# 
#         Teardown:
#             - Removes 'commit_message.txt' if it exists.
#     """
#     # Setup: create a dummy files
#     with open('commit_message.txt', 'w') as f:
#         f.write("commit_message_goes_here")
# 
#     yield
# 
#     # Teardown: remove created files
#     if os.path.exists('commit_message.txt'):
#         os.remove('commit_message.txt')

@pytest.mark.skip(reason="Skipping this test temporarily")
def test_resolve_issue(setup_files_for_test_resolve_issue):
    """
    Test the 'resolve_issue' command of the CLI application.

    This test function uses the `runner.invoke` method to simulate running the 
    'resolve_issue' command. It verifies that the command completes successfully 
    and produces the expected output and side effects.

    Args:
        etup_files_for_test_resolve_issue: A fixture that sets up the necessary files for the test.

    Assertions:
        - The command exits with a status code of 0.
        - The output contains the messages indicating the start and end of the issue 
        resolution attempt.
        - The files 'renamed-toy.py' and 'commit_message.txt' are created.
        - The content of 'commit_message.txt' matches the expected commit message.
    """
    result = runner.invoke(app, ["resolve-issue"])
    assert result.exit_code == 0
    assert "Started Issue Resolution Attempt" in result.output
    assert "Finished Issue Resolution Attempt" in result.output
    assert os.path.exists('renamed-toy.py')
    assert os.path.exists('commit_message.txt')
    with open('commit_message.txt', 'r', encoding='utf-8') as file:
        commit_message = file.read()
    assert commit_message == "commit_message_goes_here"


@pytest.mark.skip(reason="Skipping this test temporarily")
def test_get_commit_message(setup_files_for_get_commit_message):
    """
    Test the 'get_commit_message' command of the CLI application.

    This test function uses the `runner.invoke` method to simulate running the 
    'get_commit_message' command. It verifies that the command completes successfully 
    and produces the expected output and side effects.

    Args:
        setup_files_for_get_commit_message: A fixture that sets up the necessary files 
        for the test.

    Assertions:
        - The command exits with a status code of 0.
        - The output contains the expected commit message.
        - The file 'commit_message.txt' is deleted after the command completes.
    """
    result = runner.invoke(app, ["get-commit-message"])
    assert result.exit_code == 0
    assert result.output.strip() == "commit_message_goes_here"
    assert not os.path.exists('commit_message.txt')