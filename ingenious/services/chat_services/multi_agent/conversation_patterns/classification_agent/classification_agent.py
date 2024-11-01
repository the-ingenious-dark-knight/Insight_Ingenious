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
        self.task = 'Process user request using group chat.'

        if self.thread_memory == None or self.thread_memory == '':
            with open(f"{self.memory_path}/context.md", "w") as memory_file:
                memory_file.write("This is a new conversation, please continue the conversation given user question")

        if self.memory_record_switch and self.thread_memory != None and self.thread_memory != '':
            logger.log(level=logging.DEBUG,
                       msg="memory_record = True, check pattern requires optional dependencies: 'ChatHistorySummariser'.")
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
            system_message=("Tasks: "
                            " - step 1, i decide the topic of user question, I do not ask question. "
                            " - step 2,  "
                            f"check whether to record conversation: {self.memory_record_switch}, "
                            f"if true, call `chat_memory_recorder` to record the conversation in 100 words and go to next step, if false, go to the next step."
                            " - step 3, I compose a concise final response to share with the user. "
                            " - step 4, I TERMINATE the conversation."

                            "Rules for deciding the topic: "
                            f"If the user question or intent falls in to the predefined topcis:  {', '.join(self.topics)}, then the topic is defined."
                            "If no, try check if there is existing context, derive the new context by combining the current question with the existing context. "
                            " - For example, if in the RAG user asks about topic A in the previous question, then context will be about topic A."
                            " - if current question is very different from the existing context or no context, derive the topic using the current question. "
                            " - if there is no way to decide the context, say 'the question is out of my scope'."

                            "Other Rules: "
                            "- Do not give empty response. "
                            "- I only have one tool: `chat_memory_recorder`."
                            "- TERMINATE if no new information"),
            description=(
                "I **ONLY** speak after `user_proxy`, `researcher` or topic agents"
                "I can do self reflection by speak to my self."
                "Only I can TERMINATE the conversation."
            ),
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

    def add_topic_agent(self, agent: autogen.AssistantAgent):
        self.topic_agents.append(agent)

    async def get_conversation_response(self, input_message: str) -> [str, str]:
        """
        This function is the main entry point for the conversation pattern. It takes a message as input and returns a 
        response. Make sure that you have added the necessary topic agents and agent topic chats before 
        calling this function.
        """
        graph_dict = {}
        graph_dict[self.user_proxy] = [self.researcher]
        graph_dict[self.researcher] = self.topic_agents
        for topic_agent in self.topic_agents:
            graph_dict[topic_agent] = [self.researcher]

        groupchat = autogen.GroupChat(
            agents=[self.user_proxy, self.researcher] + self.topic_agents,
            messages=[],
            max_round=6,
            speaker_selection_method="auto",
            send_introductions=True,
            select_speaker_auto_verbose=False,
            allowed_or_disallowed_speaker_transitions=graph_dict,
            max_retries_for_selecting_speaker = 1,
            speaker_transitions_type="allowed",
            # select_speaker_prompt_template=(
            #     "First, select user_proxy "
            #     "next select 'researcher', "
            #     "next select the topic agents chosen by researcher,"
            #     "after talk to all required topic agent, select 'researcher' "
            # )
        )

        manager = autogen.GroupChatManager(groupchat=groupchat,
                                           llm_config=self.default_llm_config,
                                           is_termination_msg=self.termination_msg,
                                           code_execution_config=False)
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

        # Send a response back to the user
        return res.summary, context
