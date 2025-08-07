from unittest.mock import Mock, patch

import pytest

from ingenious.utils.token_counter import get_max_tokens, num_tokens_from_messages


@pytest.mark.unit
class TestTokenCounter:
    """Test token counting functionality"""

    def test_get_max_tokens_known_models(self):
        """Test max tokens for known models"""
        assert get_max_tokens("gpt-3.5-turbo") == 4096
        assert get_max_tokens("gpt-3.5-turbo-0613") == 4096
        assert get_max_tokens("gpt-3.5-turbo-16k") == 16384
        assert get_max_tokens("gpt-3.5-turbo-0125") == 16384
        assert get_max_tokens("gpt-4") == 8192
        assert get_max_tokens("gpt-4-0314") == 8192
        assert get_max_tokens("gpt-4-32k") == 32768
        assert get_max_tokens("gpt-4-32k-0314") == 32768
        assert get_max_tokens("gpt-4-0613") == 8192
        assert get_max_tokens("gpt-4-32k-0613") == 32768

    def test_get_max_tokens_unknown_model(self):
        """Test max tokens for unknown model returns default"""
        assert get_max_tokens("unknown-model") == 4096

    def test_get_max_tokens_default_model(self):
        """Test max tokens with default model parameter"""
        assert get_max_tokens() == 16384  # default is gpt-3.5-turbo-0125

    @patch("ingenious.utils.token_counter.tiktoken")
    def test_num_tokens_from_messages_basic(self, mock_tiktoken):
        """Test basic token counting for messages"""
        mock_encoding = Mock()
        mock_encoding.encode.return_value = [1, 2, 3]  # 3 tokens
        mock_tiktoken.encoding_for_model.return_value = mock_encoding

        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there"},
        ]

        result = num_tokens_from_messages(messages, "gpt-3.5-turbo-0613")

        # Should be called for each string value
        assert mock_encoding.encode.call_count == 4  # 2 roles + 2 contents
        assert result > 0

    @patch("ingenious.utils.token_counter.tiktoken")
    def test_num_tokens_from_messages_with_name(self, mock_tiktoken):
        """Test token counting with name field"""
        mock_encoding = Mock()
        mock_encoding.encode.return_value = [1, 2, 3]
        mock_tiktoken.encoding_for_model.return_value = mock_encoding

        messages = [{"role": "user", "content": "Hello", "name": "test_user"}]

        result = num_tokens_from_messages(messages, "gpt-3.5-turbo-0613")

        # Should account for tokens_per_name
        assert result > 0
        assert mock_encoding.encode.call_count == 3  # role, content, name

    @patch("ingenious.utils.token_counter.tiktoken")
    def test_num_tokens_from_messages_unknown_model(self, mock_tiktoken):
        """Test token counting with unknown model raises NotImplementedError"""
        mock_encoding = Mock()
        mock_encoding.encode.return_value = [1, 2, 3]
        mock_tiktoken.encoding_for_model.side_effect = KeyError("Model not found")
        mock_tiktoken.get_encoding.return_value = mock_encoding

        messages = [{"role": "user", "content": "Hello"}]

        with pytest.raises(
            NotImplementedError,
            match="num_tokens_from_messages\\(\\) is not implemented for model unknown-model",
        ):
            num_tokens_from_messages(messages, "unknown-model")

    @patch("ingenious.utils.token_counter.tiktoken")
    def test_num_tokens_from_messages_gpt35_turbo_fallback(self, mock_tiktoken):
        """Test GPT-3.5-turbo models fall back to specific version"""
        mock_encoding = Mock()
        mock_encoding.encode.return_value = [1, 2, 3]
        mock_tiktoken.encoding_for_model.return_value = mock_encoding

        messages = [{"role": "user", "content": "Hello"}]

        # This should recursively call with gpt-3.5-turbo-0613
        result = num_tokens_from_messages(messages, "gpt-3.5-turbo-1234")

        assert result > 0

    @patch("ingenious.utils.token_counter.tiktoken")
    def test_num_tokens_from_messages_gpt4_fallback(self, mock_tiktoken):
        """Test GPT-4 models fall back to specific version"""
        mock_encoding = Mock()
        mock_encoding.encode.return_value = [1, 2, 3]
        mock_tiktoken.encoding_for_model.return_value = mock_encoding

        messages = [{"role": "user", "content": "Hello"}]

        # This should recursively call with gpt-4-0613
        result = num_tokens_from_messages(messages, "gpt-4-1234")

        assert result > 0

    @patch("ingenious.utils.token_counter.tiktoken")
    def test_num_tokens_from_messages_unsupported_model(self, mock_tiktoken):
        """Test unsupported model raises NotImplementedError"""
        mock_tiktoken.encoding_for_model.return_value = Mock()

        messages = [{"role": "user", "content": "Hello"}]

        with pytest.raises(NotImplementedError):
            num_tokens_from_messages(messages, "unsupported-model")

    @patch("ingenious.utils.token_counter.tiktoken")
    def test_num_tokens_from_messages_empty_messages(self, mock_tiktoken):
        """Test token counting with empty messages list"""
        mock_encoding = Mock()
        mock_encoding.encode.return_value = []
        mock_tiktoken.encoding_for_model.return_value = mock_encoding

        messages = []

        result = num_tokens_from_messages(messages, "gpt-3.5-turbo-0613")

        # Should still have the base tokens for assistant response
        assert result == 3

    @patch("ingenious.utils.token_counter.tiktoken")
    def test_num_tokens_from_messages_non_string_values(self, mock_tiktoken):
        """Test token counting skips non-string values"""
        mock_encoding = Mock()
        mock_encoding.encode.return_value = [1, 2, 3]
        mock_tiktoken.encoding_for_model.return_value = mock_encoding

        messages = [{"role": "user", "content": "Hello", "metadata": {"key": "value"}}]

        result = num_tokens_from_messages(messages, "gpt-3.5-turbo-0613")

        # Should only encode string values (role and content)
        assert mock_encoding.encode.call_count == 2
        assert result > 0

    @patch("ingenious.utils.token_counter.tiktoken")
    def test_num_tokens_from_messages_model_variants(self, mock_tiktoken):
        """Test token counting for different model variants"""
        mock_encoding = Mock()
        mock_encoding.encode.return_value = [1, 2, 3]
        mock_tiktoken.encoding_for_model.return_value = mock_encoding

        messages = [{"role": "user", "content": "Hello"}]

        # Test gpt-3.5-turbo-0301 (different tokens_per_message)
        result_0301 = num_tokens_from_messages(messages, "gpt-3.5-turbo-0301")

        # Test gpt-4-0613 (different tokens_per_message)
        result_4_0613 = num_tokens_from_messages(messages, "gpt-4-0613")

        assert result_0301 > 0
        assert result_4_0613 > 0

    @patch("ingenious.utils.token_counter.tiktoken")
    @patch("ingenious.utils.token_counter.logger")
    def test_num_tokens_from_messages_keyerror_fallback(
        self, mock_logger, mock_tiktoken
    ):
        """Test fallback when model encoding not found"""
        mock_encoding = Mock()
        mock_encoding.encode.return_value = [1, 2, 3]
        mock_tiktoken.encoding_for_model.side_effect = KeyError("Model not found")
        mock_tiktoken.get_encoding.return_value = mock_encoding

        messages = [{"role": "user", "content": "Hello"}]

        # This should use cl100k_base fallback for supported models
        result = num_tokens_from_messages(messages, "gpt-3.5-turbo-0613")

        # Should log warning about model not found
        mock_logger.warning.assert_called()
        assert result > 0
        mock_tiktoken.get_encoding.assert_called_with("cl100k_base")

    @patch("ingenious.utils.token_counter.tiktoken")
    @patch("ingenious.utils.token_counter.logger")
    def test_num_tokens_from_messages_gpt35_turbo_warning(
        self, mock_logger, mock_tiktoken
    ):
        """Test warning is logged for generic gpt-3.5-turbo model"""
        mock_encoding = Mock()
        mock_encoding.encode.return_value = [1, 2, 3]
        mock_tiktoken.encoding_for_model.return_value = mock_encoding

        messages = [{"role": "user", "content": "Hello"}]

        result = num_tokens_from_messages(messages, "gpt-3.5-turbo-latest")

        # Should log warning about model update
        mock_logger.warning.assert_called()
        assert result > 0

    @patch("ingenious.utils.token_counter.tiktoken")
    @patch("ingenious.utils.token_counter.logger")
    def test_num_tokens_from_messages_gpt4_warning(self, mock_logger, mock_tiktoken):
        """Test warning is logged for generic gpt-4 model"""
        mock_encoding = Mock()
        mock_encoding.encode.return_value = [1, 2, 3]
        mock_tiktoken.encoding_for_model.return_value = mock_encoding

        messages = [{"role": "user", "content": "Hello"}]

        result = num_tokens_from_messages(messages, "gpt-4-latest")

        # Should log warning about model update
        mock_logger.warning.assert_called()
        assert result > 0

    @patch("ingenious.utils.token_counter.tiktoken")
    def test_num_tokens_from_messages_all_supported_models(self, mock_tiktoken):
        """Test token counting works for all explicitly supported models"""
        mock_encoding = Mock()
        mock_encoding.encode.return_value = [1, 2, 3]
        mock_tiktoken.encoding_for_model.return_value = mock_encoding

        messages = [{"role": "user", "content": "Hello"}]

        supported_models = [
            "gpt-3.5-turbo-0613",
            "gpt-3.5-turbo-16k-0125",
            "gpt-4-0314",
            "gpt-4-32k-0314",
            "gpt-4-0613",
            "gpt-4-32k-0613",
        ]

        for model in supported_models:
            result = num_tokens_from_messages(messages, model)
            assert result > 0

    @patch("ingenious.utils.token_counter.tiktoken")
    def test_num_tokens_from_messages_gpt35_turbo_0301_special_case(
        self, mock_tiktoken
    ):
        """Test special case for gpt-3.5-turbo-0301 with different token calculations"""
        mock_encoding = Mock()
        mock_encoding.encode.return_value = [1, 2, 3]  # 3 tokens per string
        mock_tiktoken.encoding_for_model.return_value = mock_encoding

        messages = [{"role": "user", "content": "Hello", "name": "testuser"}]

        result = num_tokens_from_messages(messages, "gpt-3.5-turbo-0301")

        # For gpt-3.5-turbo-0301: tokens_per_message=4, tokens_per_name=-1
        # Expected: (3 tokens * 3 strings) + (4 tokens per message) + (-1 tokens for name) + 3 base = 15
        expected_tokens = 9 + 4 - 1 + 3  # 15
        assert result == expected_tokens
