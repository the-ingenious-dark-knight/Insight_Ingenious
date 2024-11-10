import autogen
import autogen.retrieve_utils
import autogen.runtime_logging
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
from ingenious.services.chat_services.multi_agent.tool_factory import ToolFunctions

import logging
logger = logging.getLogger(__name__)



class ConversationPattern:

    def __init__(self, default_llm_config: dict, topics: list, memory_record_switch: bool, memory_path: str,
                 thread_memory: str):
        self.default_llm_config = default_llm_config
        self.topics = topics
        self.memory_record_switch = memory_record_switch
        self.memory_path = memory_path
        self.thread_memory = thread_memory
        self.assistant_agents: list[autogen.AssistantAgent] = []


        if not self.thread_memory:
            with open(f"{self.memory_path}/context.md", "w") as memory_file:
                memory_file.write("New conversation. Continue based on user question.")

        if self.memory_record_switch and self.thread_memory:
            logger.log(level=logging.DEBUG,
                       msg="Memory recording enabled. Requires `ChatHistorySummariser` for optional dependency.")
            with open(f"{self.memory_path}/context.md", "w") as memory_file:
                memory_file.write(self.thread_memory)

        with open(f"{self.memory_path}/context.md", "r") as memory_file:
            self.context = memory_file.read()

        self.termination_msg = lambda x: "TERMINATE" in x.get("content", "").upper()

        # Initialize agents
        if self.memory_record_switch:
            self.user_proxy =  RetrieveUserProxyAgent(
                name="user_proxy",
                is_termination_msg=self.termination_msg,
                human_input_mode="NEVER",
                max_consecutive_auto_reply=2,
                system_message= "I enhance the user question with context",
                retrieve_config={
                    "task": "qa",
                    "docs_path": [f"{self.memory_path}/context.md"],
                    "chunk_token_size": 2000,
                    "model": self.default_llm_config["model"],
                    "vector_db": "chroma",
                    "overwrite": True,
                    "get_or_create": True,
                },
                code_execution_config=False,
                silent=False
            )
        else:
            self.user_proxy = autogen.UserProxyAgent(
                name="user_proxy",
                is_termination_msg=self.termination_msg,
                human_input_mode="NEVER",
                max_consecutive_auto_reply=2,
                system_message="I enhance the user question with context",
                code_execution_config=False,
                silent=False
            )



        self.researcher = autogen.ConversableAgent(
            name="researcher",
            system_message=(
                "Tasks:\n"
                "- Solve the user question and fact check with the `web_critic_agent`.\n"
                "- Compose a final response send to the user."
                "- When the user prompt is general greetings like Hi, tell him my function concisely."
            ),
            description="I **ONLY** speak after `planner` or `web_critic_agent`.",
            llm_config=self.default_llm_config,
            human_input_mode="NEVER",
            code_execution_config=False,
            is_termination_msg=self.termination_msg,
        )




        self.planner = autogen.AssistantAgent(
            name="planner",
            system_message=(
                "Tasks:\n"
                "- Pass the question and context to `researcher`.\n"
                "- I can TERMINATE the conversation"
                "Notes:\n"
                "I cannot answer user questions directly, I need pass the question `researcher`."
            ),
            description="Responds after `user_proxy` or `web_critic_agent`.",
            llm_config=self.default_llm_config,
            human_input_mode="NEVER",
            code_execution_config=False,
            is_termination_msg=self.termination_msg,
        )

    def add_assistant_agent(self, agent: autogen.AssistantAgent):
        self.assistant_agents.append(agent)



    async def get_conversation_response(self, input_message: str) -> [str, str]:
        """
        This function is the main entry point for the conversation pattern. It takes a message as input and returns a
        response. Make sure that you have added the necessary topic agents and agent topic chats before
        calling this function.
        """
        graph_dict = {}
        graph_dict[self.user_proxy] = [self.planner]
        graph_dict[self.planner] = [self.researcher]
        graph_dict[self.researcher] = self.assistant_agents
        for assistant_agent in self.assistant_agents:
            graph_dict[assistant_agent] = [self.researcher, self.planner]


        groupchat = autogen.GroupChat(
            agents=[self.user_proxy, self.researcher, self.planner] + self.assistant_agents,
            messages=[],
            max_round=6,
            speaker_selection_method="auto",
            send_introductions=True,
            select_speaker_auto_verbose=False,
            allowed_or_disallowed_speaker_transitions=graph_dict,
            max_retries_for_selecting_speaker=1,
            speaker_transitions_type="allowed",
            # select_speaker_prompt_template
        )

        manager = autogen.GroupChatManager(groupchat=groupchat,
                                           llm_config=self.default_llm_config,
                                           is_termination_msg=self.termination_msg,
                                           code_execution_config=False)



        if self.memory_record_switch:
            self.user_proxy.retrieve_docs(input_message, 2, '')
            self.user_proxy.n_results = 2
            doc_contents = self.user_proxy._get_context(self.user_proxy._results)
            res = await self.user_proxy.a_initiate_chat(
                manager,
                message="Use group chat to solve user question. Keep the final answer concise."
                        "When there is no context, just focus on user question. "
                        "\n "
                        "Context: " + doc_contents +
                        "\nUser question: " + input_message,
                problem=input_message,
                summary_method="last_msg"
            )
        else:
            res = await self.user_proxy.a_initiate_chat(
                manager,
                message=input_message,
                summary_method="last_msg"
            )

        with open(f"{self.memory_path}/context.md", "w") as memory_file:
            memory_file.write(res.summary)
            self.context = res.summary

        # Send a response back to the user
        return res.summary, self.context
