"""
Research agent example using Azure OpenAI directly.
"""
from typing import Dict, Any, Optional
from openai import AzureOpenAI
from agents.base import BaseAgent, AgentConfig
from core.logging import get_logger


class ResearchAgent(BaseAgent):
    """An agent specialized for research and analysis tasks using Azure OpenAI directly."""
    
    def __init__(self, name: str = "research_assistant"):
        config = AgentConfig(
            name=name,
            description="A research-focused assistant specialized in analysis and investigation",
            system_message="""You are a research specialist with expertise in gathering, analyzing, and synthesizing information.

When asked to research a topic, you should:
1. Break down the topic into key components
2. Identify the most important aspects to investigate
3. Provide structured, well-organized findings
4. Include relevant context and background information
5. Suggest additional areas for exploration if relevant

Always cite your reasoning and be transparent about limitations of the analysis.""",
            model="gpt-4.1-mini",  # Using a model available in Azure OpenAI
            temperature=0.3,  # Lower temperature for more focused research
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
                max_tokens=2000,  # Increased for research responses
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
    
    async def research(self, topic: str) -> str:
        """Conduct research on a given topic."""
        prompt = f"""Please research the following topic: {topic}

Provide a comprehensive analysis including:
- Key findings and main points
- Background context
- Current status or developments
- Potential implications or significance
- Any limitations or gaps in the analysis"""
        
        return await self.run(prompt)
        
    async def close(self):
        """Close the model client connection."""
        pass  # No need to close the client
