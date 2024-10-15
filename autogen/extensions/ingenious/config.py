import yaml
from pathlib import Path
from pyautogen.extensions.ingenious.profile import Profiles


class ChatHistoryConfig:
    def __init__(self, database_type, database_path):
        self.database_type = database_type
        self.database_path = database_path


class ModelConfig:
    def __init__(self, model, api_type):
        self.model = model
        self.api_type = api_type


class LoggingConfig:
    def __init__(self, log_level, root_log_level):
        self.root_log_level = root_log_level
        self.log_Level = log_level


class Config:
    def __init__(self, name, models, chat_history, logging):
        self.chat_history = chat_history
        self.name = name
        self.models = [ModelConfig(**model) for model in models]
        self.logging = logging

    @staticmethod
    def from_yaml(file_path):
        with open(file_path, 'r') as file:
            data = yaml.safe_load(file)
            name = data['name']
            models = data['models']
            profile = data['profile']
            # Get the sensitive model information from the profile
            profile_data = Profiles()
            profile_object = profile_data.get_profile_by_name(profile)
            if profile_object is None:
                raise ValueError(f"Profile {profile} not found in profiles.yml")
            models.extend(profile_object.models)

            chat_history_data = data['chat_history']
            chat_history = ChatHistoryConfig(**chat_history_data)
            logging_data = data['logging']
            logging_config = LoggingConfig(**logging_data) 
            return Config(name, models, chat_history, logging_config)


def get_config(config_path=None):
    if config_path is None:        
        current_path = Path.cwd()
        config_path = current_path / 'config.yml'
    path = Path(config_path)
    if path.exists:
        config = Config.from_yaml(config_path)
        return config
    else:
        print("No config file found at {config_path}")
        exit(1)


