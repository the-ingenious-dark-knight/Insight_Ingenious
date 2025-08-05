from typing import Any, Dict, Optional

from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from azure.identity import (
    DefaultAzureCredential,
    ManagedIdentityCredential,
    get_bearer_token_provider,
)

from ingenious.common import AuthenticationMethod
from ingenious.config.models import ModelSettings
from ingenious.models.config import ModelConfig


def create_aoai_chat_completion_client_from_config(
    model_config: ModelConfig,
) -> AzureOpenAIChatCompletionClient:
    """
    Factory method to create an AzureOpenAIChatCompletionClient instance.

    Args:
        model_config (ModelConfig): Configuration object containing model settings

    Returns:
        AzureOpenAIChatCompletionClient: Configured client instance

    Raises:
        ValueError: If required configuration is missing
    """
    return create_aoai_chat_completion_client_from_params(
        model=model_config.model,
        base_url=model_config.base_url,
        api_version=model_config.api_version,
        deployment=model_config.deployment,
        api_key=model_config.api_key,
        authentication_method=model_config.authentication_method,
        client_id=model_config.client_id,
    )


def create_aoai_chat_completion_client_from_settings(
    model_settings: ModelSettings,
) -> AzureOpenAIChatCompletionClient:
    """
    Factory method to create an AzureOpenAIChatCompletionClient from ModelSettings.

    Args:
        model_settings (ModelSettings): Model settings object containing configuration

    Returns:
        AzureOpenAIChatCompletionClient: Configured client instance

    Raises:
        ValueError: If required configuration is missing
    """
    return create_aoai_chat_completion_client_from_params(
        model=model_settings.model,
        base_url=model_settings.base_url,
        api_version=model_settings.api_version,
        deployment=model_settings.deployment,
        api_key=model_settings.api_key,
        authentication_method=model_settings.authentication_method,
        client_id=model_settings.client_id,
    )


def create_aoai_chat_completion_client_from_params(
    model: str,
    base_url: str,
    api_version: str,
    deployment: Optional[str] = None,
    api_key: Optional[str] = None,
    authentication_method: AuthenticationMethod = AuthenticationMethod.DEFAULT_CREDENTIAL,
    client_id: Optional[str] = None,
) -> AzureOpenAIChatCompletionClient:
    """
    Factory method to create an AzureOpenAIChatCompletionClient with custom parameters.

    This method is useful when you don't have a ModelConfig object but want to
    create a client with specific parameters.

    Args:
        model (str): Model name (e.g., "gpt-4", "gpt-3.5-turbo")
        base_url (str): Azure OpenAI endpoint URL
        api_version (str): Azure OpenAI API version
        deployment (Optional[str]): Azure deployment name. If None, uses model name
        api_key (Optional[str]): API key for authentication. Required if not using default credential
        authentication_method (str): Authentication mode ("default_credential", "token", or "msi")
        client_id (Optional[str]): Client ID for MSI authentication

    Returns:
        AzureOpenAIChatCompletionClient: Configured client instance

    Raises:
        ValueError: If required parameters are missing
    """
    if not model:
        raise ValueError("Model name is required")
    if not base_url:
        raise ValueError("Base URL is required")
    if not api_version:
        raise ValueError("API version is required")

    # Prepare the configuration dictionary with only the supported parameters
    azure_config: Dict[str, Any] = {
        "model": model,
        "azure_endpoint": base_url,
        "azure_deployment": deployment or model,
        "api_version": api_version,
    }

    # Handle authentication based on authentication method
    if authentication_method == AuthenticationMethod.DEFAULT_CREDENTIAL:
        # Use Azure Default Credential for authentication
        token_provider = get_bearer_token_provider(
            DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
        )
        azure_config["azure_ad_token_provider"] = token_provider
    elif authentication_method == AuthenticationMethod.MSI:
        # Use Managed Service Identity for authentication
        credential = (
            ManagedIdentityCredential(client_id=client_id)
            if client_id
            else ManagedIdentityCredential()
        )
        token_provider = get_bearer_token_provider(
            credential, "https://cognitiveservices.azure.com/.default"
        )
        azure_config["azure_ad_token_provider"] = token_provider
    else:
        # Use API key authentication (TOKEN method)
        if not api_key:
            raise ValueError(
                "API key is required when not using default credential authentication"
            )
        azure_config["api_key"] = api_key

    return AzureOpenAIChatCompletionClient(**azure_config)
