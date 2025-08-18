from azure.cosmos import CosmosClient

from ingenious.client.azure.builder.base import AzureClientBuilder
from ingenious.common.enums import AuthenticationMethod
from ingenious.config.auth_config import AzureAuthConfig


class CosmosClientBuilder(AzureClientBuilder):
    """Builder for Azure Cosmos DB clients with multiple authentication methods."""

    def __init__(self, endpoint: str, auth_config: AzureAuthConfig):
        super().__init__(auth_config=auth_config)
        self.endpoint = endpoint

    def build(self) -> CosmosClient:
        """
        Build Azure Cosmos DB client based on configuration.

        Returns:
            CosmosClient: Configured Azure Cosmos DB client
        """
        # Get the unified credential from base class
        cred = self.credential

        # Configure client based on credential type
        if self.auth_config.authentication_method == AuthenticationMethod.TOKEN:
            # Cosmos DB expects raw string for API key, not AzureKeyCredential
            return CosmosClient(
                url=self.endpoint,
                credential=self.api_key,  # Use raw string property
            )
        else:
            # Use Azure AD authentication - credential will be TokenCredential
            from azure.core.credentials import TokenCredential

            if not isinstance(cred, TokenCredential):
                raise ValueError(
                    f"Expected TokenCredential for Azure AD auth, got {type(cred)}"
                )

            return CosmosClient(url=self.endpoint, credential=cred)
