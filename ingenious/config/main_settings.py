"""
Main settings class for Ingenious application.

This module contains the primary IngeniousSettings class that combines
all configuration models and provides the main configuration interface.
"""

from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings

from .environment import get_settings_config
from .models import (
    AzureSearchSettings,
    AzureSqlSettings,
    ChainlitSettings,
    ChatHistorySettings,
    ChatServiceSettings,
    FileStorageSettings,
    LocalSqlSettings,
    LoggingSettings,
    ModelSettings,
    PromptTunerSettings,
    ReceiverSettings,
    ToolServiceSettings,
    WebSettings,
)
from .validators import validate_configuration, validate_models_not_empty


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

    model_config = get_settings_config()

    profile: str = Field(
        "default", description="Profile name to use for environment-specific settings"
    )

    chat_history: ChatHistorySettings = Field(
        default_factory=lambda: ChatHistorySettings(),
        description="Chat history storage configuration",
    )

    models: List[ModelSettings] = Field(
        default_factory=list, description="AI model configurations"
    )

    logging: LoggingSettings = Field(
        default_factory=lambda: LoggingSettings(),
        description="Application logging configuration",
    )

    tool_service: ToolServiceSettings = Field(
        default_factory=lambda: ToolServiceSettings(),
        description="External tool service configuration",
    )

    chat_service: ChatServiceSettings = Field(
        default_factory=lambda: ChatServiceSettings(),
        description="Chat service backend configuration",
    )

    chainlit_configuration: ChainlitSettings = Field(
        default_factory=lambda: ChainlitSettings(),
        description="Chainlit chat interface configuration",
    )

    prompt_tuner: PromptTunerSettings = Field(
        default_factory=lambda: PromptTunerSettings(),
        description="Prompt tuning interface configuration",
    )

    web_configuration: WebSettings = Field(
        default_factory=lambda: WebSettings(),
        description="Web server and API configuration",
    )

    receiver_configuration: ReceiverSettings = Field(
        default_factory=lambda: ReceiverSettings(),
        description="External event receiver configuration",
    )

    local_sql_db: LocalSqlSettings = Field(
        default_factory=lambda: LocalSqlSettings(),
        description="Local SQLite database configuration",
    )

    file_storage: FileStorageSettings = Field(
        default_factory=lambda: FileStorageSettings(),
        description="File storage system configuration",
    )

    azure_search_services: Optional[List[AzureSearchSettings]] = Field(
        default=None,
        description="Azure Cognitive Search service configurations (optional)",
    )

    azure_sql_services: Optional[AzureSqlSettings] = Field(
        default=None, description="Azure SQL service configuration (optional)"
    )

    @field_validator("models")
    @classmethod
    def validate_models_not_empty_field(
        cls, v: List[ModelSettings]
    ) -> List[ModelSettings]:
        """Ensure at least one model is configured."""
        return validate_models_not_empty(v)

    def validate_configuration(self) -> None:
        """Validate the complete configuration and provide helpful feedback."""
        validate_configuration(self)
