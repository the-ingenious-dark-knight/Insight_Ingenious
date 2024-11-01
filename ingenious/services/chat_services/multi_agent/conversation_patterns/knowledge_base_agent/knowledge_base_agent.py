import logging

import autogen
import autogen.retrieve_utils
import autogen.runtime_logging
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent

from ingenious.services.chat_services.multi_agent.tool_factory import ToolFunctions

logger = logging.getLogger(__name__)


class ConversationPattern:
    def __init__(self, default_llm_config: dict, topics: list, memory_record_switch: bool, memory_path: str,
                 thread_memory: str):
        self.default_llm_config = default_llm_config
        self.topics = topics
        self.memory_record_switch = memory_record_switch
        self.memory_path = memory_path
        self.thread_memory = thread_memory
        self.topic_agents: list[autogen.AssistantAgent] = []
        self.task = """Using group chat to process the request from the user."""

        if self.thread_memory == None or self.thread_memory == '':
            with open(f"{self.memory_path}/context.md", "w") as memory_file:
                memory_file.write("This is a new conversation, please continue the conversation given user question")

        if self.memory_record_switch and self.thread_memory != None and self.thread_memory != '':
            logger.log(level=logging.DEBUG,
                       msg="Warning: if memory_record = True, the pattern requires optional dependencies: 'ChatHistorySummariser'.")
            with open(f"{self.memory_path}/context.md", "w") as memory_file:
                memory_file.write(self.thread_memory)

        self.termination_msg = lambda x: x.get("content", "") is not None and "TERMINATE" in x.get("content",
                                                                                                   "").rstrip().upper()

        # Initialize agents
        if self.memory_record_switch:
            self.user_proxy = RetrieveUserProxyAgent(
                name="user_proxy",
                is_termination_msg=self.termination_msg,
                human_input_mode="NEVER",
                max_consecutive_auto_reply=2,
                system_message=self.task,
                retrieve_config={
                    "task": "qa",
                    "docs_path": [
                        f"{self.memory_path}/context.md"
                    ],
                    "chunk_token_size": 2000,
                    "model": self.default_llm_config["model"],
                    "vector_db": "chroma",
                    "overwrite": True,  # set to True if you want to overwrite an existing collection
                    "get_or_create": True,  # set to False if don't want to reuse an existing collection
                },
                code_execution_config=False,  # we don't want to execute code in this case.
                silent=True
            )
        else:
            self.user_proxy = autogen.UserProxyAgent(
                name="user_proxy",
                is_termination_msg=self.termination_msg,
                human_input_mode="NEVER",
                max_consecutive_auto_reply=2,
                system_message=self.task,
                code_execution_config=False,
                silent=True
            )

        self.researcher = autogen.ConversableAgent(
            name="researcher",
            system_message=("I am a research planner. "
                            "Tasks: "
                            " - step 1, i write a search_query to the `search_agent` to retrieve information to solve user request."
                            " - step 2,  "
                                f"check whether to record conversation: {self.memory_record_switch}, "
                                f"if true, call `chat_memory_recorder` to record the conversation in 100 words and go to next step, "
                                "if false, just go to the next step."
                            " - step 3, I read the response from `search_agent` and compose a concise and factual final response and end the conversation."
                            "Rules for the query: "
                            f"- if the question is in predefined topics: {', '.join(self.topics)}, "
                            f"  I will ask search agent to search using the relevant index using query from user question. "
                            f"- if the question is not in predefined topics: {', '.join(self.topics)}, "
                            f"  I will pass the following query: AMBIGUOUS +' '+ keywords derived from the user question."
                            "Rules for deciding the topic: "
                            " - if there is no recorded context, I decide the topic purely based on the current question."
                            " - if there is RAG context, I derive the topic by combining the current question with the context. "
                            " - For example, if in the RAG user asks about topic A in the previous question, then context will be about topic A."
                            " - if current question is very different from the RAG context, derive the topic using the current question. "
                            " - if there is no way to decide the topic, then it is classified as not in predefined topics. "
                            "Other Rules: "
                            "- Call `search_agent` only once per chat. "
                            "- TERMINATE if no new information"),
            description=(
                "I **ONLY** speak after `user_proxy` or `search_agent`, the next speaker must be `researcher`. "
                "Only I can TERMINATE the conversation."),
            llm_config=self.default_llm_config,
            human_input_mode="NEVER",
            code_execution_config=False,
            is_termination_msg=self.termination_msg,

        )

        if self.memory_record_switch:
            print("chat_memory_recorder registered")
            autogen.register_function(
                ToolFunctions.update_memory,
                caller=self.researcher,
                executor=self.researcher,
                name="chat_memory_recorder",
                description=("A function responsible for recording and updating summarized conversation memory. "
                             "It ensures that the conversation history is accurately and concisely saved to a specified location for future reference.")
            )

    def add_function_agent(self, topic_agent: autogen.ConversableAgent,
                           executor: autogen.UserProxyAgent,
                           tool: callable,
                           tool_name: str = "",
                           tool_description: str = ""):
        """
        Adds a topic-specific agent to the list of topic agents and registers a tool (function)
        that the agent can invoke using the provided executor.
        """

        self.topic_agents.append(topic_agent)
        # Register the tool (function) with the agent and executor
        autogen.register_function(
            tool,  # The callable tool function that the agent will use
            caller=topic_agent,  # The agent that will invoke the tool
            executor=executor,  # The executor responsible for running the tool
            name=tool_name,  # Name of the tool being registered
            description=tool_description  # Description of the tool for documentation
        )

        topic_agent.register_nested_chats(
            trigger=self.researcher,
            chat_queue=[
                {
                    "sender": self.user_proxy,
                    "recipient": self.researcher,
                    "summary_method": "last_msg",
                }
            ],
        )

    async def get_conversation_response(self, input_message: str) -> [str, str]:
        """
        Main entry point for the conversation pattern. Takes a message as input and returns a response.
        """

        graph_dict = {}
        graph_dict[self.user_proxy] = [self.researcher]
        graph_dict[self.researcher] = self.topic_agents
        for topic_agent in self.topic_agents:
            graph_dict[topic_agent] = [self.researcher]

        groupchat = autogen.GroupChat(
            agents=[self.user_proxy, self.researcher] + self.topic_agents,
            messages=[],
            max_round=10,
            speaker_selection_method="auto",
            send_introductions=True,
            select_speaker_auto_verbose=False,
            allowed_or_disallowed_speaker_transitions=graph_dict,
            max_retries_for_selecting_speaker=1,
            speaker_transitions_type="allowed",
            # select_speaker_prompt_template=(
            #     "First, select user_proxy, "
            #     "next select 'researcher', "
            #     "next select 'search_agent',"
            #     "end the conversation with 'researcher' "
            # )
        )

        manager = autogen.GroupChatManager(groupchat=groupchat,
                                           llm_config=self.default_llm_config,
                                           is_termination_msg=self.termination_msg,
                                           code_execution_config=False, )

        if self.memory_record_switch:
            res = await self.user_proxy.a_initiate_chat(
                manager,
                message=self.user_proxy.message_generator,
                problem=input_message,
                summary_method="last_msg"
            )
        else:
            res = await self.user_proxy.a_initiate_chat(
                manager,
                message=input_message,
                summary_method="last_msg"
            )

        with open(f"{self.memory_path}/context.md", "r") as memory_file:
            context = memory_file.read()

        return res.summary, context
