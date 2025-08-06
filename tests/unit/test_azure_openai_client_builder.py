"""
Unit tests for Azure OpenAI Client Builder functions.

This module tests the builder functions that create AzureOpenAIChatCompletionClient
instances with different authentication methods and configuration sources.
"""

import os
from unittest.mock import Mock, patch

import pytest

from ingenious.common.enums import AuthenticationMethod
from ingenious.common.utils import (
    create_aoai_chat_completion_client_from_config,
    create_aoai_chat_completion_client_from_params,
    create_aoai_chat_completion_client_from_settings,
)


class TestAzureOpenAIClientBuilder:
    """Test cases for Azure OpenAI client builder functions."""

    def test_builder_from_params_with_default_credential(self):
        """Test building client from parameters with DEFAULT_CREDENTIAL authentication."""
        with patch(
            "ingenious.common.utils.azure_openai_client_builder.AzureOpenAIChatCompletionClient"
        ) as mock_client:
            with patch(
                "ingenious.common.utils.azure_openai_client_builder.get_bearer_token_provider"
            ) as mock_token_provider:
                with patch(
                    "ingenious.common.utils.azure_openai_client_builder.DefaultAzureCredential"
                ) as mock_credential:
                    mock_token_provider.return_value = "mock_token_provider"
                    mock_client_instance = Mock()
                    mock_client.return_value = mock_client_instance

                    client = create_aoai_chat_completion_client_from_params(
                        model="gpt-4",
                        base_url="https://test.openai.azure.com/",
                        api_version="2024-02-01",
                        authentication_method=AuthenticationMethod.DEFAULT_CREDENTIAL,
                    )

                    assert client == mock_client_instance
                    mock_credential.assert_called_once()
                    mock_token_provider.assert_called_once()
                    mock_client.assert_called_once()

    def test_builder_from_params_with_api_key(self):
        """Test building client from parameters with TOKEN (API key) authentication."""
        with patch(
            "ingenious.common.utils.azure_openai_client_builder.AzureOpenAIChatCompletionClient"
        ) as mock_client:
            mock_client_instance = Mock()
            mock_client.return_value = mock_client_instance

            client = create_aoai_chat_completion_client_from_params(
                model="gpt-4",
                base_url="https://test.openai.azure.com/",
                api_version="2024-02-01",
                api_key="test-api-key",
                authentication_method=AuthenticationMethod.TOKEN,
            )

            assert client == mock_client_instance
            mock_client.assert_called_once()

            # Verify the config passed to the client includes api_key
            call_args = mock_client.call_args[1]
            assert call_args["api_key"] == "test-api-key"

    def test_builder_from_params_with_msi(self):
        """Test building client from parameters with MSI (Managed Identity) authentication."""
        with patch(
            "ingenious.common.utils.azure_openai_client_builder.AzureOpenAIChatCompletionClient"
        ) as mock_client:
            with patch(
                "ingenious.common.utils.azure_openai_client_builder.get_bearer_token_provider"
            ) as mock_token_provider:
                with patch(
                    "ingenious.common.utils.azure_openai_client_builder.ManagedIdentityCredential"
                ) as mock_credential:
                    mock_token_provider.return_value = "mock_token_provider"
                    mock_client_instance = Mock()
                    mock_client.return_value = mock_client_instance

                    client = create_aoai_chat_completion_client_from_params(
                        model="gpt-4",
                        base_url="https://test.openai.azure.com/",
                        api_version="2024-02-01",
                        client_id="test-client-id",
                        authentication_method=AuthenticationMethod.MSI,
                    )

                    assert client == mock_client_instance
                    mock_credential.assert_called_once_with(client_id="test-client-id")
                    mock_token_provider.assert_called_once()

    def test_builder_from_params_with_client_secret(self):
        """Test building client from parameters with CLIENT_ID_AND_SECRET authentication."""
        with patch(
            "ingenious.common.utils.azure_openai_client_builder.AzureOpenAIChatCompletionClient"
        ) as mock_client:
            with patch(
                "ingenious.common.utils.azure_openai_client_builder.get_bearer_token_provider"
            ) as mock_token_provider:
                with patch(
                    "ingenious.common.utils.azure_openai_client_builder.ClientSecretCredential"
                ) as mock_credential:
                    mock_token_provider.return_value = "mock_token_provider"
                    mock_client_instance = Mock()
                    mock_client.return_value = mock_client_instance

                    client = create_aoai_chat_completion_client_from_params(
                        model="gpt-4",
                        base_url="https://test.openai.azure.com/",
                        api_version="2024-02-01",
                        client_id="test-client-id",
                        client_secret="test-client-secret",
                        tenant_id="test-tenant-id",
                        authentication_method=AuthenticationMethod.CLIENT_ID_AND_SECRET,
                    )

                    assert client == mock_client_instance
                    mock_credential.assert_called_once_with(
                        tenant_id="test-tenant-id",
                        client_id="test-client-id",
                        client_secret="test-client-secret",
                    )

    def test_builder_from_params_validation_errors(self):
        """Test that builder functions properly validate required parameters."""

        # Test missing model
        with pytest.raises(ValueError, match="Model name is required"):
            create_aoai_chat_completion_client_from_params(
                model="",
                base_url="https://test.openai.azure.com/",
                api_version="2024-02-01",
            )

        # Test missing base_url
        with pytest.raises(ValueError, match="Base URL is required"):
            create_aoai_chat_completion_client_from_params(
                model="gpt-4", base_url="", api_version="2024-02-01"
            )

        # Test missing api_version
        with pytest.raises(ValueError, match="API version is required"):
            create_aoai_chat_completion_client_from_params(
                model="gpt-4", base_url="https://test.openai.azure.com/", api_version=""
            )

    def test_builder_from_params_auth_validation_errors(self):
        """Test that builder functions validate authentication-specific requirements."""

        # Test TOKEN method without api_key
        with pytest.raises(ValueError, match="API key is required"):
            create_aoai_chat_completion_client_from_params(
                model="gpt-4",
                base_url="https://test.openai.azure.com/",
                api_version="2024-02-01",
                authentication_method=AuthenticationMethod.TOKEN,
            )

        # Test CLIENT_ID_AND_SECRET without client_id
        with pytest.raises(ValueError, match="client_id is required"):
            create_aoai_chat_completion_client_from_params(
                model="gpt-4",
                base_url="https://test.openai.azure.com/",
                api_version="2024-02-01",
                client_secret="test-secret",
                tenant_id="test-tenant",
                authentication_method=AuthenticationMethod.CLIENT_ID_AND_SECRET,
            )

        # Test CLIENT_ID_AND_SECRET without client_secret
        with pytest.raises(ValueError, match="client_secret is required"):
            create_aoai_chat_completion_client_from_params(
                model="gpt-4",
                base_url="https://test.openai.azure.com/",
                api_version="2024-02-01",
                client_id="test-client",
                tenant_id="test-tenant",
                authentication_method=AuthenticationMethod.CLIENT_ID_AND_SECRET,
            )

    def test_builder_from_config(self):
        """Test building client from ModelConfig object."""
        with patch(
            "ingenious.common.utils.azure_openai_client_builder.create_aoai_chat_completion_client_from_params"
        ) as mock_params_builder:
            mock_client = Mock()
            mock_params_builder.return_value = mock_client

            # Mock ModelConfig
            mock_config = Mock()
            mock_config.model = "gpt-4"
            mock_config.base_url = "https://test.openai.azure.com/"
            mock_config.api_version = "2024-02-01"
            mock_config.deployment = "gpt-4-deployment"
            mock_config.api_key = "test-key"
            mock_config.authentication_method = AuthenticationMethod.TOKEN
            mock_config.client_id = None
            mock_config.client_secret = None
            mock_config.tenant_id = None

            client = create_aoai_chat_completion_client_from_config(mock_config)

            assert client == mock_client
            mock_params_builder.assert_called_once_with(
                model="gpt-4",
                base_url="https://test.openai.azure.com/",
                api_version="2024-02-01",
                deployment="gpt-4-deployment",
                api_key="test-key",
                authentication_method=AuthenticationMethod.TOKEN,
                client_id=None,
                client_secret=None,
                tenant_id=None,
            )

    def test_builder_from_settings(self):
        """Test building client from ModelSettings object."""
        with patch(
            "ingenious.common.utils.azure_openai_client_builder.create_aoai_chat_completion_client_from_params"
        ) as mock_params_builder:
            mock_client = Mock()
            mock_params_builder.return_value = mock_client

            # Mock ModelSettings
            mock_settings = Mock()
            mock_settings.model = "gpt-3.5-turbo"
            mock_settings.base_url = "https://test.openai.azure.com/"
            mock_settings.api_version = "2024-02-01"
            mock_settings.deployment = "gpt-35-turbo"
            mock_settings.api_key = None
            mock_settings.authentication_method = (
                AuthenticationMethod.DEFAULT_CREDENTIAL
            )
            mock_settings.client_id = None
            mock_settings.client_secret = None
            mock_settings.tenant_id = None

            client = create_aoai_chat_completion_client_from_settings(mock_settings)

            assert client == mock_client
            mock_params_builder.assert_called_once_with(
                model="gpt-3.5-turbo",
                base_url="https://test.openai.azure.com/",
                api_version="2024-02-01",
                deployment="gpt-35-turbo",
                api_key=None,
                authentication_method=AuthenticationMethod.DEFAULT_CREDENTIAL,
                client_id=None,
                client_secret=None,
                tenant_id=None,
            )

    def test_builder_deployment_defaults_to_model(self):
        """Test that deployment parameter defaults to model name when not provided."""
        with patch(
            "ingenious.common.utils.azure_openai_client_builder.AzureOpenAIChatCompletionClient"
        ) as mock_client:
            mock_client_instance = Mock()
            mock_client.return_value = mock_client_instance

            create_aoai_chat_completion_client_from_params(
                model="gpt-4",
                base_url="https://test.openai.azure.com/",
                api_version="2024-02-01",
                api_key="test-key",
                authentication_method=AuthenticationMethod.TOKEN,
            )

            # Verify deployment defaults to model name
            call_args = mock_client.call_args[1]
            assert call_args["azure_deployment"] == "gpt-4"

    def test_builder_tenant_id_fallback_to_env(self):
        """Test that tenant_id falls back to AZURE_TENANT_ID environment variable."""
        with patch(
            "ingenious.common.utils.azure_openai_client_builder.AzureOpenAIChatCompletionClient"
        ) as mock_client:
            with patch(
                "ingenious.common.utils.azure_openai_client_builder.get_bearer_token_provider"
            ) as mock_token_provider:
                with patch(
                    "ingenious.common.utils.azure_openai_client_builder.ClientSecretCredential"
                ) as mock_credential:
                    with patch.dict(os.environ, {"AZURE_TENANT_ID": "env-tenant-id"}):
                        mock_token_provider.return_value = "mock_token_provider"
                        mock_client_instance = Mock()
                        mock_client.return_value = mock_client_instance

                        create_aoai_chat_completion_client_from_params(
                            model="gpt-4",
                            base_url="https://test.openai.azure.com/",
                            api_version="2024-02-01",
                            client_id="test-client-id",
                            client_secret="test-client-secret",
                            # tenant_id not provided - should use env var
                            authentication_method=AuthenticationMethod.CLIENT_ID_AND_SECRET,
                        )

                        # Verify ClientSecretCredential was called with env tenant_id
                        mock_credential.assert_called_once_with(
                            tenant_id="env-tenant-id",
                            client_id="test-client-id",
                            client_secret="test-client-secret",
                        )


class TestBuilderPatternDocumentation:
    """Test cases that document proper usage of the builder pattern."""

    def test_builder_pattern_usage_examples(self):
        """Document common usage patterns for the Azure OpenAI client builder."""

        # This test serves as living documentation for how to use the builder functions

        print("\n📖 Azure OpenAI Client Builder Usage Examples:")
        print(
            "\n1. Building with Default Credential (recommended for Azure environments):"
        )
        print("   client = create_aoai_chat_completion_client_from_params(")
        print("       model='gpt-4',")
        print("       base_url='https://your-endpoint.openai.azure.com/',")
        print("       api_version='2024-02-01',")
        print("       authentication_method=AuthenticationMethod.DEFAULT_CREDENTIAL")
        print("   )")

        print("\n2. Building with API Key:")
        print("   client = create_aoai_chat_completion_client_from_params(")
        print("       model='gpt-4',")
        print("       base_url='https://your-endpoint.openai.azure.com/',")
        print("       api_version='2024-02-01',")
        print("       api_key='your-api-key',")
        print("       authentication_method=AuthenticationMethod.TOKEN")
        print("   )")

        print("\n3. Building with Managed Identity:")
        print("   client = create_aoai_chat_completion_client_from_params(")
        print("       model='gpt-4',")
        print("       base_url='https://your-endpoint.openai.azure.com/',")
        print("       api_version='2024-02-01',")
        print("       client_id='your-managed-identity-client-id',")
        print("       authentication_method=AuthenticationMethod.MSI")
        print("   )")

        print("\n4. Building from configuration object:")
        print(
            "   client = create_aoai_chat_completion_client_from_config(model_config)"
        )

        print("\n5. Building from settings object:")
        print(
            "   client = create_aoai_chat_completion_client_from_settings(model_settings)"
        )


if __name__ == "__main__":
    # Run documentation examples
    test_docs = TestBuilderPatternDocumentation()
    test_docs.test_builder_pattern_usage_examples()
