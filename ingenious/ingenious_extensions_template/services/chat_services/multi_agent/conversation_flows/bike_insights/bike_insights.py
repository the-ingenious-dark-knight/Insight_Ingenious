import os
from pathlib import Path
from typing import List
import autogen
import autogen.runtime_logging
from jinja2 import Environment, FileSystemLoader
import jsonpickle
from ingenious.utils.namespace_utils import get_path_from_namespace_with_fallback
# Custom class import from ingenious_extensions 
from ingenious.services.chat_services.multi_agent.service import IConversationFlow
from ingenious_extensions_template.models.agents import Agents


class ConversationFlow(IConversationFlow):
    async def get_conversation_response(
            self,
            message: str,
            thread_memory: str = '',
            memory_record_switch=True,
            thread_chat_history: list = []
    ) -> tuple[str, str]:
        #  Get your agents from your custom class in models folder
        agents = Agents(self._config)
        # Note you can access llm models from the configuration array
        llm_config = self.Get_Models[0]
        # Note the base IConversationFlow gives you a logger for logging purposes
        self._logger.debug("Starting Flow")
        
        ag_topic_agents = List[autogen.AssistantAgent]
        for sub_agent in [f for f in agents.get_agents() if f.agent_type == "researcher"]:
            template_name = f"{sub_agent.agent_name}_prompt.jinja"
            # The abstract class has a built in property which is a jinia2 environment object. 
            # This environment object first searches for prompts 
            # within the ingenious_extensions/templates/prompts/ folder and, 
            # if it cant find this it falls back to the ingenious/templates/prompts/ folder 
            template = self._prompt_template_env.get_template(template_name)
            system_prompt = template.render(topic=sub_agent.agent_name)
            topic_agent = autogen.AssistantAgent(
                name=sub_agent.agent_name,
                system_message=system_prompt,
                description=f"I focus solely on {sub_agent.agent_name}.",
                llm_config=sub_agent.model_config,
            )
            ag_topic_agents.append(topic_agent)

        # Create the user proxy agent that will relay messages to other agents without summarization
        self.user_proxy = autogen.UserProxyAgent(
            name="user_proxy",
            is_termination_msg=self.termination_msg,
            human_input_mode="NEVER",
            max_consecutive_auto_reply=1,
            system_message="I relay messages to other agents without summarization. Do not relay the reply from chat 0 to chat 4",
            code_execution_config={
                "last_n_messages": 1,
                "work_dir": "tasks",
                "use_docker": False,
            },  # code execution config 
            silent=False
        )

        # Create the summary agent
        summary_agent = [f for f in agents.get_agents() if f.agent_type == "summary"][-1]
        summary_template = self._prompt_template_env.get_template(f"{summary_agent.agent_name}_prompt.jinja")
        summary_prompt = summary_template.render(topic="")
        ag_summary_agent = autogen.ConversableAgent(
            name=summary_agent.agent_name,
            system_message=summary_prompt,
            description=f"I collect and and present insights.",
            llm_config=summary_agent.model_config,
        )

        res = await self.user_proxy.a_initiate_chats(
            [
                {
                    "chat_id": 1,
                    "recipient": ag_topic_agents[0],
                    "message": (
                        "Extract insights from attached payload: \n" 
                        + message
                    ),
                    "silent": False                 
                },
                {
                    "chat_id": 2,
                    "recipient": ag_topic_agents[1],
                    "message": (
                        "Extract insights from attached payload: \n" 
                        + message
                    ),
                    "silent": False                 
                },
                {
                    "chat_id": 3,
                    "prerequisites": [1, 2],
                    "recipient": ag_summary_agent,
                    "silent": False,
                    "message": """Provide insights using the context provided."""
                }
            ]
        )

        response_array = []
        for i, chat_res in res.items():
            print(f"*****{i}th chat*******:")
            print(chat_res.summary)
            print("Human input in the middle:", chat_res.human_input)
            print("Conversation cost: ", chat_res.cost)
            print("\n\n")
            agent = agents.get_agents()[i-1]
            response_chat = {
                    "chat_number": {i},
                    "chat_title": agent.agent_display_name,
                    "chat_response": chat_res.summary
            }
            response_array.append(response_chat)

        return jsonpickle.encode(unpicklable=False, value=response_array), ""

