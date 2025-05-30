# Health and Status Endpoints

These endpoints provide information about the application's health and status.

## GET /health

Returns a simple health check response.

### Request

```
GET /health
```

No authentication required.

### Response

```json
{
  "status": "ok",
  "timestamp": "2023-07-15T12:34:56.789Z",
  "version": "1.0.0",
  "uptime": "2h 15m 30s"
}
```

### Status Codes

- `200 OK`: The application is healthy
- `500 Internal Server Error`: The application is experiencing issues

## GET /health/detailed

Returns detailed health information about the application.

### Request

```
GET /health/detailed
```

Authentication required.

### Response

```json
{
  "status": "ok",
  "timestamp": "2023-07-15T12:34:56.789Z",
  "version": "1.0.0",
  "system_info": {
    "python_version": "3.11.4",
    "platform": "linux",
    "cpu_count": 4,
    "memory_usage": "256 MB"
  },
  "config_status": {
    "config_file": "config.yaml",
    "auth_enabled": true
  },
  "agent_status": {
    "available_agents": ["chat", "research", "sql"],
    "active_agents": 2
  }
}
```

### Status Codes

- `200 OK`: The application is healthy
- `401 Unauthorized`: Authentication failed
- `500 Internal Server Error`: The application is experiencing issues

## GET /status

Returns a simple status message.

### Request

```
GET /status
```

No authentication required.

### Response

```json
{
  "status": "running"
}
```

### Status Codes

- `200 OK`: The application is running
