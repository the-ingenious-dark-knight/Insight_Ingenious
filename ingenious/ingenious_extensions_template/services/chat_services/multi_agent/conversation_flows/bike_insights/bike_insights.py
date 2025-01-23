import asyncio
from dataclasses import dataclass
import json
import os
from pathlib import Path
from typing import List
from autogen_core import (
    CancellationToken,
    AgentId,
    ClosureAgent,
    ClosureContext,
    DefaultTopicId,
    MessageContext,
    RoutedAgent,
    SingleThreadedAgentRuntime,
    TopicId,
    TypeSubscription,
    default_subscription,
    message_handler,
    type_subscription,
    TRACE_LOGGER_NAME
)
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
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
from ingenious.models.agent import AgentChat, Agent
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
        logging.basicConfig(level=logging.WARNING)
        logger = logging.getLogger(TRACE_LOGGER_NAME)
        logger.setLevel(logging.DEBUG)
        
        message = json.loads(message)
        #  Get your agents from your custom class in models folder
        agents = ProjectAgents(self._config)
        # Note you can access llm models from the configuration array
        llm_config = self.Get_Models()[0]
        # Note the base IConversationFlow gives you a logger for logging purposes
        self._logger.debug("Starting Flow")

        # Create a wrapper around an assistant agent to allow routing
        @dataclass
        class Message:
            content: str

        @type_subscription(topic_type="default")
        class ReceivingAgent(RoutedAgent):
            def __init__(self, model_client: AzureOpenAIChatCompletionClient, assistant_agent: AssistantAgent) -> None:
                super().__init__("DestinationAgent")
                model_client = model_client
                self._delegate = assistant_agent
            
            @message_handler
            async def handle_my_message_type(self, message: Message, ctx: MessageContext) -> None:               
                response = await self._delegate.on_messages(
                    [TextMessage(content=message, source="user")], ctx.cancellation_token
                )
               
                
        
        
        # Now add your system prompts to your agents from the prompt templates
        # Modify this if you want to modfiy the pattern used to correlate the agent name to the prompt template
        for agent in agents._agents:
            template_name = f"{agent.agent_name}_prompt.jinja"
            agent.system_prompt = await self.Get_Template(file_name=template_name, revision_id=message['revision_id'])
        
        # Now construct your autogen conversation pattern the way you want
        # In this sample I'll first define my topic agents
        ag_topic_agents = []
        for sub_agent in [f for f in agents.get_agents() if f.agent_type == "researcher"]: 
            model_client = AzureOpenAIChatCompletionClient(**sub_agent.model.__dict__)           
            assistant_agent = AssistantAgent(
                name=sub_agent.agent_name,
                system_message=sub_agent.system_prompt,
                description=f"I focus solely on {sub_agent.agent_name}.",
                model_client=model_client,
            )
            topic_agent = ReceivingAgent(model_client=model_client, assistant_agent=assistant_agent)
            ag_topic_agents.append(topic_agent)

        # Now I will create the user proxy agent that will relay messages to other agents without summarization
        self.user_proxy = UserProxyAgent(
            name="user_proxy",            
            input_func=lambda x: "I relay messages to other agents without summarization. Do not relay the reply from chat 0 to chat 2"
        )

        # Now I will create the summary agent that will summarize the insights from the topic agents
        agent = agents.get_agent_by_name(agent_name="summary_agent")
        ag_summary_agent = AssistantAgent(
            name=agent.agent_name,
            system_message=agent.system_prompt,
            description="I collect and and present insights.",
            model_client=AzureOpenAIChatCompletionClient(**agent.model.__dict__)
        )

        topic_agent: AssistantAgent = ag_topic_agents[0]
        results = []
        tasks = []

        RoutedAgent()
        # runtime = SingleThreadedAgentRuntime()    
        
        # @dataclass
        # class Message:
        #     content: str

        # @type_subscription(topic_type="default")
        # class ReceivingAgent(RoutedAgent):
        #     def __init__(self, model_client: AzureOpenAIChatCompletionClient) -> None:
        #         super().__init__("DestinationAgent")
        #         self._system_messages: List[LLMMessage] = [
        #             SystemMessage("You are a helpful AI assistant that helps with destination information.")
        #         ]
        #         self._model_client = model_client
        #     @message_handler
        #     async def on_my_message(self, message: Message, ctx: MessageContext) -> None:
        #         print(f"Received a message: {message.content}")
        #         self.on_message
                
    
        # class BroadcastingAgent(RoutedAgent):
        #     @message_handler
        #     async def on_my_message(self, message: Message, ctx: MessageContext) -> None:
        #         await self.publish_message(
        #             Message("Publishing a message from broadcasting agent!"),
        #             topic_id=TopicId(type="default", source=self.id.key),
        #         )
        
        for i, topic_agent in enumerate(ag_topic_agents):
            task = topic_agent.on_messages(
                messages=[
                    TextMessage(
                        source="User", 
                        content=(
                            "Extract insights from attached payload: \n" 
                            + json.dumps(message)
                        )
                    )
                ],
                cancellation_token=CancellationToken()
            )
            tasks.append(task)
            #await ReceivingAgent.register(runtime, topic_agent.name, lambda: ReceivingAgent("Receiving Agent"))
            

        #runtime.start()

        #await runtime.publish_message(Message("Hello"), topic_id=TopicId(type="default", source="default"))

        #await runtime.stop_when_idle()   

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

