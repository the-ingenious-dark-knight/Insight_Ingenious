import os
from unittest.mock import patch

import pytest

from ingenious.config.profile import substitute_environment_variables


@pytest.mark.unit
class TestConfig:
    """Test Config class functionality"""

    def test_config_double_substitution(self):
        """Test that environment variables are substituted correctly when called multiple times"""
        yaml_content = "value: ${TEST_VAR:default}"

        with patch.dict(os.environ, {"TEST_VAR": "substituted"}, clear=True):
            # First substitution
            result1 = substitute_environment_variables(yaml_content)
            # Second substitution (should not change the result)
            result2 = substitute_environment_variables(result1)

            assert result1 == "value: substituted"
            assert result2 == "value: substituted"
