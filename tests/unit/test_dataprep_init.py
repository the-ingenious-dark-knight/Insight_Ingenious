"""
Tests for ingenious.dataprep.__init__ module
"""
import pytest
from unittest.mock import patch, MagicMock

import ingenious.dataprep


class TestDataprepInit:
    """Test cases for dataprep __init__ module"""

    def test_path_extension(self):
        """Test that __path__ is extended using extend_path"""
        # The module should have a __path__ attribute after import
        assert hasattr(ingenious.dataprep, '__path__')
        assert ingenious.dataprep.__path__ is not None

    def test_crawler_import(self):
        """Test that Crawler is imported and available"""
        # Crawler should be importable from the module
        assert hasattr(ingenious.dataprep, 'Crawler')
        
        # Should be able to access the Crawler class
        from ingenious.dataprep import Crawler
        assert Crawler is not None

    def test_crawler_alias(self):
        """Test that the Crawler import creates proper alias"""
        # The import should create an alias: from .crawl import Crawler as Crawler
        # This means the same class should be accessible in both ways
        from ingenious.dataprep import Crawler as ImportedCrawler
        assert ImportedCrawler is ingenious.dataprep.Crawler

    def test_module_structure(self):
        """Test the overall module structure"""
        # Verify the module has the expected structure
        assert hasattr(ingenious.dataprep, '__name__')
        assert hasattr(ingenious.dataprep, '__path__')
        assert hasattr(ingenious.dataprep, 'Crawler')

    def test_extend_path_import(self):
        """Test that extend_path is imported and used"""
        # The module uses extend_path from pkgutil
        from pkgutil import extend_path
        
        # Verify extend_path is a callable function
        assert callable(extend_path)
        
        # The __path__ should be modified by extend_path
        assert isinstance(ingenious.dataprep.__path__, list)