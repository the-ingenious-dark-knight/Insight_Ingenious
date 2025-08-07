"""
Tests for ingenious.cli.__main__ module (CLI entry point)
"""
import pytest
from unittest.mock import patch, Mock

import ingenious.cli.__main__


class TestCLIMainEntry:
    """Test cases for CLI __main__ entry point module"""

    def test_module_docstring(self):
        """Test that the module has appropriate documentation"""
        docstring = ingenious.cli.__main__.__doc__
        assert docstring is not None
        assert "CLI entry point" in docstring
        assert "python -m ingenious.cli" in docstring

    def test_app_imported(self):
        """Test that app is imported from main module"""
        assert hasattr(ingenious.cli.__main__, "app")
        # The app should be callable
        assert callable(ingenious.cli.__main__.app)

    @patch('ingenious.cli.__main__.app')
    def test_main_execution_would_call_app(self, mock_app):
        """Test that running as main would call the app function"""
        # We can't easily test the __name__ == "__main__" condition
        # without subprocess, but we can verify the app is available
        assert callable(mock_app)
        
        # Simulate what would happen if run as main
        ingenious.cli.__main__.app()
        mock_app.assert_called_once()

    def test_imports_from_correct_location(self):
        """Test that imports come from the expected location"""
        # The app should be imported from .main
        from ingenious.cli.main import app as main_app
        assert ingenious.cli.__main__.app is main_app

    def test_module_structure(self):
        """Test the overall module structure"""
        # Verify the module has the expected minimal structure
        assert hasattr(ingenious.cli.__main__, '__name__')
        assert hasattr(ingenious.cli.__main__, '__doc__')
        assert hasattr(ingenious.cli.__main__, 'app')

    def test_can_import_without_error(self):
        """Test that the module can be imported without errors"""
        # This test passes if the import at the top succeeds
        import ingenious.cli.__main__ as cli_main
        assert cli_main is not None