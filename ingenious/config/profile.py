import yaml
import os
from pathlib import Path
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential


class Profiles:
    def __init__(self, profiles_path=None):
        self.profiles = Profiles._get_profiles(profiles_path)
    
    class ModelConfig:
        def __init__(self, model, api_key, base_url):
            self.model = model
            self.api_key = api_key
            self.base_url = base_url

    class ChatHistoryConfig:
        def __init__(self, database_connection_string=""):
            self.database_connection_string = database_connection_string            
    
    class AzureSearchConfig:
        def __init__(self, service, key):
            self.service = service
            self.key = key
    
    class ChainlitAuthConfig:
        def __init__(self, enable=False, github_secret="", github_client_id=""):
            self.enable = enable
            github_secret = github_secret
            github_client_id = github_client_id
    
    class ChainlitConfig:
        def __init__(self, enable=False, authentication={}):            
            authentication = Profiles.ChainlitAuthConfig(**authentication)

    class WebAuthConfig:
        def __init__(self, type="", enable=True, username="", password=""):
            self.username = username
            self.password = password

    class WebConfig:
        def __init__(self, type="fastapi", ip_address="0.0.0.0", port: int = 80, authentication={}):
            self.authentication = Profiles.WebAuthConfig(**authentication)

    class Profile:
        def __init__(self, name, models, chat_history, azure_search_services, web_configuration, chainlit_configuration):
            self.name = name
            self.models = [Profiles.ModelConfig(**model) for model in models]
            self.chat_history = Profiles.ChatHistoryConfig(**chat_history)
            self.azure_search_services: list[Profiles.AzureSearchConfig] = [Profiles.AzureSearchConfig(**as_config) for as_config in azure_search_services]
            self.web_configuration = Profiles.WebConfig(**web_configuration)
            self.chainlit_configuration = Profiles.ChainlitConfig(**chainlit_configuration)
        
        @staticmethod
        def from_yaml(file_path):
            with open(file_path, 'r') as file:
                data = yaml.safe_load(file)
                profiles = [Profiles.Profile(**profile) for profile in data]
                return profiles
            
        @staticmethod 
        def from_yaml_str(profile_yml):
            data = yaml.safe_load(profile_yml)
            profiles = [Profiles.Profile(**profile) for profile in data]
            return profiles




    @staticmethod
    def _get_profiles(profiles_path=None):
        # Load the configuration from the YAML file
        if profiles_path is None:
            if os.getenv('INGENIOUS_PROFILE_PATH') is not None:
                profiles_path = Path(os.getenv('INGENIOUS_PROFILE_PATH'))
            else:
                home_directory = os.path.expanduser('~')
                profiles_path = Path(home_directory) / Path('.ingenious') / Path('profiles.yml')
        
        if Path(profiles_path).is_file():
            print("Profile loaded from file")
            profiles = Profiles.Profile.from_yaml(profiles_path)
        else:
            print("Profile loaded from key vault")
            profiles_yml = get_kv_secret(secretName="profileymlconfig")
            profiles = Profiles.Profile.from_yaml_str(profiles_yml)

        return profiles
    
    def get_profile_by_name(self, name):
        for profile in self.profiles:
            if profile.name == name:
                return profile
        return None
    
@staticmethod
def get_kv_secret(secretName):
    keyVaultName = os.environ["KEY_VAULT_NAME"]
    KVUri = f"https://{keyVaultName}.vault.azure.net"
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=KVUri, credential=credential)
    secret = client.get_secret(secretName)
    return secret.value
