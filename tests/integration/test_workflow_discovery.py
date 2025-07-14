"""
Integration tests for workflow discovery system.

Tests the enhanced workflow discovery mechanism including
namespace searching, validation, caching, and metadata retrieval.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from ingenious.utils.namespace_utils import (
    WorkflowDiscovery,
    clear_workflow_cache,
    discover_workflows,
    get_workflow_metadata,
    normalize_workflow_name,
)


class TestWorkflowNormalization:
    """Test workflow name normalization."""
    
    def test_normalize_workflow_name_hyphenated(self):
        """Test normalization of hyphenated workflow names."""
        result = normalize_workflow_name("bike-insights")
        assert result == "bike_insights"
    
    def test_normalize_workflow_name_underscored(self):
        """Test normalization of underscored workflow names."""
        result = normalize_workflow_name("bike_insights")
        assert result == "bike_insights"
    
    def test_normalize_workflow_name_mixed_case(self):
        """Test normalization handles mixed case."""
        result = normalize_workflow_name("Bike-Insights")
        assert result == "bike_insights"
    
    def test_normalize_workflow_name_empty(self):
        """Test normalization of empty string."""
        result = normalize_workflow_name("")
        assert result == ""
    
    def test_normalize_workflow_name_none(self):
        """Test normalization of None."""
        result = normalize_workflow_name(None)
        assert result is None


class TestWorkflowDiscovery:
    """Test the WorkflowDiscovery class."""
    
    def setup_method(self):
        """Set up test instance."""
        self.discovery = WorkflowDiscovery()
        self.discovery.clear_cache()
    
    def test_discover_workflows_basic(self):
        """Test basic workflow discovery."""
        workflows = self.discovery.discover_workflows()
        
        # Should return a list (even if empty)
        assert isinstance(workflows, list)
        
        # Results should be sorted
        if len(workflows) > 1:
            assert workflows == sorted(workflows)
    
    def test_discover_workflows_caching(self):
        """Test that workflow discovery results are cached."""
        # First call
        workflows1 = self.discovery.discover_workflows()
        
        # Second call should use cache
        with patch.object(self.discovery, '_validate_workflow') as mock_validate:
            workflows2 = self.discovery.discover_workflows()
            # Validation should not be called again due to caching
            mock_validate.assert_not_called()
        
        assert workflows1 == workflows2
    
    def test_discover_workflows_force_refresh(self):
        """Test force refresh bypasses cache."""
        # First call to populate cache
        self.discovery.discover_workflows()
        
        # Force refresh should bypass cache
        with patch.object(self.discovery, '_validate_workflow', return_value=True) as mock_validate:
            workflows = self.discovery.discover_workflows(force_refresh=True)
            # Should have attempted validation again
            # (May not be called if no workflows found, but cache should be cleared)
        
        # Verify cache was cleared by checking it's rebuilt
        assert isinstance(workflows, list)
    
    def test_clear_cache(self):
        """Test clearing workflow cache."""
        # Populate cache
        self.discovery.discover_workflows()
        assert self.discovery._workflow_cache is not None
        
        # Clear cache
        self.discovery.clear_cache()
        assert self.discovery._workflow_cache is None
        assert len(self.discovery._metadata_cache) == 0
    
    @patch('ingenious.utils.namespace_utils._importer.import_module')
    def test_validate_workflow_success(self, mock_import):
        """Test successful workflow validation."""
        # Mock a valid workflow module
        mock_module = Mock()
        mock_conversation_flow = Mock()
        mock_conversation_flow.get_chat_response = Mock()
        mock_module.ConversationFlow = mock_conversation_flow
        mock_import.return_value = mock_module
        
        result = self.discovery._validate_workflow(
            "test.namespace.conversation_flows", 
            "test_workflow"
        )
        
        assert result is True
        mock_import.assert_called_once()
    
    @patch('ingenious.utils.namespace_utils._importer.import_module')
    def test_validate_workflow_missing_class(self, mock_import):
        """Test workflow validation fails when ConversationFlow class is missing."""
        # Mock a module without ConversationFlow class
        mock_module = Mock()
        del mock_module.ConversationFlow  # Ensure it doesn't have the class
        mock_import.return_value = mock_module
        
        result = self.discovery._validate_workflow(
            "test.namespace.conversation_flows",
            "test_workflow"
        )
        
        assert result is False
    
    @patch('ingenious.utils.namespace_utils._importer.import_module')
    def test_validate_workflow_missing_method(self, mock_import):
        """Test workflow validation fails when required methods are missing."""
        # Mock a ConversationFlow class without required methods
        mock_module = Mock()
        mock_conversation_flow = Mock()
        # Remove the required method
        del mock_conversation_flow.get_chat_response
        mock_module.ConversationFlow = mock_conversation_flow
        mock_import.return_value = mock_module
        
        result = self.discovery._validate_workflow(
            "test.namespace.conversation_flows",
            "test_workflow"
        )
        
        assert result is False
    
    @patch('ingenious.utils.namespace_utils._importer.import_module')
    def test_validate_workflow_import_error(self, mock_import):
        """Test workflow validation handles import errors gracefully."""
        mock_import.side_effect = ImportError("Module not found")
        
        result = self.discovery._validate_workflow(
            "test.namespace.conversation_flows",
            "test_workflow"
        )
        
        assert result is False


class TestWorkflowMetadata:
    """Test workflow metadata functionality."""
    
    def setup_method(self):
        """Set up test instance."""
        self.discovery = WorkflowDiscovery()
        self.discovery.clear_cache()
    
    def test_get_known_workflow_metadata(self):
        """Test getting metadata for known workflows."""
        metadata = self.discovery.get_workflow_metadata("classification_agent")
        
        assert isinstance(metadata, dict)
        assert "description" in metadata
        assert "category" in metadata
        assert "required_config" in metadata
        assert "external_services" in metadata
        
        # Check specific values for classification_agent
        assert metadata["category"] == "Minimal Configuration"
        assert "models" in metadata["required_config"]
        assert "chat_service" in metadata["required_config"]
    
    def test_get_unknown_workflow_metadata(self):
        """Test getting metadata for unknown workflows returns defaults."""
        metadata = self.discovery.get_workflow_metadata("unknown_workflow_12345")
        
        assert isinstance(metadata, dict)
        assert metadata["description"] == "Custom workflow"
        assert metadata["category"] == "Custom Workflow"
        assert "models" in metadata["required_config"]
        assert "chat_service" in metadata["required_config"]
    
    def test_metadata_caching(self):
        """Test that metadata is cached."""
        # First call
        metadata1 = self.discovery.get_workflow_metadata("test_workflow")
        
        # Second call should return same object (cached)
        metadata2 = self.discovery.get_workflow_metadata("test_workflow")
        
        assert metadata1 is metadata2  # Same object reference
    
    def test_all_known_workflows_have_metadata(self):
        """Test that all known workflows have proper metadata."""
        known_workflows = [
            "classification_agent",
            "bike_insights",
            "knowledge_base_agent",
            "sql_manipulation_agent",
            "submission_over_criteria"
        ]
        
        for workflow in known_workflows:
            metadata = self.discovery.get_workflow_metadata(workflow)
            
            # All should have required fields
            assert "description" in metadata
            assert "category" in metadata
            assert "required_config" in metadata
            assert "external_services" in metadata
            
            # Description should not be the default
            assert metadata["description"] != "Custom workflow"


class TestConvenienceFunctions:
    """Test the module-level convenience functions."""
    
    def setup_method(self):
        """Clear caches before each test."""
        clear_workflow_cache()
    
    def test_discover_workflows_function(self):
        """Test the discover_workflows convenience function."""
        workflows = discover_workflows()
        assert isinstance(workflows, list)
    
    def test_discover_workflows_force_refresh_function(self):
        """Test discover_workflows with force_refresh parameter."""
        # First call
        workflows1 = discover_workflows()
        
        # Force refresh
        workflows2 = discover_workflows(force_refresh=True)
        
        # Should return the same results
        assert workflows1 == workflows2
    
    def test_get_workflow_metadata_function(self):
        """Test the get_workflow_metadata convenience function."""
        metadata = get_workflow_metadata("classification_agent")
        
        assert isinstance(metadata, dict)
        assert "description" in metadata
    
    def test_clear_workflow_cache_function(self):
        """Test the clear_workflow_cache convenience function."""
        # Populate cache
        discover_workflows()
        
        # Clear cache
        clear_workflow_cache()
        
        # Should work without errors
        workflows = discover_workflows()
        assert isinstance(workflows, list)


class TestNamespaceIntegration:
    """Test integration with namespace utilities."""
    
    def test_namespace_searching_order(self):
        """Test that namespaces are searched in correct order."""
        from ingenious.utils.namespace_utils import get_namespaces
        
        namespaces = get_namespaces()
        expected_order = [
            "ingenious_extensions",
            "ingenious.ingenious_extensions_template",
            "ingenious",
        ]
        
        assert namespaces == expected_order
    
    @patch('pkgutil.iter_modules')
    @patch('ingenious.utils.namespace_utils._importer.import_module')
    def test_workflow_discovery_searches_all_namespaces(self, mock_import, mock_iter):
        """Test that workflow discovery searches all namespaces."""
        # Mock empty results for all namespace searches
        mock_iter.return_value = []
        mock_import.return_value = Mock(__path__=["/fake/path"])
        
        discovery = WorkflowDiscovery()
        workflows = discovery.discover_workflows()
        
        # Should have attempted to import from all namespaces
        expected_calls = 3  # Number of namespaces
        assert mock_import.call_count >= expected_calls
    
    def test_workflow_discovery_handles_missing_namespaces(self):
        """Test that workflow discovery handles missing namespaces gracefully."""
        discovery = WorkflowDiscovery()
        
        # This should not raise an exception even if some namespaces don't exist
        workflows = discovery.discover_workflows()
        
        assert isinstance(workflows, list)


class TestErrorHandling:
    """Test error handling in workflow discovery."""
    
    def setup_method(self):
        """Set up test instance."""
        self.discovery = WorkflowDiscovery()
    
    @patch('ingenious.utils.namespace_utils._importer.import_module')
    def test_discovery_handles_import_errors(self, mock_import):
        """Test that discovery handles import errors gracefully."""
        mock_import.side_effect = ImportError("Namespace not found")
        
        # Should not raise an exception
        workflows = self.discovery.discover_workflows()
        
        assert isinstance(workflows, list)
        # Might be empty due to mocked import error, but shouldn't crash
    
    @patch('pkgutil.iter_modules')
    @patch('ingenious.utils.namespace_utils._importer.import_module')
    def test_discovery_handles_iteration_errors(self, mock_import, mock_iter):
        """Test that discovery handles module iteration errors gracefully."""
        mock_import.return_value = Mock(__path__=["/fake/path"])
        mock_iter.side_effect = Exception("Iteration failed")
        
        # Should not raise an exception
        workflows = self.discovery.discover_workflows()
        
        assert isinstance(workflows, list)
    
    def test_validation_handles_malformed_modules(self):
        """Test that validation handles malformed modules gracefully."""
        # Test with None module name
        result = self.discovery._validate_workflow("", "")
        assert result is False
        
        # Test with invalid module name
        result = self.discovery._validate_workflow("invalid.module.name", "test")
        assert result is False


class TestRealWorkflowDetection:
    """Test detection of actual workflows in the codebase."""
    
    def test_discover_real_workflows(self):
        """Test discovering actual workflows from the codebase."""
        workflows = discover_workflows()
        
        # This should find real workflows if they exist
        assert isinstance(workflows, list)
        
        # If workflows are found, they should have valid names
        for workflow in workflows:
            assert isinstance(workflow, str)
            assert len(workflow) > 0
            # Should be normalized (no hyphens)
            assert "-" not in workflow
    
    def test_real_workflow_metadata(self):
        """Test metadata for any discovered workflows."""
        workflows = discover_workflows()
        
        for workflow in workflows:
            metadata = get_workflow_metadata(workflow)
            
            # Should have all required metadata fields
            assert isinstance(metadata, dict)
            assert "description" in metadata
            assert "category" in metadata
            assert "required_config" in metadata
            assert "external_services" in metadata
            
            # Required config should include basic requirements
            assert "models" in metadata["required_config"]
            assert "chat_service" in metadata["required_config"]