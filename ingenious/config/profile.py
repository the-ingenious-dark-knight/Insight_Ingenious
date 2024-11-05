from pydantic_core import from_json
from pydantic import ValidationError
import json
import yaml
import os
from pathlib import Path
from ingenious.models import profile as profile_models
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential


class Profiles():
    def __init__(self, profiles_path=None):
        self.profiles: profile_models.Profiles = Profiles._get_profiles(profiles_path)

    @staticmethod
    def from_yaml_str(profile_yml):
        yaml_data = yaml.safe_load(profile_yml)
        json_data = json.dumps(yaml_data)
        try:
            profiles = profile_models.Profiles.model_validate_json(json_data).root
        except ValidationError as e:
            print(f"Validation error: {e}")
            raise e
        except Exception as e:
            print(f"Error: {e}")
            raise e
        return profiles

    @staticmethod
    def from_yaml(file_path):
        with open(file_path, 'r') as file:
            file_str = file.read()
            profiles = Profiles.from_yaml_str(file_str)
            return profiles

    @staticmethod
    def _get_profiles(profiles_path=None):
        # Check if os.getenv('INGENIOUS_PROFILE') is set
        if os.getenv('APPSETTING_INGENIOUS_PROFILE', '') != '':
            print("Profile JSON loaded from environment variable")
            profile_string = os.getenv('APPSETTING_INGENIOUS_PROFILE', "{}")
            profile_object = json.loads(profile_string)
            # Convert the json string to a yaml string
            profile_yml = yaml.dump(profile_object)
            profile = Profiles.from_yaml_str(profile_yml)
            return profile

        # Load the configuration from the YAML file
        if profiles_path is None or profiles_path == '':
            if os.getenv('INGENIOUS_PROFILE_PATH', '') != '':
                print("Profile Path loaded from environment variable")
                profiles_path = Path(os.getenv('INGENIOUS_PROFILE_PATH'))
            else:
                print("Profile loaded from default path")
                home_directory = os.path.expanduser('~')
                profiles_path = Path(home_directory) / Path('.ingenious') / Path('profiles.yml')

        if Path(profiles_path).is_file(): #this might need to change to
            print("Profile loaded from file")
            profiles = Profiles.from_yaml(file_path=profiles_path)
        else:
            print("Profile loaded from key vault")
            profiles_yml = get_kv_secret(secretName="profileymlconfig")
            profiles = Profiles.from_yaml_str(profiles_yml)

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
