"""
Common enums used across the Ingenious framework.

This module contains enum definitions that are shared across different
parts of the application.
"""

from enum import Enum


class AuthenticationMethod(str, Enum):
    """Authentication methods for Azure services."""

    MSI = "msi"
    CLIENT_ID_AND_SECRET = "client_id_and_secret"
    DEFAULT_CREDENTIAL = "default_credential"
    TOKEN = "token"
