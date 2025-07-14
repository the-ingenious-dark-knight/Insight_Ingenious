import json
import os
from pathlib import Path

import yaml
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from pydantic import ValidationError

from ingenious.config.profile import Profiles
from ingenious.config.settings import IngeniousSettings
from ingenious.core.structured_logging import get_logger
from ingenious.models import config as config_models
from ingenious.models import config_ns as config_ns_models
from ingenious.models import profile as profile_models

logger = get_logger(__name__)


def substitute_environment_variables(yaml_content: str) -> str:
    """
    Substitute environment variables in YAML content.
    Supports patterns like ${VAR_NAME} and ${VAR_NAME:default_value}
    Handles nested substitutions by doing multiple passes.
    """

    def find_variable_expressions(content):
        """Find all ${...} expressions, handling nested braces correctly."""
        expressions = []
        i = 0
        while i < len(content):
            if content[i : i + 2] == "${":
                # Found start of expression
                start = i
                i += 2
                brace_count = 1
                while i < len(content) and brace_count > 0:
                    if content[i] == "{":
                        brace_count += 1
                    elif content[i] == "}":
                        brace_count -= 1
                    i += 1
                if brace_count == 0:
                    # Found complete expression
                    expressions.append((start, i, content[start + 2 : i - 1]))
            else:
                i += 1
        return expressions

    def replace_expression(content, var_expr):
        """Replace a single variable expression."""
        if ":" in var_expr:
            var_name, default_value = var_expr.split(":", 1)
            env_value = os.getenv(var_name)
            if env_value is None:
                # Provide more helpful guidance for missing environment variables
                if var_name in ["AZURE_OPENAI_API_KEY", "AZURE_OPENAI_BASE_URL"]:
                    logger.warning(
                        f"Required environment variable {var_name} not found. "
                        f"Using default value '{default_value}'. "
                        f"Please set {var_name} in your .env file for proper operation."
                    )
                elif "placeholder" in default_value.lower():
                    logger.info(
                        f"Optional service variable {var_name} not configured. "
                        f"Using placeholder '{default_value}'. This is normal for minimal setups."
                    )
                return default_value
            return env_value
        else:
            var_name = var_expr
            env_value = os.getenv(var_name)
            if env_value is None:
                logger.error(
                    f"Critical: Environment variable {var_name} not found and no default provided. "
                    f"Please set {var_name} in your .env file or provide a default value in config."
                )
                return f"${{{var_expr}}}"  # Return original if no env var found
            return env_value

    # Keep substituting until no more changes occur (handles nested substitutions)
    max_iterations = 10  # Prevent infinite loops
    for _ in range(max_iterations):
        expressions = find_variable_expressions(yaml_content)
        if not expressions:
            break  # No more expressions to substitute

        # Replace expressions from right to left to avoid index issues
        new_content = yaml_content
        for start, end, var_expr in reversed(expressions):
            replacement = replace_expression(new_content, var_expr)
            new_content = new_content[:start] + replacement + new_content[end:]

        if new_content == yaml_content:
            break  # No more changes
        yaml_content = new_content

    return yaml_content


class Config(config_models.Config):
    """
    Class to handle loading the configuration file
    """

    @staticmethod
    def from_yaml(file_path):
        with open(file_path, "r") as file:
            file_str = file.read()
            # Substitute environment variables before parsing
            file_str = substitute_environment_variables(file_str)
            return Config.from_yaml_str(file_str)

    @staticmethod
    def from_yaml_str(config_yml):
        # Substitute environment variables in the YAML string
        config_yml = substitute_environment_variables(config_yml)
        yaml_data = yaml.safe_load(config_yml)
        json_data = json.dumps(yaml_data)
        config_ns: config_ns_models.Config
        try:
            config_ns = config_ns_models.Config.model_validate_json(json_data)
        except ValidationError as e:
            # Enhanced error messages with helpful suggestions
            error_messages = []
            for error in e.errors():
                field_path = ".".join(str(part) for part in error["loc"])
                error_msg = error["msg"]
                error_type = error["type"]

                # Provide helpful suggestions based on common errors
                suggestion = ""
                if "string_type" in error_type and "endpoint" in field_path:
                    suggestion = "\n💡 Suggestion: Use a placeholder like 'https://placeholder.search.windows.net' if you don't have Azure Search"
                elif "string_type" in error_type and "database" in field_path:
                    suggestion = "\n💡 Suggestion: Use a placeholder like 'placeholder_db' if you don't have a database"
                elif "string_type" in error_type and "csv_path" in field_path:
                    suggestion = "\n💡 Suggestion: Use a placeholder like './sample_data.csv' if you don't have CSV files"
                elif "string_type" in error_type and any(
                    x in field_path for x in ["key", "secret", "password"]
                ):
                    suggestion = "\n💡 Suggestion: Use a placeholder like 'placeholder_key' for unused services"
                elif "string_type" in error_type and "url" in field_path:
                    suggestion = "\n💡 Suggestion: Use a placeholder like 'placeholder_url' for unused services"

                enhanced_msg = (
                    f"❌ Configuration Error in '{field_path}': {error_msg}{suggestion}"
                )
                error_messages.append(enhanced_msg)
                logger.debug(enhanced_msg)

            # Create a comprehensive error message
            full_error_msg = "\n🔧 Configuration Validation Failed:\n" + "\n".join(
                error_messages
            )
            full_error_msg += "\n\n🚀 Quick Fix: Run 'ingen init' to regenerate config files with valid placeholders"
            full_error_msg += (
                "\n📖 Or see: docs/QUICKSTART.md for configuration examples"
            )

            # Create a new exception with enhanced message
            enhanced_error = ValidationError.from_exception_data("Config", e.errors())
            enhanced_error.args = (full_error_msg,)
            raise enhanced_error
        except Exception as e:
            logger.debug(f"Unexpected error during validation: {e}")
            enhanced_msg = f"🔧 Configuration Error: {str(e)}\n💡 Try running 'ingen validate' to diagnose issues"
            e.args = (enhanced_msg,)
            raise e

        profile_data: profile_models.Profiles = Profiles(
            os.getenv("INGENIOUS_PROFILE_PATH", "")
        )
        profile_object: profile_models.Profile = profile_data.get_profile_by_name(
            config_ns.profile
        )
        if profile_object is None:
            raise ValueError(f"Profile {config_ns.profile} not found in profiles.yml")

        config: config_models.Config = config_models.Config(config_ns, profile_object)

        return config


@staticmethod
def get_kv_secret(secretName):
    # check if the key vault name is set in the environment variables
    if "KEY_VAULT_NAME" in os.environ:
        keyVaultName = os.environ["KEY_VAULT_NAME"]
        KVUri = f"https://{keyVaultName}.vault.azure.net"
        credential = DefaultAzureCredential()
        client = SecretClient(vault_url=KVUri, credential=credential)
        secret = client.get_secret(secretName)
        return secret.value
    else:
        raise ValueError("KEY_VAULT_NAME environment variable not set")


def get_config_new() -> IngeniousSettings:
    """
    Get configuration using the new pydantic-settings system.

    This function provides the new configuration system that:
    - Automatically loads environment variables
    - Supports .env files
    - Provides validation with helpful error messages
    - Uses nested configuration models

    Returns:
        IngeniousSettings: The loaded and validated configuration
    """
    try:
        settings = IngeniousSettings()
        settings.validate_configuration()
        return settings
    except Exception as e:
        logger.error(f"Failed to load configuration with new settings system: {e}")
        raise


@staticmethod
def get_config(config_path=None) -> config_models.Config:
    # Check if os.getenv('INGENIOUS_CONFIG') is set
    if os.getenv("APPSETTING_INGENIOUS_CONFIG"):
        config_string = os.getenv("APPSETTING_INGENIOUS_CONFIG", "")
        config_object = json.loads(config_string)
        # Convert the json string to a yaml string
        config_yml = yaml.dump(config_object)
        config = Config.from_yaml_str(config_yml)
        return config

    if config_path is None:
        env_config_path = os.getenv("INGENIOUS_PROJECT_PATH")
        if env_config_path:
            # INGENIOUS_PROJECT_PATH should point directly to the config file
            config_path = Path(env_config_path)
        else:
            # Use the default config file
            current_path = Path.cwd()
            config_path = current_path / "config.yml"

    path = Path(config_path)

    if path.exists():
        if path.is_file():
            logger.debug("Config loaded from file")
            config = Config.from_yaml(config_path)
            return config

        else:
            logger.debug(
                f"Config file at {config_path} is not a file. Falling back to key vault"
            )
            try:
                config_str = get_kv_secret("config")
                config = Config.from_yaml_str(config_str)
                return config
            except Exception:
                raise ValueError(
                    f"Config file at {config_path} is not a file. Tried falling back to key vault but KEY_VAULT_NAME environment variable not set"
                )

    else:
        logger.debug(f"No config file found at {config_path}")
        # Try the new settings system as fallback
        try:
            logger.info(
                "Attempting to load configuration using new pydantic-settings system"
            )
            new_settings = get_config_new()
            logger.info("Successfully loaded configuration using new settings system")
            # Convert new settings to old config format for backward compatibility
            return _convert_new_settings_to_old_config(new_settings)
        except Exception as e:
            logger.error(f"Failed to load configuration with new settings system: {e}")
            exit(1)


def _convert_new_settings_to_old_config(
    settings: IngeniousSettings,
) -> config_models.Config:
    """
    Convert new IngeniousSettings to old Config format for backward compatibility.

    This is a temporary bridge function to maintain compatibility while transitioning
    to the new configuration system.
    """
    # Create a mock profile for the conversion
    profile_data = {
        "name": settings.profile,
        "models": [
            {
                "model": model.model,
                "api_key": model.api_key,
                "base_url": model.base_url,
                "deployment": model.deployment,
                "api_version": model.api_version,
            }
            for model in settings.models
        ],
        "chat_history": {
            "database_connection_string": settings.chat_history.database_connection_string,
        },
        "receiver_configuration": {
            "enable": settings.receiver_configuration.enable,
            "api_url": settings.receiver_configuration.api_url,
            "api_key": settings.receiver_configuration.api_key,
        },
        "chainlit_configuration": {
            "enable": settings.chainlit_configuration.enable,
            "authentication": {
                "enable": settings.chainlit_configuration.authentication.enable,
                "github_secret": settings.chainlit_configuration.authentication.github_secret,
                "github_client_id": settings.chainlit_configuration.authentication.github_client_id,
            },
        },
        "web_configuration": {
            "authentication": {
                "enable": settings.web_configuration.authentication.enable,
                "username": settings.web_configuration.authentication.username,
                "password": settings.web_configuration.authentication.password,
                "type": settings.web_configuration.authentication.type,
            },
        },
        "azure_search_services": [
            {
                "service": service.service,
                "key": service.key,
            }
            for service in (settings.azure_search_services or [])
        ],
        "azure_sql_services": {
            "database_connection_string": settings.azure_sql_services.database_connection_string
            if settings.azure_sql_services
            else "",
        },
        "file_storage": {
            "revisions": {
                "url": settings.file_storage.revisions.url,
                "client_id": settings.file_storage.revisions.client_id,
                "token": settings.file_storage.revisions.token,
                "authentication_method": settings.file_storage.revisions.authentication_method,
            },
            "data": {
                "url": settings.file_storage.data.url,
                "client_id": settings.file_storage.data.client_id,
                "token": settings.file_storage.data.token,
                "authentication_method": settings.file_storage.data.authentication_method,
            },
        },
    }

    # Create config data
    config_data = {
        "profile": settings.profile,
        "models": [
            {
                "model": model.model,
                "api_type": model.api_type,
                "api_version": model.api_version,
                "deployment": model.deployment,
            }
            for model in settings.models
        ],
        "chat_history": {
            "database_type": settings.chat_history.database_type,
            "database_path": settings.chat_history.database_path,
            "database_name": settings.chat_history.database_name,
            "memory_path": settings.chat_history.memory_path,
        },
        "logging": {
            "root_log_level": settings.logging.root_log_level,
            "log_level": settings.logging.log_level,
        },
        "tool_service": {
            "enable": settings.tool_service.enable,
        },
        "chat_service": {
            "type": settings.chat_service.type,
        },
        "chainlit_configuration": {
            "enable": settings.chainlit_configuration.enable,
        },
        "prompt_tuner": {
            "mode": settings.prompt_tuner.mode,
            "enable": settings.prompt_tuner.enable,
        },
        "web_configuration": {
            "ip_address": settings.web_configuration.ip_address,
            "port": settings.web_configuration.port,
            "type": settings.web_configuration.type,
            "asynchronous": settings.web_configuration.asynchronous,
        },
        "local_sql_db": {
            "database_path": settings.local_sql_db.database_path,
            "sample_csv_path": settings.local_sql_db.sample_csv_path,
            "sample_database_name": settings.local_sql_db.sample_database_name,
        },
        "azure_search_services": [
            {
                "service": service.service,
                "endpoint": service.endpoint,
            }
            for service in (settings.azure_search_services or [])
        ],
        "azure_sql_services": {
            "database_name": settings.azure_sql_services.database_name,
            "table_name": settings.azure_sql_services.table_name,
        }
        if settings.azure_sql_services
        else None,
        "file_storage": {
            "revisions": {
                "enable": settings.file_storage.revisions.enable,
                "storage_type": settings.file_storage.revisions.storage_type,
                "container_name": settings.file_storage.revisions.container_name,
                "path": settings.file_storage.revisions.path,
                "add_sub_folders": settings.file_storage.revisions.add_sub_folders,
            },
            "data": {
                "enable": settings.file_storage.data.enable,
                "storage_type": settings.file_storage.data.storage_type,
                "container_name": settings.file_storage.data.container_name,
                "path": settings.file_storage.data.path,
                "add_sub_folders": settings.file_storage.data.add_sub_folders,
            },
        },
    }

    # Convert to JSON and back to create proper config objects
    config_json = json.dumps(config_data)
    profile_json = json.dumps(profile_data)

    # Create the config namespace object
    config_ns = config_ns_models.Config.model_validate_json(config_json)

    # Create a profile object
    profile_obj = profile_models.Profile.model_validate_json(profile_json)

    # Create the final config object
    return config_models.Config(config_ns, profile_obj)
