"""
SQL agent example using Azure OpenAI directly.
"""
from typing import Dict, Any, Optional
from openai import AzureOpenAI
from agents.base import BaseAgent, AgentConfig
from core.logging import get_logger


class SQLAgent(BaseAgent):
    """An agent specialized for SQL query generation and database tasks using Azure OpenAI directly."""
    
    def __init__(self, name: str = "sql_assistant"):
        config = AgentConfig(
            name=name,
            description="A SQL specialist for database queries and operations",
            system_message="""You are a SQL expert specializing in database queries, optimization, and data analysis.

When asked to work with SQL:
1. Generate clean, efficient, and well-commented SQL queries
2. Consider performance and best practices
3. Explain the logic behind complex queries
4. Suggest optimizations when applicable
5. Handle different SQL dialects appropriately (specify which one you're using)

Always prioritize data security and proper SQL practices to prevent injection attacks.""",
            model="gpt-4.1-mini",  # Using a model available in Azure OpenAI
            temperature=0.1,  # Very low temperature for precise SQL generation
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
                max_tokens=1500,
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
    
    async def generate_query(self, requirement: str, schema_info: str = "") -> str:
        """Generate a SQL query based on requirements."""
        prompt = f"""Given the following requirement: {requirement}

{f"Schema information: {schema_info}" if schema_info else ""}

Please generate a SQL query that:
1. Meets the specified requirements
2. Follows best practices
3. Includes helpful comments
4. Is optimized for performance

Provide the query along with a brief explanation of the logic."""
        
        return await self.run(prompt)
    
    async def optimize_query(self, query: str) -> str:
        """Optimize an existing SQL query."""
        prompt = f"""Please analyze and optimize the following SQL query:

{query}

Provide:
1. An optimized version of the query
2. Explanation of the optimizations made
3. Performance considerations
4. Any potential issues or improvements"""
        
        return await self.run(prompt)
        
    async def close(self):
        """Close the model client connection."""
        pass  # No need to close the client
