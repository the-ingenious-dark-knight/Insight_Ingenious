from typing import List
from ingenious.models.agent import Agent, AgentChat, AgentChats, Agents
from pydantic import BaseModel
from ingenious.models.config import Config


class ProjectAgents(Agents):
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
                agent_model_name="gpt-4o",
                agent_display_name="Customer Sentiment",
                agent_description="A sample agent.",
                agent_type="researcher",
            )
        )
        local_agents.append(
            Agent(
                agent_name="fiscal_analysis_agent",
                agent_model_name="gpt-4o",
                agent_display_name="Fiscal Analysis",
                agent_description="A sample agent.",
                agent_type="researcher",
            )
        )
        local_agents.append(
            Agent(
                agent_name="summary_agent",
                agent_model_name="gpt-4o",
                agent_display_name="Summarizer",
                agent_description="A sample agent.",
                agent_type="summary",
            )
        )

        super().__init__(local_agents, config)
            

class ProjectAgentChats(AgentChats):
    """
    A class used to represent a list of agent chats.

    Attributes
    ----------
    agent_chats : List[AgentChat]
        A list of AgentChat objects.
    """

    _local_agent_chats: AgentChats

    def __init__(self, config: Config):
        local_agent_chats = []
        local_agent_chats.append(
            AgentChat(
                agent_name="customer_sentiment_agent",
                chat_name="customer_sentiment_chat",
                user_message="To Be Populated",
                system_prompt="To Be Populated",
                chat_response="To Be Populated"
            )
        )
        local_agent_chats.append(
            AgentChat(
                agent_name="fiscal_analysis_agent",
                chat_name="fiscal_analysis_chat",
                user_message="To Be Populated",
                system_prompt="To Be Populated",
                chat_response="To Be Populated"
            )
        )
        local_agent_chats.append(
            AgentChat(
                agent_name="user_proxy",
                chat_name="user_proxy_chat",
                user_message="To Be Populated",
                system_prompt="To Be Populated",
                chat_response="To Be Populated",
                log_to_prompt_tuner=False,
                return_in_response=False
            )
        )
        local_agent_chats.append(
            AgentChat(
                agent_name="summary_agent",
                chat_name="summary_chat",
                user_message="To Be Populated",
                system_prompt="To Be Populated",
                chat_response="To Be Populated",
                log_to_prompt_tuner=True,
                return_in_response=True
            )
        )