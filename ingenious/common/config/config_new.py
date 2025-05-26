import json
import logging
import os
from pathlib import Path

import yaml

from ingenious.common.errors.common import ConfigurationError
from ingenious.domain.model.config import config_ns as config_ns_models

logger = logging.getLogger(__name__)

# Configuration singleton instance
_config_instance = None


class Config:
    """
    Class to handle loading the configuration file
    """

    @staticmethod
    def from_yaml(file_path):
        with open(file_path, "r") as file:
            file_str = file.read()
            return Config.from_yaml_str(file_str)

    @staticmethod
    def from_yaml_str(config_yml):
        try:
            yaml_data = yaml.safe_load(config_yml)
            if not yaml_data:
                raise ConfigurationError("Invalid or empty YAML configuration")

            json_data = json.dumps(yaml_data)
            config_ns: config_ns_models.Config
            try:
                config_ns = config_ns_models.Config.model_validate_json(json_data)
            except Exception as e:
                logger.debug(f"Configuration validation error: {e}")
                raise ConfigurationError(f"Invalid configuration format: {str(e)}")

            return config_ns

        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML syntax: {str(e)}")
        except ConfigurationError as e:
            raise e
        except Exception as e:
            raise ConfigurationError(f"Unexpected error loading configuration: {str(e)}")

    @staticmethod
    def get_config(config_path=None):
        # Check if config path is provided
        if not config_path:
            # Default to current directory
            config_path = os.path.join(os.getcwd(), "config.yml")
            # Fall back to test_config.yml for tests
            if not os.path.exists(config_path) and "PYTEST_CURRENT_TEST" in os.environ:
                config_path = os.path.join(os.getcwd(), "test_config.yml")

        # Ensure config file exists
        if not os.path.exists(config_path):
            raise ConfigurationError(
                f"Configuration file not found: {config_path}. "
                f"Create a config.yml file in the project root or "
                f"set the INGENIOUS_CONFIG_PATH environment variable."
            )

        logger.debug(f"Loading configuration from {config_path}")

        try:
            # Load config from file
            config_instance = Config.from_yaml(config_path)
            return config_instance
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise ConfigurationError(f"Failed to load configuration: {e}")


def get_config(
    config_path=None,
    project_path=None,
):
    """
    Load the configuration from config.yml

    Args:
        config_path (str, optional): Path to the config.yml file.
        project_path (str, optional): Path to the project directory.

    Returns:
        config_ns_models.Config: Configuration object
    """
    global _config_instance

    # If config is already loaded, return it
    if _config_instance is not None:
        return _config_instance

    # Get config file path
    if not config_path:
        if project_path:
            config_path = os.path.join(project_path, "config.yml")
        else:
            # Check environment variable first
            config_path = os.environ.get("INGENIOUS_CONFIG_PATH")
            if not config_path:
                # Default to current directory
                config_path = os.path.join(os.getcwd(), "config.yml")
                # Fall back to test_config.yml for tests
                if (
                    not os.path.exists(config_path)
                    and "PYTEST_CURRENT_TEST" in os.environ
                ):
                    config_path = os.path.join(os.getcwd(), "test_config.yml")

    # Ensure config file exists
    if not os.path.exists(config_path):
        raise ConfigurationError(
            f"Configuration file not found: {config_path}. "
            f"Create a config.yml file in the project root or "
            f"set the INGENIOUS_CONFIG_PATH environment variable."
        )

    logger.debug(f"Loading configuration from {config_path}")

    try:
        # Load config from file
        config_instance = Config.from_yaml(config_path)
        
        # Set the singleton instance
        _config_instance = config_instance
        
        return config_instance
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        raise ConfigurationError(f"Failed to load configuration: {e}")
