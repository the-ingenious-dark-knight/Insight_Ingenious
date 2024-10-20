import dataclasses as dataclass
from typing import List
import json
import yaml
from pathlib import Path
from ingenious.config.profile import Profiles
from ingenious.models import config as config_models
from ingenious.models import profile as profile_models
import os
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential


class Config(config_models.Config):
    def __init__(self, profile, models, chat_history, logging, tool_service, chat_service, azure_search_services=[], web_configuration={}):
        self.chat_history: config_models.ChatHistoryConfig = chat_history
        self.profile = profile
        self.models: list[config_models.ModelConfig] = models
        self.logging: config_models.LoggingConfig = logging
        self.tool_service = tool_service
        self.chat_service = chat_service
        self.azure_search_services: list[config_models.AzureSearchConfig] = azure_search_services
        self.web_configuration: config_models.WebConfig = web_configuration

    @staticmethod
    def from_yaml(file_path):
        with open(file_path, 'r') as file:
            file_str = file.read()
            return Config.from_yaml_str(file_str)
        
    @staticmethod
    def from_yaml_str(config_yml):
        data = yaml.safe_load(config_yml)            
        models = [config_models.ModelConfig(**model) for model in data['models']]
        profile = data['profile']
        chat_service = config_models.ChatServiceConfig(**data['chat_service'])
        tool_service = config_models.ToolServiceConfig(**data['tool_service'])
        azure_search_services = [config_models.AzureSearchConfig(**as_config) for as_config in data['azure_search_services']]
        web_configuration = config_models.WebConfig(**data['web_configuration'])
        # Get the sensitive model information from the profile
        profile_data: profile_models.Profiles = Profiles()
        profile_object = profile_data.get_profile_by_name(profile)
        if profile_object is None:
            raise ValueError(f"Profile {profile} not found in profiles.yml")
        
        for config_model in models:
            for profile_model in profile_object.models:
                if config_model.model == profile_model.model:
                    # add all attribites from the profile model to the config model
                    for key, value in profile_model.__dict__.items():
                        setattr(config_model, key, value)
                    break
        
        for as_config in azure_search_services:
            for profile_as_config in profile_object.azure_search_services:
                if as_config.service == profile_as_config.service:
                    # add all attribites from the profile model to the config model
                    for key, value in profile_as_config.__dict__.items():
                        setattr(as_config, key, value)
                    break
        
        for key, value in profile_object.web_configuration.__dict__.items():
            setattr(web_configuration, key, value)

        chat_history_data = data['chat_history']            
        chat_history = config_models.ChatHistoryConfig(**chat_history_data)
        for key, value in profile_object.chat_history.__dict__.items():
            setattr(chat_history, key, value)

        logging_data = data['logging']
        logging_config = config_models.LoggingConfig(**logging_data) 
        return Config(
            profile=profile,
            models=models,
            chat_history=chat_history,
            logging=logging_config,
            tool_service=tool_service,
            chat_service=chat_service,
            azure_search_services=azure_search_services,
            web_configuration=web_configuration
        )


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
def get_config(config_path=None) -> Config:
    
    # Check if os.getenv('INGENIOUS_CONFIG') is set
    if os.getenv('APPSETTING_INGENIOUS_CONFIG'):
        config_string = os.getenv('APPSETTING_INGENIOUS_CONFIG', "")
        config_object = json.loads(config_string)
        # Convert the json string to a yaml string
        config_yml = yaml.dump(config_object)
        config = Config.from_yaml_str(config_yml)
        return config
    
    if config_path is None: 
        env_config_path = os.getenv('INGENIOUS_PROJECT_PATH')
        if env_config_path:
            config_path = env_config_path
        else:
            # Use the default config file
            current_path = Path.cwd()
            config_path = current_path / 'config.yml'
    path = Path(config_path)
    if path.exists:
        if Path(config_path).is_file():
            print("Config loaded from file")
            config = Config.from_yaml(config_path)
            return config

        else:            
            print("Config loaded from key vault")
            config_str = get_kv_secret("profileymlconfig")
            config = Config.from_yaml_str(config_str)
            return config
        
    else:
        print("No config file found at {config_path}")
        exit(1)




