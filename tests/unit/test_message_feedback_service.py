"""
Tests for ingenious.services.message_feedback_service module
"""

from unittest.mock import AsyncMock, Mock

import pytest

from ingenious.models.message_feedback import (
    MessageFeedbackRequest,
    MessageFeedbackResponse,
)
from ingenious.services.message_feedback_service import MessageFeedbackService


class TestMessageFeedbackService:
    """Test cases for MessageFeedbackService class"""

    def setup_method(self):
        """Set up test fixtures"""
        self.mock_chat_history_repository = Mock()
        self.service = MessageFeedbackService(self.mock_chat_history_repository)

    def test_init(self):
        """Test MessageFeedbackService initialization"""
        repository = Mock()
        service = MessageFeedbackService(repository)
        assert service.chat_history_repository is repository

    @pytest.mark.asyncio
    async def test_update_message_feedback_success(self):
        """Test successful message feedback update"""
        # Setup test data
        message_id = "msg_123"
        thread_id = "thread_456"
        user_id = "user_789"

        request = MessageFeedbackRequest(
            message_id=message_id,
            thread_id=thread_id,
            user_id=user_id,
            positive_feedback=True,
        )

        # Mock message from repository
        mock_message = Mock()
        mock_message.user_id = user_id
        self.mock_chat_history_repository.get_message = AsyncMock(
            return_value=mock_message
        )
        self.mock_chat_history_repository.update_message_feedback = AsyncMock()

        # Execute
        result = await self.service.update_message_feedback(message_id, request)

        # Verify
        assert isinstance(result, MessageFeedbackResponse)
        assert result.message == f"Feedback submitted for message {message_id}."

        # Verify repository calls
        self.mock_chat_history_repository.get_message.assert_called_once_with(
            message_id, thread_id
        )
        self.mock_chat_history_repository.update_message_feedback.assert_called_once_with(
            message_id, thread_id, True
        )

    @pytest.mark.asyncio
    async def test_update_message_feedback_mismatched_message_id(self):
        """Test update fails when message IDs don't match"""
        request = MessageFeedbackRequest(
            message_id="different_id",
            thread_id="thread_456",
            user_id="user_789",
            positive_feedback=True,
        )

        with pytest.raises(
            ValueError, match="Message ID does not match message feedback request."
        ):
            await self.service.update_message_feedback("msg_123", request)

        # Verify no repository calls were made
        self.mock_chat_history_repository.get_message.assert_not_called()
        self.mock_chat_history_repository.update_message_feedback.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_message_feedback_message_not_found(self):
        """Test update fails when message is not found"""
        message_id = "msg_123"
        thread_id = "thread_456"

        request = MessageFeedbackRequest(
            message_id=message_id,
            thread_id=thread_id,
            user_id="user_789",
            positive_feedback=True,
        )

        # Mock repository to return None (message not found)
        self.mock_chat_history_repository.get_message = AsyncMock(return_value=None)

        with pytest.raises(ValueError, match=f"Message {message_id} not found."):
            await self.service.update_message_feedback(message_id, request)

        # Verify get_message was called but update_message_feedback was not
        self.mock_chat_history_repository.get_message.assert_called_once_with(
            message_id, thread_id
        )
        self.mock_chat_history_repository.update_message_feedback.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_message_feedback_mismatched_user_id(self):
        """Test update fails when user IDs don't match"""
        message_id = "msg_123"
        thread_id = "thread_456"

        request = MessageFeedbackRequest(
            message_id=message_id,
            thread_id=thread_id,
            user_id="user_789",
            positive_feedback=True,
        )

        # Mock message with different user ID
        mock_message = Mock()
        mock_message.user_id = "different_user"
        self.mock_chat_history_repository.get_message = AsyncMock(
            return_value=mock_message
        )

        with pytest.raises(
            ValueError, match="User ID does not match message feedback request."
        ):
            await self.service.update_message_feedback(message_id, request)

        # Verify get_message was called but update_message_feedback was not
        self.mock_chat_history_repository.get_message.assert_called_once_with(
            message_id, thread_id
        )
        self.mock_chat_history_repository.update_message_feedback.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_message_feedback_with_none_user_ids(self):
        """Test update succeeds when both user IDs are None"""
        message_id = "msg_123"
        thread_id = "thread_456"

        request = MessageFeedbackRequest(
            message_id=message_id,
            thread_id=thread_id,
            user_id=None,
            positive_feedback=False,
        )

        # Mock message with None user ID
        mock_message = Mock()
        mock_message.user_id = None
        self.mock_chat_history_repository.get_message = AsyncMock(
            return_value=mock_message
        )
        self.mock_chat_history_repository.update_message_feedback = AsyncMock()

        # Execute
        result = await self.service.update_message_feedback(message_id, request)

        # Verify success
        assert isinstance(result, MessageFeedbackResponse)
        assert result.message == f"Feedback submitted for message {message_id}."

        # Verify repository calls
        self.mock_chat_history_repository.update_message_feedback.assert_called_once_with(
            message_id, thread_id, False
        )

    @pytest.mark.asyncio
    async def test_update_message_feedback_with_empty_string_user_ids(self):
        """Test update succeeds when both user IDs are empty strings"""
        message_id = "msg_123"
        thread_id = "thread_456"

        request = MessageFeedbackRequest(
            message_id=message_id,
            thread_id=thread_id,
            user_id="",
            positive_feedback=True,
        )

        # Mock message with empty string user ID
        mock_message = Mock()
        mock_message.user_id = ""
        self.mock_chat_history_repository.get_message = AsyncMock(
            return_value=mock_message
        )
        self.mock_chat_history_repository.update_message_feedback = AsyncMock()

        # Execute
        result = await self.service.update_message_feedback(message_id, request)

        # Verify success
        assert isinstance(result, MessageFeedbackResponse)

    @pytest.mark.asyncio
    async def test_update_message_feedback_mixed_none_and_empty_user_ids(self):
        """Test update succeeds when one user ID is None and other is empty string"""
        message_id = "msg_123"
        thread_id = "thread_456"

        request = MessageFeedbackRequest(
            message_id=message_id,
            thread_id=thread_id,
            user_id=None,
            positive_feedback=True,
        )

        # Mock message with empty string user ID (should be treated as equivalent to None)
        mock_message = Mock()
        mock_message.user_id = ""
        self.mock_chat_history_repository.get_message = AsyncMock(
            return_value=mock_message
        )
        self.mock_chat_history_repository.update_message_feedback = AsyncMock()

        # Execute
        result = await self.service.update_message_feedback(message_id, request)

        # Verify success
        assert isinstance(result, MessageFeedbackResponse)
