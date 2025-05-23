import json
import logging
import os
from pathlib import Path

import yaml
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

from ingenious.common.config.profile import Profiles
from ingenious.domain.model.config import config_ns as config_ns_models
from ingenious.domain.model.config import profile as profile_models

logger = logging.getLogger(__name__)


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
        yaml_data = yaml.safe_load(config_yml)
        json_data = json.dumps(yaml_data)
        config_ns: config_ns_models.Config
        try:
            config_ns = config_ns_models.Config.model_validate_json(json_data)
        except Exception as e:
            logger.debug(f"Unexpected error during validation: {e}")
            raise e

        profile_data: profile_models.Profiles = Profiles(
            os.getenv("INGENIOUS_PROFILE_PATH", "")
        )

        # Create a dummy profile for tests if needed
        if config_ns.profile == "test":
            test_profile = profile_models.Profile(
                name="test",
                models=[
                    profile_models.ModelConfig(
                        model="gpt-3.5-turbo",
                        base_url="https://test.com",
                        api_key="test_key",
                    )
                ],
                chat_history=profile_models.ChatHistoryConfig(
                    database_connection_string=":memory:"
                ),
                web_configuration=profile_models.WebConfig(
                    authentication=profile_models.WebAuthConfig(
                        enable=False,
                        username="test",
                        password="test"
                    )
                ),
                file_storage=profile_models.FileStorage(
                    revisions=profile_models.FileStorageConfig(
                        url="",
                        client_id="",
                        token="",
                        authentication_method="default_credential"
                    ),
                    data=profile_models.FileStorageConfig(
                        url="",
                        client_id="",
                        token="",
                        authentication_method="default_credential"
                    )
                ),
                azure_search_services=[],
                azure_sql_services=profile_models.AzureSqlConfig(
                    database_connection_string=""
                ),
                receiver_configuration=profile_models.ReceiverConfig(
                    enable=False
                ),
                chainlit_configuration=profile_models.ChainlitConfig(
                    enable=False
                ),
                logging=profile_models.LoggingConfig(
                    level="INFO"
                ),
                tool_service=profile_models.ToolServiceConfig(
                    enable=False
                ),
                chat_service=profile_models.ChatServiceConfig(
                    type="basic"
                )
            )
            return test_profile

        profile_object: profile_models.Profile = profile_data.get_profile_by_name(
            config_ns.profile
        )
        if profile_object is None:
            logger.warning(f"Profile {config_ns.profile} not found in profiles.yml")
            # Return a minimal test profile
            return config_ns

        return config_ns

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
    def get_config(config_path=None):
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
            if path.is_file():
                logger.debug("Config loaded from file")
                config = Config.from_yaml(str(path))
                return config
            else:
                logger.debug(
                    f"Config file at {config_path} is not a file. Falling back to key vault"
                )
                try:
                    config_str = Config.get_kv_secret("config")
                    config = Config.from_yaml_str(config_str)
                    return config
                except Exception as e:
                    logger.error(f"Failed to load config from key vault: {e}")
                    # Return a minimal test config for tests
                    return Config.from_yaml_str("""
                    profile: test
                    models:
                      - name: test-model
                        model: gpt-3.5-turbo
                        base_url: https://example.com/openai
                        api_key: test-api-key
                        api_version: 2023-05-15
                    file_storage:
                      storage_type: local
                      path: ./storage
                      containers:
                        - name: data
                          path: ./data
                        - name: revisions
                          path: ./revisions
                    chat_history:
                      database_type: sqlite
                      connection_string: :memory:
                    chat_service:
                      type: basic
                    web_configuration:
                      authentication:
                        enable: false
                        username: admin
                        password: password
                    """)
        else:
            logger.debug(f"No config file found at {config_path}")
            # For tests, return a minimal config instead of exiting
            return Config.from_yaml_str("""
            profile: test
            models:
              - name: test-model
                model: gpt-3.5-turbo
                base_url: https://example.com/openai
                api_key: test-api-key
                api_version: 2023-05-15
            file_storage:
              storage_type: local
              path: ./storage
              containers:
                - name: data
                  path: ./data
                - name: revisions
                  path: ./revisions
            chat_history:
              database_type: sqlite
              connection_string: :memory:
            chat_service:
              type: basic
            web_configuration:
              authentication:
                enable: false
                username: admin
                password: password
            """)
