# ingenious-slim

A slim fork of the Insight Ingenious project for building AutoGen-based agent APIs with FastAPI. This lightweight template provides a solid foundation for creating multi-agent applications with clean architecture and simple configuration.

## ✨ Features

- **Minimal Abstraction**: Thin wrapper over AutoGen and FastAPI
- **Simple Configuration**: YAML + .env files (no complex profiles)
- **Ready-to-Use Agents**: Chat, Research, and SQL agents included
- **RESTful API**: Clean endpoints for agent interaction
- **Basic Authentication**: HTTP Basic Auth built-in
- **Developer-Friendly**: Easy to understand, extend, and maintain
- **Template-First**: Git-clonable foundation, not a library

## Important Notes

- This project **exclusively uses** `uv` for Python package management and environment operations.
- This project **only supports** Azure OpenAI integrations, not standard OpenAI.

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd ingenious-slim

# Copy environment template
cp .env.example .env
```

### 2. Install Dependencies

```bash
# Using uv
uv add -e .
```

### 3. Configure

Edit `config.yaml` to customize your setup:

```yaml
app:
  name: "My Agent API"
  debug: false

auth:
  enabled: true

models:
  default_llm:
    model: "gpt-4.1-mini"
    temperature: 0.7

agents:
  enabled:
    - "chat"
    - "research"
    - "sql"
```

### 4. Run the Server

```bash
# Using the built-in command
uv run python main.py

# Or using uvicorn directly
uv run uvicorn main:app --reload

# With custom config
uv run python main.py --config my-config.yaml
```

### 5. Test the API

Visit `http://localhost:8000/docs` for interactive API documentation, or:

```bash
curl -u admin:your_password http://localhost:8000/api/v1/health
```

## 📚 Documentation

Comprehensive documentation is available in the [docs](./docs/) directory:

- [Getting Started](./docs/getting_started.md)
- [Guides](./docs/guides/index.md)
- [API Reference](./docs/api/index.md)
- [Architecture](./docs/architecture/index.md)
- [Examples](./docs/examples/index.md)
- [Complete Table of Contents](./docs/toc.md)

### Key Documentation Topics

- [Package Management with uv](./docs/guides/package_management.md)
- [Azure OpenAI Integration](./docs/guides/azure_openai.md)
- [Custom Agents](./docs/guides/custom_agents.md)
- [Authentication](./docs/guides/authentication.md)
- [Deployment](./docs/guides/deployment.md)

### Configuration

#### Application Config (config.yaml)

```yaml
app:
  name: "AutoGen FastAPI Template"
  version: "1.0.0"
  debug: false

server:
  host: "0.0.0.0"
  port: 8000

auth:
  enabled: true

models:
  default_llm:
    model: "gpt-4"
    temperature: 0.7
    max_tokens: 1000

agents:
  enabled:
    - "chat"
    - "research"
    - "sql"

  configs:
    chat:
      system_message: "You are a helpful assistant."
    sql:
      database_path: "data.db"

logging:
  level: "INFO"
  format: "json"
```

### API Endpoints

#### Health Check
- `GET /api/v1/health` - Basic health check
- `GET /api/v1/health/detailed` - Detailed system information

#### Agent Management
- `GET /api/v1/agents/types` - List available agent types
- `GET /api/v1/agents` - List agent instances
- `GET /api/v1/agents/{name}` - Get agent information
- `POST /api/v1/agents` - Create agent instance
- `DELETE /api/v1/agents/{name}` - Delete agent instance

#### Chat
- `POST /api/v1/chat` - Send message to agent

### Example API Usage

```python
import requests

# Chat with an agent
response = requests.post(
    "http://localhost:8000/api/v1/chat",
    json={
        "agent_name": "default_chat",
        "message": "Hello, how are you?"
    },
    auth=("admin", "your_password")
)

print(response.json()["response"])
```

## 🤖 Built-in Agents

### Chat Agent
Basic conversational agent for general questions and assistance.

```python
# Create a custom chat agent
requests.post("/api/v1/agents", json={
    "agent_type": "chat",
    "name": "my_assistant",
    "config": {
        "system_message": "You are a helpful coding assistant."
    }
})
```

### Research Agent
Web-enabled agent for research and information gathering.

```python
# Use the research agent
requests.post("/api/v1/chat", json={
    "agent_name": "default_research",
    "message": "What are the latest developments in AI safety?"
})
```

### SQL Agent
Database querying and analysis agent with built-in sample data.

```python
# Query database
requests.post("/api/v1/chat", json={
    "agent_name": "default_sql",
    "message": "Show me the database schema and total sales by customer"
})
```

## 🛠 Creating Custom Agents

### 1. Create Agent Class

```python
from agents.base import BaseAgent
from typing import Dict, Any, Optional

class MyCustomAgent(BaseAgent):
    def setup_autogen(self) -> None:
        """Setup AutoGen agents."""
        self.assistant = self.create_assistant_agent(
            name=f"{self.name}_assistant",
            system_message="You are a specialized assistant for..."
        )
        self.user_proxy = self.create_user_proxy_agent()
        self.autogen_agents = [self.assistant, self.user_proxy]

    async def chat(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Handle chat messages."""
        chat_result = self.user_proxy.initiate_chat(
            self.assistant,
            message=message,
            max_turns=1
        )

        # Extract response from chat history
        messages = chat_result.chat_history
        for msg in reversed(messages):
            if msg.get("name") == self.assistant.name:
                return msg.get("content", "No response generated.")

        return "Error: No response generated."
```

### 2. Register Agent

```python
from agents.registry import register_agent

# Register your custom agent
register_agent("custom", MyCustomAgent)
```

### 3. Use Your Agent

```python
# Create instance via API
requests.post("/api/v1/agents", json={
    "agent_type": "custom",
    "name": "my_custom_instance"
})

# Use the agent
requests.post("/api/v1/chat", json={
    "agent_name": "my_custom_instance",
    "message": "Hello from my custom agent!"
})
```

## 📁 Project Structure

```
autogen-fastapi-template/
├── core/                   # Core functionality
│   ├── config.py          # Configuration management
│   ├── auth.py            # Authentication
│   └── logging.py         # Logging setup
├── agents/                # Agent system
│   ├── base.py            # Base agent class
│   ├── registry.py        # Agent registry
│   └── examples/          # Example agents
│       ├── chat_agent.py
│       ├── research_agent.py
│       └── sql_agent.py
├── api/                   # FastAPI routes
│   ├── chat.py            # Chat endpoints
│   ├── agents.py          # Agent management
│   └── health.py          # Health checks
├── tests/                 # Test suite
├── examples/              # Usage examples
├── main.py               # Application entry point
├── config.yaml           # Configuration file
├── .env.example          # Environment template
└── pyproject.toml        # Project dependencies
```
