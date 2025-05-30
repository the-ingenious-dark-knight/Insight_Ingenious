# Core Components

This document details the core components of the Insight Ingenious application.

## Overview

The core components provide foundational services used throughout the application:

- **Configuration Management**: Loading and accessing application settings
- **Authentication**: Securing API endpoints
- **Logging**: Capturing application events and errors

## Configuration Management

The configuration system is designed to be simple yet flexible, using YAML files and environment variables.

### Key Features

- YAML-based configuration
- Environment variable overrides
- Simple accessor pattern

### Implementation

The `core/config.py` module provides:

- `Config` class: Pydantic model for type-safe configuration
- `get_config()` function: Access the global configuration
- `reload_config()` function: Reload configuration from disk

```python
from core.config import get_config

# Access configuration
config = get_config()
app_name = config.app.name
debug_mode = config.app.debug
```

### Configuration Loading Process

1. Load default values from Pydantic model defaults
2. Load settings from YAML file
3. Override with environment variables
4. Cache the configuration for efficient access

## Authentication

The authentication system provides HTTP Basic Authentication for API endpoints.

### Key Features

- HTTP Basic Authentication
- Optional authentication
- Simple dependency injection pattern

### Implementation

The `core/auth.py` module provides:

- `get_current_user()` function: FastAPI dependency for requiring authentication
- `optional_auth()` function: FastAPI dependency for optional authentication
- `require_auth()` function: Check if authentication is required

```python
from fastapi import Depends
from core.auth import get_current_user

@app.get("/protected")
async def protected_endpoint(current_user: str = Depends(get_current_user)):
    return {"message": f"Hello, {current_user}!"}
```

### Authentication Flow

1. Client sends request with HTTP Basic Authentication header
2. FastAPI extracts credentials
3. `get_current_user()` validates credentials against configuration
4. If valid, the endpoint handler is called; otherwise, a 401 response is returned

## Logging

The logging system provides structured logging with optional JSON formatting.

### Key Features

- JSON or human-readable formatting
- Structured context data
- Log level configuration

### Implementation

The `core/logging.py` module provides:

- `setup_logging()` function: Configure the logging system
- `get_logger()` function: Get a standard logger
- `get_structured_logger()` function: Get a logger with context data

```python
from core.logging import get_logger, get_structured_logger

# Standard logger
logger = get_logger(__name__)
logger.info("Something happened")

# Structured logger with context
logger = get_structured_logger(__name__, user_id="123", action="login")
logger.info("User logged in")
```

### Logging Flow

1. Application initializes logging during startup
2. Components get loggers as needed
3. Log messages are formatted according to configuration
4. Messages are written to stdout/stderr
