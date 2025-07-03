import logging
from typing import List, Tuple

from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.teams import SelectorGroupChat
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient

logger = logging.getLogger(__name__)


class ConversationPattern:
    def __init__(
        self,
        default_llm_config: dict,
        topics: list,
        memory_record_switch: bool,
        memory_path: str,
        thread_memory: str,
    ):
        self.default_llm_config = default_llm_config
        self.topics = topics
        self.memory_record_switch = memory_record_switch
        self.memory_path = memory_path
        self.thread_memory = thread_memory
        self.topic_agents: List[AssistantAgent] = []
        self.context = ""

        # Create Azure OpenAI model client from config
        self.model_client = AzureOpenAIChatCompletionClient(
            model=default_llm_config.get(
                "azure_deployment", default_llm_config.get("model", "gpt-4o")
            ),
            api_key=default_llm_config.get("api_key", "mock-openai-key"),
            azure_endpoint=default_llm_config.get(
                "azure_endpoint", "http://127.0.0.1:3001"
            ),
            api_version=default_llm_config.get("api_version", "2024-08-01-preview"),
        )

        # Initialize context file
        if not self.thread_memory:
            with open(f"{self.memory_path}/context.md", "w") as memory_file:
                memory_file.write("New conversation. Continue based on user question.")

        if self.memory_record_switch and self.thread_memory:
            logger.log(
                level=logging.DEBUG,
                msg="Memory recording enabled. Requires `ChatHistorySummariser` for optional dependency.",
            )
            with open(f"{self.memory_path}/context.md", "w") as memory_file:
                memory_file.write(self.thread_memory)

        try:
            with open(f"{self.memory_path}/context.md", "r") as memory_file:
                self.context = memory_file.read()
        except FileNotFoundError:
            self.context = ""

        # Initialize planner agent
        self.planner = AssistantAgent(
            name="planner",
            model_client=self.model_client,
            system_message=(
                "Tasks:\n"
                f"-Pass the payload as plain text to predefined topic agent: {', '.join(self.topics)}.\n"
                "- Wait topic agent compose the final response and say TERMINATE ."
                "- I do not provide answer to user question.\n"
            ),
        )

    def add_topic_agent(self, agent_name: str, system_message: str):
        """Add a topic agent to the conversation pattern"""
        topic_agent = AssistantAgent(
            name=agent_name,
            model_client=self.model_client,
            system_message=system_message,
        )
        self.topic_agents.append(topic_agent)

    async def get_conversation_response(self, input_message: str) -> Tuple[str, str]:
        """
        This function is the main entry point for the conversation pattern. It takes a message as input and returns a
        response. Make sure that you have added the necessary topic agents and agent topic chats before
        calling this function.
        """
        try:
            # Create a group chat with all agents
            all_agents = [self.planner] + self.topic_agents

            # Create a group chat team
            team = SelectorGroupChat(
                participants=all_agents,
                model_client=self.model_client,
                selector_prompt="Select the most appropriate agent to handle the task based on the topic",
            )

            # Run the conversation
            result = await team.run(
                task=(
                    "Extract insights from the payload, ensuring that only one type of topic agent is selected. \n"
                    "The output must be in JSON format, containing only the JSON string within {} and no additional text outside."
                    "Payload: " + input_message
                )
            )

            # Get the final message content
            final_message = (
                result.messages[-1].content if result.messages else "No response"
            )

            # Update context
            with open(f"{self.memory_path}/context.md", "w") as memory_file:
                memory_file.write(final_message)
                self.context = final_message

            return final_message, self.context

        except Exception as e:
            logger.error(f"Error in conversation response: {e}")
            return f"Error: {str(e)}", self.context

    async def close(self):
        """Close the model client connection"""
        await self.model_client.close()
