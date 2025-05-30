"""
Base agent classes and utilities for the AutoGen FastAPI template.
"""
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
import asyncio
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
# Import the OpenAI client directly for better Azure compatibility
from autogen_ext.models.openai import OpenAIChatCompletionClient
from core.config import get_config


class AgentConfig(BaseModel):
    """Configuration for an agent."""
    name: str
    description: str
    system_message: str
    model: str = "gpt-4o"
    temperature: float = 0.1
    max_tokens: Optional[int] = None
    tools: List[str] = []


class BaseAgent:
    """Base class for all agents in the system."""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self._agent = None
        self._model_client = None
        
    def _get_model_client(self) -> OpenAIChatCompletionClient:
        """Get OpenAI model client."""
        if self._model_client is None:
            config = get_config()
            # Get the first model config or create a default one
            model_config = next(iter(config.models.values())) if config.models else None
            if not model_config:
                # Create default model config if none exists
                from core.config import ModelConfig
                model_config = ModelConfig()
            
            # Check for Azure OpenAI configuration
            if model_config.base_url and model_config.api_version:
                print(f"Using Azure OpenAI: {model_config.base_url}")
                # Use the same initialization pattern that works in our test script
                self._model_client = OpenAIChatCompletionClient(
                    model=self.config.model,
                    api_key=model_config.api_key,
                    azure_endpoint=model_config.base_url,
                    api_version=model_config.api_version,
                )
            else:
                print("Using standard OpenAI")
                # Simplify OpenAI client initialization to match the pattern
                self._model_client = OpenAIChatCompletionClient(
                    model=self.config.model,
                    api_key=model_config.api_key,
                )
        return self._model_client
    
    def _create_agent(self):
        """Create the underlying AutoGen agent."""
        raise NotImplementedError("Subclasses must implement _create_agent")
    
    @property
    def agent(self):
        """Get the underlying AutoGen agent."""
        if self._agent is None:
            self._agent = self._create_agent()
        return self._agent
    
    async def run(self, message: str, **kwargs) -> str:
        """Run the agent with a message."""
        try:
            result = await self.agent.run(task=message)
            return str(result)
        except Exception as e:
            import traceback
            error_msg = f"Error running agent {self.config.name}: {str(e)}\n{traceback.format_exc()}"
            print(error_msg)
            return error_msg
    
    async def close(self):
        """Close the model client connection."""
        if self._model_client:
            await self._model_client.close()


class AssistantAgentWrapper(BaseAgent):
    """Wrapper for AutoGen AssistantAgent."""
    
    def _create_agent(self) -> AssistantAgent:
        """Create an AutoGen AssistantAgent."""
        return AssistantAgent(
            name=self.config.name,
            model_client=self._get_model_client(),
            system_message=self.config.system_message,
        )


class UserProxyAgentWrapper(BaseAgent):
    """Wrapper for AutoGen UserProxyAgent."""
    
    def _create_agent(self) -> UserProxyAgent:
        """Create an AutoGen UserProxyAgent."""
        return UserProxyAgent(
            name=self.config.name,
            model_client=self._get_model_client(),
        )
