# Advanced Scenarios

This document provides examples of advanced usage scenarios for the Insight Ingenious application.

## Multi-Agent Workflows

Combining multiple agents to create complex workflows:

```python
import asyncio
from agents.registry import AgentRegistry
from typing import List, Dict

async def research_and_summarize(topic: str) -> Dict[str, str]:
    """
    Research a topic and generate a summary, recommendations, and key insights.
    
    Args:
        topic: The topic to research
        
    Returns:
        Dictionary containing research results, summary, recommendations, and insights
    """
    # Get agents
    research_agent = AgentRegistry.get_agent("research")
    chat_agent = AgentRegistry.get_agent("chat")
    
    # Step 1: Research the topic
    research_prompt = f"Research the following topic in detail: {topic}"
    research_results = await research_agent.run(research_prompt)
    
    # Step 2: Generate a summary
    summary_prompt = f"Summarize the following research in 3-5 paragraphs:\n\n{research_results}"
    summary = await chat_agent.run(summary_prompt)
    
    # Step 3: Generate recommendations
    recommendations_prompt = f"Based on this research, provide 5 practical recommendations:\n\n{research_results}"
    recommendations = await chat_agent.run(recommendations_prompt)
    
    # Step 4: Extract key insights
    insights_prompt = f"Extract 3-5 key insights from this research:\n\n{research_results}"
    insights = await chat_agent.run(insights_prompt)
    
    # Clean up
    await research_agent.close()
    await chat_agent.close()
    
    return {
        "research": research_results,
        "summary": summary,
        "recommendations": recommendations,
        "insights": insights
    }

# Example usage
async def demo_research_workflow():
    topic = "sustainable energy solutions for developing countries"
    results = await research_and_summarize(topic)
    
    print(f"TOPIC: {topic}\n")
    print(f"SUMMARY:\n{results['summary']}\n")
    print(f"RECOMMENDATIONS:\n{results['recommendations']}\n")
    print(f"KEY INSIGHTS:\n{results['insights']}\n")

if __name__ == "__main__":
    asyncio.run(demo_research_workflow())
```

## Agent Chains with Intermediate Processing

Creating agent chains with custom processing between steps:

```python
import asyncio
from agents.registry import AgentRegistry
import re
from typing import List, Dict, Any

def extract_data_points(text: str) -> List[str]:
    """Extract structured data points from text."""
    # This is a simplified example - in a real application,
    # you might use more sophisticated NLP techniques
    data_points = []
    lines = text.split("\n")
    for line in lines:
        line = line.strip()
        if line and not line.startswith("#") and ":" in line:
            data_points.append(line)
    return data_points

def categorize_points(data_points: List[str]) -> Dict[str, List[str]]:
    """Categorize data points into groups."""
    categories = {
        "economic": [],
        "environmental": [],
        "social": [],
        "technical": [],
        "other": []
    }
    
    keywords = {
        "economic": ["cost", "price", "economy", "financial", "market", "investment"],
        "environmental": ["environment", "climate", "pollution", "emission", "sustainable"],
        "social": ["community", "people", "social", "cultural", "education", "health"],
        "technical": ["technology", "efficiency", "system", "design", "implementation"]
    }
    
    for point in data_points:
        categorized = False
        for category, terms in keywords.items():
            if any(term in point.lower() for term in terms):
                categories[category].append(point)
                categorized = True
                break
        
        if not categorized:
            categories["other"].append(point)
    
    return categories

async def advanced_analysis_workflow(topic: str) -> Dict[str, Any]:
    """
    Advanced analysis workflow with intermediate processing.
    
    Args:
        topic: The topic to analyze
        
    Returns:
        Dictionary containing analysis results
    """
    # Get agents
    research_agent = AgentRegistry.get_agent("research")
    analysis_agent = AgentRegistry.get_agent("chat")
    sql_agent = AgentRegistry.get_agent("sql")
    
    # Step 1: Initial research
    research_prompt = f"Research {topic} and list key data points in a structured format with each point on a new line."
    research_results = await research_agent.run(research_prompt)
    
    # Step 2: Extract and categorize data points
    data_points = extract_data_points(research_results)
    categories = categorize_points(data_points)
    
    # Step 3: Generate analysis for each category
    analysis_results = {}
    for category, points in categories.items():
        if points:
            points_text = "\n".join(points)
            analysis_prompt = f"Analyze these {category} factors related to {topic}:\n\n{points_text}"
            analysis_results[category] = await analysis_agent.run(analysis_prompt)
    
    # Step 4: Generate data model for storing results
    data_model_prompt = f"Create a SQL schema to store analysis results for {topic} with these categories: {', '.join(categories.keys())}"
    data_model = await sql_agent.run(data_model_prompt)
    
    # Clean up
    await research_agent.close()
    await analysis_agent.close()
    await sql_agent.close()
    
    return {
        "topic": topic,
        "data_points": data_points,
        "categories": categories,
        "analysis": analysis_results,
        "data_model": data_model
    }

# Example usage
async def demo_advanced_workflow():
    topic = "electric vehicle adoption in urban areas"
    results = await advanced_analysis_workflow(topic)
    
    print(f"TOPIC: {topic}\n")
    print(f"TOTAL DATA POINTS: {len(results['data_points'])}\n")
    
    for category, analysis in results['analysis'].items():
        print(f"{category.upper()} ANALYSIS ({len(results['categories'][category])} points):")
        print(f"{analysis}\n")
    
    print(f"DATA MODEL:\n{results['data_model']}")

if __name__ == "__main__":
    asyncio.run(demo_advanced_workflow())
```

## Custom Agent with Tool Capabilities

Creating an agent with specialized tool capabilities:

```python
import asyncio
import json
from typing import Dict, Any, List, Optional, Callable
from openai import AzureOpenAI
from agents.base import BaseAgent, AgentConfig
from agents.registry import register_agent
from core.logging import get_logger

logger = get_logger(__name__)

class ToolAgent(BaseAgent):
    """Custom agent with tool capabilities."""
    
    def __init__(self, name="tool_assistant"):
        config = AgentConfig(
            name=name,
            description="An assistant with tool capabilities",
            system_message="""You are an AI assistant with the ability to use tools.
            When you need to use a tool, use the exact format:
            
            TOOL_CALL: <tool_name>
            <tool_parameters_as_json>
            
            Wait for the tool response before continuing.""",
            model="gpt-4.1-mini",
            temperature=0.5,
        )
        super().__init__(config)
        self._client = None
        self._tools = {}
    
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
    
    def register_tool(self, name: str, description: str, function: Callable):
        """Register a tool that the agent can use."""
        self._tools[name] = {
            "description": description,
            "function": function
        }
    
    def _extract_tool_calls(self, text: str) -> List[Dict[str, Any]]:
        """Extract tool calls from the response text."""
        tool_calls = []
        
        # Find all tool calls in the format:
        # TOOL_CALL: <tool_name>
        # <tool_parameters_as_json>
        import re
        pattern = r"TOOL_CALL: (\w+)\n([\s\S]+?)(?=TOOL_CALL:|$)"
        matches = re.finditer(pattern, text)
        
        for match in matches:
            tool_name = match.group(1)
            params_text = match.group(2).strip()
            
            try:
                # Parse parameters as JSON
                params = json.loads(params_text)
                
                tool_calls.append({
                    "tool": tool_name,
                    "parameters": params
                })
            except json.JSONDecodeError:
                logger.error(f"Failed to parse tool parameters: {params_text}")
        
        return tool_calls
    
    async def _execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> str:
        """Execute a tool and return the result."""
        if tool_name not in self._tools:
            return f"Error: Tool '{tool_name}' not found."
        
        try:
            result = await self._tools[tool_name]["function"](**parameters)
            return f"TOOL_RESULT: {tool_name}\n{json.dumps(result, indent=2)}"
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {str(e)}")
            return f"Error executing tool {tool_name}: {str(e)}"
    
    async def run(self, message: str, **kwargs) -> str:
        """Run the agent with a message."""
        try:
            client = self._get_client()
            
            # Start with user message
            messages = [
                {"role": "system", "content": self.config.system_message},
                {"role": "user", "content": message}
            ]
            
            # Maximum number of tool call iterations
            max_iterations = 5
            iterations = 0
            
            while iterations < max_iterations:
                # Get response
                response = client.chat.completions.create(
                    model=self.config.model,
                    messages=messages,
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens or 1000
                )
                
                response_text = response.choices[0].message.content.strip()
                
                # Check for tool calls
                tool_calls = self._extract_tool_calls(response_text)
                
                # If no tool calls, we're done
                if not tool_calls:
                    return response_text
                
                # Execute tools and add results to messages
                messages.append({"role": "assistant", "content": response_text})
                
                for tool_call in tool_calls:
                    tool_result = await self._execute_tool(tool_call["tool"], tool_call["parameters"])
                    messages.append({"role": "user", "content": tool_result})
                
                iterations += 1
            
            # If we reach here, we've hit the maximum iterations
            return response_text
        
        except Exception as e:
            logger.error(f"Error in tool agent: {str(e)}")
            return f"Error: {str(e)}"
    
    async def close(self):
        """Clean up resources."""
        self._client = None

# Example tools
async def weather_tool(location: str) -> Dict[str, Any]:
    """Simulate getting weather data for a location."""
    # In a real implementation, this would call a weather API
    import random
    conditions = ["sunny", "cloudy", "rainy", "snowy"]
    return {
        "location": location,
        "temperature": random.randint(0, 30),
        "condition": random.choice(conditions),
        "humidity": random.randint(30, 90)
    }

async def calculator_tool(operation: str, x: float, y: float) -> Dict[str, Any]:
    """Perform a mathematical operation."""
    result = None
    if operation == "add":
        result = x + y
    elif operation == "subtract":
        result = x - y
    elif operation == "multiply":
        result = x * y
    elif operation == "divide":
        if y == 0:
            return {"error": "Division by zero"}
        result = x / y
    else:
        return {"error": f"Unknown operation: {operation}"}
    
    return {
        "operation": operation,
        "x": x,
        "y": y,
        "result": result
    }

# Example usage
async def demo_tool_agent():
    # Create and register the agent
    agent = ToolAgent()
    agent.register_tool("weather", "Get weather information for a location", weather_tool)
    agent.register_tool("calculator", "Perform mathematical calculations", calculator_tool)
    
    # Register with the global registry
    register_agent("tool", lambda: agent)
    
    # Example queries
    queries = [
        "What's the weather like in New York?",
        "Can you calculate 15 multiplied by 7?",
        "First tell me the weather in Tokyo, then calculate 25 divided by 5."
    ]
    
    for query in queries:
        print(f"QUERY: {query}")
        response = await agent.run(query)
        print(f"RESPONSE:\n{response}\n")
    
    # Clean up
    await agent.close()

if __name__ == "__main__":
    asyncio.run(demo_tool_agent())
```

## Batch Processing with Agents

Processing a batch of items with agents:

```python
import asyncio
from agents.registry import AgentRegistry
from typing import List, Dict, Any
import json

async def process_batch(items: List[Dict[str, Any]], agent_type: str, prompt_template: str) -> List[Dict[str, Any]]:
    """
    Process a batch of items using an agent.
    
    Args:
        items: List of items to process
        agent_type: Type of agent to use
        prompt_template: Template for generating prompts
        
    Returns:
        List of items with results added
    """
    # Get agent
    agent = AgentRegistry.get_agent(agent_type)
    
    # Process items
    results = []
    for item in items:
        # Generate prompt
        prompt = prompt_template.format(**item)
        
        # Process with agent
        response = await agent.run(prompt)
        
        # Add result to item
        item_with_result = item.copy()
        item_with_result["result"] = response
        results.append(item_with_result)
    
    # Clean up
    await agent.close()
    
    return results

# Example usage
async def demo_batch_processing():
    # Example batch of customer feedback
    feedback_items = [
        {"id": 1, "customer": "John", "feedback": "The product is great but shipping took too long."},
        {"id": 2, "customer": "Sarah", "feedback": "Customer service was excellent! Very helpful."},
        {"id": 3, "customer": "Mike", "feedback": "The app crashes whenever I try to upload photos."},
        {"id": 4, "customer": "Lisa", "feedback": "Pricing is a bit high compared to competitors."}
    ]
    
    # Prompt template
    prompt_template = """
    Analyze the following customer feedback and provide:
    1. Sentiment (positive, negative, or neutral)
    2. Main topics/concerns
    3. Suggested action items
    
    Feedback: "{feedback}"
    
    Format your response as JSON with keys: sentiment, topics, actions
    """
    
    # Process batch
    results = await process_batch(feedback_items, "chat", prompt_template)
    
    # Display results
    print("BATCH PROCESSING RESULTS:")
    for item in results:
        print(f"\nCUSTOMER: {item['customer']} (ID: {item['id']})")
        print(f"FEEDBACK: {item['feedback']}")
        print(f"ANALYSIS: {item['result']}")
        
        # Try to parse JSON from result
        try:
            analysis = json.loads(item['result'])
            print(f"SENTIMENT: {analysis.get('sentiment', 'N/A')}")
            print(f"TOPICS: {', '.join(analysis.get('topics', []))}")
            print(f"ACTIONS: {', '.join(analysis.get('actions', []))}")
        except:
            pass

if __name__ == "__main__":
    asyncio.run(demo_batch_processing())
```

## Dynamic Agent Selection

Dynamically selecting the most appropriate agent for a task:

```python
import asyncio
from agents.registry import AgentRegistry
from typing import Dict, Any, List

async def route_query(query: str) -> Dict[str, Any]:
    """
    Route a query to the most appropriate agent.
    
    Args:
        query: The user query
        
    Returns:
        Dictionary with routing decision and response
    """
    # Get a router agent (using chat agent for classification)
    router = AgentRegistry.get_agent("chat")
    
    # Define agent types and their capabilities
    agent_types = {
        "chat": "General questions, conversations, explanations",
        "research": "In-depth research, information gathering, analysis",
        "sql": "Database queries, SQL generation, data analysis",
    }
    
    # Create a prompt to determine the best agent
    agent_descriptions = "\n".join([f"- {name}: {desc}" for name, desc in agent_types.items()])
    routing_prompt = f"""
    Classify the following query and determine which agent would be best suited to handle it.
    Available agents:
    {agent_descriptions}
    
    Query: "{query}"
    
    Respond with just the agent name (chat, research, or sql) that is most appropriate.
    """
    
    # Get routing decision
    agent_type = await router.run(routing_prompt)
    agent_type = agent_type.strip().lower()
    
    # Clean up router
    await router.close()
    
    # Validate agent type
    valid_types = list(agent_types.keys())
    if agent_type not in valid_types:
        agent_type = "chat"  # Default to chat if invalid
    
    # Get the appropriate agent
    agent = AgentRegistry.get_agent(agent_type)
    
    # Process query with selected agent
    response = await agent.run(query)
    
    # Clean up
    await agent.close()
    
    return {
        "query": query,
        "selected_agent": agent_type,
        "response": response
    }

# Example usage
async def demo_dynamic_routing():
    queries = [
        "What is the capital of France?",
        "Research the impact of artificial intelligence on education",
        "Create a SQL query to find all customers who made a purchase in the last 30 days",
        "How does photosynthesis work?",
        "Analyze the trends in renewable energy adoption worldwide"
    ]
    
    for query in queries:
        result = await route_query(query)
        print(f"\nQUERY: {query}")
        print(f"ROUTED TO: {result['selected_agent']}")
        print(f"RESPONSE: {result['response'][:150]}...")  # Truncate long responses

if __name__ == "__main__":
    asyncio.run(demo_dynamic_routing())
```
