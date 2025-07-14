"""
Pydantic Settings-based configuration management for Ingenious.

This module provides a modern configuration system using pydantic-settings that:
- Automatically loads environment variables
- Supports .env files
- Provides validation with helpful error messages
- Uses nested configuration models for different components
- Includes comprehensive documentation via model docstrings
"""

import os
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class ChatHistorySettings(BaseModel):
    """Configuration for chat history storage.

    Supports both SQLite (local) and Azure SQL (cloud) storage options.
    For local development, SQLite is recommended. For production, use Azure SQL.
    """

    database_type: str = Field(
        "sqlite",
        description="Type of database: 'sqlite' for local, 'azuresql' for cloud",
    )
    database_path: str = Field(
        "./tmp/high_level_logs.db",
        description="File path for SQLite database (ignored for Azure SQL)",
    )
    database_connection_string: str = Field(
        "", description="Connection string for Azure SQL (leave empty for SQLite)"
    )
    database_name: str = Field(
        "", description="Database name for Azure SQL (ignored for SQLite)"
    )
    memory_path: str = Field(
        "./tmp", description="Path for memory storage and temporary files"
    )


class ModelSettings(BaseModel):
    """Configuration for AI models.

    Defines which AI models to use and how to connect to them.
    Supports Azure OpenAI, OpenAI, and other compatible endpoints.
    """

    model: str = Field(..., description="Model name (e.g., 'gpt-4', 'gpt-3.5-turbo')")
    api_type: str = Field("rest", description="API type: 'rest' for HTTP APIs")
    api_version: str = Field(
        "2023-03-15-preview", description="API version for Azure OpenAI"
    )
    deployment: str = Field("", description="Azure OpenAI deployment name (optional)")
    api_key: str = Field("", description="API key for the model service")
    base_url: str = Field("", description="Base URL for the API endpoint")

    @field_validator("api_key")
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        """Validate that API key is provided for production use."""
        # Only validate if the key is explicitly a placeholder
        # Allow empty strings for testing and development
        if v and "placeholder" in v.lower():
            raise ValueError(
                "API key is required. Set the appropriate environment variable "
                "(e.g., AZURE_OPENAI_API_KEY) or provide a valid key."
            )
        return v

    @field_validator("base_url")
    @classmethod
    def validate_base_url(cls, v: str) -> str:
        """Validate that base URL is provided and properly formatted."""
        # Only validate if the URL is explicitly a placeholder
        # Allow empty strings for testing and development
        if v and "placeholder" in v.lower():
            raise ValueError(
                "Base URL is required. Set the appropriate environment variable "
                "(e.g., AZURE_OPENAI_BASE_URL) or provide a valid URL."
            )
        if v and not v.startswith(("http://", "https://")):
            raise ValueError("Base URL must start with 'http://' or 'https://'")
        return v


class ChainlitSettings(BaseModel):
    """Configuration for Chainlit chat interface.

    Enables a Python-based chat interface for development and testing.
    Disable in production if using custom web interfaces.
    """

    enable: bool = Field(
        False,
        description="Enable Chainlit chat interface (recommended for development)",
    )

    class AuthenticationSettings(BaseModel):
        """Authentication settings for Chainlit interface."""

        enable: bool = Field(False, description="Enable authentication for Chainlit")
        github_secret: str = Field(
            "", description="GitHub OAuth secret (if using GitHub auth)"
        )
        github_client_id: str = Field(
            "", description="GitHub OAuth client ID (if using GitHub auth)"
        )

    authentication: AuthenticationSettings = Field(
        default_factory=AuthenticationSettings,
        description="Authentication configuration for Chainlit",
    )


class PromptTunerSettings(BaseModel):
    """Configuration for the prompt tuning interface.

    Provides a web interface for editing and testing prompts.
    Useful for development and experimentation with prompt engineering.
    """

    mode: str = Field(
        "fast_api", description="Mode for prompt tuner: 'fast_api' for web interface"
    )
    enable: bool = Field(True, description="Enable prompt tuner interface")


class ChatServiceSettings(BaseModel):
    """Configuration for the chat service backend.

    Defines how the chat service processes conversations.
    Currently supports multi-agent workflows.
    """

    type: str = Field(
        "multi_agent",
        description="Chat service type: 'multi_agent' for agent workflows",
    )


class ToolServiceSettings(BaseModel):
    """Configuration for external tool integrations.

    Enables integration with external tools and services.
    Disable if only using built-in functionality.
    """

    enable: bool = Field(False, description="Enable external tool service integrations")


class LoggingSettings(BaseModel):
    """Configuration for application logging.

    Controls log levels and output formatting.
    Use 'debug' for development, 'info' or 'warning' for production.
    """

    root_log_level: str = Field(
        "info", description="Root logger level: 'debug', 'info', 'warning', 'error'"
    )
    log_level: str = Field(
        "info",
        description="Application logger level: 'debug', 'info', 'warning', 'error'",
    )

    @field_validator("root_log_level", "log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level values."""
        valid_levels = {"debug", "info", "warning", "error", "critical"}
        if v.lower() not in valid_levels:
            raise ValueError(f"Log level must be one of: {', '.join(valid_levels)}")
        return v.lower()


class AzureSearchSettings(BaseModel):
    """Configuration for Azure Cognitive Search integration.

    Enables document search and retrieval capabilities.
    Optional - leave empty if not using Azure Search.
    """

    service: str = Field("", description="Azure Search service name")
    endpoint: str = Field("", description="Azure Search service endpoint URL")
    key: str = Field("", description="Azure Search service API key")


class AzureSqlSettings(BaseModel):
    """Configuration for Azure SQL integration.

    Enables SQL database operations and queries.
    Optional - leave empty if not using Azure SQL.
    """

    database_name: str = Field("", description="Azure SQL database name")
    table_name: str = Field("", description="Default table name for operations")
    database_connection_string: str = Field(
        "", description="Azure SQL connection string"
    )


class WebAuthenticationSettings(BaseModel):
    """Authentication settings for web interfaces."""

    enable: bool = Field(False, description="Enable web authentication")
    username: str = Field("admin", description="Username for basic authentication")
    password: str = Field("", description="Password for basic authentication")
    type: str = Field(
        "basic", description="Authentication type: 'basic' for HTTP basic auth"
    )


class WebSettings(BaseModel):
    """Configuration for web server and API endpoints.

    Controls how the web service is exposed and secured.
    Adjust IP and port based on deployment requirements.
    """

    ip_address: str = Field(
        "0.0.0.0",
        description="IP address to bind the web server (0.0.0.0 for all interfaces)",
    )
    port: int = Field(8000, description="Port number for the web server")
    type: str = Field(
        "fastapi", description="Web framework type: 'fastapi' for FastAPI"
    )
    asynchronous: bool = Field(
        False, description="Enable asynchronous response handling"
    )
    authentication: WebAuthenticationSettings = Field(
        default_factory=WebAuthenticationSettings,
        description="Web authentication configuration",
    )

    @field_validator("port")
    @classmethod
    def validate_port(cls, v: int) -> int:
        """Validate port number range."""
        if not 1 <= v <= 65535:
            raise ValueError("Port must be between 1 and 65535")
        return v


class LocalSqlSettings(BaseModel):
    """Configuration for local SQLite database operations.

    Used for local development and testing with sample data.
    Points to CSV files and local database paths.
    """

    database_path: str = Field(
        "/tmp/sample_sql_db", description="Path to local SQLite database file"
    )
    sample_csv_path: str = Field(
        "", description="Path to sample CSV files for data loading"
    )
    sample_database_name: str = Field(
        "sample_sql_db", description="Name for the sample database"
    )


class FileStorageContainerSettings(BaseModel):
    """Configuration for file storage containers.

    Supports both local file system and Azure Blob Storage.
    """

    enable: bool = Field(True, description="Enable this storage container")
    storage_type: str = Field(
        "local",
        description="Storage type: 'local' for filesystem, 'azure' for blob storage",
    )
    container_name: str = Field(
        "", description="Container name for Azure storage (ignored for local)"
    )
    path: str = Field(
        "./", description="Storage path (local directory or Azure blob prefix)"
    )
    add_sub_folders: bool = Field(
        True, description="Create subdirectories for organization"
    )
    # Azure-specific settings
    url: str = Field(
        "", description="Azure storage account URL (for Azure storage only)"
    )
    client_id: str = Field(
        "", description="Azure client ID for authentication (for Azure storage only)"
    )
    token: str = Field("", description="Azure access token (for Azure storage only)")
    authentication_method: str = Field(
        "default_credential",
        description="Authentication method for Azure: 'default_credential', 'msi', etc.",
    )


class FileStorageSettings(BaseModel):
    """Configuration for file storage system.

    Manages storage for revisions and data files.
    Supports local and cloud storage options.
    """

    revisions: FileStorageContainerSettings = Field(
        default_factory=FileStorageContainerSettings,
        description="Storage configuration for revision files",
    )
    data: FileStorageContainerSettings = Field(
        default_factory=FileStorageContainerSettings,
        description="Storage configuration for data files",
    )


class ReceiverSettings(BaseModel):
    """Configuration for external event receivers.

    Enables integration with external systems that send events.
    Optional - disable if not using external integrations.
    """

    enable: bool = Field(False, description="Enable external event receiver")
    api_url: str = Field("", description="URL for receiving external events")
    api_key: str = Field(
        "DevApiKey", description="API key for authenticating external events"
    )


class IngeniousSettings(BaseSettings):
    """Main settings class for Ingenious application.

    This class automatically loads configuration from:
    1. Environment variables (with INGENIOUS_ prefix)
    2. .env files (.env, .env.local, .env.dev, .env.prod)
    3. Default values defined in the model

    Example usage:
        settings = IngeniousSettings()
        print(f"Web server will run on port {settings.web_configuration.port}")

    Environment variable examples:
        INGENIOUS_WEB_CONFIGURATION__PORT=8080
        INGENIOUS_MODELS__0__API_KEY=your-api-key
        INGENIOUS_LOGGING__ROOT_LOG_LEVEL=debug
    """

    model_config = SettingsConfigDict(
        env_prefix="INGENIOUS_",
        env_nested_delimiter="__",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        validate_assignment=True,
    )

    # Core configuration sections
    profile: str = Field(
        "default", description="Profile name to use for environment-specific settings"
    )

    chat_history: ChatHistorySettings = Field(
        default_factory=ChatHistorySettings,
        description="Chat history storage configuration",
    )

    models: List[ModelSettings] = Field(
        default_factory=list, description="AI model configurations"
    )

    logging: LoggingSettings = Field(
        default_factory=LoggingSettings, description="Application logging configuration"
    )

    tool_service: ToolServiceSettings = Field(
        default_factory=ToolServiceSettings,
        description="External tool service configuration",
    )

    chat_service: ChatServiceSettings = Field(
        default_factory=ChatServiceSettings,
        description="Chat service backend configuration",
    )

    chainlit_configuration: ChainlitSettings = Field(
        default_factory=ChainlitSettings,
        description="Chainlit chat interface configuration",
    )

    prompt_tuner: PromptTunerSettings = Field(
        default_factory=PromptTunerSettings,
        description="Prompt tuning interface configuration",
    )

    web_configuration: WebSettings = Field(
        default_factory=WebSettings, description="Web server and API configuration"
    )

    receiver_configuration: ReceiverSettings = Field(
        default_factory=ReceiverSettings,
        description="External event receiver configuration",
    )

    local_sql_db: LocalSqlSettings = Field(
        default_factory=LocalSqlSettings,
        description="Local SQLite database configuration",
    )

    file_storage: FileStorageSettings = Field(
        default_factory=FileStorageSettings,
        description="File storage system configuration",
    )

    # Optional services
    azure_search_services: Optional[List[AzureSearchSettings]] = Field(
        default=None,
        description="Azure Cognitive Search service configurations (optional)",
    )

    azure_sql_services: Optional[AzureSqlSettings] = Field(
        default=None, description="Azure SQL service configuration (optional)"
    )

    @field_validator("models")
    @classmethod
    def validate_models_not_empty(cls, v: List[ModelSettings]) -> List[ModelSettings]:
        """Ensure at least one model is configured."""
        if not v:
            # Try to create a default model configuration with environment variables
            api_key = os.getenv("AZURE_OPENAI_API_KEY", "")
            base_url = os.getenv("AZURE_OPENAI_BASE_URL", "")

            # If no environment variables are set, just return empty list
            # This allows for testing scenarios where models are configured separately
            if not api_key and not base_url:
                raise ValueError(
                    "At least one model must be configured. "
                    "Set AZURE_OPENAI_API_KEY and AZURE_OPENAI_BASE_URL environment variables "
                    "or provide model configurations."
                )

            return [
                ModelSettings(
                    model=os.getenv("AZURE_OPENAI_MODEL", "gpt-4"),
                    api_key=api_key,
                    base_url=base_url,
                    deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT", ""),
                )
            ]
        return v

    def validate_configuration(self) -> None:
        """Validate the complete configuration and provide helpful feedback."""
        errors = []

        # Check for common configuration issues
        if not self.models:
            errors.append(
                "No models configured. Set AZURE_OPENAI_API_KEY and AZURE_OPENAI_BASE_URL."
            )

        for i, model in enumerate(self.models):
            if model.api_key and "placeholder" in model.api_key.lower():
                errors.append(
                    f"Model {i + 1} has placeholder API key. "
                    "Set a valid API key in environment variables."
                )

            if model.base_url and "placeholder" in model.base_url.lower():
                errors.append(
                    f"Model {i + 1} has placeholder base URL. "
                    "Set a valid base URL in environment variables."
                )

        if (
            self.web_configuration.authentication.enable
            and not self.web_configuration.authentication.password
        ):
            errors.append(
                "Web authentication is enabled but no password is set. "
                "Set WEB_AUTH_PASSWORD environment variable."
            )

        if errors:
            error_msg = "Configuration validation failed:\n" + "\n".join(
                f"- {error}" for error in errors
            )
            error_msg += "\n\nSee documentation for configuration examples."
            raise ValueError(error_msg)

    @classmethod
    def load_from_env_file(cls, env_file: str = ".env") -> "IngeniousSettings":
        """Load settings from a specific .env file."""
        return cls(_env_file=env_file)

    @classmethod
    def create_minimal_config(cls) -> "IngeniousSettings":
        """Create a minimal configuration for development."""
        return cls(
            models=[
                ModelSettings(
                    model="gpt-4",
                    api_key=os.getenv("AZURE_OPENAI_API_KEY", "test-api-key"),
                    base_url=os.getenv(
                        "AZURE_OPENAI_BASE_URL", "https://test.openai.azure.com/"
                    ),
                    deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4"),
                )
            ],
            logging=LoggingSettings(root_log_level="debug", log_level="debug"),
            web_configuration=WebSettings(
                port=8000, authentication=WebAuthenticationSettings(enable=False)
            ),
        )
