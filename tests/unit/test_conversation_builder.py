"""
Tests for ingenious.utils.conversation_builder module
"""

from unittest.mock import AsyncMock, Mock, mock_open, patch

import pytest

from ingenious.utils.conversation_builder import (
    Sync_Prompt_Templates,
    build_assistant_message,
    build_message,
    build_system_prompt,
    build_user_message,
)


class TestBuildSystemPrompt:
    """Test cases for build_system_prompt function"""

    def test_build_system_prompt_without_user_name(self):
        """Test building system prompt without user name"""
        system_prompt = "You are a helpful assistant."

        result = build_system_prompt(system_prompt)

        expected = {"role": "system", "content": "You are a helpful assistant."}
        assert result == expected
        assert "name" not in result

    def test_build_system_prompt_with_user_name(self):
        """Test building system prompt with user name"""
        system_prompt = "You are a helpful assistant."
        user_name = "alice"

        result = build_system_prompt(system_prompt, user_name)

        expected = {
            "role": "system",
            "content": "You are a helpful assistant.",
            "name": "alice",
        }
        assert result == expected

    def test_build_system_prompt_empty_content(self):
        """Test building system prompt with empty content"""
        result = build_system_prompt("", "bob")

        expected = {"role": "system", "content": "", "name": "bob"}
        assert result == expected

    def test_build_system_prompt_none_user_name(self):
        """Test building system prompt with None user name"""
        result = build_system_prompt("Test prompt", None)

        expected = {"role": "system", "content": "Test prompt"}
        assert result == expected
        assert "name" not in result


class TestBuildUserMessage:
    """Test cases for build_user_message function"""

    def test_build_user_message_without_user_name(self):
        """Test building user message without user name"""
        user_prompt = "Hello, how are you?"

        result = build_user_message(user_prompt, None)

        expected = {"role": "user", "content": "Hello, how are you?"}
        assert result == expected
        assert "name" not in result

    def test_build_user_message_with_user_name(self):
        """Test building user message with user name"""
        user_prompt = "Hello, how are you?"
        user_name = "charlie"

        result = build_user_message(user_prompt, user_name)

        expected = {"role": "user", "content": "Hello, how are you?", "name": "charlie"}
        assert result == expected

    def test_build_user_message_empty_content(self):
        """Test building user message with empty content"""
        result = build_user_message("", "david")

        expected = {"role": "user", "content": "", "name": "david"}
        assert result == expected


class TestBuildAssistantMessage:
    """Test cases for build_assistant_message function"""

    def test_build_assistant_message_with_content_only(self):
        """Test building assistant message with content only"""
        content = "I'm doing well, thank you!"

        result = build_assistant_message(content)

        expected = {"role": "assistant", "content": "I'm doing well, thank you!"}
        assert result == expected
        assert "tool_calls" not in result

    def test_build_assistant_message_with_tool_calls_only(self):
        """Test building assistant message with tool calls only"""
        tool_calls = [
            {"id": "call_1", "type": "function", "function": {"name": "test_func"}}
        ]

        result = build_assistant_message(None, tool_calls)

        expected = {
            "role": "assistant",
            "tool_calls": [
                {"id": "call_1", "type": "function", "function": {"name": "test_func"}}
            ],
        }
        assert result == expected
        assert "content" not in result

    def test_build_assistant_message_with_both_content_and_tool_calls(self):
        """Test building assistant message with both content and tool calls"""
        content = "Let me help you with that."
        tool_calls = [
            {"id": "call_2", "type": "function", "function": {"name": "helper_func"}}
        ]

        result = build_assistant_message(content, tool_calls)

        expected = {
            "role": "assistant",
            "content": "Let me help you with that.",
            "tool_calls": [
                {
                    "id": "call_2",
                    "type": "function",
                    "function": {"name": "helper_func"},
                }
            ],
        }
        assert result == expected

    def test_build_assistant_message_with_none_content(self):
        """Test building assistant message with None content"""
        result = build_assistant_message(None)

        expected = {"role": "assistant"}
        assert result == expected
        assert "content" not in result
        assert "tool_calls" not in result

    def test_build_assistant_message_with_empty_tool_calls(self):
        """Test building assistant message with empty tool calls list"""
        content = "No tools needed."

        result = build_assistant_message(content, [])

        expected = {"role": "assistant", "content": "No tools needed."}
        assert result == expected
        assert "tool_calls" not in result


class TestBuildMessage:
    """Test cases for build_message function"""

    def test_build_message_system_role(self):
        """Test building message with system role"""
        result = build_message("system", "You are helpful.", "user1")

        expected = {"role": "system", "content": "You are helpful."}
        assert result == expected

    def test_build_message_user_role(self):
        """Test building message with user role"""
        result = build_message("user", "Hello!", "user1")

        expected = {"role": "user", "content": "Hello!", "name": "user1"}
        assert result == expected

    def test_build_message_assistant_role(self):
        """Test building message with assistant role"""
        result = build_message("assistant", "Hi there!", "user1")

        expected = {"role": "assistant", "content": "Hi there!"}
        assert result == expected

    def test_build_message_invalid_role(self):
        """Test building message with invalid role"""
        with pytest.raises(ValueError, match="Invalid message role."):
            build_message("invalid", "content", "user1")

    def test_build_message_none_content(self):
        """Test building message with None content"""
        result = build_message("user", None, "user1")

        expected = {"role": "user", "content": "None", "name": "user1"}
        assert result == expected

    def test_build_message_system_role_ignores_user_name(self):
        """Test that system role ignores user_name parameter"""
        result = build_message("system", "System message", "ignored_user")

        expected = {"role": "system", "content": "System message"}
        assert result == expected
        assert "name" not in result


class TestSyncPromptTemplates:
    """Test cases for Sync_Prompt_Templates function"""

    @pytest.mark.asyncio
    async def test_sync_prompt_templates_local_storage(self):
        """Test Sync_Prompt_Templates with local storage type"""
        mock_config = Mock()
        mock_config.file_storage.revisions.storage_type = "local"

        with patch("ingenious.utils.conversation_builder.FileStorage") as mock_fs_cls:
            with patch("ingenious.utils.conversation_builder.logger") as mock_logger:
                await Sync_Prompt_Templates(mock_config, "v1.0")

                # Should log that local storage was detected
                mock_logger.debug.assert_called_once_with(
                    "Local storage type detected", storage_type="local"
                )

    @pytest.mark.asyncio
    async def test_sync_prompt_templates_non_local_storage_no_files(self):
        """Test Sync_Prompt_Templates with non-local storage and no jinja files"""
        mock_config = Mock()
        mock_config.file_storage.revisions.storage_type = "azure"

        mock_fs = Mock()
        mock_fs.list_files = AsyncMock(return_value=[])

        with patch(
            "ingenious.utils.conversation_builder.FileStorage", return_value=mock_fs
        ):
            with patch("ingenious.utils.conversation_builder.logger") as mock_logger:
                await Sync_Prompt_Templates(mock_config, "v1.0")

                # Should have listed files but found none
                mock_fs.list_files.assert_called_once_with(file_path="prompts/v1.0")
                # No files to download, so no debug messages for downloading
                assert not any(
                    "Downloading template" in str(call)
                    for call in mock_logger.debug.call_args_list
                )

    @pytest.mark.asyncio
    async def test_sync_prompt_templates_non_local_storage_with_files(self):
        """Test Sync_Prompt_Templates with non-local storage and jinja files"""
        mock_config = Mock()
        mock_config.file_storage.revisions.storage_type = "azure"

        mock_fs = Mock()
        mock_fs.list_files = AsyncMock(
            return_value=[
                "prompts/v1.0/template1.jinja",
                "prompts/v1.0/template2.jinja",
                "prompts/v1.0/readme.txt",  # Should be filtered out
            ]
        )
        mock_fs.read_file = AsyncMock(
            side_effect=["Template 1 content", "Template 2 content"]
        )

        with patch(
            "ingenious.utils.conversation_builder.FileStorage", return_value=mock_fs
        ):
            with patch("ingenious.utils.conversation_builder.logger") as mock_logger:
                with patch("pathlib.Path.mkdir") as mock_mkdir:
                    with patch("builtins.open", mock_open()) as mock_file_open:
                        await Sync_Prompt_Templates(mock_config, "v1.0")

        # Should have listed files
        mock_fs.list_files.assert_called_once_with(file_path="prompts/v1.0")

        # Should have created directory
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

        # Should have read 2 jinja files (filtered out the .txt file)
        assert mock_fs.read_file.call_count == 2
        mock_fs.read_file.assert_any_call(
            file_name="template1.jinja", file_path="prompts/v1.0"
        )
        mock_fs.read_file.assert_any_call(
            file_name="template2.jinja", file_path="prompts/v1.0"
        )

        # Should have opened 2 files for writing
        assert mock_file_open.call_count == 2

        # Should have logged download activities
        download_calls = [
            call
            for call in mock_logger.debug.call_args_list
            if "Downloading template" in str(call)
        ]
        assert len(download_calls) == 2

        # Should have logged save activities
        save_calls = [
            call
            for call in mock_logger.debug.call_args_list
            if "Template saved" in str(call)
        ]
        assert len(save_calls) == 2

    @pytest.mark.asyncio
    async def test_sync_prompt_templates_file_filtering(self):
        """Test that only .jinja files are processed"""
        mock_config = Mock()
        mock_config.file_storage.revisions.storage_type = "azure"

        mock_fs = Mock()
        mock_fs.list_files = AsyncMock(
            return_value=[
                "prompts/v1.0/template.jinja",
                "prompts/v1.0/config.json",
                "prompts/v1.0/another.jinja",
                "prompts/v1.0/image.png",
            ]
        )
        mock_fs.read_file = AsyncMock(
            side_effect=["Template content", "Another template content"]
        )

        with patch(
            "ingenious.utils.conversation_builder.FileStorage", return_value=mock_fs
        ):
            with patch("ingenious.utils.conversation_builder.logger"):
                with patch("pathlib.Path.mkdir"):
                    with patch("builtins.open", mock_open()):
                        await Sync_Prompt_Templates(mock_config, "v2.0")

        # Should only have read 2 .jinja files
        assert mock_fs.read_file.call_count == 2
        mock_fs.read_file.assert_any_call(
            file_name="template.jinja", file_path="prompts/v2.0"
        )
        mock_fs.read_file.assert_any_call(
            file_name="another.jinja", file_path="prompts/v2.0"
        )

    @pytest.mark.asyncio
    async def test_sync_prompt_templates_file_path_extraction(self):
        """Test that file names are extracted correctly from paths"""
        mock_config = Mock()
        mock_config.file_storage.revisions.storage_type = "s3"

        mock_fs = Mock()
        mock_fs.list_files = AsyncMock(return_value=["deep/nested/path/template.jinja"])
        mock_fs.read_file = AsyncMock(return_value="Template content")

        with patch(
            "ingenious.utils.conversation_builder.FileStorage", return_value=mock_fs
        ):
            with patch("ingenious.utils.conversation_builder.logger"):
                with patch("pathlib.Path.mkdir"):
                    with patch("builtins.open", mock_open()):
                        await Sync_Prompt_Templates(mock_config, "v1.0")

        # Should extract just the filename from the full path
        mock_fs.read_file.assert_called_once_with(
            file_name="template.jinja", file_path="prompts/v1.0"
        )
