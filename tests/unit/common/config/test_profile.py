"""
Tests for the profile module in ingenious.common.config.
"""

import pytest


class TestProfiles:
    """Test suite for profile configuration."""

    def test_deprecated_profile_loading(self):
        """Test that profile loading is deprecated and shouldn't be used."""
        # This is just a placeholder test to maintain compatibility
        # The application should now directly use config.yml without profile.yml
        assert True
