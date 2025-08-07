import os
import tempfile
from unittest.mock import patch

import pytest

from ingenious.utils.env_substitution import (
    load_yaml_with_env_substitution,
    substitute_env_vars,
)


@pytest.mark.unit
class TestEnvSubstitution:
    """Test environment variable substitution functionality"""

    def test_substitute_env_vars_with_existing_var(self):
        """Test substitution with existing environment variable"""
        with patch.dict(os.environ, {"TEST_VAR": "test_value"}):
            result = substitute_env_vars("${TEST_VAR:default}")
            assert result == "test_value"

    def test_substitute_env_vars_with_default(self):
        """Test substitution with default value when var doesn't exist"""
        with patch.dict(os.environ, {}, clear=True):
            result = substitute_env_vars("${MISSING_VAR:default_value}")
            assert result == "default_value"

    def test_substitute_env_vars_without_default(self):
        """Test substitution without default value"""
        with patch.dict(os.environ, {}, clear=True):
            result = substitute_env_vars("${MISSING_VAR}")
            assert result == ""

    def test_substitute_env_vars_with_existing_var_no_default(self):
        """Test substitution with existing var and no default"""
        with patch.dict(os.environ, {"TEST_VAR": "test_value"}):
            result = substitute_env_vars("${TEST_VAR}")
            assert result == "test_value"

    def test_substitute_env_vars_multiple_vars(self):
        """Test substitution with multiple environment variables"""
        with patch.dict(os.environ, {"VAR1": "value1", "VAR2": "value2"}):
            result = substitute_env_vars("${VAR1:default1} and ${VAR2:default2}")
            assert result == "value1 and value2"

    def test_substitute_env_vars_mixed_existing_and_missing(self):
        """Test substitution with mix of existing and missing vars"""
        with patch.dict(os.environ, {"EXISTING_VAR": "exists"}, clear=True):
            result = substitute_env_vars(
                "${EXISTING_VAR:default1} and ${MISSING_VAR:default2}"
            )
            assert result == "exists and default2"

    def test_substitute_env_vars_empty_default(self):
        """Test substitution with empty default value"""
        with patch.dict(os.environ, {}, clear=True):
            result = substitute_env_vars("${MISSING_VAR:}")
            assert result == ""

    def test_substitute_env_vars_no_placeholders(self):
        """Test substitution with no placeholders"""
        result = substitute_env_vars("plain text without variables")
        assert result == "plain text without variables"

    def test_substitute_env_vars_special_characters_in_default(self):
        """Test substitution with special characters in default value"""
        with patch.dict(os.environ, {}, clear=True):
            result = substitute_env_vars("${VAR:default:with:colons}")
            assert result == "default:with:colons"

    def test_substitute_env_vars_nested_braces(self):
        """Test that nested braces are handled correctly"""
        with patch.dict(os.environ, {"VAR": "value"}):
            result = substitute_env_vars("${VAR:default} and {not_a_var}")
            assert result == "value and {not_a_var}"

    def test_substitute_env_vars_malformed_expressions(self):
        """Test handling of malformed variable expressions"""
        # Missing closing brace
        result = substitute_env_vars("${UNCLOSED_VAR")
        assert result == "${UNCLOSED_VAR"

        # Missing opening brace
        result = substitute_env_vars("MISSING_OPEN}")
        assert result == "MISSING_OPEN}"

    def test_substitute_env_vars_complex_nested_braces(self):
        """Test handling of complex nested braces"""
        with patch.dict(os.environ, {"VAR": "test"}):
            # Should only substitute the outermost complete expression
            result = substitute_env_vars("${VAR:{nested}}")
            assert result == "test"

    def test_substitute_env_vars_empty_variable_name(self):
        """Test handling of empty variable names"""
        result = substitute_env_vars("${}")
        assert result == ""

        result = substitute_env_vars("${:default}")
        assert result == "default"

    def test_substitute_env_vars_iterative_substitution(self):
        """Test nested/iterative substitutions"""
        with patch.dict(os.environ, {"VAR1": "${VAR2}", "VAR2": "final_value"}):
            result = substitute_env_vars("${VAR1}")
            assert result == "final_value"

    def test_substitute_env_vars_circular_reference_protection(self):
        """Test protection against circular references"""
        with patch.dict(os.environ, {"VAR1": "${VAR2}", "VAR2": "${VAR1}"}):
            # Should not cause infinite loop, should stop after max iterations
            result = substitute_env_vars("${VAR1}")
            # After max iterations, should contain one of the circular refs
            assert "${VAR" in result

    def test_substitute_env_vars_max_iterations_limit(self):
        """Test that substitution respects max iteration limit"""
        # Create a chain longer than max_iterations (10)
        env_vars = {}
        for i in range(12):
            if i == 11:
                env_vars[f"VAR{i}"] = "final_value"
            else:
                env_vars[f"VAR{i}"] = f"${{VAR{i + 1}}}"

        with patch.dict(os.environ, env_vars):
            result = substitute_env_vars("${VAR0}")
            # Should not resolve completely due to iteration limit
            assert "${VAR" in result

    def test_substitute_env_vars_multiline_content(self):
        """Test substitution in multiline content"""
        content = """
        line1: ${VAR1}
        line2: ${VAR2:default}
        line3: plain text
        """
        with patch.dict(os.environ, {"VAR1": "value1"}):
            result = substitute_env_vars(content)
            expected = """
        line1: value1
        line2: default
        line3: plain text
        """
            assert result == expected

    def test_substitute_env_vars_special_characters_in_values(self):
        """Test handling of special characters in environment variable values"""
        with patch.dict(os.environ, {"SPECIAL_VAR": "value with $pecial ch@r@cters!"}):
            result = substitute_env_vars("${SPECIAL_VAR}")
            assert result == "value with $pecial ch@r@cters!"

    def test_substitute_env_vars_dollar_sign_without_brace(self):
        """Test dollar signs that are not part of variable expressions"""
        result = substitute_env_vars("$100 costs $200")
        assert result == "$100 costs $200"

    def test_substitute_env_vars_multiple_same_variable(self):
        """Test multiple occurrences of the same variable"""
        with patch.dict(os.environ, {"REPEAT_VAR": "repeated"}):
            result = substitute_env_vars("${REPEAT_VAR} and ${REPEAT_VAR} again")
            assert result == "repeated and repeated again"


@pytest.mark.unit
class TestLoadYamlWithEnvSubstitution:
    """Test the load_yaml_with_env_substitution function"""

    def test_load_yaml_file_basic(self):
        """Test loading and substituting a YAML file"""
        yaml_content = """
database:
  host: ${DB_HOST:localhost}
  port: ${DB_PORT:5432}
  name: ${DB_NAME}
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            temp_path = f.name

        try:
            with patch.dict(os.environ, {"DB_NAME": "production"}):
                result = load_yaml_with_env_substitution(temp_path)

                assert "localhost" in result  # default value used
                assert "5432" in result  # default value used
                assert "production" in result  # env var value used
                assert "${DB_HOST:localhost}" not in result  # substitution happened
                assert "${DB_PORT:5432}" not in result  # substitution happened
                assert "${DB_NAME}" not in result  # substitution happened
        finally:
            os.unlink(temp_path)

    def test_load_yaml_file_with_complex_structure(self):
        """Test loading YAML with nested substitutions"""
        yaml_content = """
app:
  name: ${APP_NAME:MyApp}
  config:
    url: https://${HOST:example.com}:${PORT:8080}/api
    credentials:
      username: ${USER}
      password: ${PASS:default_pass}
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            temp_path = f.name

        try:
            with patch.dict(os.environ, {"HOST": "prod.example.com", "USER": "admin"}):
                result = load_yaml_with_env_substitution(temp_path)

                assert "MyApp" in result  # default used
                assert "prod.example.com" in result  # env var used
                assert "8080" in result  # default used
                assert "admin" in result  # env var used
                assert "default_pass" in result  # default used
        finally:
            os.unlink(temp_path)

    def test_load_yaml_file_not_found(self):
        """Test loading non-existent file raises appropriate error"""
        with pytest.raises(FileNotFoundError):
            load_yaml_with_env_substitution("/nonexistent/file.yaml")

    def test_load_empty_yaml_file(self):
        """Test loading empty YAML file"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("")
            temp_path = f.name

        try:
            result = load_yaml_with_env_substitution(temp_path)
            assert result == ""
        finally:
            os.unlink(temp_path)

    def test_load_yaml_no_substitutions(self):
        """Test loading YAML file without any variable expressions"""
        yaml_content = """
simple:
  key1: value1
  key2: value2
  key3: 123
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            temp_path = f.name

        try:
            result = load_yaml_with_env_substitution(temp_path)
            assert result == yaml_content
        finally:
            os.unlink(temp_path)
