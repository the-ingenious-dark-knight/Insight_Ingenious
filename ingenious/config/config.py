import json
import logging
import os
from pathlib import Path

import yaml
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

from ingenious.config.profile import Profiles
from ingenious.models import config as config_models
from ingenious.models import config_ns as config_ns_models
from ingenious.models import profile as profile_models

logger = logging.getLogger(__name__)


class Config(config_models.Config):
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
        yaml_data = yaml.safe_load(config_yml)
        json_data = json.dumps(yaml_data)
        config_ns: config_ns_models.Config
        try:
            config_ns = config_ns_models.Config.model_validate_json(json_data)
        except config_models.ValidationError as e:
            for error in e.errors():
                logger.debug(
                    f"Validation error in \
                    field '{error['loc']}': {error['msg']}"
                )
            raise e
        except Exception as e:
            logger.debug(f"Unexpected error during validation: {e}")
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
            config_path = env_config_path
        else:
            # Use the default config file
            current_path = Path.cwd()
            config_path = current_path / "config.yml"

    path = Path(config_path)

    if path.exists():
        if Path(config_path).is_file():
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
        exit(1)
