"""
Common utilities for the Ingenious framework.

This package contains utility modules that can be used across different
parts of the application, including client factories and helper functions.
"""

from .azure_openai_client_factory import (
    create_azure_openai_chat_completion_client_with_custom_config,
    create_azure_openai_chat_completion_client_with_model_config,
)

__all__ = [
    "create_azure_openai_chat_completion_client_with_model_config",
    "create_azure_openai_chat_completion_client_with_custom_config",
]
