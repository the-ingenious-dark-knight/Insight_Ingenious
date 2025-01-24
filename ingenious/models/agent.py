from abc import ABC, abstractmethod
import asyncio
from autogen_core import MessageContext
from pydantic import BaseModel
from ingenious.models.config import Config, ModelConfig
from typing import List, Optional
import logging
from autogen_core.logging import LLMCallEvent



class AgentChat(BaseModel):
    """
    A class used to represent a chat between an agent and a user or between agents

    Attributes
    ----------
    agent_name : str
        The name of the agent.
    user_message : str
        The message sent by the user.
    system_prompt : str
        The message sent by the agent.
    """
    chat_name: str
    target_agent_name: str
    source_agent_name: str
    user_message: str
    system_prompt: str
    chat_response: str


class AgentChats(BaseModel):
    """
    A class used to represent a list of AgentChats.

    Attributes
    ----------
    agent_chats : List[AgentChat]
        A list of AgentChat objects.
    """

    _agent_chats: List[AgentChat] = []

    def __init__(self):
        super().__init__()

    def add_agent_chat(self, agent_chat: AgentChat):
        self._agent_chats.append(agent_chat)

    def get_agent_chats(self):
        return self._agent_chats

    def get_agent_chat_by_name(self, agent_name: str) -> AgentChat:
        for agent_chat in self._agent_chats:
            if agent_chat.agent_name == agent_name:
                return agent_chat
        raise ValueError(f"AgentChat with name {agent_name} not found")
    
    def get_agent_chats_by_name(self, agent_name: str) -> List[AgentChat]:
        agent_chats = []
        for agent_chat in self._agent_chats:
            if agent_chat.agent_name == agent_name:
                agent_chats.append(agent_chat)
        return agent_chats



class Agent(BaseModel):
    """
    A class used to represent an Agent.

    Attributes
    ----------
    agent_name : str
        The name of the agent.
    agent_model_name : str
        The name of the model associated with the agent. This should match the name of the associated model in config.yml
    agent_display_name : str
        The display name of the agent.
    agent_description : str
        A brief description of the agent.
    agent_type : str
        The type/category of the agent.
    """
    agent_name: str
    agent_model_name: str
    agent_display_name: str
    agent_description: str
    agent_type: str
    model: Optional[ModelConfig] = None
    system_prompt: Optional[str] = None
    log_to_prompt_tuner: bool = True
    return_in_response: bool = False

    def get_agent_chat(self, content: str,  ctx: MessageContext):
        agent_chat: AgentChat = AgentChat(
            source_agent_name=ctx.topic_id.source,
            target_agent_name=self.agent_name,
            chat_name=self.agent_name + "",
            user_message=content,
            chat_response="UNDEFINED"
        )
        return agent_chat

    def log(self, agent_chat: AgentChat, queue: asyncio.Queue[AgentChat]):
        if self.log_to_prompt_tuner or self.return_in_response:
            queue.put(agent_chat)


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
        super().__init__()
        self._agents = agents       
        for agent in self._agents:
            for model in config.models:
                if model.model == agent.agent_model_name:
                    agent.model = model
                    break
        if not agent.model:
            raise ValueError(f"Model {agent.model_name} not found in config.yml")
        
    def get_agents(self):
        return self._agents
    
    def get_agent_by_name(self, agent_name: str) -> Agent:
        for agent in self._agents:
            if agent.agent_name == agent_name:
                return agent
        raise ValueError(f"Agent with name {agent_name} not found")
    
    

class AgentMessage(BaseModel):
    content: str


class LLMUsageTracker(logging.Handler):
    def __init__(self) -> None:
        """Logging handler that tracks the number of tokens used in the prompt and completion."""
        super().__init__()
        self._prompt_tokens = 0
        self._completion_tokens = 0

    @property
    def tokens(self) -> int:
        return self._prompt_tokens + self._completion_tokens

    @property
    def prompt_tokens(self) -> int:
        return self._prompt_tokens

    @property
    def completion_tokens(self) -> int:
        return self._completion_tokens

    def reset(self) -> None:
        self._prompt_tokens = 0
        self._completion_tokens = 0

    def emit(self, record: logging.LogRecord) -> None:
        """Emit the log record. To be used by the logging module."""
        try:
            # Use the StructuredMessage if the message is an instance of it
            if isinstance(record.msg, LLMCallEvent):
                event = record.msg
                self._prompt_tokens += event.prompt_tokens
                self._completion_tokens += event.completion_tokens
        except Exception:
            self.handleError(record)


class IProjectAgents(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def Get_Project_Agents(self, config: Config) -> Agents:
        pass
