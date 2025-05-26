"""
Tests for the config module in ingenious.common.config.
"""

import pytest

from ingenious.common.config import get_config
from ingenious.common.errors import ConfigurationError


class TestConfig:
    """Test suite for config loading and validation."""

    def test_load_config_from_path(self, sample_config_file):
        """Test loading config from specific file paths."""
        config = get_config(config_path=str(sample_config_file))
        assert config is not None
        assert config.web_configuration.port == 8000
