"""
Simple configuration management using YAML and environment variables.

This module provides a clean, simple way to manage application configuration
using YAML files and environment variables, replacing the complex profile system.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv


class ServerConfig(BaseModel):
    """Server configuration settings."""
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")


class AuthConfig(BaseModel):
    """Authentication configuration."""
    enabled: bool = Field(default=True, description="Enable authentication")
    username: Optional[str] = Field(default=None, description="Auth username from env")
    password: Optional[str] = Field(default=None, description="Auth password from env")


class ModelConfig(BaseModel):
    """LLM model configuration."""
    model: str = Field(default="gpt-4", description="Model name")
    temperature: float = Field(default=0.7, description="Temperature setting")
    max_tokens: int = Field(default=1000, description="Maximum tokens")
    api_key: Optional[str] = Field(default=None, description="API key from env")
    base_url: Optional[str] = Field(default=None, description="Base URL for Azure OpenAI")
    api_version: Optional[str] = Field(default=None, description="API version for Azure OpenAI")


class AppConfig(BaseModel):
    """Application configuration."""
    name: str = Field(default="AutoGen FastAPI Template", description="App name")
    version: str = Field(default="1.0.0", description="App version")
    debug: bool = Field(default=False, description="Debug mode")


class LoggingConfig(BaseModel):
    """Logging configuration."""
    level: str = Field(default="INFO", description="Log level")
    format: str = Field(default="json", description="Log format")


class Config(BaseModel):
    """Main configuration container."""
    app: AppConfig = Field(default_factory=AppConfig)
    server: ServerConfig = Field(default_factory=ServerConfig)
    auth: AuthConfig = Field(default_factory=AuthConfig)
    models: Dict[str, ModelConfig] = Field(default_factory=dict)
    agents: Dict[str, Any] = Field(default_factory=dict)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)


def load_config(config_path: str = "config.yaml") -> Config:
    """
    Load configuration from YAML file and environment variables.
    
    Args:
        config_path: Path to the YAML configuration file
        
    Returns:
        Loaded and validated configuration
    """
    # Load environment variables from .env file
    load_dotenv()
    
    # Load YAML configuration
    config_file = Path(config_path)
    if config_file.exists():
        with open(config_file, 'r') as f:
            yaml_config = yaml.safe_load(f) or {}
    else:
        yaml_config = {}
    
    # Create config object
    config = Config(**yaml_config)
    
    # Override with environment variables
    _load_env_overrides(config)
    
    return config


def _load_env_overrides(config: Config) -> None:
    """Load environment variable overrides into configuration."""
    
    # Authentication
    if auth_username := os.getenv("AUTH_USERNAME"):
        config.auth.username = auth_username
    if auth_password := os.getenv("AUTH_PASSWORD"):
        config.auth.password = auth_password
    
    # Models - load API keys
    if openai_key := os.getenv("OPENAI_API_KEY"):
        if "default_llm" not in config.models:
            config.models["default_llm"] = ModelConfig()
        config.models["default_llm"].api_key = openai_key
    
    # Azure OpenAI configuration
    if azure_key := os.getenv("AZURE_OPENAI_API_KEY"):
        if "default_llm" not in config.models:
            config.models["default_llm"] = ModelConfig()
        config.models["default_llm"].api_key = azure_key
    
    if azure_endpoint := os.getenv("AZURE_OPENAI_ENDPOINT"):
        if "default_llm" not in config.models:
            config.models["default_llm"] = ModelConfig()
        config.models["default_llm"].base_url = azure_endpoint
    
    if azure_version := os.getenv("AZURE_OPENAI_API_VERSION"):
        if "default_llm" not in config.models:
            config.models["default_llm"] = ModelConfig()
        config.models["default_llm"].api_version = azure_version
    
    # Server overrides
    if host := os.getenv("SERVER_HOST"):
        config.server.host = host
    if port := os.getenv("SERVER_PORT"):
        config.server.port = int(port)
    
    # App overrides
    if debug := os.getenv("DEBUG"):
        config.app.debug = debug.lower() in ("true", "1", "yes")


# Global configuration instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = load_config()
    return _config


def reload_config(config_path: str = "config.yaml") -> Config:
    """Reload configuration from file."""
    global _config
    _config = load_config(config_path)
    return _config
