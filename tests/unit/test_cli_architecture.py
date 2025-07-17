"""
Tests for the CLI architecture components.

This module tests the BaseCommand class, CommandRegistry, and shared utilities
to ensure the refactored CLI architecture works correctly.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from rich.console import Console

from ingenious.cli.base import BaseCommand, CommandError, ExitCode, create_console
from ingenious.cli.commands.help import HelpCommand, StatusCommand
from ingenious.cli.registry import CommandRegistry
from ingenious.cli.utilities import (
    ConfigUtils,
    FileOperations,
    ValidationUtils,
)


class TestCommand(BaseCommand):
    """Test command implementation for testing BaseCommand."""

    def execute(self, test_arg: str = "default") -> str:
        """Test execute method."""
        return f"executed with {test_arg}"


class FailingCommand(BaseCommand):
    """Test command that raises exceptions."""

    def execute(self, should_fail: bool = True) -> None:
        """Test execute method that fails."""
        if should_fail:
            raise CommandError("Test error", ExitCode.VALIDATION_ERROR)


class TestBaseCommand:
    """Test cases for BaseCommand class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.console = Mock(spec=Console)
        self.console.get_time = Mock(return_value=0.0)
        self.console.is_jupyter = False
        self.console.is_interactive = True
        self.console.__enter__ = Mock(return_value=self.console)
        self.console.__exit__ = Mock(return_value=None)
        self.command = TestCommand(self.console)

    def test_command_initialization(self):
        """Test that BaseCommand initializes correctly."""
        assert self.command.console == self.console
        assert hasattr(self.command, "logger")
        assert self.command._progress is None

    def test_successful_execution(self):
        """Test successful command execution."""
        result = self.command.run(test_arg="test_value")
        assert result == "executed with test_value"

    def test_command_error_handling(self):
        """Test that CommandError is handled correctly."""
        failing_command = FailingCommand(self.console)

        with pytest.raises(Exception):  # typer.Exit or click.exceptions.Exit
            failing_command.run(should_fail=True)

    def test_print_methods(self):
        """Test that print methods call console correctly."""
        self.command.print_success("success message")
        self.command.print_error("error message")
        self.command.print_warning("warning message")
        self.command.print_info("info message")

        # Verify console.print was called
        assert self.console.print.call_count >= 4

    @patch("rich.progress.Progress")
    def test_progress_methods(self, mock_progress_class):
        """Test progress tracking methods."""
        mock_progress = Mock()
        mock_progress_class.return_value = mock_progress

        # Test start progress
        progress = self.command.start_progress("Testing...")
        assert progress is not None
        assert self.command._progress is not None

        # Test stop progress
        self.command.stop_progress()
        assert self.command._progress is None

    @patch.dict(
        os.environ,
        {
            "INGENIOUS_PROJECT_PATH": "/test/config.yml",
            "INGENIOUS_PROFILE_PATH": "/test/profiles.yml",
        },
    )
    @patch("pathlib.Path.exists")
    def test_validate_config_paths_success(self, mock_exists):
        """Test successful config path validation."""
        mock_exists.return_value = True

        paths = self.command.validate_config_paths()

        assert paths["config"] == "/test/config.yml"
        assert paths["profile"] == "/test/profiles.yml"

    @patch.dict(os.environ, {}, clear=True)
    @patch("pathlib.Path.exists")
    def test_validate_config_paths_fallback(self, mock_exists):
        """Test config path validation with fallback."""
        mock_exists.return_value = True

        with patch("pathlib.Path.cwd") as mock_cwd:
            mock_cwd.return_value = Path("/current")
            paths = self.command.validate_config_paths()

            assert paths["config"] == "/current/config.yml"
            assert paths["profile"] == "/current/profiles.yml"

    def test_check_environment_vars_success(self):
        """Test successful environment variable checking."""
        with patch.dict(os.environ, {"TEST_VAR": "test_value"}):
            env_vars = self.command.check_environment_vars(["TEST_VAR"])
            assert env_vars["TEST_VAR"] == "test_value"

    def test_check_environment_vars_missing(self):
        """Test environment variable checking with missing vars."""
        with pytest.raises(CommandError) as exc_info:
            self.command.check_environment_vars(["MISSING_VAR"])

        assert exc_info.value.exit_code == ExitCode.INVALID_CONFIG


class TestCommandRegistry:
    """Test cases for CommandRegistry class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.console = Mock(spec=Console)
        self.registry = CommandRegistry(self.console)

    def test_registry_initialization(self):
        """Test that CommandRegistry initializes correctly."""
        assert self.registry.console == self.console
        assert len(self.registry._commands) == 0
        assert len(self.registry._registered_modules) == 0

    def test_register_command(self):
        """Test command registration."""
        self.registry.register_command(
            "test", TestCommand, "Test command", "test_module"
        )

        assert "test" in self.registry._commands
        command_info = self.registry.get_command("test")
        assert command_info.name == "test"
        assert command_info.command_class == TestCommand
        assert command_info.description == "Test command"

    def test_register_command_conflict(self):
        """Test command registration conflict handling."""
        # Register first command
        self.registry.register_command("test", TestCommand, "First command")

        # Try to register conflicting command
        with pytest.raises(ValueError):
            self.registry.register_command("test", TestCommand, "Second command")

    def test_register_command_force_override(self):
        """Test force overriding command registration."""
        # Register first command
        self.registry.register_command("test", TestCommand, "First command")

        # Force override
        self.registry.register_command(
            "test", FailingCommand, "Second command", force=True
        )

        command_info = self.registry.get_command("test")
        assert command_info.command_class == FailingCommand

    def test_list_commands(self):
        """Test command listing."""
        self.registry.register_command("test1", TestCommand, "Test 1")
        self.registry.register_command("test2", FailingCommand, "Test 2", hidden=True)

        # Test listing visible commands
        visible_commands = self.registry.list_commands(include_hidden=False)
        assert len(visible_commands) == 1
        assert visible_commands[0].name == "test1"

        # Test listing all commands
        all_commands = self.registry.list_commands(include_hidden=True)
        assert len(all_commands) == 2

    def test_create_command_instance(self):
        """Test command instance creation."""
        self.registry.register_command("test", TestCommand, "Test command")

        instance = self.registry.create_command_instance("test")
        assert isinstance(instance, TestCommand)
        assert instance.console == self.console

    def test_validate_commands(self):
        """Test command validation."""
        self.registry.register_command("test", TestCommand, "Test command")

        errors = self.registry.validate_commands()
        assert len(errors) == 0  # TestCommand should be valid


class TestFileOperations:
    """Test cases for FileOperations utility class."""

    def test_ensure_directory(self):
        """Test directory creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_dir = Path(temp_dir) / "test_subdir"

            result = FileOperations.ensure_directory(test_dir)

            assert result == test_dir
            assert test_dir.exists()
            assert test_dir.is_dir()

    def test_backup_file(self):
        """Test file backup creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.txt"
            test_file.write_text("test content")

            backup_path = FileOperations.backup_file(test_file)

            assert backup_path is not None
            assert backup_path.exists()
            assert backup_path.read_text() == "test content"

    def test_safe_remove_file(self):
        """Test safe file removal."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.txt"
            test_file.write_text("test content")

            result = FileOperations.safe_remove(test_file)

            assert result is True
            assert not test_file.exists()

    def test_copy_tree_safe(self):
        """Test safe directory tree copying."""
        with tempfile.TemporaryDirectory() as temp_dir:
            src_dir = Path(temp_dir) / "source"
            dst_dir = Path(temp_dir) / "destination"

            # Create source structure
            src_dir.mkdir()
            (src_dir / "file.txt").write_text("content")

            result = FileOperations.copy_tree_safe(src_dir, dst_dir)

            assert result is True
            assert dst_dir.exists()
            assert (dst_dir / "file.txt").exists()


class TestValidationUtils:
    """Test cases for ValidationUtils utility class."""

    def test_validate_file_extension(self):
        """Test file extension validation."""
        assert ValidationUtils.validate_file_extension("test.yml", [".yml", ".yaml"])
        assert ValidationUtils.validate_file_extension("test.yaml", [".yml", ".yaml"])
        assert not ValidationUtils.validate_file_extension(
            "test.txt", [".yml", ".yaml"]
        )

    def test_validate_port(self):
        """Test port validation."""
        # Valid ports
        assert ValidationUtils.validate_port(80)[0] is True
        assert ValidationUtils.validate_port("8080")[0] is True
        assert ValidationUtils.validate_port(65535)[0] is True

        # Invalid ports
        assert ValidationUtils.validate_port(0)[0] is False
        assert ValidationUtils.validate_port(65536)[0] is False
        assert ValidationUtils.validate_port("not_a_number")[0] is False

    def test_validate_url(self):
        """Test URL validation."""
        # Valid URLs
        assert ValidationUtils.validate_url("https://example.com")[0] is True
        assert ValidationUtils.validate_url("http://localhost:8080")[0] is True

        # Invalid URLs
        assert ValidationUtils.validate_url("not_a_url")[0] is False
        assert ValidationUtils.validate_url("")[0] is False


class TestConfigUtils:
    """Test cases for ConfigUtils utility class."""

    @patch.dict(os.environ, {"INGENIOUS_PROJECT_PATH": "/env/config.yml"})
    def test_resolve_config_path_env_var(self):
        """Test config path resolution from environment variable."""
        path = ConfigUtils.resolve_config_path()
        assert path == Path("/env/config.yml")

    @patch.dict(os.environ, {}, clear=True)
    def test_resolve_config_path_default(self):
        """Test config path resolution to default."""
        with patch("pathlib.Path.cwd") as mock_cwd:
            mock_cwd.return_value = Path("/current")
            path = ConfigUtils.resolve_config_path()
            assert path == Path("/current/config.yml")

    def test_load_env_file(self):
        """Test environment file loading."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write("KEY1=value1\nKEY2=value2\n# Comment\nKEY3='quoted value'")
            f.flush()

            env_vars = ConfigUtils.load_env_file(f.name)

            assert env_vars["KEY1"] == "value1"
            assert env_vars["KEY2"] == "value2"
            assert env_vars["KEY3"] == "quoted value"
            assert "Comment" not in env_vars

        # Clean up
        os.unlink(f.name)


class TestCreateConsole:
    """Test cases for console creation function."""

    def test_create_console(self):
        """Test console creation with custom theme."""
        console = create_console()

        assert isinstance(console, Console)
        # Note: Rich Console doesn't always expose theme attribute directly


class TestHelpCommand:
    """Test cases for HelpCommand."""

    def setup_method(self):
        """Set up test fixtures."""
        self.console = Mock(spec=Console)
        self.command = HelpCommand(self.console)

    def test_general_help(self):
        """Test general help display."""
        self.command.execute()

        # Verify console.print was called multiple times
        assert self.console.print.call_count > 0

    def test_specific_help_topics(self):
        """Test specific help topics."""
        topics = ["setup", "workflows", "config", "deployment"]

        for topic in topics:
            self.console.reset_mock()
            self.command.execute(topic=topic)
            assert self.console.print.call_count > 0

    def test_invalid_help_topic(self):
        """Test invalid help topic handling."""
        with pytest.raises(CommandError):
            self.command.execute(topic="invalid_topic")


class TestStatusCommand:
    """Test cases for StatusCommand."""

    def setup_method(self):
        """Set up test fixtures."""
        self.console = Mock(spec=Console)
        self.command = StatusCommand(self.console)

    @patch.dict(
        os.environ,
        {
            "INGENIOUS_PROJECT_PATH": "/test/config.yml",
            "INGENIOUS_PROFILE_PATH": "/test/profiles.yml",
        },
    )
    @patch("pathlib.Path.exists")
    def test_status_check(self, mock_exists):
        """Test status checking."""
        mock_exists.return_value = True

        self.command.execute()

        # Verify console output was generated
        assert self.console.print.call_count > 0


# Run tests if script is executed directly
if __name__ == "__main__":
    pytest.main([__file__])
