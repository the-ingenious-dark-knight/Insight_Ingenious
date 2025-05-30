"""
Agent registry for managing available agents.
"""
from typing import Dict, Type, List, Optional
from agents.base import BaseAgent
from agents.examples.chat_agent import ChatAgent
from agents.examples.research_agent import ResearchAgent
from agents.examples.sql_agent import SQLAgent
from agents.examples.azure_openai_agent import AzureOpenAIAgent


class AgentRegistry:
    """Registry for all available agents."""
    
    _agents: Dict[str, Type[BaseAgent]] = {
        "chat": ChatAgent,
        "research": ResearchAgent,
        "sql": SQLAgent,
        "azure": AzureOpenAIAgent,
    }
    
    _instances: Dict[str, BaseAgent] = {}
    
    @classmethod
    def get_agent(cls, agent_type: str, name: str = None) -> BaseAgent:
        """Get an agent instance by type."""
        if agent_type not in cls._agents:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        agent_class = cls._agents[agent_type]
        if name:
            instance_key = f"{agent_type}:{name}"
            if instance_key not in cls._instances:
                cls._instances[instance_key] = agent_class(name=name)
            return cls._instances[instance_key]
        else:
            instance_key = f"{agent_type}:default"
            if instance_key not in cls._instances:
                cls._instances[instance_key] = agent_class()
            return cls._instances[instance_key]
    
    @classmethod
    def list_agents(cls) -> List[str]:
        """List all available agent types."""
        return list(cls._agents.keys())
    
    @classmethod
    def list_agent_instances(cls) -> List[str]:
        """List all agent instances."""
        return list(cls._instances.keys())
    
    @classmethod
    def register_agent(cls, agent_type: str, agent_class: Type[BaseAgent]):
        """Register a new agent type."""
        cls._agents[agent_type] = agent_class
    
    @classmethod
    def create_agent(cls, agent_type: str, name: str) -> BaseAgent:
        """Create a new agent instance and register it."""
        return cls.get_agent(agent_type, name)


# Accessor function for compatibility
def get_agent_registry() -> AgentRegistry:
    """Get the agent registry."""
    return AgentRegistry


# Helper function for registering agents
def register_agent(agent_type: str, agent_class: Type[BaseAgent]):
    """Register a new agent type."""
    AgentRegistry.register_agent(agent_type, agent_class)
