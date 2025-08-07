"""
Tests for ingenious.api.routes.message_feedback module
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi import HTTPException

from ingenious.api.routes.message_feedback import router, submit_message_feedback
from ingenious.models.message_feedback import (
    MessageFeedbackRequest,
    MessageFeedbackResponse,
)


class TestMessageFeedbackAPI:
    """Test cases for message feedback API routes"""

    def test_router_exists(self):
        """Test that router is properly configured"""
        from fastapi import APIRouter

        from ingenious.api.routes.message_feedback import router

        assert isinstance(router, APIRouter)
        assert router is not None

    def test_logger_configured(self):
        """Test that logger is properly configured"""
        from ingenious.api.routes.message_feedback import logger

        assert logger is not None
        assert hasattr(logger, "error")

    def test_imports_exist(self):
        """Test that all required imports are available"""
        import ingenious.api.routes.message_feedback as fb_module

        # Test that all required imports are accessible
        assert hasattr(fb_module, "APIRouter")
        assert hasattr(fb_module, "Depends")
        assert hasattr(fb_module, "HTTPException")
        assert hasattr(fb_module, "Annotated")
        assert hasattr(fb_module, "get_logger")
        assert hasattr(fb_module, "HTTPError")
        assert hasattr(fb_module, "MessageFeedbackRequest")
        assert hasattr(fb_module, "MessageFeedbackResponse")
        assert hasattr(fb_module, "get_message_feedback_service")
        assert hasattr(fb_module, "MessageFeedbackService")

    @pytest.mark.asyncio
    async def test_submit_message_feedback_success(self):
        """Test successful message feedback submission"""
        # Mock service
        mock_service = Mock()
        mock_response = MessageFeedbackResponse(
            message="Feedback submitted successfully"
        )
        mock_service.update_message_feedback = AsyncMock(return_value=mock_response)

        # Mock request
        request = MessageFeedbackRequest(
            message_id="msg_123",
            thread_id="thread_456",
            user_id="user_789",
            positive_feedback=True,
        )

        # Test the function directly
        result = await submit_message_feedback("msg_123", request, mock_service)

        # Verify results
        assert result == mock_response
        mock_service.update_message_feedback.assert_called_once_with("msg_123", request)

    @pytest.mark.asyncio
    async def test_submit_message_feedback_negative_feedback(self):
        """Test submitting negative feedback"""
        # Mock service
        mock_service = Mock()
        mock_response = MessageFeedbackResponse(message="Negative feedback recorded")
        mock_service.update_message_feedback = AsyncMock(return_value=mock_response)

        # Mock request with negative feedback
        request = MessageFeedbackRequest(
            message_id="msg_456",
            thread_id="thread_789",
            user_id="user_abc",
            positive_feedback=False,
        )

        # Test the function directly
        result = await submit_message_feedback("msg_456", request, mock_service)

        # Verify results
        assert result == mock_response
        mock_service.update_message_feedback.assert_called_once_with("msg_456", request)

    @pytest.mark.asyncio
    async def test_submit_message_feedback_value_error(self):
        """Test message feedback submission when service raises ValueError"""
        # Mock service that raises ValueError
        mock_service = Mock()
        mock_service.update_message_feedback = AsyncMock(
            side_effect=ValueError("Message ID does not match")
        )

        # Mock request
        request = MessageFeedbackRequest(
            message_id="msg_123",
            thread_id="thread_456",
            user_id="user_789",
            positive_feedback=True,
        )

        # Test that HTTPException is raised
        with pytest.raises(HTTPException) as exc_info:
            await submit_message_feedback("msg_123", request, mock_service)

        # Verify exception details
        assert exc_info.value.status_code == 400
        assert "Message ID does not match" in str(exc_info.value.detail)
        mock_service.update_message_feedback.assert_called_once_with("msg_123", request)

    @pytest.mark.asyncio
    async def test_submit_message_feedback_different_value_errors(self):
        """Test message feedback submission with different ValueError messages"""
        mock_service = Mock()

        request = MessageFeedbackRequest(
            message_id="msg_test",
            thread_id="thread_test",
            user_id="user_test",
            positive_feedback=True,
        )

        # Test different error scenarios
        error_messages = [
            "Message not found",
            "User ID does not match",
            "Invalid feedback data",
            "Permission denied",
        ]

        for error_msg in error_messages:
            mock_service.update_message_feedback = AsyncMock(
                side_effect=ValueError(error_msg)
            )

            with pytest.raises(HTTPException) as exc_info:
                await submit_message_feedback("msg_test", request, mock_service)

            assert exc_info.value.status_code == 400
            assert error_msg in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_submit_message_feedback_with_none_user_id(self):
        """Test submitting feedback with None user_id"""
        # Mock service
        mock_service = Mock()
        mock_response = MessageFeedbackResponse(message="Feedback submitted")
        mock_service.update_message_feedback = AsyncMock(return_value=mock_response)

        # Mock request with None user_id
        request = MessageFeedbackRequest(
            message_id="msg_none",
            thread_id="thread_none",
            user_id=None,
            positive_feedback=True,
        )

        # Test the function
        result = await submit_message_feedback("msg_none", request, mock_service)

        # Verify results
        assert result == mock_response
        mock_service.update_message_feedback.assert_called_once_with(
            "msg_none", request
        )

    @pytest.mark.asyncio
    async def test_submit_message_feedback_logging_on_error(self):
        """Test that errors are properly logged"""
        mock_service = Mock()
        mock_service.update_message_feedback = AsyncMock(
            side_effect=ValueError("Test logging error")
        )

        request = MessageFeedbackRequest(
            message_id="msg_log",
            thread_id="thread_log",
            user_id="user_log",
            positive_feedback=False,
        )

        with patch("ingenious.api.routes.message_feedback.logger") as mock_logger:
            with pytest.raises(HTTPException):
                await submit_message_feedback("msg_log", request, mock_service)

            # Verify that error logging was called
            mock_logger.error.assert_called_once()
            call_args = mock_logger.error.call_args
            assert "Failed to submit message feedback" in call_args[0][0]
            assert call_args[1]["message_id"] == "msg_log"
            assert "Test logging error" in call_args[1]["error"]
            assert call_args[1]["exc_info"] is True

    def test_route_configuration(self):
        """Test that the route is properly configured"""
        # Check that the router has routes
        assert len(router.routes) > 0

        # Find the message feedback route
        feedback_route = None
        for route in router.routes:
            if (
                hasattr(route, "path")
                and "/messages/{message_id}/feedback" in route.path
            ):
                feedback_route = route
                break

        assert feedback_route is not None
        assert "PUT" in feedback_route.methods

    def test_response_model_configuration(self):
        """Test that response models are properly configured"""
        # The route should have proper response configuration
        feedback_route = None
        for route in router.routes:
            if (
                hasattr(route, "path")
                and "/messages/{message_id}/feedback" in route.path
            ):
                feedback_route = route
                break

        assert feedback_route is not None
        # The route should have responses configured
        if hasattr(feedback_route, "responses"):
            assert feedback_route.responses is not None

    @pytest.mark.asyncio
    async def test_submit_message_feedback_with_various_message_ids(self):
        """Test feedback submission with various message ID formats"""
        mock_service = Mock()
        mock_response = MessageFeedbackResponse(message="Success")
        mock_service.update_message_feedback = AsyncMock(return_value=mock_response)

        request = MessageFeedbackRequest(
            message_id="test",
            thread_id="thread",
            user_id="user",
            positive_feedback=True,
        )

        # Test different message ID formats
        message_ids = [
            "simple_123",
            "msg-with-dashes",
            "msg_with_underscores",
            "UPPERCASE_MSG",
            "123456789",
            "msg.with.dots",
        ]

        for message_id in message_ids:
            # Update request to match message_id
            request.message_id = message_id
            result = await submit_message_feedback(message_id, request, mock_service)
            assert result == mock_response
            mock_service.update_message_feedback.assert_called_with(message_id, request)

    def test_module_structure(self):
        """Test the overall module structure"""
        import ingenious.api.routes.message_feedback as fb_module

        # Verify the module has the expected structure
        assert hasattr(fb_module, "logger")
        assert hasattr(fb_module, "router")
        assert hasattr(fb_module, "submit_message_feedback")

        # Verify function is async
        import asyncio

        assert asyncio.iscoroutinefunction(fb_module.submit_message_feedback)

    @pytest.mark.asyncio
    async def test_submit_message_feedback_only_catches_value_error(self):
        """Test that only ValueError is caught and converted to HTTPException"""
        mock_service = Mock()

        request = MessageFeedbackRequest(
            message_id="msg_test",
            thread_id="thread_test",
            user_id="user_test",
            positive_feedback=True,
        )

        # Test that other exceptions are not caught
        mock_service.update_message_feedback = AsyncMock(
            side_effect=RuntimeError("Runtime error")
        )

        with pytest.raises(RuntimeError):
            await submit_message_feedback("msg_test", request, mock_service)
