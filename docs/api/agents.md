# Agent Management Endpoints

These endpoints allow you to manage agents in the system.

## GET /agents

Returns a list of all available agent instances.

### Request

```
GET /agents
```

Authentication required.

### Response

```json
[
  "chat_agent_1",
  "research_agent_2",
  "sql_agent_3"
]
```

### Status Codes

- `200 OK`: Successful request
- `401 Unauthorized`: Authentication failed

## GET /agents/types

Returns a list of all available agent types.

### Request

```
GET /agents/types
```

Authentication required.

### Response

```json
[
  "chat",
  "research",
  "sql",
  "azure"
]
```

### Status Codes

- `200 OK`: Successful request
- `401 Unauthorized`: Authentication failed

## GET /agents/{agent_name}

Returns detailed information about a specific agent.

### Request

```
GET /agents/{agent_name}
```

Path Parameters:

- `agent_name`: The name of the agent to retrieve

Authentication required.

### Response

```json
{
  "name": "chat_agent_1",
  "type": "chat",
  "config": {
    "model": "gpt-4.1-mini",
    "temperature": 0.7,
    "system_message": "You are a helpful assistant..."
  },
  "agents_count": 1
}
```

### Status Codes

- `200 OK`: Successful request
- `401 Unauthorized`: Authentication failed
- `404 Not Found`: Agent not found

## POST /agents

Creates a new agent instance.

### Request

```
POST /agents
```

Authentication required.

Request Body:

```json
{
  "agent_type": "chat",
  "name": "my_custom_chat_agent",
  "config": {
    "system_message": "Custom system message for this agent",
    "temperature": 0.5
  }
}
```

### Response

```json
{
  "success": true
}
```

### Status Codes

- `200 OK`: Agent created successfully
- `400 Bad Request`: Invalid request body
- `401 Unauthorized`: Authentication failed
- `404 Not Found`: Agent type not found
- `409 Conflict`: Agent with that name already exists

## DELETE /agents/{agent_name}

Deletes an agent instance.

### Request

```
DELETE /agents/{agent_name}
```

Path Parameters:

- `agent_name`: The name of the agent to delete

Authentication required.

### Response

```json
{
  "success": true
}
```

### Status Codes

- `200 OK`: Agent deleted successfully
- `401 Unauthorized`: Authentication failed
- `404 Not Found`: Agent not found
