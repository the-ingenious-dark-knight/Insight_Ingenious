# Creating Custom Agents

This guide explains how to create custom agents by extending the BaseAgent class.

## Overview

The Insight Ingenious project is designed to be easily extensible with custom agents. You can create specialized agents for specific tasks by extending the `BaseAgent` class.

## Basic Agent Structure

All agents should inherit from the `BaseAgent` class and implement the required methods:

```python
from agents.base import BaseAgent, AgentConfig
from openai import AzureOpenAI

class MyCustomAgent(BaseAgent):
    """A custom agent for specific tasks."""
    
    def __init__(self, name: str = "my_custom_agent"):
        config = AgentConfig(
            name=name,
            description="A description of my custom agent",
            system_message="System prompt that guides the agent's behavior",
            model="gpt-4.1-mini",
            temperature=0.5,
        )
        super().__init__(config)
        self._client = None
    
    def _get_client(self):
        """Get the Azure OpenAI client."""
        if self._client is None:
            # Create client with Azure OpenAI configuration
            config = self._get_model_config()
            self._client = AzureOpenAI(
                api_key=config.api_key,
                azure_endpoint=config.endpoint,
                api_version=config.api_version
            )
        return self._client
    
    def _get_model_config(self):
        """Get the model configuration."""
        from core.config import get_config
        config = get_config()
        return next(iter(config.models.values()))
    
    async def run(self, message: str, **kwargs) -> str:
        """Run the agent with a message."""
        try:
            client = self._get_client()
            
            response = client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": self.config.system_message},
                    {"role": "user", "content": message}
                ],
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens or 1000
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error in custom agent: {str(e)}")
            return f"Error: {str(e)}"
    
    async def close(self):
        """Clean up resources."""
        self._client = None
```

## Registering Your Agent

To make your agent available in the application, you need to register it with the `AgentRegistry`:

```python
from agents.registry import register_agent
from my_module import MyCustomAgent

# Register the agent
register_agent("my_custom", MyCustomAgent)
```

You can add this code to your application startup, or create a module that gets imported during initialization.

## Example: Creating a Specialized Agent

Here's an example of a specialized agent for creative writing:

```python
class WritingAgent(BaseAgent):
    """Custom agent that specializes in writing assistance and content creation."""
    
    def __init__(self, name="writing_assistant"):
        config = AgentConfig(
            name=name,
            description="A writing assistant for creative content",
            system_message="""You are an expert writing assistant.
            You can help with creative writing, editing, and content creation.
            Always provide constructive feedback and suggestions.
            When asked to write something, be creative, engaging, and follow
            the user's style preferences and requirements.""",
            model="gpt-4.1-mini",
            temperature=0.8,
        )
        super().__init__(config)
        self._client = None
    
    # Implement other required methods...
    
    async def generate_story(self, prompt: str, genre: str = "general") -> str:
        """Generate a short story based on the prompt and genre."""
        message = f"Write a short story in the {genre} genre based on this prompt: {prompt}"
        return await self.run(message)
```

## Advanced Agent Capabilities

You can extend your agents with additional capabilities:

### Custom Methods

Add specialized methods for your agent's specific functionality:

```python
async def analyze_data(self, data: str) -> str:
    """Analyze data and provide insights."""
    message = f"Analyze this data and provide key insights:\n\n{data}"
    return await self.run(message)
```

### State Management

For agents that need to maintain state:

```python
def __init__(self, name: str = "stateful_agent"):
    # ... standard initialization ...
    self._memory = {}

async def remember(self, key: str, value: str):
    """Store information in the agent's memory."""
    self._memory[key] = value
    
async def recall(self, key: str) -> str:
    """Retrieve information from the agent's memory."""
    return self._memory.get(key, "I don't remember that.")
```

## Testing Your Agent

Create test scripts to verify your agent's functionality:

```python
async def test_custom_agent():
    """Test the custom agent functionality."""
    agent = MyCustomAgent()
    
    # Test basic functionality
    response = await agent.run("Hello, can you help me with something?")
    print(f"Response: {response}")
    
    # Test specialized methods
    if hasattr(agent, "specialized_method"):
        result = await agent.specialized_method("test input")
        print(f"Specialized method result: {result}")
    
    # Clean up
    await agent.close()
```

Run your test with:

```bash
uv run python -m your_test_module
```

## Best Practices

1. **Keep system messages focused**: Write clear, specific system messages that guide the agent's behavior
2. **Handle errors gracefully**: Always include error handling in your methods
3. **Clean up resources**: Implement the `close()` method to clean up resources
4. **Use appropriate temperature**: Set the temperature based on the creativity needed for the task
5. **Document your agent**: Include clear docstrings and comments
