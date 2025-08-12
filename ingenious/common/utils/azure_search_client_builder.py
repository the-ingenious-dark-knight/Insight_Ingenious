"""
Azure AI Search Client Builder Utilities

This module provides builder functions for creating Azure Search `SearchClient`
instances using different configuration sources and authentication methods,
mirroring the approach used by the Azure OpenAI builder.

Supported authentication methods (see AuthenticationMethod enum):
- DEFAULT_CREDENTIAL: Uses DefaultAzureCredential
- TOKEN: Uses API key via AzureKeyCredential
- MSI: Uses Managed Identity (system or user-assigned)
- CLIENT_ID_AND_SECRET: Uses Entra ID app (client secret)

Notes:
- When using Entra ID (DEFAULT_CREDENTIAL, MSI, CLIENT_ID_AND_SECRET), the
  SDK scopes tokens appropriately (search default scope). No custom token
  provider is required.
"""

from typing import Optional

from azure.core.credentials import AzureKeyCredential
from azure.identity import (
    ClientSecretCredential,
    DefaultAzureCredential,
    ManagedIdentityCredential,
)
from azure.search.documents import SearchClient

from ingenious.common.enums import AuthenticationMethod
from ingenious.config.models import AzureSearchSettings


def create_search_client_from_settings(
    search_settings: AzureSearchSettings, index_name: str
) -> SearchClient:
    """
    Build a SearchClient from AzureSearchSettings.

    If authentication_method is not provided, defaults to TOKEN when a key is present
    in settings; otherwise DEFAULT_CREDENTIAL.
    """
    if not search_settings:
        raise ValueError("Azure Search settings are required")
    if not index_name:
        raise ValueError("Index name is required")

    # Derive endpoint from service if endpoint not provided in settings
    endpoint = getattr(search_settings, "endpoint", None)
    if not endpoint:
        service = getattr(search_settings, "service", None)
        if service:
            endpoint = f"https://{service}.search.windows.net"
        else:
            raise ValueError("Azure Search endpoint or service name is required")

    # Resolve authentication method: explicit arg > settings value > key presence
    method = getattr(
        search_settings,
        "authentication_method",
        AuthenticationMethod.DEFAULT_CREDENTIAL,
    )

    api_key = getattr(search_settings, "key", None)
    client_id = getattr(search_settings, "client_id", None)
    client_secret = getattr(search_settings, "client_secret", None)
    tenant_id = getattr(search_settings, "tenant_id", None)

    return create_search_client_from_params(
        endpoint=endpoint,
        index_name=index_name,
        authentication_method=method,
        api_key=api_key,
        client_id=client_id,
        client_secret=client_secret,
        tenant_id=tenant_id,
    )


def create_search_client_from_params(
    endpoint: str,
    index_name: str,
    authentication_method: AuthenticationMethod = AuthenticationMethod.DEFAULT_CREDENTIAL,
    api_key: Optional[str] = None,
    client_id: Optional[str] = None,
    client_secret: Optional[str] = None,
    tenant_id: Optional[str] = None,
) -> SearchClient:
    """
    Build a SearchClient using explicit parameters.

    Args:
        endpoint: Azure AI Search service endpoint URL
        index_name: Name of the index to target
        authentication_method: One of AuthenticationMethod
        api_key: Required when using TOKEN method
        client_id: Optional client id for MSI or CLIENT_ID_AND_SECRET
        client_secret: Required for CLIENT_ID_AND_SECRET
        tenant_id: Required for CLIENT_ID_AND_SECRET (falls back to AZURE_TENANT_ID)
    """
    if not endpoint:
        raise ValueError("Endpoint is required")
    if not index_name:
        raise ValueError("Index name is required")

    # Determine credential based on auth method
    if authentication_method == AuthenticationMethod.DEFAULT_CREDENTIAL:
        credential = DefaultAzureCredential()
    elif authentication_method == AuthenticationMethod.MSI:
        credential = (
            ManagedIdentityCredential(client_id=client_id)
            if client_id
            else ManagedIdentityCredential()
        )
    elif authentication_method == AuthenticationMethod.CLIENT_ID_AND_SECRET:
        if not client_id:
            raise ValueError(
                "client_id is required when using CLIENT_ID_AND_SECRET authentication"
            )
        if not client_secret:
            raise ValueError(
                "client_secret is required when using CLIENT_ID_AND_SECRET authentication"
            )

        effective_tenant_id = tenant_id
        if not effective_tenant_id:
            import os

            effective_tenant_id = os.getenv("AZURE_TENANT_ID")

        if not effective_tenant_id:
            raise ValueError(
                "tenant_id is required when using CLIENT_ID_AND_SECRET authentication. "
                "Provide tenant_id in configuration or set AZURE_TENANT_ID environment variable"
            )

        credential = ClientSecretCredential(
            tenant_id=effective_tenant_id,
            client_id=client_id,
            client_secret=client_secret,
        )
    else:
        # TOKEN -> API key
        if not api_key:
            raise ValueError(
                "API key is required when using TOKEN authentication for Azure Search"
            )
        credential = AzureKeyCredential(api_key)

    return SearchClient(endpoint=endpoint, index_name=index_name, credential=credential)
