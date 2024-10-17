import json
import yaml
from pathlib import Path
from ingenious.config.profile import Profiles
import os
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential


class ChatHistoryConfig:
    def __init__(self, database_type: str, database_path: str = "", database_connection_string: str = "", database_name: str = "", memory_path: str = ""):
        self.database_type = database_type
        self.database_path = database_path
        self.database_connection_string = database_connection_string
        self.database_name = database_name
        self.memory_path = memory_path


class ModelConfig:
    def __init__(self, model, api_type, api_version):
        self.model = model
        self.api_type = api_type
        self.api_version = api_version
        self.base_url = ""
        #self.api_rate_limit = 60
        self.api_key = ""


class ChatServiceConfig:
    def __init__(self, type):
        self.type = type


class ToolServiceConfig:
    def __init__(self, enable):
        self.enable = enable


class LoggingConfig:
    def __init__(self, root_log_level, log_level):
        
        self.root_log_level = root_log_level
        self.log_level = log_level


class AzureSearchConfig:
    def __init__(self, service, endpoint, key=""):
        self.service = service
        self.endpoint = endpoint
        self.key = key


class WebAuthConfig:
    def __init__(self, type="", enable=True, username="", password=""):
        self.type = type
        self.enable = enable
        self.username = username
        self.password = password


class WebConfig:
    def __init__(self, type="fastapi", ip_address="0.0.0.0", port: int = 80, authentication={}):
        self.type = type
        self.ip_address = ip_address
        self.port = port
        self.authentication = Profiles.WebAuthConfig(**authentication)


class Config:
    def __init__(self, profile, models, chat_history, logging, tool_service, chat_service, azure_search_services=[], web_configuration={}):
        self.chat_history: ChatHistoryConfig = chat_history
        self.profile = profile
        self.models: list[ModelConfig] = models
        self.logging: LoggingConfig = logging
        self.tool_service = tool_service
        self.chat_service = chat_service
        self.azure_search_services: list[AzureSearchConfig] = azure_search_services
        self.web_configuration: WebConfig = web_configuration

    @staticmethod
    def from_yaml(file_path):
        with open(file_path, 'r') as file:
            file_str = file.read()
            return Config.from_yaml_str(file_str)
        
    @staticmethod
    def from_yaml_str(config_yml):
        data = yaml.safe_load(config_yml)            
        models = [ModelConfig(**model) for model in data['models']]
        profile = data['profile']
        chat_service = ChatServiceConfig(**data['chat_service'])
        tool_service = ToolServiceConfig(**data['tool_service'])
        azure_search_services = [AzureSearchConfig(**as_config) for as_config in data['azure_search_services']]
        web_configuration = WebConfig(**data['web_configuration'])
        # Get the sensitive model information from the profile
        profile_data = Profiles()
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
        chat_history = ChatHistoryConfig(**chat_history_data)
        for key, value in profile_object.chat_history.__dict__.items():
            setattr(chat_history, key, value)

        logging_data = data['logging']
        logging_config = LoggingConfig(**logging_data) 
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
def get_config(config_path=None):
    
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




