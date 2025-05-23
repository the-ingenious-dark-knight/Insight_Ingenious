"""
Pytest configuration file for Insight Ingenious tests.

This module contains fixtures and configuration settings for pytest.
"""

import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

# Add the project root to the path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Create a temporary config file for testing
with open("test_config.yml", "w") as f:
    yaml.dump({
        "profile": "test",
        "models": [
            {
                "name": "test-model",
                "model": "gpt-3.5-turbo",
                "base_url": "https://example.com/openai",
                "api_key": "test-api-key",
                "api_version": "2023-05-15",
                "api_type": "azure"  # This was missing
            }
        ],
        "file_storage": {
            "storage_type": "local",
            "path": "./storage",
            "containers": [
                {"name": "data", "path": "./data"},
                {"name": "revisions", "path": "./revisions"}
            ]
        },
        "chat_history": {
            "database_type": "sqlite",
            "connection_string": ":memory:"
        },
        "chat_service": {
            "type": "basic"
        },
        "web_configuration": {
            "authentication": {
                "enable": False,
                "username": "admin",
                "password": "password"
            }
        },
        # Missing required fields
        "logging": {
            "root_log_level": "INFO",
            "log_level": "INFO"
        },
        "tool_service": {
            "enable": False
        },
        "chainlit_configuration": {
            "enable": False
        },
        "azure_search_services": [],
        "local_sql_db": {
            "connection_string": ""
        },
        "azure_sql_services": {
            "database_connection_string": ""
        }
    }, f)

# Patch the get_config method to use our test file
@pytest.fixture(autouse=True)
def mock_config():
    """Automatically mock the config module for all tests."""
    # Import here to avoid circular import issues
    from ingenious.common.config.config import Config, get_config

    orig_get_config = Config.get_config

    def get_test_config(*args, **kwargs):
        return orig_get_config("test_config.yml")

    with patch('ingenious.common.config.config.Config.get_config', side_effect=get_test_config):
        with patch('ingenious.common.config.config.get_config', side_effect=get_test_config):
            with patch('ingenious.common.config.profile.Profiles.get_kv_secret', return_value="[]"):
                yield


@pytest.fixture
def temp_dir():
    """Create a temporary directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def sample_profile_dict():
    """
    Create a sample profile dictionary.

    Returns:
        dict: Sample profile dictionary
    """
    return [{
        "name": "test",
        "models": [
            {
                "model": "gpt-4o",
                "api_key": "test_api_key",
                "base_url": "https://test.openai.azure.com/openai/deployments/test"
            }
        ],
        "chat_history": {
            "database_connection_string": ""
        },
        "azure_search_services": [
            {
                "service": "test_service",
                "key": "test_key"
            }
        ],
        "azure_sql_services": {
            "database_connection_string": ""
        },
        "receiver_configuration": {
            "enable": False,
            "api_url": "",
            "api_key": ""
        },
        "chainlit_configuration": {
            "enable": False,
            "authentication": {
                "enable": False,
                "github_secret": "",
                "github_client_id": ""
            }
        },
        "web_configuration": {
            "authentication": {
                "enable": False,
                "username": "test_user",
                "password": "test_password"
            }
        },
        "file_storage": {
            "revisions": {
                "url": "",
                "client_id": "",
                "token": "",
                "authentication_method": "default_credential"
            },
            "data": {
                "url": "",
                "client_id": "",
                "token": "",
                "authentication_method": "default_credential"
            }
        }
    }]


@pytest.fixture
def sample_config_dict():
    """
    Create a sample config dictionary.

    Returns:
        dict: Sample config dictionary
    """
    return {
        "profile": "test",
        "models": [
            {
                "name": "test-model",
                "model": "gpt-3.5-turbo",
                "base_url": "https://example.com/openai",
                "api_key": "test-api-key",
                "api_version": "2023-05-15"
            }
        ],
        "file_storage": {
            "storage_type": "local",
            "path": "./storage",
            "containers": [
                {"name": "data", "path": "./data"},
                {"name": "revisions", "path": "./revisions"}
            ]
        },
        "chat_history": {
            "database_type": "sqlite",
            "connection_string": ":memory:"
        },
        "chat_service": {
            "type": "basic"
        },
        "web_configuration": {
            "authentication": {
                "enable": False,
                "username": "admin",
                "password": "password"
            }
        }
    }


@pytest.fixture
def sample_config_file(temp_dir, sample_config_dict):
    """
    Create a sample config.yml file.

    Args:
        temp_dir: Temporary directory fixture
        sample_config_dict: Sample config dictionary fixture

    Returns:
        Path: Path to the created config file
    """
    config_path = temp_dir / "config.yml"
    with open(config_path, "w") as f:
        yaml.dump(sample_config_dict, f)
    return config_path


@pytest.fixture
def sample_profile_file(temp_dir, sample_profile_dict):
    """
    Create a sample profiles.yml file.

    Args:
        temp_dir: Temporary directory fixture
        sample_profile_dict: Sample profile dictionary fixture

    Returns:
        Path: Path to the created profile file
    """
    profile_path = temp_dir / "profiles.yml"
    with open(profile_path, "w") as f:
        yaml.dump(sample_profile_dict, f)
    return profile_path


@pytest.fixture
def mock_env_vars(monkeypatch, sample_config_file, sample_profile_file):
    """
    Set up environment variables for testing.

    Args:
        monkeypatch: Pytest monkeypatch fixture
        sample_config_file: Sample config file fixture
        sample_profile_file: Sample profile file fixture
    """
    monkeypatch.setenv("INGENIOUS_CONFIG_PATH", str(sample_config_file))
    monkeypatch.setenv("INGENIOUS_PROFILES_PATH", str(sample_profile_file))
    monkeypatch.setenv("INGENIOUS_PROJECT_PATH", str(sample_config_file.parent))

    # Reset any existing config singleton
    from ingenious.common.config import config
    if hasattr(config, "_config_instance"):
        config._config_instance = None
