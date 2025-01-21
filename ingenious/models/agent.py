from pydantic import BaseModel
from ingenious.models.config import Config, ModelConfig
from typing import List, Optional


class Agent(BaseModel):
    """
    A class used to represent an Agent.

    Attributes
    ----------
    agent_name : str
        The name of the agent.
    model_name : str
        The name of the model associated with the agent. This should match the name of the associated model in config.yml
    agent_display_name : str
        The display name of the agent.
    agent_description : str
        A brief description of the agent.
    agent_type : str
        The type/category of the agent.
    """
    agent_name: str
    model_name: str
    agent_display_name: str
    agent_description: str
    agent_type: str
    model: Optional[ModelConfig] = None


class Agents(BaseModel):
    """
    A class used to represent a list of Agents.

    Attributes
    ----------
    agents : List[Agent]
        A list of Agent objects.
    """

    _agents: List[Agent]

    def __init__(self, agents: List[Agent], config: Config):
        self.super().__init__()
        self.agents = agents       
        for agent in self.agents:
            for model in config.models:
                if model.model == agent.model_name:
                    agent.model = model
                    break
        if not agent.model:
            raise ValueError(f"Model {agent.model_name} not found in config.yml")
        
    def get_agents(self):
        return self.agents