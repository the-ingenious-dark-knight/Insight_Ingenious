from pydantic import BaseModel, Field, ValidationError, RootModel
from typing import List, Dict, Optional


class ModelConfig(BaseModel):
    model: str
    api_key: str
    base_url: str


class ChatHistoryConfig(BaseModel):
    database_connection_string: str = ""


class AzureSearchConfig(BaseModel):
    service: str
    key: str


class ChainlitAuthConfig(BaseModel):
    enable: bool = False
    github_secret: str = ""
    github_client_id: str = ""


class ChainlitConfig(BaseModel):
    authentication: ChainlitAuthConfig = Field(default_factory=ChainlitAuthConfig)


class ToolServiceConfig(BaseModel):
    pass


class ChatServiceConfig(BaseModel):
    pass


class WebAuthConfig(BaseModel):
    type: str = ""
    enable: bool = True
    username: str = ""
    password: str = ""


class WebConfig(BaseModel):    
    authentication: WebAuthConfig = Field(default_factory=WebAuthConfig)


class LoggingConfig(BaseModel):
    pass


class Profile(BaseModel):
    name: str
    models: List[ModelConfig]
    chat_history: ChatHistoryConfig
    chat_service: ChatServiceConfig = Field(default_factory=ChatServiceConfig, description="Chat service configuration")
    azure_search_services: List[AzureSearchConfig]
    web_configuration: WebConfig
    chainlit_configuration: ChainlitConfig
    tool_service: ToolServiceConfig = Field(default_factory=ToolServiceConfig, description="Tool service configuration")
    logging: LoggingConfig = Field(default_factory=LoggingConfig, description="Logging configuration")


class Profiles(RootModel[List[Profile]]):
    pass
