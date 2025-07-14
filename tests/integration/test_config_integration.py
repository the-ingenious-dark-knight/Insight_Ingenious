import os
import tempfile
from unittest.mock import patch

import pytest

from ingenious.config.config import get_config
from ingenious.config.settings import IngeniousSettings


@pytest.mark.integration
class TestConfigIntegration:
    """Integration tests for configuration loading and processing"""

    def test_get_config_integration(self):
        """Test complete get_config() workflow"""
        with patch.dict(os.environ, {
            'AZURE_OPENAI_API_KEY': 'integration-test-key',
            'AZURE_OPENAI_BASE_URL': 'https://integration.openai.azure.com/',
            'AZURE_OPENAI_MODEL': 'gpt-4',
            'INGENIOUS_PROFILE': 'integration',
            'INGENIOUS_WEB_CONFIGURATION__PORT': '9000',
            'INGENIOUS_LOGGING__LOG_LEVEL': 'debug',
        }):
            config = get_config()
            
            # Verify the configuration was loaded correctly
            assert config is not None
            assert isinstance(config, IngeniousSettings)
            assert len(config.models) >= 1
            assert config.models[0].model == "gpt-4"
            assert config.models[0].api_key == "integration-test-key"
            assert config.models[0].base_url == "https://integration.openai.azure.com/"
            assert config.profile == "integration"
            assert config.web_configuration.port == 9000
            assert config.logging.log_level == "debug"

    def test_env_file_integration(self):
        """Test loading configuration from .env file in integration context"""
        env_content = """
# Integration test environment file
AZURE_OPENAI_API_KEY=env-file-test-key
AZURE_OPENAI_BASE_URL=https://envfile.openai.azure.com/
AZURE_OPENAI_MODEL=gpt-3.5-turbo
INGENIOUS_PROFILE=envfile_profile
INGENIOUS_CHAT_HISTORY__DATABASE_TYPE=sqlite
INGENIOUS_CHAT_HISTORY__DATABASE_PATH=./tmp/integration_test.db
INGENIOUS_WEB_CONFIGURATION__PORT=8080
INGENIOUS_WEB_CONFIGURATION__AUTHENTICATION__ENABLE=true
INGENIOUS_WEB_CONFIGURATION__AUTHENTICATION__USERNAME=testuser
INGENIOUS_WEB_CONFIGURATION__AUTHENTICATION__PASSWORD=testpass
INGENIOUS_LOGGING__ROOT_LOG_LEVEL=warning
INGENIOUS_LOGGING__LOG_LEVEL=warning
        """.strip()

        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write(env_content)
            env_file = f.name

        try:
            # Set minimal environment and load from file
            with patch.dict(os.environ, {
                'AZURE_OPENAI_API_KEY': 'env-file-test-key',
                'AZURE_OPENAI_BASE_URL': 'https://envfile.openai.azure.com/',
                'AZURE_OPENAI_MODEL': 'gpt-3.5-turbo',
            }):
                settings = IngeniousSettings(_env_file=env_file)
                
                # Verify file-based configuration
                assert settings.profile == "envfile_profile"
                assert settings.models[0].model == "gpt-3.5-turbo"
                assert settings.models[0].api_key == "env-file-test-key"
                assert settings.chat_history.database_type == "sqlite"
                assert settings.chat_history.database_path == "./tmp/integration_test.db"
                assert settings.web_configuration.port == 8080
                assert settings.web_configuration.authentication.enable is True
                assert settings.web_configuration.authentication.username == "testuser"
                assert settings.logging.root_log_level == "warning"
        finally:
            os.unlink(env_file)

    def test_config_validation_integration(self):
        """Test configuration validation in integration context"""
        # Test with invalid configuration
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="At least one model must be configured"):
                get_config()

    def test_config_backward_compatibility_integration(self):
        """Test that new config system provides backward compatibility"""
        with patch.dict(os.environ, {
            'AZURE_OPENAI_API_KEY': 'compat-test-key',
            'AZURE_OPENAI_BASE_URL': 'https://compat.openai.azure.com/',
        }):
            config = get_config()
            
            # Test backward compatibility - ensure common attributes exist
            assert hasattr(config, 'models')
            assert hasattr(config, 'chat_history')
            assert hasattr(config, 'web_configuration')
            assert hasattr(config, 'logging')
            assert hasattr(config, 'profile')
            
            # Test nested attribute access patterns that existed in old system
            assert hasattr(config.models[0], 'model')
            assert hasattr(config.models[0], 'api_key')
            assert hasattr(config.models[0], 'base_url')
            assert hasattr(config.chat_history, 'database_type')
            assert hasattr(config.web_configuration, 'port')
            assert hasattr(config.web_configuration, 'authentication')

    def test_multiple_environment_scenarios(self):
        """Test configuration in different environment scenarios"""
        
        # Scenario 1: Development environment
        dev_env = {
            'AZURE_OPENAI_API_KEY': 'dev-key',
            'AZURE_OPENAI_BASE_URL': 'https://dev.openai.azure.com/',
            'INGENIOUS_PROFILE': 'development',
            'INGENIOUS_LOGGING__LOG_LEVEL': 'debug',
            'INGENIOUS_WEB_CONFIGURATION__AUTHENTICATION__ENABLE': 'false',
        }
        
        with patch.dict(os.environ, dev_env, clear=True):
            dev_config = get_config()
            assert dev_config.profile == "development"
            assert dev_config.logging.log_level == "debug"
            assert dev_config.web_configuration.authentication.enable is False
        
        # Scenario 2: Production environment
        prod_env = {
            'AZURE_OPENAI_API_KEY': 'prod-key',
            'AZURE_OPENAI_BASE_URL': 'https://prod.openai.azure.com/',
            'INGENIOUS_PROFILE': 'production',
            'INGENIOUS_LOGGING__LOG_LEVEL': 'warning',
            'INGENIOUS_WEB_CONFIGURATION__AUTHENTICATION__ENABLE': 'true',
            'INGENIOUS_WEB_CONFIGURATION__AUTHENTICATION__USERNAME': 'admin',
            'INGENIOUS_WEB_CONFIGURATION__AUTHENTICATION__PASSWORD': 'secure-password',
        }
        
        with patch.dict(os.environ, prod_env, clear=True):
            prod_config = get_config()
            assert prod_config.profile == "production"
            assert prod_config.logging.log_level == "warning"
            assert prod_config.web_configuration.authentication.enable is True
            assert prod_config.web_configuration.authentication.username == "admin"

    def test_config_error_handling_integration(self):
        """Test error handling in integration scenarios"""
        
        # Test with missing required configuration
        with patch.dict(os.environ, {
            'AZURE_OPENAI_MODEL': 'gpt-4',
            # Missing API_KEY and BASE_URL
        }, clear=True):
            with pytest.raises(ValueError):
                get_config()
        
        # Test with invalid log level
        with patch.dict(os.environ, {
            'AZURE_OPENAI_API_KEY': 'test-key',
            'AZURE_OPENAI_BASE_URL': 'https://test.openai.azure.com/',
            'INGENIOUS_LOGGING__LOG_LEVEL': 'invalid_level',
        }):
            with pytest.raises(Exception):  # ValidationError from pydantic
                get_config()

    def test_config_environment_override_integration(self):
        """Test that environment variables properly override defaults"""
        custom_env = {
            'AZURE_OPENAI_API_KEY': 'override-key',
            'AZURE_OPENAI_BASE_URL': 'https://override.openai.azure.com/',
            'AZURE_OPENAI_MODEL': 'gpt-3.5-turbo',
            'INGENIOUS_PROFILE': 'custom',
            'INGENIOUS_WEB_CONFIGURATION__PORT': '7777',
            'INGENIOUS_WEB_CONFIGURATION__IP_ADDRESS': '127.0.0.1',
            'INGENIOUS_CHAT_HISTORY__DATABASE_TYPE': 'azuresql',
            'INGENIOUS_CHAT_HISTORY__MEMORY_PATH': '/custom/memory/path',
            'INGENIOUS_TOOL_SERVICE__ENABLE': 'true',
            'INGENIOUS_CHAINLIT_CONFIGURATION__ENABLE': 'true',
        }
        
        with patch.dict(os.environ, custom_env, clear=True):
            config = get_config()
            
            # Verify all overrides work
            assert config.profile == "custom"
            assert config.models[0].model == "gpt-3.5-turbo"
            assert config.models[0].api_key == "override-key"
            assert config.web_configuration.port == 7777
            assert config.web_configuration.ip_address == "127.0.0.1"
            assert config.chat_history.database_type == "azuresql"
            assert config.chat_history.memory_path == "/custom/memory/path"
            assert config.tool_service.enable is True
            assert config.chainlit_configuration.enable is True