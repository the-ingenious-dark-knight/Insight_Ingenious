# API Reference

This section documents the available API endpoints in the ingenious-slim application.

## API Structure

The API is organized into the following sections:

- **Health and Status**: Endpoints for monitoring the application's health
- **Agent Management**: Endpoints for managing agents
- **Chat**: Endpoints for interacting with agents

## Base URL

By default, the API is available at:

```
http://localhost:8000
```

## Authentication

Most endpoints require HTTP Basic Authentication. Include the username and password with each request:

```bash
curl -u username:password http://localhost:8000/api/endpoint
```

## Contents

- [Health and Status Endpoints](./health.md)
- [Agent Management Endpoints](./agents.md)
- [Chat Endpoints](./chat.md)
