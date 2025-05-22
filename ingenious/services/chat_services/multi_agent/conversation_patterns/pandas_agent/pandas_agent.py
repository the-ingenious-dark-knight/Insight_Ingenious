import autogen
import autogen.retrieve_utils
import autogen.runtime_logging

import logging
logger = logging.getLogger(__name__)

import shutil
import os

class ConversationPattern:

    def __init__(self, default_llm_config: dict, topics: list, memory_record_switch: bool, memory_path: str,
                 thread_memory: str):

        tmp_folder_path = 'tmp/code'
        if os.path.exists(tmp_folder_path):
            # Delete everything under the tmp folder
            for item in os.listdir(tmp_folder_path):
                item_path = os.path.join(tmp_folder_path, item)
                if os.path.isfile(item_path) or os.path.islink(item_path):
                    os.unlink(item_path)  # Delete file or symlink
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)  # Delete directory
            print("All files and folders under /tmp have been deleted.")
        else:
            print(f"The path {tmp_folder_path} does not exist.")

        self.default_llm_config = default_llm_config
        self.topics = topics
        self.memory_record_switch = memory_record_switch
        self.memory_path = memory_path
        self.thread_memory = thread_memory


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


        # Initialize customised agents for the group chat.
        self.sql_writer = None
        self.creator = None

        # Initialize core agents.
        self.user_proxy = autogen.UserProxyAgent(
            name="user_proxy", human_input_mode="NEVER", max_consecutive_auto_reply=0,
            code_execution_config={"use_docker": False}
        )


        # self.planner = autogen.AssistantAgent(
        #     name="planner",
        #     system_message=(
        #         """Tasks:\n"
        #         - Pass the question and context to `researcher`, do not suggest query.\n
        #         - Format your output based on the row count:
        #           - **Single Row**: Use the format `{{column_name: value, column_name: value}}`.
        #           - **Multiple Rows**: Use a list format with each row as a dictionary, e.g., `[{{column_name: value}}, {{column_name: value}}]`
        #         "- Wait `researcher` compose the final response and then say TERMINATE ."""
        #     ),
        #     description="Responds after `user_proxy`, `sql_writer` or  `analyst_agent`",
        #     llm_config=self.default_llm_config,
        #     human_input_mode="NEVER",
        #     code_execution_config={"work_dir":"coding", "use_docker":False},
        #     is_termination_msg=self.termination_msg,
        # )


        # self.researcher = autogen.ConversableAgent(
        #     name="researcher",
        #     system_message=(
        #         "Tasks:\n"
        #         "- Pass the user question to `sql_writer`, do not suggest query and table to use.\n"
        #         "- Pass the data to `analyst_agent`, do not suggest query and table to use.\n"
        #         "- Compose a final response.\n"
        #         "Note:"
        #         "- Never ask follow up question."
        #     ),
        #     description="I **ONLY** speak after `planner`",
        #     llm_config=self.default_llm_config,
        #     human_input_mode="NEVER",
        #     code_execution_config=False,
        #     is_termination_msg=self.termination_msg,
        # )


    async def get_conversation_response(self, input_message: str) -> [str, str]:
        """
        This function is the main entry point for the conversation pattern. It takes a message as input and returns a
        response. Make sure that you have added the necessary topic agents and agent topic chats before
        calling this function.
        """
        # graph_dict = {}
        # graph_dict[self.user_proxy] = [self.planner]
        # graph_dict[self.planner] = [self.researcher, self.analyst_agent]
        # graph_dict[self.researcher] = [self.sql_writer, self.planner]
        # graph_dict[self.sql_writer] = [self.planner]
        # graph_dict[self.analyst_agent] = [self.planner]
        #
        #
        # groupchat = autogen.GroupChat(
        #     agents=[self.user_proxy, self.researcher, self.planner, self.sql_writer, self.analyst_agent],
        #     messages=[],
        #     max_round=10,
        #     speaker_selection_method="auto",
        #     send_introductions=True,
        #     select_speaker_auto_verbose=False,
        #     allowed_or_disallowed_speaker_transitions=graph_dict,
        #     max_retries_for_selecting_speaker=1,
        #     speaker_transitions_type="allowed",
        #     # select_speaker_prompt_template
        # )
        #
        # manager = autogen.GroupChatManager(groupchat=groupchat,
        #                                    llm_config=self.default_llm_config,
        #                                    is_termination_msg=self.termination_msg,
        #                                    code_execution_config=False)


        # if self.memory_record_switch:
        #     self.user_proxy.retrieve_docs(input_message, 2, '')
        #     self.user_proxy.n_results = 2
        #     doc_contents = self.user_proxy._get_context(self.user_proxy._results)
        #     res = await self.user_proxy.a_initiate_chat(
        #         manager,
        #         message="Use group chat to solve user question. Keep the final answer concise."
        #                 "The last speaker should be `planner`."
        #                 "\nUser question: " + input_message,
        #         problem=input_message,
        #         summary_method="last_msg"
        #     )
        # else:
        #     res = await self.user_proxy.a_initiate_chat(
        #         manager,
        #         message=input_message,
        #         summary_method="last_msg"
        #     )

        res = await self.user_proxy.a_initiate_chat(
            self.creator,
            message=input_message,
            summary_method="last_msg"
        )

        with open(f"{self.memory_path}/context.md", "w") as memory_file:
            memory_file.write(res.summary)
            self.context = res.summary

        # Send a response back to the user
        return res.summary, self.context
