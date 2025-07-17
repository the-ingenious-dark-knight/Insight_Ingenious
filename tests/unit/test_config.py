import json
import os
import tempfile
from unittest.mock import Mock, mock_open, patch

import pytest
import yaml
from pydantic import ValidationError

from ingenious.config import (
    AzureSearchSettings,
    IngeniousSettings,
    ModelSettings,
    WebSettings,
    get_config,
)
from ingenious.config.profile import substitute_environment_variables


@pytest.mark.unit
class TestSubstituteEnvironmentVariables:
    """Test environment variable substitution in config"""

    def test_substitute_with_existing_var(self):
        """Test substitution with existing environment variable"""
        yaml_content = "endpoint: ${TEST_ENDPOINT}"

        with patch.dict(os.environ, {"TEST_ENDPOINT": "https://test.endpoint.com"}):
            result = substitute_environment_variables(yaml_content)
            assert result == "endpoint: https://test.endpoint.com"

    def test_substitute_with_default_value(self):
        """Test substitution with default value when var doesn't exist"""
        yaml_content = "endpoint: ${MISSING_ENDPOINT:https://default.endpoint.com}"

        with patch.dict(os.environ, {}, clear=True):
            result = substitute_environment_variables(yaml_content)
            assert result == "endpoint: https://default.endpoint.com"

    def test_substitute_azure_openai_warning(self):
        """Test substitution with Azure OpenAI variables shows warning"""
        yaml_content = "api_key: ${AZURE_OPENAI_API_KEY:default_key}"

        with (
            patch.dict(os.environ, {}, clear=True),
            patch("builtins.print") as mock_print,
        ):
            result = substitute_environment_variables(yaml_content)

            assert result == "api_key: default_key"
            mock_print.assert_called_once()
            assert "AZURE_OPENAI_API_KEY" in str(mock_print.call_args)

    def test_substitute_placeholder_info(self):
        """Test substitution with placeholder value shows info"""
        yaml_content = "service: ${OPTIONAL_SERVICE:placeholder_service}"

        with (
            patch.dict(os.environ, {}, clear=True),
            patch("builtins.print") as mock_print,
        ):
            result = substitute_environment_variables(yaml_content)

            assert result == "service: placeholder_service"
            mock_print.assert_called_once()
            assert "OPTIONAL_SERVICE" in str(mock_print.call_args)

    def test_substitute_missing_var_no_default(self):
        """Test substitution with missing var and no default shows error"""
        yaml_content = "required: ${REQUIRED_VAR}"

        with (
            patch.dict(os.environ, {}, clear=True),
            patch("builtins.print") as mock_print,
        ):
            result = substitute_environment_variables(yaml_content)

            assert result == "required: ${REQUIRED_VAR}"  # Returns original
            mock_print.assert_called_once()
            assert "REQUIRED_VAR" in str(mock_print.call_args)

    def test_substitute_multiple_variables(self):
        """Test substitution with multiple environment variables"""
        yaml_content = """
        endpoint: ${API_ENDPOINT:https://default.com}
        key: ${API_KEY}
        optional: ${OPTIONAL_VAR:default_value}
        """

        with patch.dict(os.environ, {"API_KEY": "secret_key"}, clear=True):
            result = substitute_environment_variables(yaml_content)

            assert "https://default.com" in result
            assert "secret_key" in result
            assert "default_value" in result

    def test_substitute_no_variables(self):
        """Test substitution with no variables to substitute"""
        yaml_content = """
        plain_config:
          value: "no variables here"
          number: 42
        """

        result = substitute_environment_variables(yaml_content)
        assert result == yaml_content

    def test_substitute_complex_default_value(self):
        """Test substitution with complex default value containing colons"""
        yaml_content = "url: ${DATABASE_URL:postgresql://user:pass@localhost:5432/db}"

        with patch.dict(os.environ, {}, clear=True):
            result = substitute_environment_variables(yaml_content)
            assert result == "url: postgresql://user:pass@localhost:5432/db"

    def test_substitute_existing_var_overrides_default(self):
        """Test that existing environment variable overrides default"""
        yaml_content = "value: ${TEST_VAR:default_value}"

        with patch.dict(os.environ, {"TEST_VAR": "actual_value"}):
            result = substitute_environment_variables(yaml_content)
            assert result == "value: actual_value"

    def test_substitute_empty_default(self):
        """Test substitution with empty default value"""
        yaml_content = "empty: ${EMPTY_VAR:}"

        with patch.dict(os.environ, {}, clear=True):
            result = substitute_environment_variables(yaml_content)
            assert result == "empty: "


@pytest.mark.unit
class TestConfig:
    """Test Config class functionality"""

    def test_config_from_yaml_str_valid(self):
        """Test creating Config from valid YAML string"""
        # yaml_content = """
        # test_key: test_value
        # """

        with (
            patch(
                "ingenious.config.config.config_ns_models.Config.model_validate_json"
            ) as mock_validate,
            patch("ingenious.config.config.Profiles") as mock_profiles,
            patch("ingenious.config.config.config_models.Config") as mock_config_model,
        ):
            mock_config = Mock()
            mock_config.profile = "test_profile"
            mock_validate.return_value = mock_config
            mock_profiles.return_value.get_profile_by_name.return_value = Mock()
            mock_config_model.return_value = Mock()

            # _result = Config.from_yaml_str(yaml_content)
            pass

            # Verify that validation was called
            mock_validate.assert_called_once()

            # Verify the JSON data structure
            call_args = mock_validate.call_args[0][0]
            parsed_data = json.loads(call_args)
            assert "test_key" in parsed_data
            assert parsed_data["test_key"] == "test_value"

    def test_config_from_yaml_str_with_env_substitution(self):
        """Test creating Config from YAML string with environment variables"""
        # Create a temporary profile file
        profile_content = """
- name: test_profile
  models:
    - model: gpt-3.5-turbo
      api_key: test-key
      base_url: https://test.openai.azure.com/
      deployment: gpt-35-turbo
      api_version: 2023-03-15-preview
  chat_history:
    database_connection_string: ""
  receiver_configuration:
    enable: false
    api_url: ""
    api_key: "DevApiKey"
  web_configuration:
    authentication:
      enable: false
      username: "admin"
      password: "admin123"
      type: "basic"
"""

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yml", delete=False
        ) as profile_f:
            profile_f.write(profile_content)
            profile_file = profile_f.name

        try:
            with patch.dict(
                os.environ,
                {
                    "TEST_PROFILE": "test_profile",
                    "TEST_MODEL": "gpt-3.5-turbo",
                    "INGENIOUS_PROFILE_PATH": profile_file,
                },
                clear=True,
            ):
                # TODO: Re-enable this test when Config.from_yaml_str is available
                # config = Config.from_yaml_str(yaml_content)
                # assert config is not None
                # assert len(config.models) == 1
                # assert config.models[0].model == "gpt-3.5-turbo"
                pass

        finally:
            os.unlink(profile_file)

    def test_config_from_yaml_str_validation_error(self):
        """Test Config creation with validation error"""
        # TODO: Re-enable this test when Config.from_yaml_str is available
        # yaml_content = """
        # invalid_structure:
        #   missing_required_fields: true
        # """

        validation_errors = [
            {"loc": ("agents",), "msg": "Field required", "type": "missing"}
        ]

        mock_validation_error = ValidationError.from_exception_data(
            "Config", validation_errors
        )

        with patch(
            "ingenious.config.config.config_ns_models.Config.model_validate_json"
        ) as mock_validate:
            mock_validate.side_effect = mock_validation_error

            with pytest.raises(ValidationError):
                # Config.from_yaml_str(yaml_content)
                pass

    def test_config_from_yaml_str_validation_error_with_suggestions(self):
        """Test Config creation with validation error containing helpful suggestions"""
        # TODO: Re-enable this test when Config.from_yaml_str is available
        # yaml_content = """
        # agents:
        #   - name: test
        #     endpoint: null
        # """

        validation_errors = [
            {
                "loc": ("agents", 0, "endpoint"),
                "msg": "Input should be a valid string",
                "type": "string_type",
            }
        ]

        mock_validation_error = ValidationError.from_exception_data(
            "Config", validation_errors
        )

        with patch(
            "ingenious.config.config.config_ns_models.Config.model_validate_json"
        ) as mock_validate:
            mock_validate.side_effect = mock_validation_error

            with pytest.raises(ValidationError):
                # Config.from_yaml_str(yaml_content)
                pass

    def test_config_from_yaml_file(self):
        """Test creating Config from YAML file"""
        yaml_content = """
        agents:
          - name: file_agent
            description: Agent from file
            model: gpt-3.5-turbo
        """

        with (
            patch("builtins.open", mock_open(read_data=yaml_content)),
            patch("ingenious.config.config.Config.from_yaml_str") as mock_from_yaml_str,
        ):
            mock_config = Mock()
            mock_from_yaml_str.return_value = mock_config

            # result = Config.from_yaml("test_config.yaml")
            result = None

            mock_from_yaml_str.assert_called_once_with(yaml_content)
            assert result == mock_config

    def test_config_from_yaml_file_with_env_vars(self):
        """Test creating Config from YAML file with environment variables"""
        yaml_content = """
profile: ${TEST_PROFILE:test_profile}

models:
  - model: ${TEST_MODEL:gpt-4}
    api_type: rest
    api_version: 2023-03-15-preview

logging:
  root_log_level: info
  log_level: info

chat_history:
  database_type: sqlite
  database_path: ./tmp/test.db
  memory_path: ./tmp

tool_service:
  enable: false

chat_service:
  type: multi_agent


web_configuration:
  ip_address: 0.0.0.0
  port: 8000
  type: fastapi
  asynchronous: false

local_sql_db:
  database_path: /tmp/test_db
  sample_csv_path: ""
  sample_database_name: test_db
"""

        # Create a temporary profile file
        profile_content = """
- name: test_profile
  models:
    - model: gpt-3.5-turbo
      api_key: test-key
      base_url: https://test.openai.azure.com/
      deployment: gpt-35-turbo
      api_version: 2023-03-15-preview
  chat_history:
    database_connection_string: ""
  receiver_configuration:
    enable: false
    api_url: ""
    api_key: "DevApiKey"
  web_configuration:
    authentication:
      enable: false
      username: "admin"
      password: "admin123"
      type: "basic"
"""

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yml", delete=False
        ) as profile_f:
            profile_f.write(profile_content)
            profile_file = profile_f.name

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as config_f:
            config_f.write(yaml_content)
            config_file = config_f.name

        try:
            with patch.dict(
                os.environ,
                {
                    "TEST_PROFILE": "test_profile",
                    "TEST_MODEL": "gpt-3.5-turbo",
                    "INGENIOUS_PROFILE_PATH": profile_file,
                },
                clear=True,
            ):
                # config = Config.from_yaml(config_file)
                config = None

                # Verify environment variable substitution occurred
                assert config is not None
                assert len(config.models) == 1
                assert (
                    config.models[0].model == "gpt-3.5-turbo"
                )  # Environment variable was substituted

        finally:
            os.unlink(profile_file)
            os.unlink(config_file)

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

    def test_config_from_yaml_str_empty_yaml(self):
        """Test creating Config from empty YAML string"""
        # TODO: Re-enable this test when Config.from_yaml_str is available
        # yaml_content = ""

        with (
            patch(
                "ingenious.config.config.config_ns_models.Config.model_validate_json"
            ) as mock_validate,
            patch("ingenious.config.config.Profiles") as mock_profiles,
            patch("ingenious.config.config.config_models.Config") as mock_config_model,
        ):
            mock_config = Mock()
            mock_config.profile = "test_profile"
            mock_validate.return_value = mock_config
            mock_profiles.return_value.get_profile_by_name.return_value = Mock()
            mock_config_model.return_value = Mock()

            # Config.from_yaml_str(yaml_content)
            pass

            # Should still try to validate even with empty content
            mock_validate.assert_called_once()

    def test_config_from_yaml_str_invalid_yaml(self):
        """Test creating Config from invalid YAML string"""
        # TODO: Re-enable this test when Config.from_yaml_str is available
        # yaml_content = """
        # invalid: yaml: content:
        #   - unmatched: [brackets
        # """

        with pytest.raises(yaml.YAMLError):
            # Config.from_yaml_str(yaml_content)
            pass


@pytest.mark.unit
class TestIngeniousSettings:
    """Test new Pydantic settings-based configuration"""

    def test_settings_default_creation(self):
        """Test creating settings with default values"""
        with patch.dict(
            os.environ,
            {
                "AZURE_OPENAI_API_KEY": "test-key",
                "AZURE_OPENAI_BASE_URL": "https://test.openai.azure.com/",
            },
            clear=True,
        ):
            settings = IngeniousSettings()

            assert settings.profile == "default"
            assert settings.chat_history.database_type == "sqlite"
            assert settings.logging.root_log_level == "info"
            assert settings.web_configuration.port == 8000
            assert len(settings.models) == 1
            assert settings.models[0].api_key == "test-key"

    def test_settings_env_var_loading(self):
        """Test loading settings from environment variables"""
        with patch.dict(
            os.environ,
            {
                "INGENIOUS_PROFILE": "production",
                "INGENIOUS_WEB_CONFIGURATION__PORT": "9000",
                "INGENIOUS_LOGGING__ROOT_LOG_LEVEL": "warning",
                "AZURE_OPENAI_API_KEY": "prod-key",
                "AZURE_OPENAI_BASE_URL": "https://prod.openai.azure.com/",
            },
            clear=True,
        ):
            settings = IngeniousSettings()

            assert settings.profile == "production"
            assert settings.web_configuration.port == 9000
            assert settings.logging.root_log_level == "warning"
            assert settings.models[0].api_key == "prod-key"

    def test_settings_validation_errors(self):
        """Test validation errors provide helpful messages"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError) as exc_info:
                IngeniousSettings()

            error_message = str(exc_info.value)
            assert "At least one model must be configured" in error_message
            assert "AZURE_OPENAI_API_KEY" in error_message

    def test_settings_model_validation(self):
        """Test model-specific validation"""
        with pytest.raises(ValueError) as exc_info:
            ModelSettings(
                model="gpt-4",
                api_key="placeholder_key",
                base_url="https://api.openai.com/",
            )

        assert "API key is required" in str(exc_info.value)

    def test_settings_web_port_validation(self):
        """Test web port validation"""
        with pytest.raises(ValueError) as exc_info:
            WebSettings(port=70000)

        assert "Port must be between 1 and 65535" in str(exc_info.value)

    def test_settings_log_level_validation(self):
        """Test log level validation"""
        with patch.dict(
            os.environ,
            {
                "INGENIOUS_LOGGING__ROOT_LOG_LEVEL": "invalid_level",
                "AZURE_OPENAI_API_KEY": "test-key",
                "AZURE_OPENAI_BASE_URL": "https://test.openai.azure.com/",
            },
            clear=True,
        ):
            with pytest.raises(ValueError) as exc_info:
                IngeniousSettings()

            assert "Log level must be one of" in str(exc_info.value)

    def test_settings_from_env_file(self):
        """Test loading settings from .env file"""
        env_content = """
INGENIOUS_PROFILE=test_env
INGENIOUS_WEB_CONFIGURATION__PORT=8080
AZURE_OPENAI_API_KEY=env-file-key
AZURE_OPENAI_BASE_URL=https://env.openai.azure.com/
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write(env_content)
            env_file = f.name

        try:
            # Set environment for models since pydantic-settings list parsing is complex
            with patch.dict(
                os.environ,
                {
                    "AZURE_OPENAI_API_KEY": "env-file-key",
                    "AZURE_OPENAI_BASE_URL": "https://env.openai.azure.com/",
                },
                clear=True,
            ):
                settings = IngeniousSettings.load_from_env_file(env_file)

                assert settings.profile == "test_env"
                assert settings.web_configuration.port == 8080
                assert settings.models[0].api_key == "env-file-key"
        finally:
            os.unlink(env_file)

    def test_settings_minimal_config(self):
        """Test creating minimal configuration"""
        with patch.dict(
            os.environ,
            {
                "AZURE_OPENAI_API_KEY": "minimal-key",
                "AZURE_OPENAI_BASE_URL": "https://minimal.openai.azure.com/",
            },
            clear=True,
        ):
            settings = IngeniousSettings.create_minimal_config()

            assert len(settings.models) == 1
            assert settings.models[0].model == "gpt-4.1-nano"
            assert settings.logging.root_log_level == "debug"
            assert not settings.web_configuration.authentication.enable

    def test_settings_configuration_validation(self):
        """Test complete configuration validation"""
        with patch.dict(
            os.environ,
            {
                "AZURE_OPENAI_API_KEY": "test-key",
                "AZURE_OPENAI_BASE_URL": "https://test.openai.azure.com/",
            },
            clear=True,
        ):
            settings = IngeniousSettings()

            # Should not raise any exceptions
            settings.validate_configuration()

    def test_settings_configuration_validation_errors(self):
        """Test configuration validation with errors"""
        # Create settings without triggering model validation first
        with patch.dict(
            os.environ,
            {
                "AZURE_OPENAI_API_KEY": "test-key",
                "AZURE_OPENAI_BASE_URL": "https://test.openai.azure.com/",
            },
            clear=True,
        ):
            settings = IngeniousSettings()
            # Use model_construct to bypass validation during creation
            placeholder_model = ModelSettings.model_construct(
                model="gpt-4", api_key="placeholder_key", base_url="placeholder_url"
            )
            settings.models = [placeholder_model]

        with pytest.raises(ValueError) as exc_info:
            settings.validate_configuration()

        error_message = str(exc_info.value)
        assert "Configuration validation failed" in error_message
        assert "placeholder" in error_message.lower()

    def test_get_config_new_function(self):
        """Test the new get_config_new function"""
        with patch.dict(
            os.environ,
            {
                "AZURE_OPENAI_API_KEY": "new-config-key",
                "AZURE_OPENAI_BASE_URL": "https://new-config.openai.azure.com/",
            },
            clear=True,
        ):
            settings = get_config()

            assert isinstance(settings, IngeniousSettings)
            assert settings.models[0].api_key == "new-config-key"

    def test_nested_environment_variables(self):
        """Test nested environment variable configuration"""
        with patch.dict(
            os.environ,
            {
                "INGENIOUS_CHAT_HISTORY__DATABASE_TYPE": "azuresql",
                "INGENIOUS_CHAT_HISTORY__DATABASE_NAME": "prod_db",
                "INGENIOUS_WEB_CONFIGURATION__AUTHENTICATION__ENABLE": "true",
                "INGENIOUS_WEB_CONFIGURATION__AUTHENTICATION__PASSWORD": "secure_pass",
                "AZURE_OPENAI_API_KEY": "test-key",
                "AZURE_OPENAI_BASE_URL": "https://test.openai.azure.com/",
            },
            clear=True,
        ):
            settings = IngeniousSettings()

            assert settings.chat_history.database_type == "azuresql"
            assert settings.chat_history.database_name == "prod_db"
            assert settings.web_configuration.authentication.enable is True
            assert settings.web_configuration.authentication.password == "secure_pass"

    def test_optional_services_configuration(self):
        """Test configuration of optional services"""
        # Create settings with explicit azure search services
        with patch.dict(
            os.environ,
            {
                "AZURE_OPENAI_API_KEY": "test-key",
                "AZURE_OPENAI_BASE_URL": "https://test.openai.azure.com/",
            },
            clear=True,
        ):
            settings = IngeniousSettings(
                azure_search_services=[
                    AzureSearchSettings(
                        service="test-search",
                        endpoint="https://test-search.search.windows.net",
                        key="search-key",
                    )
                ]
            )

            assert settings.azure_search_services is not None
            assert len(settings.azure_search_services) == 1
            assert settings.azure_search_services[0].service == "test-search"
            assert (
                settings.azure_search_services[0].endpoint
                == "https://test-search.search.windows.net"
            )

    def test_file_storage_configuration(self):
        """Test file storage configuration options"""
        with patch.dict(
            os.environ,
            {
                "INGENIOUS_FILE_STORAGE__REVISIONS__STORAGE_TYPE": "azure",
                "INGENIOUS_FILE_STORAGE__REVISIONS__CONTAINER_NAME": "revisions",
                "INGENIOUS_FILE_STORAGE__REVISIONS__URL": "https://storage.blob.core.windows.net",
                "AZURE_OPENAI_API_KEY": "test-key",
                "AZURE_OPENAI_BASE_URL": "https://test.openai.azure.com/",
            },
            clear=True,
        ):
            settings = IngeniousSettings()

            assert settings.file_storage.revisions.storage_type == "azure"
            assert settings.file_storage.revisions.container_name == "revisions"
            assert (
                settings.file_storage.revisions.url
                == "https://storage.blob.core.windows.net"
            )

    def test_models_nested_environment_variables(self):
        """Test models configuration with nested environment variables"""
        with patch.dict(
            os.environ,
            {
                "INGENIOUS_MODELS__0__MODEL": "gpt-4.1-nano",
                "INGENIOUS_MODELS__0__API_KEY": "test-nested-key",
                "INGENIOUS_MODELS__0__BASE_URL": "https://nested.openai.azure.com/",
                "INGENIOUS_MODELS__0__API_VERSION": "2024-12-01-preview",
                "INGENIOUS_MODELS__0__DEPLOYMENT": "gpt-4.1-nano",
                "INGENIOUS_MODELS__1__MODEL": "gpt-3.5-turbo",
                "INGENIOUS_MODELS__1__API_KEY": "test-nested-key-2",
                "INGENIOUS_MODELS__1__BASE_URL": "https://nested2.openai.azure.com/",
                "INGENIOUS_MODELS__1__DEPLOYMENT": "gpt-35-turbo",
            },
            clear=True,
        ):
            settings = IngeniousSettings()

            assert len(settings.models) == 2
            assert settings.models[0].model == "gpt-4.1-nano"
            assert settings.models[0].api_key == "test-nested-key"
            assert settings.models[0].base_url == "https://nested.openai.azure.com/"
            assert settings.models[0].api_version == "2024-12-01-preview"
            assert settings.models[0].deployment == "gpt-4.1-nano"

            assert settings.models[1].model == "gpt-3.5-turbo"
            assert settings.models[1].api_key == "test-nested-key-2"
            assert settings.models[1].base_url == "https://nested2.openai.azure.com/"
            assert settings.models[1].deployment == "gpt-35-turbo"

    def test_models_json_string_format(self):
        """Test models configuration with JSON string format"""
        models_json = '[{"model": "gpt-4.1-nano", "api_key": "test-json-key", "base_url": "https://json.openai.azure.com/", "api_version": "2024-12-01-preview", "deployment": "gpt-4.1-nano"}]'

        with patch.dict(
            os.environ,
            {
                "INGENIOUS_MODELS": models_json,
            },
            clear=True,
        ):
            settings = IngeniousSettings()

            assert len(settings.models) == 1
            assert settings.models[0].model == "gpt-4.1-nano"
            assert settings.models[0].api_key == "test-json-key"
            assert settings.models[0].base_url == "https://json.openai.azure.com/"
            assert settings.models[0].api_version == "2024-12-01-preview"
            assert settings.models[0].deployment == "gpt-4.1-nano"
