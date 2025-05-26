from typing import List, Optional

from pydantic import BaseModel, Field

# Import directly to avoid circular imports
from ingenious.domain.model.config import config_ns


class ChatHistoryConfig(config_ns.ChatHistoryConfig):
    database_connection_string: str = Field(
        "", description="Connection string for the database. Only used for cosmosdb"
    )

    def __init__(
        self,
        config: config_ns.ChatHistoryConfig,
    ):
        super().__init__(
            database_type=config.database_type,
            database_path=config.database_path,
            database_connection_string=config.database_connection_string,
            database_name=config.database_name,
            memory_path=config.memory_path,
        )


class ModelConfig(config_ns.ModelConfig):
    class Config:
        arbitrary_types_allowed = True

    def __init__(
        self, config: config_ns.ModelConfig,
    ):
        super().__init__(
            model=config.model,
            api_type=config.api_type,
            api_version=config.api_version,
            api_key=config.api_key,
            base_url=config.base_url,
        )


class ChainlitConfig(config_ns.ChainlitConfig):
    def __init__(
        self, config: config_ns.ChainlitConfig,
    ):
        super().__init__(
            enable=config.enable,
            authentication=config.authentication,
        )


class ChatServiceConfig(config_ns.ChatServiceConfig):
    def __init__(
        self, config: config_ns.ChatServiceConfig,
    ):
        super().__init__(type=config.type)


class ToolServiceConfig(config_ns.ToolServiceConfig):
    def __init__(
        self, config: config_ns.ToolServiceConfig,
    ):
        super().__init__(enable=config.enable)


class LoggingConfig(config_ns.LoggingConfig):
    def __init__(
        self, config: config_ns.LoggingConfig,
    ):
        super().__init__(
            root_log_level=config.root_log_level,
            log_level=config.log_level,
        )


class WebConfig(config_ns.WebConfig):
    def __init__(
        self, config: config_ns.WebConfig,
    ):
        super().__init__(
            ip_address=config.ip_address,
            port=config.port,
            authentication=config.authentication,
        )


class FileStorageConfig(config_ns.FileStorageContainer):
    def __init__(
        self, config: config_ns.FileStorageContainer,
    ):
        super().__init__(
            enable=config.enable,
            storage_type=config.storage_type,
            container_name=config.container_name,
            path=config.path,
            add_sub_folders=config.add_sub_folders,
            url=config.url,
            client_id=config.client_id,
            token=config.token,
            authentication_method=config.authentication_method,
        )


class FileStorage(config_ns.FileStorage):
    def __init__(
        self, config: config_ns.FileStorage,
    ):
        super().__init__(
            revisions=config.revisions,
            data=config.data,
            storage_type=config.storage_type,
            path=config.path,
            containers=config.containers,
        )


class AzureSearchConfig(config_ns.AzureSearchConfig):
    def __init__(
        self, config: config_ns.AzureSearchConfig,
    ):
        super().__init__(
            service=config.service,
            key=config.key,
        )


class AzureSqlConfig(config_ns.AzureSqlConfig):
    def __init__(
        self, config: config_ns.AzureSqlConfig,
    ):
        super().__init__(
            database_connection_string=config.database_connection_string,
        )


class ReceiverConfig(config_ns.ReceiverConfig):
    def __init__(
        self, config: config_ns.ReceiverConfig,
    ):
        super().__init__(
            enable=config.enable,
            api_url=config.api_url,
            api_key=config.api_key,
        )


class Config(config_ns.Config):
    """Combined configuration object with config and profile data."""

    def __init__(self, config: config_ns.Config):
        """
        Initialize the Config object with config and profile data.

        Args:
            config: Config model from config.yml
        """
        # Take values from config or profile
        self.web_configuration = WebConfig(config.web_configuration)
        self.models = [ModelConfig(model) for model in config.models]
        self.chat_history = ChatHistoryConfig(config.chat_history)
        self.chat_service = ChatServiceConfig(config.chat_service)
        self.tool_service = ToolServiceConfig(config.tool_service)
        self.logging = LoggingConfig(config.logging)
        self.file_storage = FileStorage(config.file_storage)
        self.azure_search_services = [
            AzureSearchConfig(service) for service in config.azure_search_services
        ]
        self.azure_sql_services = AzureSqlConfig(config.azure_sql_services)
        self.receiver_configuration = ReceiverConfig(config.receiver_configuration)
        self.chainlit_configuration = ChainlitConfig(config.chainlit_configuration)
