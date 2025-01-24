import asyncio
from dataclasses import dataclass
import json
import os
from pathlib import Path
import time
from typing import List
from autogen_core import (
    CancellationToken,
    AgentId,
    ClosureAgent,
    ClosureContext,
    DefaultSubscription,
    DefaultTopicId,
    MessageContext,
    RoutedAgent,
    SingleThreadedAgentRuntime,
    TopicId,
    TypeSubscription,
    default_subscription,
    message_handler,
    type_subscription,
    TRACE_LOGGER_NAME,
    EVENT_LOGGER_NAME
)
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console

from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.base import Response
from jinja2 import Environment, FileSystemLoader
import jsonpickle
from ingenious.utils.namespace_utils import get_path_from_namespace_with_fallback
# Custom class import from ingenious_extensions 
from ingenious.services.chat_services.multi_agent.service import IConversationFlow
from ingenious.ingenious_extensions_template.models.agent import ProjectAgents
from ingenious.models.agent import AgentChat, Agent, AgentMessage, LLMUsageTracker, AgentChats
import logging


class ConversationFlow(IConversationFlow):
    async def get_conversation_response(
            self,
            message: str,
            thread_memory: str = '',
            memory_record_switch=True,
            thread_chat_history: list = [],
            event_type: str = None
    ) -> tuple[str, str]:
        
        # Logging for autogen
        logger = logging.getLogger(EVENT_LOGGER_NAME)
        logger.setLevel(logging.INFO)
        llm_usage = LLMUsageTracker()
        logger.handlers = [llm_usage]
        
        message = json.loads(message)
        #  Get your agents and agent chats from your custom class in models folder
        project_agents = ProjectAgents()
        agents = project_agents.Get_Project_Agents(self._config)

        # Note you can access llm models from the configuration array
        llm_config = self.Get_Models()[0]
        # Note the base IConversationFlow gives you a logger for logging purposes
        self._logger.debug("Starting Flow")

        # Now add your system prompts to your agents from the prompt templates
        # Modify this if you want to modfiy the pattern used to correlate the agent name to the prompt template
        for agent in agents.get_agents():
            template_name = f"{agent.agent_name}_prompt.jinja"
            agent.system_prompt = await self.Get_Template(file_name=template_name, revision_id=message['revision_id'])

        # Create wrappers around the autogen chat agent classes to allow routing of messages to the correct agents
        queue = asyncio.Queue[AgentChat]()

        ## Class for topic reasearcher agents
        @type_subscription(topic_type="researcher")
        class ReceivingAgent(RoutedAgent):
            def __init__(self, model_client: AzureOpenAIChatCompletionClient, assistant_agent: AssistantAgent, agent: Agent) -> None:
                super().__init__("DestinationAgent")
                model_client = model_client
                self._delegate = assistant_agent
                self._agent: Agent = agent
            
            @message_handler
            async def handle_my_message_type(self, message: AgentMessage, ctx: MessageContext) -> None:                  
                agent_chat = self._agent.get_agent_chat(content=message.content, ctx=ctx)
                agent_chat.chat_response = await self._delegate.on_messages(
                    [TextMessage(content=message.user_message, source="user")], ctx.cancellation_token
                )
                # Post the now complete incoming message into the queue if required
                # This is important if you want to log the message to the prompt tuner
                # It is also important if you want to return the message in the final response
                self._agent.log(agent_chat, queue)
                
                # Publish the outgoing message to the next agent
                await self.publish_message(
                    AgentMessage(content=agent_chat.chat_response),
                    topic_id=TopicId(type="user_proxy", source=self.id.key)
                )
        
        # # Class for agent that will relay messages to other agents without summarization
        @type_subscription(topic_type="user_proxy")
        class UserProxyAgent(RoutedAgent):
            _response_count: int = 0
            _agent: Agent
            _agent_message: AgentMessage

            def __init__(self) -> None:
                super().__init__("UserProxyAgent")
                self._agent = agents.get_agent_chat_by_name("user_proxy")
                self._agent_message = AgentMessage(content="")

            @message_handler
            async def handle_user_message(self, message: AgentMessage, ctx: MessageContext) -> None:
                self._response_count += 1
                self._agent_message.content += message.content + "\n"
                self._agent.get_agent_chat(content=message.content, ctx=MessageContext())
                self._agent.log(message, queue)

                if self._response_count >= 2:
                    await self.publish_message(
                        self._agent_message,
                        topic_id=TopicId(type="summary_agent", source=self.id.key)
                    )

        # # Class for agent that will receive responses from other agents and provide final insights
        @type_subscription(topic_type="summary_agent")
        class SummaryAgent(RoutedAgent):
            def __init__(self, model_client: AzureOpenAIChatCompletionClient, assistant_agent: AssistantAgent, agent: Agent) -> None:
                super().__init__("SummaryAgent")
                model_client = model_client
                self._delegate = assistant_agent
                self._agent: AgentChat = agent

            @message_handler
            async def handle_summary_message(self, message: AgentMessage, ctx: MessageContext) -> None:
                self._agent.get_agent_chat(content=message.content, ctx=ctx)
                self._agent.chat_response = await self._delegate.on_messages(
                    [TextMessage(content=message.content, source="summary_agent")], ctx.cancellation_token
                )
                self._agent.log(self._agent, queue)

        # Now construct your autogen conversation pattern the way you want
        # In this sample I'll first define my topic agents
        runtime = SingleThreadedAgentRuntime()
        ag_topic_agents = []
        for sub_agent in [f for f in agents.get_agents() if f.agent_type == "researcher"]:
            model_client = AzureOpenAIChatCompletionClient(**sub_agent.model.__dict__)
            assistant_agent = AssistantAgent(
                name=sub_agent.agent_name,
                system_message=sub_agent.system_prompt,
                description="I am an AI assistant that helps with research.",
                model_client=model_client
            )
            topic_agent = await ReceivingAgent.register(runtime, sub_agent.agent_name, lambda: ReceivingAgent(model_client=model_client, assistant_agent=assistant_agent, agent_chats=agent_chats))
            ag_topic_agents.append(topic_agent)

        await UserProxyAgent.register(runtime, "user_proxy", lambda: UserProxyAgent(agent_chat=agent_chats.get_agent_chat_by_name("user_proxy")))
        
        agent = agents.get_agent_by_name(agent_name="summary_agent")
        model_client = AzureOpenAIChatCompletionClient(**agent.model.__dict__)
        ag_summary_agent = AssistantAgent(
            name=agent.agent_name,
            system_message=agent.system_prompt,
            description="I collect and and present insights.",
            model_client=AzureOpenAIChatCompletionClient(**agent.model.__dict__)
        )

        await SummaryAgent.register(runtime, "summary_agent", lambda: SummaryAgent(model_client=model_client, assistant_agent=ag_summary_agent))

        topic_agent: AssistantAgent = ag_topic_agents[0]
        results = []
        tasks = []

        runtime.start()

        message: AgentChat = agent_chats.get_agent_chat_by_name("user_proxy")

        await runtime.publish_message(Message(json.dumps(message)), topic_id=TopicId(type="researcher", source="default"))
        await runtime.stop_when_idle()

        res = await queue.get()
        responses = (await asyncio.gather(*tasks))
        for i, response in enumerate(responses):
            response_object = Response(**response.__dict__)
            results.append(response_object.chat_message)
            
        sum_response = await ag_summary_agent.on_messages(
            messages=[
                TextMessage(
                    source=ag_topic_agents[0].name,                    
                    content="\n\n".join([response.chat_message.content for response in responses])
                )
            ],
            cancellation_token=CancellationToken()
        )

        results.append(sum_response.chat_message)

        response_array = []
        for i, chat_message in enumerate(results):
            chat_res = TextMessage(**chat_message.__dict__)
            print(f"*****{i}th chat*******:")
            print("\n\n")
            response_chat = {
                    "chat_number": {i},
                    "chat_title": chat_res.source,
                    "chat_response": chat_res.content,
                    "chat_input": message
            }
            response_array.append(response_chat)

        await self.write_llm_responses_to_file(
            response_array=response_array,
            event_type="default",
            revison_id=message['revision_id'],
            identifier=message['identifier']
        )

        return jsonpickle.encode(unpicklable=False, value=response_array), ""

