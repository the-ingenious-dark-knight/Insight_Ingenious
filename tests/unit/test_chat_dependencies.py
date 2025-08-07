"""
Tests for ingenious.services.chat_dependencies module
"""
import pytest
from unittest.mock import Mock, patch, MagicMock

from ingenious.services.chat_dependencies import (
    get_di_container,
    get_chat_history_repository, 
    get_chat_service,
    get_message_feedback_service
)


class TestChatDependencies:
    """Test cases for chat dependencies module"""

    def test_module_docstring(self):
        """Test that the module has appropriate documentation"""
        import ingenious.services.chat_dependencies as chat_deps
        docstring = chat_deps.__doc__
        assert docstring is not None
        assert "Chat service related dependency injection" in docstring
        assert "FastAPI dependency injection functions" in docstring

    @patch('ingenious.services.chat_dependencies.get_container')
    def test_get_di_container(self, mock_get_container):
        """Test get_di_container function"""
        mock_container = Mock()
        mock_get_container.return_value = mock_container
        
        result = get_di_container()
        
        mock_get_container.assert_called_once()
        assert result is mock_container

    @patch('ingenious.services.chat_dependencies.get_container')
    def test_get_di_container_returns_container_type(self, mock_get_container):
        """Test that get_di_container returns Container type"""
        from ingenious.services.container import Container
        mock_container = Mock(spec=Container)
        mock_get_container.return_value = mock_container
        
        result = get_di_container()
        
        assert result is mock_container

    def test_get_chat_history_repository(self):
        """Test get_chat_history_repository function"""
        mock_container = Mock()
        mock_repository = Mock()
        mock_container.chat_history_repository.return_value = mock_repository
        
        result = get_chat_history_repository(container=mock_container)
        
        mock_container.chat_history_repository.assert_called_once()
        assert result is mock_repository

    def test_get_chat_history_repository_calls_container_method(self):
        """Test that get_chat_history_repository calls the correct container method"""
        from ingenious.db.chat_history_repository import ChatHistoryRepository
        
        mock_container = Mock()
        mock_repository = Mock(spec=ChatHistoryRepository)
        mock_container.chat_history_repository.return_value = mock_repository
        
        result = get_chat_history_repository(container=mock_container)
        
        mock_container.chat_history_repository.assert_called_once_with()
        assert result is mock_repository

    def test_get_chat_service(self):
        """Test get_chat_service function"""
        mock_container = Mock()
        mock_service = Mock()
        mock_container.chat_service_factory.return_value = mock_service
        
        result = get_chat_service(container=mock_container)
        
        mock_container.chat_service_factory.assert_called_once_with(conversation_flow="")
        assert result is mock_service

    def test_get_chat_service_calls_factory_with_empty_conversation_flow(self):
        """Test that get_chat_service calls factory with empty conversation flow"""
        from ingenious.services.chat_service import ChatService
        
        mock_container = Mock()
        mock_service = Mock(spec=ChatService)
        mock_container.chat_service_factory.return_value = mock_service
        
        result = get_chat_service(container=mock_container)
        
        # Verify it's called with empty string as conversation_flow
        mock_container.chat_service_factory.assert_called_once_with(conversation_flow="")
        assert result is mock_service

    def test_get_message_feedback_service(self):
        """Test get_message_feedback_service function"""
        mock_container = Mock()
        mock_service = Mock()
        mock_container.message_feedback_service.return_value = mock_service
        
        result = get_message_feedback_service(container=mock_container)
        
        mock_container.message_feedback_service.assert_called_once()
        assert result is mock_service

    def test_get_message_feedback_service_calls_container_method(self):
        """Test that get_message_feedback_service calls the correct container method"""
        from ingenious.services.message_feedback_service import MessageFeedbackService
        
        mock_container = Mock()
        mock_service = Mock(spec=MessageFeedbackService)
        mock_container.message_feedback_service.return_value = mock_service
        
        result = get_message_feedback_service(container=mock_container)
        
        mock_container.message_feedback_service.assert_called_once_with()
        assert result is mock_service

    def test_imports_exist(self):
        """Test that all expected imports are available"""
        import ingenious.services.chat_dependencies as chat_deps
        
        # Test that all required imports are accessible
        assert hasattr(chat_deps, 'Depends')
        assert hasattr(chat_deps, 'ChatHistoryRepository')
        assert hasattr(chat_deps, 'ChatService')
        assert hasattr(chat_deps, 'Container')
        assert hasattr(chat_deps, 'get_container')
        assert hasattr(chat_deps, 'MessageFeedbackService')

    def test_all_functions_are_callable(self):
        """Test that all dependency functions are callable"""
        assert callable(get_di_container)
        assert callable(get_chat_history_repository)
        assert callable(get_chat_service)
        assert callable(get_message_feedback_service)

    def test_function_docstrings(self):
        """Test that all functions have appropriate docstrings"""
        assert get_di_container.__doc__ is not None
        assert "dependency injection container" in get_di_container.__doc__
        
        assert get_chat_history_repository.__doc__ is not None
        assert "chat history repository" in get_chat_history_repository.__doc__
        
        assert get_chat_service.__doc__ is not None
        assert "chat service" in get_chat_service.__doc__
        
        assert get_message_feedback_service.__doc__ is not None
        assert "message feedback service" in get_message_feedback_service.__doc__

    @patch('ingenious.services.chat_dependencies.get_container')
    def test_integration_with_fastapi_depends(self, mock_get_container):
        """Test integration with FastAPI Depends decorator"""
        from fastapi import Depends
        
        # Verify that the functions can be used with FastAPI Depends
        mock_container = Mock()
        mock_get_container.return_value = mock_container
        
        # This simulates how FastAPI would call the dependency functions
        container_dep = get_di_container()
        assert container_dep is mock_container
        
        # Test that other functions work with the container
        mock_repository = Mock()
        mock_container.chat_history_repository.return_value = mock_repository
        
        repository_dep = get_chat_history_repository(container=container_dep)
        assert repository_dep is mock_repository