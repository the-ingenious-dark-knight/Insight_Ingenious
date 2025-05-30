"""
Example: Creating Custom Agents

This example demonstrates how to create custom agents by extending the BaseAgent class.
"""

from typing import Dict, Any, Optional
from openai import AzureOpenAI
from agents.base import BaseAgent, AgentConfig
from agents.registry import register_agent
from core.logging import get_logger


class MathAgent(BaseAgent):
    """
    Custom agent that specializes in mathematical calculations and explanations.
    
    This agent demonstrates how to create a specialized agent with custom
    system prompts and specific capabilities.
    """
    
    def __init__(self, name="math_assistant"):
        config = AgentConfig(
            name=name,
            description="Mathematical expert and tutor",
            system_message="""You are a mathematical expert and tutor. Your specialties include:

1. Solving mathematical problems step-by-step
2. Explaining mathematical concepts clearly
3. Helping with calculations from basic arithmetic to advanced calculus
4. Providing mathematical proofs and derivations
5. Converting between different mathematical notations

Always show your work and explain your reasoning. If a problem is complex, break it down into smaller steps.""",
            model="gpt-4.1-mini",  # Using a model available in Azure OpenAI
            temperature=0.2,  # Lower temperature for more precise math
        )
        super().__init__(config)
        self._client = None
        self.logger = get_logger()
        
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
                max_tokens=1500,
                temperature=self.config.temperature,
                model=deployment
            )
            
            return response.choices[0].message.content
        except Exception as e:
            import traceback
            error_msg = f"Error running agent {self.config.name}: {str(e)}\n{traceback.format_exc()}"
            self.logger.error(error_msg)
            return error_msg
    
    async def chat(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Handle mathematical queries and problems.
        
        Args:
            message: Mathematical question or problem
            context: Optional context
            
        Returns:
            Mathematical solution with explanation
        """
        try:
            self.logger.info("Processing math query", extra={"message_length": len(message)})
            
            # Enhance the prompt with mathematical context
            math_prompt = f"""Please solve this mathematical problem or answer this mathematical question:

{message}

Please:
1. Show all steps in your solution
2. Explain your reasoning
3. Double-check your work
4. If applicable, provide alternative approaches
"""
            
            return await self.run(math_prompt)
            
        except Exception as e:
            self.logger.error(f"Error in math agent: {e}")
            return "I encountered an error while solving this mathematical problem. Please try rephrasing your question."
    
    async def close(self):
        """Close the model client connection."""
        pass  # No need to close the client


class WritingAgent(BaseAgent):
    """
    Custom agent that specializes in writing assistance and content creation.
    
    This agent demonstrates how to create an agent with specialized writing capabilities.
    """
    
    def __init__(self, name="writing_assistant"):
        config = AgentConfig(
            name=name,
            description="Writing assistant and content creator",
            system_message="""You are an expert writing coach, editor, and creative content writer. Your role is to:

1. Help improve writing clarity, style, and structure
2. Provide constructive feedback on content
3. Generate original, engaging content
4. Adapt tone and style to match requirements
5. Create compelling narratives and descriptions
6. Help with brainstorming and idea development
7. Ensure content is well-structured and purposeful

You are encouraging, constructive, and always provide specific, actionable feedback. You are creative, versatile, and always aim to produce high-quality, original content.""",
            model="gpt-4.1-mini",  # Using a model available in Azure OpenAI
            temperature=0.7,  # Higher temperature for creative writing
        )
        super().__init__(config)
        self._client = None
        self.logger = get_logger()
        
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
                max_tokens=2000,  # Increased for writing content
                temperature=self.config.temperature,
                model=deployment
            )
            
            return response.choices[0].message.content
        except Exception as e:
            import traceback
            error_msg = f"Error running agent {self.config.name}: {str(e)}\n{traceback.format_exc()}"
            self.logger.error(error_msg)
            return error_msg
    
    async def chat(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Handle writing assistance requests.
        
        Args:
            message: Writing request or content to review
            context: Optional context (writing type, audience, etc.)
            
        Returns:
            Writing assistance response
        """
        try:
            self.logger.info("Processing writing request", extra={"message_length": len(message)})
            
            # Determine the type of writing assistance needed
            writing_prompt = f"""I need help with writing. Here's my request:

{message}

Please provide appropriate help (editing, creation, feedback, etc.) with:
1. Specific, actionable advice
2. Clear explanations for any suggestions
3. Examples or alternatives where helpful
"""
            
            return await self.run(writing_prompt)
            
        except Exception as e:
            self.logger.error(f"Error in writing agent: {e}")
            return "I encountered an error while helping with your writing. Please try again."
    
    async def close(self):
        """Close the model client connection."""
        pass  # No need to close the client


def register_custom_agents():
    """Register the custom agents with the global registry."""
    register_agent("math", MathAgent)
    register_agent("writing", WritingAgent)


def demo_custom_agents():
    """Demonstrate the custom agents."""
    from agents.registry import get_agent_registry
    
    # Register the custom agents
    register_custom_agents()
    
    registry = get_agent_registry()
    
    # Create instances of the custom agents
    print("Creating custom agents...")
    
    math_agent = registry.create_agent("math", "my_math_tutor")
    writing_agent = registry.create_agent("writing", "my_writing_assistant")
    
    print(f"Created agents: {registry.list_agent_instances()}")
    
    # Note: Actually running these would require Azure OpenAI API keys
    # In a real scenario, you would run:
    
    # Math example
    # math_response = await math_agent.chat("What is the derivative of x^3 + 2x^2 - 5x + 1?")
    # print(f"Math Agent: {math_response}")
    
    # Writing example  
    # writing_response = await writing_agent.chat("Can you help me write a professional email to request a meeting with my manager?")
    # print(f"Writing Agent: {writing_response}")
    
    print("Custom agents are ready for use!")


if __name__ == "__main__":
    demo_custom_agents()
