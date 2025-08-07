"""
Tests for ingenious.dataprep.crawl.__init__ module
"""
import pytest

import ingenious.dataprep.crawl


class TestCrawlInit:
    """Test cases for crawl __init__ module"""

    def test_crawler_import(self):
        """Test that Crawler is imported and available"""
        # Crawler should be importable from the module
        assert hasattr(ingenious.dataprep.crawl, 'Crawler')
        
        # Should be able to access the Crawler class
        from ingenious.dataprep.crawl import Crawler
        assert Crawler is not None

    def test_crawler_alias(self):
        """Test that the Crawler import creates proper alias"""
        # The import should create an alias: from .crawler import Crawler as Crawler
        # This means the same class should be accessible in both ways
        from ingenious.dataprep.crawl import Crawler as ImportedCrawler
        assert ImportedCrawler is ingenious.dataprep.crawl.Crawler

    def test_module_structure(self):
        """Test the overall module structure"""
        # Verify the module has the expected structure
        assert hasattr(ingenious.dataprep.crawl, '__name__')
        assert hasattr(ingenious.dataprep.crawl, 'Crawler')

    def test_import_statement_works(self):
        """Test that the import statement in __init__.py works correctly"""
        # Test direct import
        crawler_direct = ingenious.dataprep.crawl.Crawler
        
        # Test import from statement
        from ingenious.dataprep.crawl import Crawler
        
        # They should be the same object
        assert crawler_direct is Crawler

    def test_can_import_without_error(self):
        """Test that the module can be imported without errors"""
        # This test passes if the import at the top succeeds
        import ingenious.dataprep.crawl as crawl
        assert crawl is not None

    def test_crawler_is_available_as_attribute(self):
        """Test that Crawler is available as module attribute"""
        assert hasattr(ingenious.dataprep.crawl, 'Crawler')
        crawler = ingenious.dataprep.crawl.Crawler
        assert crawler is not None

    def test_module_name_matches_package_structure(self):
        """Test that module name matches the expected package structure"""
        module_name = ingenious.dataprep.crawl.__name__
        assert module_name == 'ingenious.dataprep.crawl'
        assert 'dataprep' in module_name
        assert 'crawl' in module_name

    def test_single_export(self):
        """Test that the module primarily exports Crawler"""
        # The module should mainly export Crawler
        # We can test this by checking that Crawler is the main public interface
        assert hasattr(ingenious.dataprep.crawl, 'Crawler')
        
        # Test that we can import Crawler successfully
        from ingenious.dataprep.crawl import Crawler
        assert Crawler is not None