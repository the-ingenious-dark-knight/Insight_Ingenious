import yaml
import os


class Profiles:
    def __init__(self, profiles_path=None):
        self.profiles = Profiles._get_profiles(profiles_path)
    
    class ModelConfig:
        def __init__(self, model, api_key, base_url):
            self.model = model
            self.api_key = api_key
            self.base_url = base_url

    class ChatHistoryConfig:
        def __init__(self, database_username=None, database_password=None):
            self.database_username = database_username
            self.database_password = database_password

    class Profile:
        def __init__(self, name, models, chat_history):
            self.name = name
            self.models = [Profiles.ModelConfig(**model) for model in models]
            self.chat_history = Profiles.ChatHistoryConfig(**chat_history)

        @staticmethod
        def from_yaml(file_path):
            with open(file_path, 'r') as file:
                data = yaml.safe_load(file)
                profiles = [Profiles.Profile(**profile) for profile in data]
                return profiles
    
    @staticmethod
    def _get_profiles(profiles_path=None):
        # Load the configuration from the YAML file
        if profiles_path is None:
            home_directory = os.path.expanduser('~')
            profiles_path = os.path.join(home_directory, 'profiles.yml')
        
        profiles = Profiles.Profile.from_yaml(profiles_path)
        return profiles
    
    def get_profile_by_name(self, name):
        for profile in self.profiles:
            if profile.name == name:
                return profile
        return None
