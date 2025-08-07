"""
Tests for ingenious.utils.lazy_group module
"""

from unittest.mock import Mock, patch

import pytest
from click import Command, Context
from typer.core import TyperGroup

from ingenious.utils.lazy_group import LazyGroup


class TestLazyGroup:
    """Test cases for LazyGroup class"""

    def test_init(self):
        """Test LazyGroup initialization"""
        group = LazyGroup()
        assert isinstance(group, TyperGroup)
        assert hasattr(group, "_loaders")
        assert "document-processing" in group._loaders
        assert "dataprep" in group._loaders

    def test_list_commands_basic(self):
        """Test list_commands returns sorted command names"""
        group = LazyGroup()
        ctx = Mock(spec=Context)

        # Mock the parent method to return some commands
        with patch.object(TyperGroup, "list_commands", return_value=["cmd1", "cmd2"]):
            commands = group.list_commands(ctx)

            # Should include both parent commands and lazy-loaded commands
            assert "cmd1" in commands
            assert "cmd2" in commands
            assert "document-processing" in commands
            assert "dataprep" in commands
            # Should be sorted
            assert commands == sorted(commands)

    def test_list_commands_deduplication(self):
        """Test list_commands removes duplicates"""
        group = LazyGroup()
        ctx = Mock(spec=Context)

        # Mock parent to return a command that's also in loaders
        with patch.object(
            TyperGroup, "list_commands", return_value=["dataprep", "other-cmd"]
        ):
            commands = group.list_commands(ctx)

            # Should not have duplicates
            assert commands.count("dataprep") == 1
            assert "other-cmd" in commands
            assert "document-processing" in commands

    def test_get_command_main_command_exists(self):
        """Test get_command returns main command when it exists"""
        group = LazyGroup()
        ctx = Mock(spec=Context)
        mock_command = Mock(spec=Command)

        with patch.object(TyperGroup, "get_command", return_value=mock_command):
            result = group.get_command(ctx, "some-main-command")
            assert result is mock_command

    def test_get_command_unknown_command(self):
        """Test get_command returns None for unknown commands"""
        group = LazyGroup()
        ctx = Mock(spec=Context)

        with patch.object(TyperGroup, "get_command", return_value=None):
            result = group.get_command(ctx, "unknown-command")
            assert result is None

    @patch("ingenious.utils.lazy_group.importlib.import_module")
    @patch("ingenious.utils.lazy_group.typer.main.get_command")
    def test_get_command_lazy_load_success(self, mock_get_command, mock_import):
        """Test successful lazy loading of a command"""
        group = LazyGroup()
        ctx = Mock(spec=Context)

        # Mock the module and attribute
        mock_module = Mock()
        mock_sub_app = Mock()
        mock_module.doc_app = mock_sub_app
        mock_import.return_value = mock_module

        # Mock typer.main.get_command
        mock_click_command = Mock(spec=Command)
        mock_get_command.return_value = mock_click_command

        with patch.object(TyperGroup, "get_command", return_value=None):
            result = group.get_command(ctx, "document-processing")

            assert result is mock_click_command
            mock_import.assert_called_once_with("ingenious.document_processing.cli")
            mock_get_command.assert_called_once_with(mock_sub_app)

    @patch("ingenious.utils.lazy_group.importlib.import_module")
    def test_get_command_lazy_load_already_click_command(self, mock_import):
        """Test lazy loading when sub_app is already a Click command"""
        group = LazyGroup()
        ctx = Mock(spec=Context)

        # Mock the module and attribute - sub_app is already a Command
        mock_module = Mock()
        mock_sub_app = Mock(spec=Command)
        mock_module.doc_app = mock_sub_app
        mock_import.return_value = mock_module

        with patch.object(TyperGroup, "get_command", return_value=None):
            result = group.get_command(ctx, "document-processing")

            assert result is mock_sub_app
            mock_import.assert_called_once_with("ingenious.document_processing.cli")

    @patch("ingenious.utils.lazy_group.importlib.import_module")
    @patch("ingenious.utils.lazy_group.typer.echo")
    def test_get_command_lazy_load_module_not_found(self, mock_echo, mock_import):
        """Test lazy loading when module is not found"""
        import typer

        group = LazyGroup()
        ctx = Mock(spec=Context)

        # Mock ModuleNotFoundError
        mock_import.side_effect = ModuleNotFoundError(
            "No module named 'ingenious.document_processing.cli'"
        )

        with patch.object(TyperGroup, "get_command", return_value=None):
            # Should raise typer.Exit
            with pytest.raises(typer.Exit) as exc_info:
                group.get_command(ctx, "document-processing")

            # Check the exit code
            assert exc_info.value.exit_code == 1

            # Should display helpful message
            mock_echo.assert_called_once()
            error_msg = mock_echo.call_args[0][0]
            assert "[document-processing] extra not installed" in error_msg
            assert "pip install 'insight-ingenious[document-processing]'" in error_msg

    def test_loaders_registry_structure(self):
        """Test the structure of the _loaders registry"""
        group = LazyGroup()

        # Check document-processing entry
        doc_loader = group._loaders["document-processing"]
        assert doc_loader[0] == "ingenious.document_processing.cli"
        assert doc_loader[1] == "doc_app"
        assert doc_loader[2] == "document-processing"

        # Check dataprep entry
        dataprep_loader = group._loaders["dataprep"]
        assert dataprep_loader[0] == "ingenious.dataprep.cli"
        assert dataprep_loader[1] == "dataprep"
        assert dataprep_loader[2] == "dataprep"

    def test_class_exports(self):
        """Test that LazyGroup is properly exported"""
        from ingenious.utils.lazy_group import __all__

        assert "LazyGroup" in __all__
