# Agent System

This document details the agent system of the Insight Ingenious application.

## Overview

The agent system provides a framework for creating, managing, and interacting with AI agents. It's designed to be flexible and extensible, allowing for easy creation of custom agents.

## Key Components

- **BaseAgent**: Abstract base class for all agents
- **AgentConfig**: Configuration model for agents
- **AgentRegistry**: Central registry for managing agent instances
- **Example Agents**: Ready-to-use agent implementations

## BaseAgent

The `BaseAgent` class provides a common interface for all agents:

```python
class BaseAgent:
    """Base class for all agents in the system."""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self._agent = None
        self._model_client = None
    
    async def run(self, message: str, **kwargs) -> str:
        """Run the agent with a message."""
        # Implementation in subclasses
    
    async def close(self):
        """Clean up resources."""
        # Implementation in subclasses
```

### Agent Lifecycle

1. **Initialization**: The agent is created with a configuration
2. **Run**: The agent processes messages and generates responses
3. **Close**: The agent cleans up resources when no longer needed

## AgentConfig

The `AgentConfig` class defines the configuration for an agent:

```python
class AgentConfig(BaseModel):
    """Configuration for an agent."""
    name: str
    description: str
    system_message: str
    model: str = "gpt-4o"
    temperature: float = 0.1
    max_tokens: Optional[int] = None
    tools: List[str] = []
```

## AgentRegistry

The `AgentRegistry` class manages agent instances:

```python
class AgentRegistry:
    """Registry for all available agents."""
    
    _agents: Dict[str, Type[BaseAgent]] = {
        "chat": ChatAgent,
        "research": ResearchAgent,
        "sql": SQLAgent,
        "azure": AzureOpenAIAgent,
    }
    
    _instances: Dict[str, BaseAgent] = {}
    
    @classmethod
    def get_agent(cls, agent_type: str, name: str = None) -> BaseAgent:
        """Get an agent instance by type."""
        # Implementation
```

### Agent Registration Process

1. Agent classes are registered in the `_agents` dictionary
2. When an agent is requested, the registry creates or returns an instance
3. Instances are cached in the `_instances` dictionary for reuse

## Azure OpenAI Integration

All agents use Azure OpenAI for AI capabilities:

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

## Example Agents

The application includes several example agents:

- **ChatAgent**: General conversational agent
- **ResearchAgent**: Specialized for research and analysis
- **SQLAgent**: Specialized for SQL queries and database tasks
- **AzureOpenAIAgent**: Direct Azure OpenAI integration

### Example: ChatAgent

```python
class ChatAgent(BaseAgent):
    """A simple conversational agent using Azure OpenAI directly."""
    
    def __init__(self, name: str = "chat_assistant"):
        config = AgentConfig(
            name=name,
            description="A helpful conversational assistant",
            system_message="""You are a helpful and friendly conversational assistant. 
            Respond naturally and helpfully to user queries.""",
            model="gpt-4.1-mini",
            temperature=0.7,
        )
        super().__init__(config)
        self._client = None
```

## Creating Custom Agents

To create a custom agent:

1. Inherit from `BaseAgent`
2. Implement required methods
3. Register the agent with `AgentRegistry`

```python
from agents.base import BaseAgent, AgentConfig
from agents.registry import register_agent

class MyCustomAgent(BaseAgent):
    """A custom agent for specific tasks."""
    
    def __init__(self, name: str = "my_custom_agent"):
        config = AgentConfig(
            name=name,
            description="My custom agent",
            system_message="Custom system message",
            model="gpt-4.1-mini",
            temperature=0.5,
        )
        super().__init__(config)
        self._client = None
    
    # Implement required methods
    
# Register the agent
register_agent("my_custom", MyCustomAgent)
```
