import autogen
import autogen.retrieve_utils
import autogen.runtime_logging
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent

from ingenious.services.chat_services.multi_agent.tool_factory import ToolFunctions


class ConversationPattern:

    def __init__(self, default_llm_config: dict):
        self.default_llm_config = default_llm_config
        self.topics = []

        print("Warning this pattern requires optional dependencies: 'ChatHistorySummariser'.")

        self.termination_msg = lambda x: x.get("content", "") is not None and "TERMINATE" in x.get("content",
                                                                                                   "").rstrip().upper()

        # Initialize agents
        self.user_proxy = RetrieveUserProxyAgent(
            name="user_proxy",
            is_termination_msg=self.termination_msg,
            human_input_mode="NEVER",
            max_consecutive_auto_reply=2,
            system_message="I am a proxy for the user, ensuring that their messages are properly routed through the system. "
                           "When there is not context, just tell the researcher to send a message to the user.",
            retrieve_config={
                "task": "qa",
                "docs_path": [
                    "tmp/context.md"
                ],
                "chunk_token_size": 4000,
                "model": self.default_llm_config["model"],
                "vector_db": "chroma",
                "overwrite": True,  # set to True if you want to overwrite an existing collection
                "get_or_create": True,  # set to False if don't want to reuse an existing collection
            },
            code_execution_config=False,  # we don't want to execute code in this case.
            silent=True
        )

        self.researcher = autogen.ConversableAgent(
            name="researcher",
            system_message="I do not call tools other than chat_memory_recorder."
                           "I talk to relevant topic agents and gather their response. "
                           "I compile and relay summary to user without adding extra details. "
                           "I do not derive new topics out of the original user question. "
                           "After talking with the topic agents,"
                           "I record a concise chat history by calling chat_memory_recorder at the end of each conversation with "
                           "2 arguments: conversation_text: str, last_response: str"
                           "Return TERMINATE when no new information is received.",
            description="I select and delegate tasks to topic agents, compiling and relaying their findings in a final summary. "
                        "I cannot provide direct answers, add extra info, or call functions.",
            llm_config=self.default_llm_config,
            human_input_mode="NEVER",
            code_execution_config=False,
            is_termination_msg=self.termination_msg
        )

        self.classification_agent = autogen.AssistantAgent(
            name="classifier",
            system_message="I am an assistant agent responsible for classifying messages into appropriate topics. "
                           "I am **ONLY** permitted to respond **immediately** after `user_proxy`. "
                           "The current question's context should always take priority over any retrieved context.",
            description="I **ONLY** classify user messages to a appropriate topic and record in the conversation",
            llm_config=self.default_llm_config,
            is_termination_msg=self.termination_msg,
        )



        autogen.register_function(
            ToolFunctions.update_memory,
            caller=self.researcher,
            executor=self.researcher,
            name="chat_memory_recorder",
            description="A function responsible for recording and updating summarized conversation memory. "
                        "It ensures that the conversation history is accurately saved to a specified location for future reference."
        )



        self.topic_agents: list[autogen.AssistantAgent] = []

    def add_topic_agent(self, agent: autogen.AssistantAgent):
        self.topic_agents.append(agent)

    async def get_conversation_response(self, input_message: str, thread_chat_history: list = []) -> str:
        """
        This function is the main entry point for the conversation pattern. It takes a message as input and returns a 
        response. Make sure that you have added the necessary topic agents and agent topic chats before 
        calling this function.
        """
        # chat_history_json = json.dumps(thread_chat_history)

        topics = []
        for agent in self.topic_agents:
            topics.append(agent.name)

        # get distinct topics
        topics = list(set(topics))

        # Update the system message of the classification agent to include the topics
        system_message = "I am an assistant agent responsible for classifying messages to a topic. " \
                         "I am **ONLY** allowed to respond **immediately** after `user_proxy`."
        system_message += f" Classify the message strictly into provided topics: {', '.join(topics)}. " \
                          "Do not provide any responses beyond the classification. Focus on the user's overall intent, even if terms seem out of place. " \
                          "Use prior messages to guide classification. If unclear, return 'neither'; if related to both, return 'both'."

        self.classification_agent.update_system_message(system_message)

        graph_dict = {}
        graph_dict[self.user_proxy] = [self.classification_agent]
        graph_dict[self.classification_agent] = [self.researcher]
        graph_dict[self.researcher] = self.topic_agents
        for topic_agent in self.topic_agents:
            graph_dict[topic_agent] = [self.researcher]


        # Define the GroupChat with the agent transitions
        groupchat = autogen.GroupChat(
            agents=[self.user_proxy, self.classification_agent, self.researcher] + self.topic_agents,
            messages=[],
            max_round=10,
            speaker_selection_method="auto",
            send_introductions=True,
            select_speaker_auto_verbose=False,
            allowed_or_disallowed_speaker_transitions=graph_dict,
            speaker_transitions_type="allowed",
            select_speaker_auto_multiple_template=(
                "You provided more than one name in your text, please return just the name of the next speaker. "
                "To determine the speaker use these prioritised rules:\n"
                "1. If the context refers to themselves as a speaker e.g. 'As the...' , choose that speaker's name.\n"
                "2. If it refers to the 'next' speaker name, choose that name.\n"
                "3. Otherwise, choose the first provided speaker's name in the context.\n"
                "The names are case-sensitive and should not be abbreviated or changed, classifier is not accepted\n"
                "Respond with ONLY the name of the speaker and DO NOT provide a reason."
            ),
            select_speaker_auto_none_template=(
                "You didn't choose a speaker. As a reminder, to determine the speaker use these prioritised rules:\n"
                "1. If the context refers to themselves as a speaker e.g. 'As the...' , choose that speaker's name.\n"
                "2. If it refers to the 'next' speaker name, choose that name.\n"
                "3. Otherwise, choose the first provided speaker's name in the context.\n"
                "The names are case-sensitive and should not be abbreviated or changed.\n"
                "The only names that are accepted are {agentlist}, classifier is not accepted.\n"
                "Respond with ONLY the name of the speaker and DO NOT provide a reason."
            ),
            select_speaker_prompt_template=(
                "Route the conversation to the 'classifier' if the topic is not available. "
                "Once classified, pass it to the 'researcher' to decide which topic ageng to choose"
                "according to the response from 'researcher' select the first topic agent. "
                "After receiving the response, the 'researcher' summarizes for the user, then queries the next topic agent, repeating the process. "
                "Do not select any agent for two consecutive responses."
                "After hearing from all topic agents, the 'researcher' compiles a final summary. "
            )
        )

        manager = autogen.GroupChatManager(groupchat=groupchat,
                                           llm_config=self.default_llm_config,
                                           is_termination_msg=self.termination_msg,
                                           code_execution_config=False, )

        # Start chatting with the boss as this is the user proxy agent.
        res = await self.user_proxy.a_initiate_chat(
            manager,
            message=self.user_proxy.message_generator,
            problem=input_message,
            summary_method="last_msg",
        )

        # Send a response back to the user
        return res.summary
