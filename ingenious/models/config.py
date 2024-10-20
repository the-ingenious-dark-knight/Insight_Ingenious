import dataclasses as dataclass
from typing import List, Dict
from dataclasses import dataclass, field
from typing import List, Dict



@dataclass
class ChatHistoryConfig:
    database_type: str
    database_path: str = ""
    database_connection_string: str = ""
    database_name: str = ""
    memory_path: str = ""


@dataclass
class ModelConfig:
    model: str
    api_type: str
    api_version: str
    base_url: str = ""
    api_key: str = ""


@dataclass
class ChatServiceConfig:
    type: str


@dataclass
class ToolServiceConfig:
    enable: bool


@dataclass
class LoggingConfig:
    root_log_level: str
    log_level: str


@dataclass
class AzureSearchConfig:
    service: str
    endpoint: str
    key: str = ""


@dataclass
class WebAuthConfig:
    type: str = ""
    enable: bool = True
    username: str = ""
    password: str = ""


@dataclass
class WebConfig:
    ip_address: str
    port: int 
    authentication: WebAuthConfig = field(default_factory=WebAuthConfig)
    type: str = "fastapi"

    def __init__(self, ip_address: str, port: int,  type="fastapi", authentication={}):
        self.port = port
        self.ip_address = ip_address
        self.type = type
        self.authentication = WebAuthConfig(**authentication)



@dataclass
class Config:
    chat_history: ChatHistoryConfig
    profile: 'Profiles.Profile'
    models: List[ModelConfig]
    logging: LoggingConfig
    tool_service: ToolServiceConfig
    chat_service: ChatServiceConfig
    azure_search_services: List[AzureSearchConfig]
    web_configuration: WebConfig
