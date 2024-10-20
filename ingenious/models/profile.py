from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class ModelConfig:
    model: str
    api_key: str
    base_url: str


@dataclass
class ChatHistoryConfig:
    database_connection_string: str = ""


@dataclass
class AzureSearchConfig:
    service: str
    key: str


@dataclass
class ChainlitAuthConfig:
    enable: bool = False
    github_secret: str = ""
    github_client_id: str = ""


@dataclass
class ChainlitConfig:
    enable: bool = False
    authentication: ChainlitAuthConfig = field(default_factory=ChainlitAuthConfig)

    def __init__(self, enable=False, authentication={}):
        authentication = ChainlitAuthConfig(**authentication)


@dataclass
class WebAuthConfig:
    type: str = ""
    enable: bool = True
    username: str = ""
    password: str = ""


@dataclass
class WebConfig:    
    authentication: WebAuthConfig = field(default_factory=WebAuthConfig)

    def __init__(self, authentication={}):
        self.authentication = WebAuthConfig(**authentication)


@dataclass
class Profile:
    name: str
    models: List[ModelConfig]
    chat_history: ChatHistoryConfig
    azure_search_services: List[AzureSearchConfig]
    web_configuration: WebConfig
    chainlit_configuration: ChainlitConfig

    def __init__(self, name, models, chat_history, azure_search_services, web_configuration, chainlit_configuration):
        self.name = name
        self.models = [ModelConfig(**model) for model in models]
        self.chat_history = ChatHistoryConfig(**chat_history)
        self.azure_search_services: list[AzureSearchConfig] = [AzureSearchConfig(**as_config) for as_config in azure_search_services]
        self.web_configuration = WebConfig(**web_configuration)
        self.chainlit_configuration = ChainlitConfig(**chainlit_configuration)


@dataclass
class Profiles:
    profiles: List[Profile] = field(default_factory=list)
