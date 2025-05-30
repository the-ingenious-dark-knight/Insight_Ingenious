# Chat Endpoints

These endpoints allow you to interact with agents through chat interfaces.

## POST /chat

Send a message to an agent.

### Request

```
POST /chat
```

Authentication required.

Request Body:

```json
{
  "message": "Hello, can you help me with something?",
  "agent_type": "chat",
  "context": {
    "custom_data": "any additional context"
  }
}
```

Parameters:

- `message` (required): The message to send to the agent
- `agent_type` (optional): The type of agent to use (defaults to "chat")
- `context` (optional): Additional context for the conversation

### Response

```json
{
  "response": "Hello! I'd be happy to help you. What do you need assistance with?",
  "agent_type": "chat",
  "agent_name": "chat_1"
}
```

### Status Codes

- `200 OK`: Successful request
- `400 Bad Request`: Invalid request body
- `401 Unauthorized`: Authentication failed
- `404 Not Found`: Agent type not found
- `500 Internal Server Error`: Error processing the request

## POST /agents/{agent_type}/chat

Send a message to a specific type of agent.

### Request

```
POST /agents/{agent_type}/chat
```

Path Parameters:

- `agent_type`: The type of agent to chat with (e.g., "chat", "research", "sql")

Query Parameters:

- `message`: The message to send to the agent

Authentication required.

### Response

```json
{
  "response": "Here's the information you requested...",
  "agent_type": "research",
  "agent_name": "research_1"
}
```

### Status Codes

- `200 OK`: Successful request
- `400 Bad Request`: Invalid request
- `401 Unauthorized`: Authentication failed
- `404 Not Found`: Agent type not found
- `500 Internal Server Error`: Error processing the request

## Usage Examples

### Basic Chat Interaction

```bash
curl -X POST \
  -u username:password \
  -H "Content-Type: application/json" \
  -d '{"message": "What is Python programming?", "agent_type": "chat"}' \
  http://localhost:8000/chat
```

### Research Query

```bash
curl -X POST \
  -u username:password \
  -H "Content-Type: application/json" \
  -d '{"message": "Research the impact of AI on healthcare", "agent_type": "research"}' \
  http://localhost:8000/chat
```

### SQL Query Generation

```bash
curl -X POST \
  -u username:password \
  -H "Content-Type: application/json" \
  -d '{"message": "Create a query to find all users who registered in the last 30 days", "agent_type": "sql"}' \
  http://localhost:8000/chat
```

### Using the Alternate Endpoint

```bash
curl -X POST \
  -u username:password \
  "http://localhost:8000/agents/research/chat?message=Tell%20me%20about%20quantum%20computing"
```
