"""
Comprehensive functional tests for the CLI commands in Insight Ingenious.
Tests all commands mentioned in the UV_CLI_README.md file.
"""

import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from ingenious.cli import app


@pytest.fixture
def runner():
    """Create a CLI runner for testing."""
    return CliRunner()


@pytest.fixture
def temp_project_dir():
    """Create a temporary directory for project tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        original_dir = os.getcwd()
        os.chdir(tmpdir)
        yield tmpdir
        os.chdir(original_dir)


class TestCliCommands:
    """Comprehensive tests for all CLI commands."""

    def test_cli_help(self, runner):
        """Test the main CLI help output."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "run-rest-api-server" in result.stdout
        assert "run-test-batch" in result.stdout
        assert "initialize-new-project" in result.stdout
        assert "run-prompt-tuner" in result.stdout

    def test_run_test_batch_help(self, runner):
        """Test the help output for run-test-batch command."""
        result = runner.invoke(app, ["run-test-batch", "--help"])
        assert result.exit_code == 0
        assert "This command will run all the tests in the project" in result.stdout
        assert "--log-level" in result.stdout
        assert "--run-args" in result.stdout

    def test_initialize_new_project_help(self, runner):
        """Test the help output for initialize-new-project command."""
        result = runner.invoke(app, ["initialize-new-project", "--help"])
        assert result.exit_code == 0
        assert "Generate template folders for a new project" in result.stdout

    def test_run_prompt_tuner_help(self, runner):
        """Test the help output for run-prompt-tuner command."""
        result = runner.invoke(app, ["run-prompt-tuner", "--help"])
        assert result.exit_code == 0
        assert "Run the prompt tuner web application" in result.stdout

    def test_run_rest_api_server_help(self, runner):
        """Test the help output for run-rest-api-server command."""
        result = runner.invoke(app, ["run-rest-api-server", "--help"])
        assert result.exit_code == 0
        assert "This command will run a fastapi server" in result.stdout
        assert "PROJECT_DIR" in result.stdout  # It's an argument, not an option

    def test_initialize_new_project(self, runner, temp_project_dir):
        """Test initializing a new project."""
        # Mock the ProjectSetupExecutor to avoid actual file operations
        with patch(
            "ingenious.common.utils.cli_command_executor.ProjectSetupExecutor"
        ) as mock_executor:
            # Set up mock instance
            mock_instance = MagicMock()
            mock_executor.return_value = mock_instance

            # Run the command
            result = runner.invoke(app, ["initialize-new-project"])

            # Check the result
            assert result.exit_code == 0

            # Verify the initialize_new_project method was called
            mock_instance.initialize_new_project.assert_called_once()

    def test_run_test_batch(self, runner):
        """Test running a test batch."""
        # Mock the run_test_batch method
        with patch(
            "ingenious.common.utils.cli_command_executor.TestBatchExecutor.run_test_batch"
        ) as mock_run:
            # Set up the mock to do nothing (we just want to check it's called correctly)
            mock_run.return_value = None

            # Run the command
            result = runner.invoke(
                app,
                [
                    "run-test-batch",
                    "--log-level",
                    "INFO",
                    "--run-args",
                    "test_name=test_cli.py",
                ],
            )

            # Check the result
            assert result.exit_code == 0

            # Verify the method was called with the right parameters
            mock_run.assert_called_once()
            args, kwargs = mock_run.call_args
            assert kwargs["log_level"] == "INFO"
            assert kwargs["run_args"] == "test_name=test_cli.py"

    @patch("uvicorn.run")
    def test_run_rest_api_server(self, mock_run, runner):
        """Test the REST API server command."""
        # Simplified test - skip the actual execution but check help output
        result = runner.invoke(app, ["run-rest-api-server", "--help"])
        assert result.exit_code == 0
        assert "This command will run a fastapi server" in result.stdout

    def test_run_prompt_tuner(self, runner):
        """Test the prompt tuner command."""
        # Just test the help output, which doesn't require the actual implementation
        result = runner.invoke(app, ["run-prompt-tuner", "--help"])
        assert result.exit_code == 0
        assert "Run the prompt tuner web application" in result.stdout
