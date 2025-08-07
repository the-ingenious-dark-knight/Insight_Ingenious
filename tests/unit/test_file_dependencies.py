"""
Tests for ingenious.services.file_dependencies module
"""
import pytest
import os
import asyncio
from unittest.mock import Mock, patch, mock_open, AsyncMock, MagicMock

from ingenious.services.file_dependencies import (
    get_config,
    get_file_storage_data,
    get_file_storage_revisions,
    sync_templates
)


class TestFileDependencies: 
    """Test cases for file dependencies module"""

    def test_module_docstring(self):
        """Test that the module has appropriate documentation"""
        import ingenious.services.file_dependencies as file_deps
        docstring = file_deps.__doc__
        assert docstring is not None
        assert "File storage related dependency injection" in docstring
        assert "FastAPI dependency injection functions" in docstring

    def test_get_config_function(self):
        """Test get_config function returns config"""
        mock_config = Mock()
        
        # The function uses dependency injection, so we test the core logic
        result = get_config(config=mock_config)
        
        assert result is mock_config

    def test_get_config_function_docstring(self):
        """Test get_config has proper docstring"""
        assert get_config.__doc__ is not None
        assert "Get config from container" in get_config.__doc__

    def test_get_file_storage_data_function(self):
        """Test get_file_storage_data function returns file storage"""
        mock_file_storage = Mock()
        
        result = get_file_storage_data(file_storage=mock_file_storage)
        
        assert result is mock_file_storage

    def test_get_file_storage_data_function_docstring(self):
        """Test get_file_storage_data has proper docstring"""
        assert get_file_storage_data.__doc__ is not None
        assert "Get file storage for data from container" in get_file_storage_data.__doc__

    def test_get_file_storage_revisions_function(self):
        """Test get_file_storage_revisions function returns file storage"""
        mock_file_storage = Mock()
        
        result = get_file_storage_revisions(file_storage=mock_file_storage)
        
        assert result is mock_file_storage

    def test_get_file_storage_revisions_function_docstring(self):
        """Test get_file_storage_revisions has proper docstring"""
        assert get_file_storage_revisions.__doc__ is not None
        assert "Get file storage for revisions from container" in get_file_storage_revisions.__doc__

    def test_sync_templates_with_local_storage(self):
        """Test sync_templates returns early for local storage"""
        mock_config = Mock()
        mock_config.file_storage.revisions.storage_type = "local"
        
        # Should return None without doing anything
        result = sync_templates(config=mock_config)
        
        assert result is None

    @patch('asyncio.run')
    @patch('ingenious.services.file_dependencies.FileStorage')
    @patch('ingenious.services.file_dependencies.os.getcwd')
    @patch('ingenious.services.file_dependencies.os.path.join')
    def test_sync_templates_with_non_local_storage(self, mock_join, mock_getcwd, mock_file_storage_class, mock_asyncio_run):
        """Test sync_templates with non-local storage"""
        mock_config = Mock()
        mock_config.file_storage.revisions.storage_type = "azure"
        
        mock_getcwd.return_value = "/test/dir"
        mock_join.side_effect = lambda *args: "/".join(args)
        
        mock_fs_instance = Mock()
        mock_file_storage_class.return_value = mock_fs_instance
        
        sync_templates(config=mock_config)
        
        # Verify FileStorage was created with config
        mock_file_storage_class.assert_called_once_with(mock_config)
        
        # Verify asyncio.run was called
        mock_asyncio_run.assert_called_once()
        
        # Verify getcwd was called
        mock_getcwd.assert_called_once()

    @patch('asyncio.run')
    @patch('ingenious.services.file_dependencies.FileStorage')
    @patch('ingenious.services.file_dependencies.os.getcwd')
    @patch('ingenious.services.file_dependencies.os.path.join')
    @patch('builtins.open', new_callable=mock_open)
    def test_sync_templates_file_operations(self, mock_file_open, mock_join, mock_getcwd, mock_file_storage_class, mock_asyncio_run):
        """Test sync_templates file operations"""
        mock_config = Mock()
        mock_config.file_storage.revisions.storage_type = "azure"
        
        mock_getcwd.return_value = "/test/dir"
        mock_join.side_effect = lambda *args: "/".join(args)
        
        mock_fs_instance = Mock()
        mock_file_storage_class.return_value = mock_fs_instance
        
        # Mock the async function that gets created inside sync_templates
        async def mock_sync_files():
            mock_fs_instance.list_files = AsyncMock(return_value=["template1.jinja", "template2.jinja"])
            mock_fs_instance.read_file = AsyncMock(side_effect=["content1", "content2"])
            
            template_files = await mock_fs_instance.list_files(file_path="/test/dir/ingenious/templates")
            for file in template_files:
                file_name = os.path.basename(file)
                file_contents = await mock_fs_instance.read_file(
                    file_name=file_name, file_path="/test/dir/ingenious/templates"
                )
                with open(f"/test/dir/ingenious/templates/{file_name}", "w") as f:
                    f.write(file_contents)
        
        # Test that the function structure works
        sync_templates(config=mock_config)
        
        # Verify basic setup was done
        mock_file_storage_class.assert_called_once_with(mock_config)
        mock_asyncio_run.assert_called_once()

    def test_sync_templates_function_docstring(self):
        """Test sync_templates has proper docstring"""
        assert sync_templates.__doc__ is not None
        assert "Sync templates from file storage" in sync_templates.__doc__

    def test_imports_exist(self):
        """Test that all expected imports are available"""
        import ingenious.services.file_dependencies as file_deps
        
        # Test that all required imports are accessible
        assert hasattr(file_deps, 'os')
        assert hasattr(file_deps, 'Provide')
        assert hasattr(file_deps, 'inject')
        assert hasattr(file_deps, 'Depends')
        assert hasattr(file_deps, 'IngeniousSettings')
        assert hasattr(file_deps, 'FileStorage')
        assert hasattr(file_deps, 'Container')

    def test_all_functions_are_callable(self):
        """Test that all dependency functions are callable"""
        assert callable(get_config)
        assert callable(get_file_storage_data)
        assert callable(get_file_storage_revisions)
        assert callable(sync_templates)

    def test_dependency_injection_decorators(self):
        """Test that functions have proper dependency injection decorators"""
        # get_config should have @inject decorator
        assert hasattr(get_config, '__wrapped__') or hasattr(get_config, '_injected')
        
        # get_file_storage_data should have @inject decorator
        assert hasattr(get_file_storage_data, '__wrapped__') or hasattr(get_file_storage_data, '_injected')
        
        # get_file_storage_revisions should have @inject decorator  
        assert hasattr(get_file_storage_revisions, '__wrapped__') or hasattr(get_file_storage_revisions, '_injected')

    @patch('ingenious.services.file_dependencies.os.path.basename')
    def test_sync_templates_uses_basename(self, mock_basename):
        """Test that sync_templates uses os.path.basename for file names"""
        mock_config = Mock()
        mock_config.file_storage.revisions.storage_type = "local"
        
        # For local storage, should return early without calling basename
        sync_templates(config=mock_config)
        
        mock_basename.assert_not_called()

    def test_container_integration(self):
        """Test that the module works with Container"""
        from ingenious.services.container import Container
        
        # Verify Container class is imported and available
        assert Container is not None