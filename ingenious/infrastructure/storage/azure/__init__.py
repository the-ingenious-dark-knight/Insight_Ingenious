import logging

from azure.identity import (
    ClientSecretCredential,
    DefaultAzureCredential,
    ManagedIdentityCredential,
)
from azure.storage.blob import BlobServiceClient

from ingenious.domain.model.config import (
    AuthenticationMethod as file_storage_AuthenticationMethod,
)
from ingenious.domain.model.config import Config, FileStorageContainer
from ingenious.infrastructure.storage.azure.blob_operations import AzureBlobOperations
from ingenious.infrastructure.storage.azure.path_helper import AzurePathHelper
from ingenious.infrastructure.storage.files_repository import IFileStorage

logger = logging.getLogger(__name__)


class azure_FileStorageRepository(IFileStorage):
    """Implementation of IFileStorage for Azure Blob Storage."""

    def __init__(self, config: Config, fs_config: FileStorageContainer):
        """
        Initialize the Azure File Storage Repository.

        Args:
            config: The application configuration
            fs_config: The file storage container configuration
        """
        self.config = config
        self.fs_config = fs_config
        self.blob_service_client = self._create_blob_service_client()
        self.path_helper = AzurePathHelper(fs_config)
        self.blob_operations = AzureBlobOperations(self.blob_service_client, fs_config)

    def _create_blob_service_client(self) -> BlobServiceClient:
        """
        Create a BlobServiceClient based on the authentication method.

        Returns:
            A configured BlobServiceClient
        """
        url = self.fs_config.url
        token = self.fs_config.token
        client_id = self.fs_config.client_id
        auth_method = self.fs_config.authentication_method

        if auth_method == file_storage_AuthenticationMethod.TOKEN:
            return BlobServiceClient(account_url=url, credential=token)

        if auth_method == file_storage_AuthenticationMethod.CLIENT_ID_AND_SECRET:
            cred = ClientSecretCredential(client_id, token)
            return BlobServiceClient(account_url=url, credential=cred)

        if auth_method == file_storage_AuthenticationMethod.MSI:
            cred = ManagedIdentityCredential(client_id=client_id)
            return BlobServiceClient(account_url=url, credential=cred)

        # Default to DefaultAzureCredential
        return BlobServiceClient(account_url=url, credential=DefaultAzureCredential())

    async def write_file(self, contents: str, file_name: str, file_path: str):
        """
        Write content to a file in Azure Blob Storage.

        Args:
            contents: The content to write
            file_name: The name of the file
            file_path: The path to the file
        """
        blob_path = self.path_helper.construct_blob_path(file_path, file_name)
        await self.blob_operations.upload_blob(contents, blob_path)

    async def read_file(self, file_name: str, file_path: str) -> str:
        """
        Read content from a file in Azure Blob Storage.

        Args:
            file_name: The name of the file
            file_path: The path to the file

        Returns:
            The file content as a string
        """
        blob_path = self.path_helper.construct_blob_path(file_path, file_name)
        content = await self.blob_operations.download_blob(blob_path)
        return content or ""

    async def delete_file(self, file_name: str, file_path: str):
        """
        Delete a file from Azure Blob Storage.

        Args:
            file_name: The name of the file
            file_path: The path to the file
        """
        blob_path = self.path_helper.construct_blob_path(file_path, file_name)
        await self.blob_operations.delete_blob(blob_path)

    async def list_files(self, file_path: str):
        """
        List files in a directory in Azure Blob Storage.

        Args:
            file_path: The path to list files from

        Returns:
            A list of file names
        """
        prefix = self.path_helper.construct_blob_path(file_path)

        # Ensure the prefix ends with a forward slash if it's a directory
        if self.path_helper.is_directory(prefix) and not prefix.endswith("/"):
            prefix += "/"

        return await self.blob_operations.list_blobs(prefix)

    async def check_if_file_exists(self, file_path: str, file_name: str) -> bool:
        """
        Check if a file exists in Azure Blob Storage.

        Args:
            file_path: The path to the file
            file_name: The name of the file

        Returns:
            True if the file exists, False otherwise
        """
        blob_path = self.path_helper.construct_blob_path(file_path, file_name)
        return await self.blob_operations.blob_exists(blob_path)

    async def get_base_path(self) -> str:
        """
        Get the base path of the Azure Blob Storage container.

        Returns:
            The base path as a string
        """
        return self.fs_config.url + "/" + self.fs_config.path
