# Basic Usage Examples

This document provides examples of basic usage of the Insight Ingenious application.

## Running the Examples

All examples should be run using `uv`:

```bash
uv run python -m examples.basic_usage
```

## Basic Chat Example

The simplest way to use the application is to interact with the chat agent:

```python
from agents.registry import AgentRegistry

async def basic_chat_example():
    """Example of basic chat interaction."""
    # Get a chat agent
    agent = AgentRegistry.get_agent("chat")
    
    # Send a message
    response = await agent.run("Hello! Can you tell me about Python programming?")
    print(f"User: Hello! Can you tell me about Python programming?")
    print(f"Agent: {response}")
    
    # Clean up
    await agent.close()
```

## Research Agent Example

For research and information gathering:

```python
async def research_example():
    """Example of research agent interaction."""
    # Get a research agent
    agent = AgentRegistry.get_agent("research")
    
    # Send a research request
    topic = "the impact of artificial intelligence on software development"
    response = await agent.run(f"Please research {topic}")
    print(f"Research Topic: {topic}")
    print(f"Research Results:\n{response}")
    
    # Clean up
    await agent.close()
```

## SQL Agent Example

For SQL query generation:

```python
async def sql_example():
    """Example of SQL agent interaction."""
    # Get a SQL agent
    agent = AgentRegistry.get_agent("sql")
    
    # Send a SQL request
    requirement = "Create a query to find all users who registered in the last 30 days"
    response = await agent.run(requirement)
    print(f"SQL Requirement: {requirement}")
    print(f"Generated SQL:\n{response}")
    
    # Clean up
    await agent.close()
```

## Combining Multiple Agents

You can use multiple agents together:

```python
async def multi_agent_example():
    """Example of using multiple agents together."""
    # Get a research agent
    research_agent = AgentRegistry.get_agent("research")
    
    # Get a chat agent
    chat_agent = AgentRegistry.get_agent("chat")
    
    # Research a topic
    topic = "the latest advancements in renewable energy"
    research_results = await research_agent.run(f"Please research {topic}")
    
    # Ask the chat agent to summarize
    summary = await chat_agent.run(f"Summarize this research in 3 bullet points: {research_results}")
    
    print(f"Research Topic: {topic}")
    print(f"Summary:\n{summary}")
    
    # Clean up
    await research_agent.close()
    await chat_agent.close()
```

## Error Handling

It's important to handle errors properly:

```python
async def error_handling_example():
    """Example of error handling."""
    try:
        # Get a chat agent
        agent = AgentRegistry.get_agent("nonexistent_agent")
        
        # This will not be reached if the agent type doesn't exist
        response = await agent.run("Hello!")
        print(f"Response: {response}")
        
        # Clean up
        await agent.close()
    except ValueError as e:
        print(f"Error: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
```

## Complete Example

Here's a complete example that demonstrates basic usage:

```python
import asyncio
from agents.registry import AgentRegistry

async def main():
    # Chat example
    await basic_chat_example()
    
    # Research example
    await research_example()
    
    # SQL example
    await sql_example()

if __name__ == "__main__":
    asyncio.run(main())
```

Save this as `my_example.py` and run:

```bash
uv run python my_example.py
```
