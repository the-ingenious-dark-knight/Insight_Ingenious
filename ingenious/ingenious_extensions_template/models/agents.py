from typing import List
from ingenious.models.agent import Agent, Agents
from pydantic import BaseModel
from ingenious.models.config import Config

class SampleAgents(Agents):
    """
    A class used to represent a your sample list of agents.

    Attributes
    ----------
    agents : List[Agent]
        A list of Agent objects.
    """

    def __init__(self, config: Config):        
        local_agents = []
        local_agents.append(
            Agent(
                agent_name="customer_sentiment_agent",
                model_name="gpt-4o",
                agent_display_name="Customer Sentiment",
                agent_description="A sample agent.",
                agent_type="researcher",
            )
        )
        local_agents.append(
            Agent(
                agent_name="fiscal_analysis_agent",
                model_name="gpt-4o",
                agent_display_name="Fiscal Analysis",
                agent_description="A sample agent.",
                agent_type="researcher",
            )
        )
        local_agents.append(
            Agent(
                agent_name="summary_agent",
                model_name="gpt-4o",
                agent_display_name="Summarizer",
                agent_description="A sample agent.",
                agent_type="summary",
            )
        )

        self.super().__init__(local_agents, config)
            
