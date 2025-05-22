# API Documentation

This document provides a detailed reference for the Insight Ingenious REST API.

## Base URL

All API endpoints are relative to your base URL:
```
http://<host>:<port>/api/v1
```

By default, this would be:
```
http://127.0.0.1:8000/api/v1
```

## Authentication

Authentication methods depend on your configuration. By default, the API does not require authentication in development mode. For production deployments, configure API keys or OAuth authentication.

## Common Headers

| Header | Description | Required |
|--------|-------------|----------|
| `Content-Type` | Should be set to `application/json` for all requests with a body | Yes |
| `Authorization` | Authentication token (if configured) | Depends on configuration |

## Endpoints

### Chat

#### Start or Continue a Chat

```
POST /chat
```

Request body:
```json
{
  "conversation_id": "string",
  "message": "string",
  "conversation_flow": "string",
  "thread_id": "string (optional)",
  "metadata": { (optional)
    "key": "value"
  }
}
```

Response:
```json
{
  "conversation_id": "string",
  "message_id": "string",
  "thread_id": "string",
  "response": "string",
  "created_at": "datetime",
  "metadata": {
    "key": "value"
  }
}
```

#### Get Chat History

```
GET /chat/{conversation_id}
```

Response:
```json
{
  "conversation_id": "string",
  "messages": [
    {
      "message_id": "string",
      "role": "string",
      "content": "string",
      "created_at": "datetime"
    }
  ]
}
```

### Message Feedback

#### Submit Message Feedback

```
POST /message-feedback
```

Request body:
```json
{
  "message_id": "string",
  "rating": "number",
  "feedback_text": "string (optional)"
}
```

Response:
```json
{
  "message_id": "string",
  "feedback_id": "string",
  "status": "success"
}
```

### Prompts

#### List Available Prompts

```
GET /prompts
```

Response:
```json
{
  "prompts": [
    {
      "id": "string",
      "name": "string",
      "description": "string",
      "created_at": "datetime",
      "updated_at": "datetime"
    }
  ]
}
```

#### Get Prompt Detail

```
GET /prompts/{prompt_id}
```

Response:
```json
{
  "id": "string",
  "name": "string",
  "description": "string",
  "content": "string",
  "variables": [
    {
      "name": "string",
      "description": "string",
      "required": "boolean"
    }
  ],
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Diagnostic

#### Health Check

```
GET /health
```

Response:
```json
{
  "status": "healthy",
  "version": "string",
  "services": {
    "database": "healthy",
    "file_storage": "healthy"
  }
}
```

## Error Handling

The API uses standard HTTP status codes to indicate success or failure:

- `200 OK`: The request was successful
- `400 Bad Request`: The request was malformed
- `401 Unauthorized`: Authentication is required
- `403 Forbidden`: The authenticated user does not have permission
- `404 Not Found`: The requested resource was not found
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: An unexpected server error occurred

Error response structure:
```json
{
  "detail": "Error message",
  "code": "ERROR_CODE",
  "timestamp": "datetime"
}
```

## Rate Limiting

The API implements rate limiting to prevent abuse. Rate limits may vary based on your deployment configuration.

## Extensions

Custom API routes can be added through extensions. Refer to the Extensions documentation for details on how to add custom endpoints.
