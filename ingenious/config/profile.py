import json
import os
import re
from pathlib import Path

import yaml
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from pydantic import ValidationError

from ingenious.models import profile as profile_models


def substitute_environment_variables(yaml_content: str) -> str:
    """
    Substitute environment variables in YAML content.
    Supports patterns like ${VAR_NAME} and ${VAR_NAME:default_value}
    """

    def replacer(match):
        var_expr = match.group(1)
        if ":" in var_expr:
            var_name, default_value = var_expr.split(":", 1)
            return os.getenv(var_name, default_value)
        else:
            var_name = var_expr
            env_value = os.getenv(var_name)
            if env_value is None:
                print(
                    f"Warning: Environment variable {var_name} not found and no default provided"
                )
                return match.group(0)  # Return original if no env var found
            return env_value

    # Pattern matches ${VAR_NAME} or ${VAR_NAME:default}
    pattern = r"\$\{([^}]+)\}"
    return re.sub(pattern, replacer, yaml_content)


class Profiles:
    def __init__(self, profiles_path=None):
        self.profiles: profile_models.Profiles = Profiles._get_profiles(profiles_path)

    @staticmethod
    def from_yaml_str(profile_yml):
        # Substitute environment variables in the profile YAML
        profile_yml = substitute_environment_variables(profile_yml)
        yaml_data = yaml.safe_load(profile_yml)
        json_data = json.dumps(yaml_data)
        try:
            profiles = profile_models.Profiles.model_validate_json(json_data).root
        except ValidationError as e:
            print("❌ Profile validation failed! Common issues and solutions:")
            for error in e.errors():
                field_path = " -> ".join(str(x) for x in error["loc"])
                error_msg = error["msg"]

                print(f"   🔸 Field: {field_path}")
                print(f"      Error: {error_msg}")

                # Provide helpful suggestions based on common errors
                if "string_type" in error_msg and field_path.endswith("api_key"):
                    print(
                        "      💡 Tip: Make sure AZURE_OPENAI_API_KEY is set in your .env file"
                    )
                elif "string_type" in error_msg and field_path.endswith("base_url"):
                    print(
                        "      💡 Tip: Make sure AZURE_OPENAI_BASE_URL is set in your .env file"
                    )
                elif "string_type" in error_msg and "password" in field_path:
                    print(
                        "      💡 Tip: Set WEB_AUTH_PASSWORD='' in .env or disable web auth"
                    )
                elif "string_type" in error_msg and any(
                    x in field_path for x in ["azure_search", "azure_sql", "storage"]
                ):
                    print(
                        "      💡 Tip: For minimal setup, these can be empty strings ('')"
                    )
                else:
                    print(
                        "      💡 Tip: Check your profiles.yml file and .env variables"
                    )
                print()

            print(
                "📖 For help: see PLAN.md or run 'ingen workflows bike_insights' (Hello World)"
            )
            raise e
        except Exception as e:
            print(f"Unexpected error during validation: {e}")
            raise e
        return profiles

    @staticmethod
    def from_yaml(file_path):
        with open(file_path, "r") as file:
            file_str = file.read()
            # Substitute environment variables before parsing
            file_str = substitute_environment_variables(file_str)
            profiles = Profiles.from_yaml_str(file_str)
            return profiles

    @staticmethod
    def _get_profiles(profiles_path=None):
        # Check if os.getenv('INGENIOUS_PROFILE') is set
        if os.getenv("APPSETTING_INGENIOUS_PROFILE", "") != "":
            # print("Profile JSON loaded from environment variable")
            profile_string = os.getenv("APPSETTING_INGENIOUS_PROFILE", "{}")
            profile_object = json.loads(profile_string)
            # Convert the json string to a yaml string
            profile_yml = yaml.dump(profile_object)
            profile = Profiles.from_yaml_str(profile_yml)
            return profile

        # Load the configuration from the YAML file
        if profiles_path is None or profiles_path == "":
            if os.getenv("INGENIOUS_PROFILE_PATH", "") != "":
                print("Profile Path loaded from environment variable")
                profiles_path_object = Path(os.getenv("INGENIOUS_PROFILE_PATH"))
            else:
                print("Profile loaded from default path")
                home_directory = os.path.expanduser("~")
                profiles_path_object = (
                    Path(home_directory) / Path(".ingenious") / Path("profiles.yml")
                )
        else:
            profiles_path_object = Path(profiles_path)

        if profiles_path_object.is_file():
            print("Profile loaded from file")
            profiles = Profiles.from_yaml(file_path=str(profiles_path_object))
        else:
            print(f"Profile not found at {profiles_path}")
            print("Trying to load profile from key vault")
            profiles_yml = get_kv_secret(secretName="profile")
            profiles = Profiles.from_yaml_str(profiles_yml)

        return profiles

    def get_profile_by_name(self, name):
        for profile in self.profiles:
            if profile.name == name:
                return profile
        return None


@staticmethod
def get_kv_secret(secretName):
    try:
        keyVaultName = os.environ["KEY_VAULT_NAME"]
    except KeyError:
        raise ValueError("KEY_VAULT_NAME environment variable not set")

    KVUri = f"https://{keyVaultName}.vault.azure.net"
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=KVUri, credential=credential)
    secret = client.get_secret(secretName)
    return secret.value
