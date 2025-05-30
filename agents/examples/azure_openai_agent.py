"""
Custom Azure OpenAI agent that uses the direct client that works in our test script.
"""
from typing import Dict, Any, Optional, List
import asyncio
from openai import AzureOpenAI
from agents.base import BaseAgent, AgentConfig
from core.logging import get_logger


class AzureOpenAIAgent(BaseAgent):
    """A simple conversational agent using Azure OpenAI directly."""
    
    def __init__(self, name: str = "azure_chat_assistant"):
        config = AgentConfig(
            name=name,
            description="A helpful conversational assistant using Azure OpenAI",
            system_message="You are a helpful and friendly conversational assistant. Respond naturally and helpfully to user queries.",
            model="gpt-4.1-mini",
            temperature=0.7,
        )
        super().__init__(config)
        self._client = None
        
    def _get_client(self):
        """Get the Azure OpenAI client."""
        if self._client is None:
            config = self._get_model_config()
            self._client = AzureOpenAI(
                api_version=config.api_version,
                azure_endpoint=config.base_url,
                api_key=config.api_key,
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
            deployment = self.config.model
            
            response = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": self.config.system_message,
                    },
                    {
                        "role": "user",
                        "content": message,
                    }
                ],
                max_tokens=1000,
                temperature=self.config.temperature,
                model=deployment
            )
            
            return response.choices[0].message.content
        except Exception as e:
            import traceback
            error_msg = f"Error running agent {self.config.name}: {str(e)}\n{traceback.format_exc()}"
            # Log error using logging instead of print
            logger = get_logger()
            logger.error(error_msg)
            return error_msg
    
    async def chat(self, message: str) -> str:
        """Simple chat interface."""
        return await self.run(message)
        
    async def close(self):
        """Close the model client connection."""
        pass  # No need to close the client
