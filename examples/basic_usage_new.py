"""
Basic usage examples for the AutoGen FastAPI template.
"""
import asyncio
from agents.registry import AgentRegistry


async def basic_chat_example():
    """Example of basic chat interaction."""
    print("🤖 Basic Chat Example")
    print("-" * 50)
    
    # Get a chat agent
    agent = AgentRegistry.get_agent("chat")
    
    # Send a message
    response = await agent.run("Hello! Can you tell me about Python programming?")
    print(f"User: Hello! Can you tell me about Python programming?")
    print(f"Agent: {response}")
    
    # Clean up
    await agent.close()
    print()


async def research_example():
    """Example of research agent interaction."""
    print("🔍 Research Agent Example")
    print("-" * 50)
    
    # Get a research agent
    agent = AgentRegistry.get_agent("research")
    
    # Send a research request
    topic = "the impact of artificial intelligence on software development"
    response = await agent.run(f"Please research {topic}")
    print(f"Research Topic: {topic}")
    print(f"Research Results:\n{response}")
    
    # Clean up
    await agent.close()
    print()


async def sql_example():
    """Example of SQL agent interaction."""
    print("💾 SQL Agent Example")
    print("-" * 50)
    
    # Get a SQL agent
    agent = AgentRegistry.get_agent("sql")
    
    # Send a SQL request
    requirement = "Create a query to find all users who registered in the last 30 days"
    response = await agent.run(requirement)
    print(f"SQL Requirement: {requirement}")
    print(f"Generated SQL:\n{response}")
    
    # Clean up
    await agent.close()
    print()


async def main():
    """Run all examples."""
    print("🚀 AutoGen FastAPI Template - Basic Usage Examples")
    print("=" * 60)
    print()
    
    try:
        await basic_chat_example()
        await research_example()
        await sql_example()
        
        print("✅ All examples completed successfully!")
        
    except Exception as e:
        print(f"❌ Error running examples: {e}")


if __name__ == "__main__":
    asyncio.run(main())
