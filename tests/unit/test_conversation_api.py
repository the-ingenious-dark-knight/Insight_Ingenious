"""
Tests for ingenious.api.routes.conversation module
"""

from unittest.mock import AsyncMock, Mock

import pytest
from fastapi import HTTPException

from ingenious.api.routes.conversation import get_conversation, router
from ingenious.models.message import Message


class TestConversationAPI:
    """Test cases for conversation API routes"""

    def test_router_exists(self):
        """Test that router is properly configured"""
        from fastapi import APIRouter

        from ingenious.api.routes.conversation import router

        assert isinstance(router, APIRouter)
        assert router is not None

    def test_logger_configured(self):
        """Test that logger is properly configured"""
        from ingenious.api.routes.conversation import logger

        assert logger is not None
        assert hasattr(logger, "error")

    def test_imports_exist(self):
        """Test that all required imports are available"""
        import ingenious.api.routes.conversation as conv_module

        # Test that all required imports are accessible
        assert hasattr(conv_module, "List")
        assert hasattr(conv_module, "APIRouter")
        assert hasattr(conv_module, "Depends")
        assert hasattr(conv_module, "HTTPException")
        assert hasattr(conv_module, "Annotated")
        assert hasattr(conv_module, "get_logger")
        assert hasattr(conv_module, "ChatHistoryRepository")
        assert hasattr(conv_module, "HTTPError")
        assert hasattr(conv_module, "Message")
        assert hasattr(conv_module, "get_chat_history_repository")

    @pytest.mark.asyncio
    async def test_get_conversation_success(self):
        """Test successful conversation retrieval"""
        # Mock repository
        mock_repository = Mock()
        mock_messages = [
            Message(
                role="user", content="Hello", user_id="user1", thread_id="thread_123"
            ),
            Message(
                role="assistant",
                content="Hi there!",
                user_id="user1",
                thread_id="thread_123",
            ),
        ]
        mock_repository.get_thread_messages = AsyncMock(return_value=mock_messages)

        # Test the function directly
        result = await get_conversation("thread_123", mock_repository)

        # Verify results
        assert result == mock_messages
        mock_repository.get_thread_messages.assert_called_once_with("thread_123")

    @pytest.mark.asyncio
    async def test_get_conversation_empty_result(self):
        """Test conversation retrieval with empty result"""
        # Mock repository returning None
        mock_repository = Mock()
        mock_repository.get_thread_messages = AsyncMock(return_value=None)

        # Test the function directly
        result = await get_conversation("thread_456", mock_repository)

        # Verify empty list is returned
        assert result == []
        mock_repository.get_thread_messages.assert_called_once_with("thread_456")

    @pytest.mark.asyncio
    async def test_get_conversation_empty_list(self):
        """Test conversation retrieval with empty list"""
        # Mock repository returning empty list
        mock_repository = Mock()
        mock_repository.get_thread_messages = AsyncMock(return_value=[])

        # Test the function directly
        result = await get_conversation("thread_789", mock_repository)

        # Verify empty list is returned
        assert result == []
        mock_repository.get_thread_messages.assert_called_once_with("thread_789")

    @pytest.mark.asyncio
    async def test_get_conversation_repository_exception(self):
        """Test conversation retrieval when repository raises exception"""
        # Mock repository that raises an exception
        mock_repository = Mock()
        mock_repository.get_thread_messages = AsyncMock(
            side_effect=ValueError("Database error")
        )

        # Test that HTTPException is raised
        with pytest.raises(HTTPException) as exc_info:
            await get_conversation("thread_error", mock_repository)

        # Verify exception details
        assert exc_info.value.status_code == 400
        assert "Database error" in str(exc_info.value.detail)
        mock_repository.get_thread_messages.assert_called_once_with("thread_error")

    @pytest.mark.asyncio
    async def test_get_conversation_different_exception_types(self):
        """Test conversation retrieval with different exception types"""
        mock_repository = Mock()

        # Test RuntimeError
        mock_repository.get_thread_messages = AsyncMock(
            side_effect=RuntimeError("Runtime error")
        )
        with pytest.raises(HTTPException) as exc_info:
            await get_conversation("thread_runtime", mock_repository)
        assert exc_info.value.status_code == 400
        assert "Runtime error" in str(exc_info.value.detail)

        # Test generic Exception
        mock_repository.get_thread_messages = AsyncMock(
            side_effect=Exception("Generic error")
        )
        with pytest.raises(HTTPException) as exc_info:
            await get_conversation("thread_generic", mock_repository)
        assert exc_info.value.status_code == 400
        assert "Generic error" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_get_conversation_with_various_thread_ids(self):
        """Test conversation retrieval with various thread ID formats"""
        mock_repository = Mock()
        mock_messages = [
            Message(
                role="user", content="Test", user_id="user1", thread_id="thread_test"
            )
        ]
        mock_repository.get_thread_messages = AsyncMock(return_value=mock_messages)

        # Test different thread ID formats
        thread_ids = [
            "simple_123",
            "thread-with-dashes",
            "thread_with_underscores",
            "UPPERCASE_THREAD",
            "123456789",
            "thread.with.dots",
        ]

        for thread_id in thread_ids:
            result = await get_conversation(thread_id, mock_repository)
            assert result == mock_messages
            mock_repository.get_thread_messages.assert_called_with(thread_id)

    def test_route_configuration(self):
        """Test that the route is properly configured"""
        # Check that the router has routes
        assert len(router.routes) > 0

        # Find the get conversation route
        conversation_route = None
        for route in router.routes:
            if hasattr(route, "path") and "/conversations/{thread_id}" in route.path:
                conversation_route = route
                break

        assert conversation_route is not None
        assert "GET" in conversation_route.methods

    def test_response_model_configuration(self):
        """Test that response models are properly configured"""
        # The route should have proper response configuration
        # This tests the API documentation setup
        conversation_route = None
        for route in router.routes:
            if hasattr(route, "path") and "/conversations/{thread_id}" in route.path:
                conversation_route = route
                break

        assert conversation_route is not None
        # The route should have responses configured
        if hasattr(conversation_route, "responses"):
            assert conversation_route.responses is not None

    @pytest.mark.asyncio
    async def test_get_conversation_logging_on_error(self):
        """Test that errors are properly logged"""
        from unittest.mock import patch

        mock_repository = Mock()
        mock_repository.get_thread_messages = AsyncMock(
            side_effect=ValueError("Test error")
        )

        with patch("ingenious.api.routes.conversation.logger") as mock_logger:
            with pytest.raises(HTTPException):
                await get_conversation("test_thread", mock_repository)

            # Verify that error logging was called
            mock_logger.error.assert_called_once()
            call_args = mock_logger.error.call_args
            assert "Failed to get conversation" in call_args[0][0]
            assert call_args[1]["thread_id"] == "test_thread"
            assert "Test error" in call_args[1]["error"]
            assert call_args[1]["exc_info"] is True

    def test_module_structure(self):
        """Test the overall module structure"""
        import ingenious.api.routes.conversation as conv_module

        # Verify the module has the expected structure
        assert hasattr(conv_module, "logger")
        assert hasattr(conv_module, "router")
        assert hasattr(conv_module, "get_conversation")

        # Verify function is async
        import asyncio

        assert asyncio.iscoroutinefunction(conv_module.get_conversation)
