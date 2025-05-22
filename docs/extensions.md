# Extending Insight Ingenious

This document explains how to extend and customize Insight Ingenious to fit your specific needs.

## Extension Structure

Insight Ingenious provides a template for creating extensions in the `ingenious_extensions_template` directory. This template includes the following structure:

```
ingenious_extensions_template/
  ├── __init__.py
  ├── config.template.yml
  ├── profiles.template.yml
  ├── readme.md
  ├── api/
  │   └── routes/
  │       └── custom.py
  ├── models/
  ├── sample_data/
  ├── services/
  ├── templates/
  └── tests/
```

To create your own extension:

1. Copy the `ingenious_extensions_template` directory
2. Rename it to `ingenious_extensions`
3. Customize the code to fit your needs

## Extension Points

Insight Ingenious offers several extension points:

### 1. Custom API Routes

Create custom API endpoints by extending the API routes:

```python
# ingenious_extensions/api/routes/custom.py
from fastapi import APIRouter, Depends
from ingenious.models.api_routes import IApiRoutes
from ingenious.config.config import Config

class Api_Routes(IApiRoutes):
    def __init__(self, config: Config, app: "FastAPI"):
        self.router = APIRouter()
        self.config = config
        self.app = app

    def add_custom_routes(self):
        @self.router.get("/custom-endpoint")
        async def custom_endpoint():
            return {"message": "This is a custom endpoint"}
            
        # Include your router
        self.app.include_router(self.router, prefix="/api/v1", tags=["Custom"])
```

### 2. Custom Agents

Create custom agent types:

```python
# ingenious_extensions/models/custom_agent.py
from ingenious.models.agent import Agent
from typing import Dict, Any
from ingenious.models.message import Message

class CustomAgent(Agent):
    async def process_message(self, message: Message) -> str:
        # Custom processing logic
        return f"Custom response to: {message.content}"
```

Register your custom agent in the configuration:

```yaml
agents:
  - name: "my_custom_agent"
    type: "custom"  # The system will look for a CustomAgent class
    model_config:
      model: "gpt-4o"
    system_prompt: "You are a custom agent."
```

### 3. Custom Chat Services

Create custom chat service implementations:

```python
# ingenious_extensions/services/chat_services/custom/service.py
from ingenious.services.chat_service import IChatService
from ingenious.models.chat import ChatRequest, ChatResponse
from ingenious.db.chat_history_repository import ChatHistoryRepository
from ingenious.config.config import Config

class custom_chat_service(IChatService):
    def __init__(self, config: Config, chat_history_repository: ChatHistoryRepository, conversation_flow: str):
        self.config = config
        self.chat_history_repository = chat_history_repository
        self.conversation_flow = conversation_flow

    async def get_chat_response(self, chat_request: ChatRequest) -> ChatResponse:
        # Custom chat service implementation
        return ChatResponse(
            conversation_id=chat_request.conversation_id,
            message_id="custom-message-id",
            response="Custom response from service",
            created_at=datetime.now().isoformat()
        )
```

Enable your custom chat service in the configuration:

```yaml
conversation_flows:
  - name: "custom_flow"
    type: "custom"  # Points to your custom_chat_service
    # Additional configuration...
```

### 4. Custom Templates

Create custom prompt templates:

```
# ingenious_extensions/templates/prompts/custom_prompt.j2
You are a {{ agent_type }} designed to help with {{ task }}.

User query: {{ query }}

Please provide a detailed response.
```

Use your template in code:

```python
from ingenious.utils.template_utils import render_template

prompt = render_template(
    "custom_prompt.j2", 
    {"agent_type": "research assistant", "task": "academic research", "query": user_query}
)
```

### 5. Custom Data Models

Create custom data models:

```python
# ingenious_extensions/models/custom_data.py
from pydantic import BaseModel
from typing import List, Optional

class CustomData(BaseModel):
    id: str
    name: str
    attributes: List[str]
    metadata: Optional[dict] = None
```

### 6. Database Extensions

Extend database functionality:

```python
# ingenious_extensions/db/custom_repository.py
from ingenious.db import BaseRepository

class CustomRepository(BaseRepository):
    def __init__(self, db_client):
        super().__init__(db_client)
        
    async def custom_query(self, query_params):
        # Implementation
        pass
```

## Configuring Extensions

Extensions are configured through the main `config.yml` file:

```yaml
extensions:
  enabled: true
  custom_routes: true
  custom_agents: true
  custom_services: true
```

## Packaging Extensions

You can package your extensions for distribution:

1. Create a `setup.py` file in your extension directory:

```python
from setuptools import setup, find_packages

setup(
    name="ingenious-extension-name",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "insight-ingenious>=0.1.0",
    ],
    include_package_data=True,
)
```

2. Package your extension:

```bash
python setup.py sdist bdist_wheel
```

3. Install in another project:

```bash
pip install path/to/ingenious-extension-name-0.1.0.whl
```

## Extension Best Practices

1. **Maintain Compatibility**: Ensure your extensions are compatible with the core Insight Ingenious version
2. **Follow Naming Conventions**: Use consistent naming patterns for your extension components
3. **Write Tests**: Include tests for your extension functionality
4. **Document**: Add README and documentation for your extension
5. **Keep Dependencies Minimal**: Avoid introducing unnecessary dependencies
6. **Error Handling**: Implement proper error handling in your extension code
7. **Versioning**: Version your extensions to track changes and compatibility

## Example: Creating a Simple Extension

Here's a complete example of creating a simple extension:

1. **Copy the template**:
```bash
cp -r ingenious_extensions_template ingenious_extensions
```

2. **Create a custom agent**:
```python
# ingenious_extensions/models/weather_agent.py
from ingenious.models.agent import Agent
from typing import Dict, Any
from ingenious.models.message import Message

class WeatherAgent(Agent):
    async def process_message(self, message: Message) -> str:
        # In a real implementation, this would call a weather API
        return f"The weather is sunny today! (Response to: {message.content})"
```

3. **Create a custom API route**:
```python
# ingenious_extensions/api/routes/custom.py
from fastapi import APIRouter
from ingenious.models.api_routes import IApiRoutes
from ingenious.config.config import Config

class Api_Routes(IApiRoutes):
    def __init__(self, config: Config, app):
        self.router = APIRouter()
        self.config = config
        self.app = app

    def add_custom_routes(self):
        @self.router.get("/weather")
        async def get_weather(city: str):
            return {"city": city, "condition": "sunny", "temperature": 25}
            
        self.app.include_router(self.router, prefix="/api/v1", tags=["Weather"])
```

4. **Update configuration**:
```yaml
# config.yml
agents:
  - name: "weather_agent"
    type: "weather"
    model_config:
      model: "gpt-4o"
    system_prompt: "You are a weather information agent."

conversation_flows:
  - name: "weather_info"
    type: "basic"
    primary_agent: "weather_agent"
```

5. **Test your extension**:
```bash
ingen_cli run-rest-api-server
```

Then make a request to your new endpoint:
```bash
curl "http://127.0.0.1:8000/api/v1/weather?city=London"
```
