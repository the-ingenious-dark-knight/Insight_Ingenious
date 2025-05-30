# Integration Points

This document details the integration points of the Insight Ingenious application with external systems and libraries.

## Overview

Insight Ingenious integrates with several external systems and libraries to provide its functionality. The primary integration is with Azure OpenAI for AI capabilities.

## Azure OpenAI Integration

Insight Ingenious **exclusively** uses Azure OpenAI for all AI capabilities. This integration is handled through the AzureOpenAI client.

### Integration Points

- **Model Client**: The `AzureOpenAI` client from the Azure OpenAI SDK
- **Authentication**: API keys and endpoint configuration
- **Model Selection**: Configuration of which Azure OpenAI models to use

### Implementation

```python
from openai import AzureOpenAI

def _get_client(self):
    """Get the Azure OpenAI client."""
    if self._client is None:
        config = self._get_model_config()
        self._client = AzureOpenAI(
            api_key=config.api_key,
            azure_endpoint=config.endpoint,
            api_version=config.api_version
        )
    return self._client
```

### Configuration

Azure OpenAI integration is configured through environment variables:

```
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_API_VERSION=2023-05-15
```

## AutoGen Integration

Insight Ingenious uses AutoGen for agent capabilities. This integration is handled through the AutoGen agent classes.

### Integration Points

- **Agent Classes**: `AssistantAgent` and `UserProxyAgent` from AutoGen
- **Agent Creation**: Configuration and initialization of AutoGen agents
- **Model Configuration**: Passing Azure OpenAI configuration to AutoGen

### Implementation

```python
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

class AssistantAgentWrapper(BaseAgent):
    """Wrapper for AutoGen AssistantAgent."""
    
    def _create_agent(self) -> AssistantAgent:
        """Create the underlying AutoGen agent."""
        model_client = self._get_model_client()
        agent = AssistantAgent(
            name=self.config.name,
            system_message=self.config.system_message,
            llm_config={
                "model": self.config.model,
                "temperature": self.config.temperature,
                "model_client": model_client,
            }
        )
        return agent
```

## FastAPI Integration

The application uses FastAPI for the API layer.

### Integration Points

- **Application Instance**: The main FastAPI application
- **Routers**: FastAPI routers for organizing endpoints
- **Dependency Injection**: FastAPI's dependency injection system
- **Middleware**: FastAPI middleware for cross-cutting concerns

### Implementation

```python
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI app
app = FastAPI(
    title=config.app.name,
    version=config.app.version,
    debug=config.app.debug,
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router, prefix="/health", tags=["health"])
app.include_router(chat_router, prefix="/api/v1", tags=["chat"])
```

## Pydantic Integration

The application uses Pydantic for data validation and settings management.

### Integration Points

- **Settings Models**: Pydantic models for application configuration
- **API Models**: Pydantic models for API request/response contracts
- **Validation**: Automatic validation of incoming data

### Implementation

```python
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

class AgentConfig(BaseModel):
    """Configuration for an agent."""
    name: str = Field(..., description="Agent name")
    description: str = Field(..., description="Agent description")
    system_message: str = Field(..., description="System message for the agent")
    model: str = Field(default="gpt-4o", description="Model name")
    temperature: float = Field(default=0.1, description="Temperature setting")
    max_tokens: Optional[int] = Field(default=None, description="Maximum tokens")
    tools: List[str] = Field(default_factory=list, description="Available tools")
```

## Python Package Management with uv

The application uses uv for Python package management.

### Integration Points

- **Dependency Management**: Installing and managing dependencies
- **Virtual Environment**: Running Python code in isolated environments
- **Package Resolution**: Resolving dependencies and versions

### Implementation

uv is used for all Python package management and script execution:

```bash
# Install dependencies
uv pip install -e .

# Run the application
uv run python main.py

# Run tests
uv run pytest
```
