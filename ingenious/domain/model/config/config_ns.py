from enum import Enum
from typing import List

from pydantic import BaseModel, Field


class AuthenticationMethod(str, Enum):
    DEFAULT_CREDENTIAL = "default_credential"
    CLIENT_SECRET = "client_secret"
    MANAGED_IDENTITY = "managed_identity"


class WebAuthConfig(BaseModel):
    type: str = Field("", description="Authentication type")
    enable: bool = Field(True, description="Enable authentication")
    username: str = Field("", description="Username for authentication")
    password: str = Field("", description="Password for authentication")


class ChatHistoryConfig(BaseModel):
    database_type: str = Field(
        "sqlite",
        description="Type of the database (e.g., sqlite, cosmosdb). Default is sqlite",
    )
    database_path: str = Field(
        "./tmp/high_level_logs.db",
        description="File path to the database, if applicable. Only used for sqlite",
    )
    database_connection_string: str = Field(
        "", description="Connection string for the database. Only used for cosmosdb"
    )
    database_name: str = Field(
        "", description="Name of the database. Only used for cosmosdb"
    )
    memory_path: str = Field("./tmp", description="Path to the memory storage.")


class ModelConfig(BaseModel):
    model: str = Field(..., description="Name of the model")
    api_type: str = Field(..., description="Type of the API (e.g., rest, grpc)")
    api_version: str = Field(..., description="Version of the API")
    api_key: str = Field("", description="API key for the model")
    base_url: str = Field("", description="Base URL for the model API")


class ChainlitAuthConfig(BaseModel):
    enable: bool = Field(False, description="Enable Chainlit authentication")
    github_secret: str = Field("", description="GitHub secret for Chainlit authentication")
    github_client_id: str = Field("", description="GitHub client ID for Chainlit authentication")


class ChainlitConfig(BaseModel):
    enable: bool = Field(
        False,
        description="Enables or Disables the Python based Chainlit chat interface",
    )
    authentication: ChainlitAuthConfig = Field(default_factory=lambda: ChainlitAuthConfig())


class ChatServiceConfig(BaseModel):
    type: str = Field(
        "multi_agent", description="Right now only valid value is 'multi_agent'"
    )


class ToolServiceConfig(BaseModel):
    enable: bool = Field(False, description="Enables or Disables the Tool Service")


class LoggingConfig(BaseModel):
    root_log_level: str = Field("debug", description="Root log level")
    log_level: str = Field("debug", description="Log level")


class AzureSearchConfig(BaseModel):
    service: str = Field(..., description="Name of the service")
    endpoint: str = Field(..., description="Endpoint of the service")
    key: str = Field("", description="API key for Azure Search")


class AzureSqlConfig(BaseModel):
    database_name: str = Field("", description="Name of the database.")
    table_name: str = Field("", description="Name of the table.")
    database_connection_string: str = Field(
        "", description="azure SQL Connection string"
    )


class WebConfig(BaseModel):
    ip_address: str = Field("0.0.0.0", description="IP address of the web server")
    port: int = Field(80, description="Port of the web server")
    type: str = Field("fastapi", description="Type of the web server (e.g. fastapi)")
    asynchronous: bool = Field(
        False, description="Enables or Disables the Asynchronous Response"
    )
    authentication: WebAuthConfig = Field(
        default_factory=WebAuthConfig,
        description="Authentication config for the web server",
    )


class ReceiverConfig(BaseModel):
    enable: bool = Field(True, description="Enables or Disables the Receiver")
    api_url: str = Field("", description="API URL for the Receiver")
    api_key: str = Field("", description="API key for the Receiver")


class FileStorageContainer(BaseModel):
    enable: bool = Field(True, description="Enables or Disables File Storage")
    storage_type: str = Field("local", description="Type of the File Storage")
    container_name: str = Field(
        default="",
        description="Name of the container. Used for Azure storage. Not used for local storage.",
    )
    path: str = Field(
        "./",
        description="Path to the file storage. Used for local storage and Azure storage.",
    )
    add_sub_folders: bool = Field(
        default=True,
        description="Add sub_folders to the path. Used for local storage and Azure storage.",
    )
    url: str = Field("", description="File Storage SAS URL")
    client_id: str = Field("", description="File Storage SAS Client ID")
    token: str = Field("", description="File Storage SAS Token")
    authentication_method: AuthenticationMethod = Field(
        AuthenticationMethod.DEFAULT_CREDENTIAL,
        description="File Storage SAS Authentication Method",
    )


class FileStorage(BaseModel):
    revisions: FileStorageContainer = Field(
        default_factory=lambda: FileStorageContainer(
            enable=True,
            storage_type="local",
            container_name="",
            path="./",
            add_sub_folders=True,
        ),
        description="File Storage configuration for revisions",
    )
    data: FileStorageContainer = Field(
        default_factory=lambda: FileStorageContainer(
            enable=True,
            storage_type="local",
            container_name="",
            path="./",
            add_sub_folders=True,
        ),
        description="File Storage configuration for data",
    )


class LocaldbConfig(BaseModel):
    database_path: str = Field("/tmp/sample_sql_db", description="Database path")
    sample_csv_path: str = Field("", description="Sample csv path")
    sample_database_name: str = Field(
        "sample_sql_db", description="Sample database name"
    )


class AuthenticationMethod(str, Enum):
    MSI = "msi"
    CLIENT_ID_AND_SECRET = "client_id_and_secret"
    DEFAULT_CREDENTIAL = "default_credential"
    TOKEN = "token"


class Config(BaseModel):
    """
    This is the configuration class for the config.yml file.
    """

    profile: str = Field("default", description="Profile name for configuration")
    models: List[ModelConfig]
    logging: LoggingConfig
    tool_service: ToolServiceConfig
    chat_service: ChatServiceConfig
    chat_history: ChatHistoryConfig
    chainlit_configuration: ChainlitConfig
    azure_search_services: List[AzureSearchConfig]
    azure_sql_services: AzureSqlConfig
    web_configuration: WebConfig
    local_sql_db: LocaldbConfig = Field(
        default_factory=lambda: LocaldbConfig(),
        description="Local SQL database configuration",
    )
    file_storage: FileStorage = Field(
        default_factory=lambda: FileStorage(
            revisions=FileStorageContainer(
                enable=True,
                storage_type="local",
                container_name="",
                path="./",
                add_sub_folders=True,
            ),
            data=FileStorageContainer(
                enable=True,
                storage_type="local",
                container_name="",
                path="./",
                add_sub_folders=True,
            ),
        ),
        description="File Storage configuration",
    )
    receiver_configuration: ReceiverConfig = Field(
        default_factory=lambda: ReceiverConfig(),
        description="Receiver configuration",
    )
