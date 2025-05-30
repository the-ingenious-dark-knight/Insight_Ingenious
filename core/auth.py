"""
Simple authentication module for basic HTTP authentication.

Provides straightforward authentication mechanisms without complex abstractions.
"""

import secrets
from typing import Optional
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from .config import get_config


security = HTTPBasic()


class AuthError(HTTPException):
    """Authentication error exception."""
    
    def __init__(self, detail: str = "Invalid authentication credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Basic"},
        )


def get_current_user(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    """
    Verify authentication credentials and return username.
    
    Args:
        credentials: HTTP Basic authentication credentials
        
    Returns:
        Username if authentication is successful
        
    Raises:
        AuthError: If authentication fails
    """
    config = get_config()
    
    # If auth is disabled, return a default user
    if not config.auth.enabled:
        return "anonymous"
    
    # Check if credentials are configured
    if not config.auth.username or not config.auth.password:
        raise AuthError("Authentication not properly configured")
    
    # Verify credentials
    is_correct_username = secrets.compare_digest(
        credentials.username, config.auth.username
    )
    is_correct_password = secrets.compare_digest(
        credentials.password, config.auth.password
    )
    
    if not (is_correct_username and is_correct_password):
        raise AuthError("Incorrect username or password")
    
    return credentials.username


def optional_auth(credentials: Optional[HTTPBasicCredentials] = Depends(security)) -> Optional[str]:
    """
    Optional authentication - returns username if provided and valid, None otherwise.
    
    Args:
        credentials: Optional HTTP Basic authentication credentials
        
    Returns:
        Username if authentication is provided and valid, None otherwise
    """
    config = get_config()
    
    if not config.auth.enabled or not credentials:
        return None
    
    try:
        return get_current_user(credentials)
    except AuthError:
        return None


def require_auth() -> bool:
    """Check if authentication is required based on configuration."""
    config = get_config()
    return config.auth.enabled
