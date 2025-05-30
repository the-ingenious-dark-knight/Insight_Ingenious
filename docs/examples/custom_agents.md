# Custom Agent Examples

This document provides examples of how to create and use custom agents in the Insight Ingenious application.

## Creating a Basic Custom Agent

Here's an example of creating a simple custom agent:

```python
from typing import Dict, Any, Optional
from openai import AzureOpenAI
from agents.base import BaseAgent, AgentConfig
from agents.registry import register_agent
from core.logging import get_logger

logger = get_logger(__name__)

class MathAgent(BaseAgent):
    """Custom agent that specializes in mathematical calculations and explanations."""
    
    def __init__(self, name="math_assistant"):
        config = AgentConfig(
            name=name,
            description="A mathematics specialist for calculations and explanations",
            system_message="""You are a mathematics expert.
            You can solve mathematical problems, explain mathematical concepts,
            and provide step-by-step solutions. Always show your work and
            explain the reasoning behind your answers.""",
            model="gpt-4.1-mini",
            temperature=0.1,
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
            logger.error(f"Error in math agent: {str(e)}")
            return f"Error: {str(e)}"
    
    async def solve_equation(self, equation: str) -> str:
        """Solve a mathematical equation."""
        message = f"Solve this equation and show your work: {equation}"
        return await self.run(message)
    
    async def explain_concept(self, concept: str) -> str:
        """Explain a mathematical concept."""
        message = f"Explain this mathematical concept in simple terms: {concept}"
        return await self.run(message)
    
    async def close(self):
        """Clean up resources."""
        self._client = None
```

## Registering the Custom Agent

After creating the agent class, you need to register it:

```python
from agents.registry import register_agent
from my_agents import MathAgent

# Register the agent
register_agent("math", MathAgent)
```

## Using the Custom Agent

Once registered, you can use your custom agent:

```python
from agents.registry import AgentRegistry

async def math_agent_example():
    """Example of using the custom math agent."""
    # Get a math agent
    agent = AgentRegistry.get_agent("math")
    
    # Solve an equation
    equation = "x^2 + 5x + 6 = 0"
    solution = await agent.solve_equation(equation)
    print(f"Equation: {equation}")
    print(f"Solution:\n{solution}")
    
    # Explain a concept
    concept = "calculus"
    explanation = await agent.explain_concept(concept)
    print(f"Concept: {concept}")
    print(f"Explanation:\n{explanation}")
    
    # Clean up
    await agent.close()
```

## Creating an Agent with State

Here's an example of an agent that maintains state:

```python
class MemoryAgent(BaseAgent):
    """Custom agent that maintains memory of previous interactions."""
    
    def __init__(self, name="memory_assistant"):
        config = AgentConfig(
            name=name,
            description="An assistant that remembers previous interactions",
            system_message="""You are an assistant with a memory.
            You can remember information from previous interactions and
            recall it when needed.""",
            model="gpt-4.1-mini",
            temperature=0.7,
        )
        super().__init__(config)
        self._client = None
        self._memory = {}
        self._conversation_history = []
    
    # Standard methods (_get_client, _get_model_config, run, close)
    
    async def remember(self, key: str, value: str):
        """Store information in the agent's memory."""
        self._memory[key] = value
        return f"I'll remember that {key} is {value}."
    
    async def recall(self, key: str) -> str:
        """Retrieve information from the agent's memory."""
        if key in self._memory:
            return f"I remember that {key} is {self._memory[key]}."
        else:
            return f"I don't have any information about {key}."
    
    async def chat(self, message: str) -> str:
        """Chat with memory of previous interactions."""
        # Add message to history
        self._conversation_history.append({"role": "user", "content": message})
        
        # Prepare messages with history
        messages = [{"role": "system", "content": self.config.system_message}]
        messages.extend(self._conversation_history)
        
        # Get response
        client = self._get_client()
        response = client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens or 1000
        )
        
        response_text = response.choices[0].message.content.strip()
        
        # Add response to history
        self._conversation_history.append({"role": "assistant", "content": response_text})
        
        return response_text
```

## Combining Multiple Custom Agents

You can create more complex systems by combining multiple custom agents:

```python
async def multi_agent_workflow():
    """Example of a workflow using multiple custom agents."""
    # Get agents
    math_agent = AgentRegistry.get_agent("math")
    research_agent = AgentRegistry.get_agent("research")
    writing_agent = AgentRegistry.get_agent("writing")
    
    # Step 1: Research a mathematical topic
    topic = "machine learning algorithms"
    research = await research_agent.run(f"Research {topic}")
    
    # Step 2: Extract and solve equations
    equations = extract_equations(research)
    solutions = []
    for eq in equations:
        solution = await math_agent.solve_equation(eq)
        solutions.append(solution)
    
    # Step 3: Create a report
    report_request = f"Write a report on {topic} including these solutions: {solutions}"
    report = await writing_agent.run(report_request)
    
    # Clean up
    await math_agent.close()
    await research_agent.close()
    await writing_agent.close()
    
    return report

def extract_equations(text):
    """Extract equations from text (simplified example)."""
    # In a real implementation, use regex or more sophisticated parsing
    return ["y = mx + b", "E = mc^2"]
```

## Complete Example

Here's a complete example that demonstrates creating and using a custom agent:

```python
import asyncio
from typing import Dict, Any, Optional
from openai import AzureOpenAI
from agents.base import BaseAgent, AgentConfig
from agents.registry import register_agent, AgentRegistry
from core.logging import get_logger

logger = get_logger(__name__)

class TranslationAgent(BaseAgent):
    """Custom agent for language translation."""
    
    def __init__(self, name="translator"):
        config = AgentConfig(
            name=name,
            description="A language translation specialist",
            system_message="""You are a language translation expert.
            You can translate text between different languages accurately,
            preserving meaning, tone, and cultural context.""",
            model="gpt-4.1-mini",
            temperature=0.3,
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
            logger.error(f"Error in translation agent: {str(e)}")
            return f"Error: {str(e)}"
    
    async def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """Translate text from source language to target language."""
        message = f"Translate this text from {source_lang} to {target_lang}: {text}"
        return await self.run(message)
    
    async def close(self):
        """Clean up resources."""
        self._client = None

# Register the agent
register_agent("translation", TranslationAgent)

async def translation_example():
    """Example using the translation agent."""
    # Get a translation agent
    agent = AgentRegistry.get_agent("translation")
    
    # Translate text
    text = "Hello, how are you today?"
    source = "English"
    target = "Spanish"
    
    translation = await agent.translate(text, source, target)
    
    print(f"Original ({source}): {text}")
    print(f"Translation ({target}): {translation}")
    
    # Clean up
    await agent.close()

# Run the example
if __name__ == "__main__":
    asyncio.run(translation_example())
```

Save this as `translation_example.py` and run:

```bash
uv run python translation_example.py
```
