# Authentication Guide

This guide explains how to set up and manage authentication for the Insight Ingenious API.

## Overview

The application uses HTTP Basic Authentication to secure API endpoints. This is a simple authentication scheme built into the HTTP protocol, where the client must send a username and password with each request.

## Enabling/Disabling Authentication

Authentication can be enabled or disabled in the `config.yaml` file:

```yaml
auth:
  enabled: true  # Set to false to disable authentication
```

## Setting Credentials

Authentication credentials are set through environment variables for security:

```
AUTH_USERNAME=admin
AUTH_PASSWORD=your-secure-password
```

These should be added to your `.env` file or set in your environment.

## Authentication in API Requests

When making requests to the API, you need to include the authentication credentials:

### Using cURL

```bash
curl -u admin:your-password http://localhost:8000/api/v1/health
```

### Using Python Requests

```python
import requests

response = requests.get(
    "http://localhost:8000/api/v1/health",
    auth=("admin", "your-password")
)
```

### Using the Swagger UI

When accessing the Swagger UI at `http://localhost:8000/docs`, you'll be prompted for your username and password.

## Protected Endpoints

All API endpoints are protected by authentication by default, except for:

- `/health` - Basic health check
- `/docs` and `/redoc` - API documentation (though you'll need to authenticate to try the endpoints)

## Implementation Details

Authentication is implemented using FastAPI's built-in security utilities:

```python
from fastapi import Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from core.auth import get_current_user

# In your router:
@router.get("/protected-endpoint")
async def protected_endpoint(current_user: str = Depends(get_current_user)):
    return {"message": f"Hello, {current_user}!"}
```

## Custom Authentication

If you need to implement a different authentication scheme:

1. Modify the `auth.py` module in the `core` package
2. Implement your custom authentication logic
3. Update the API endpoints to use your new authentication mechanism

## Security Considerations

- HTTP Basic Authentication sends credentials in base64 encoding, which is not secure over plain HTTP
- Always use HTTPS in production to encrypt credentials
- Consider implementing a more robust authentication scheme for production use, such as OAuth2 or JWT

## Troubleshooting

Common authentication issues:

1. **Authentication failing**: Check that your environment variables are set correctly
2. **"Authentication required" errors**: Ensure you're including the credentials with each request
3. **Can't authenticate in development**: Make sure authentication is enabled in your configuration
