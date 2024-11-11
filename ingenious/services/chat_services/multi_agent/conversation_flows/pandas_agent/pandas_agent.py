
import ingenious.config.config as config
from ingenious.models.chat import ChatResponse
from ingenious.services.chat_services.multi_agent.conversation_patterns.pandas_agent.pandas_agent import \
    ConversationPattern
from ingenious.services.chat_services.multi_agent.tool_factory import SQL_ToolFunctions, PandasExecutor
from autogen.agentchat.contrib.multimodal_conversable_agent import MultimodalConversableAgent  # for GPT-4V
import autogen
import matplotlib.pyplot as plt
from PIL import Image
import os
import chainlit

working_dir = "tmp/code/"
class FigureCreator(autogen.ConversableAgent):
    def __init__(self, n_iters=2, user_name='', **kwargs):
        """
        Initializes a FigureCreator instance.

        This agent facilitates the creation of visualizations through a collaborative effort among its child agents: commander, coder, and critics.

        Parameters:
            - n_iters (int, optional): The number of "improvement" iterations to run. Defaults to 2.
            - **kwargs: keyword arguments for the parent AssistantAgent.
        """
        super().__init__(**kwargs)
        self.register_reply([autogen.Agent, None], reply_func=FigureCreator._reply_user, position=0)
        self._n_iters = n_iters
        self.file_name = 'demo_result.jpg'
        self.termination_msg = lambda x: "TERMINATE" in x.get("content", "").upper()

    def _reply_user(self, messages=None, sender=None, config=None):
        if all((messages is None, sender is None)):
            error_msg = f"Either {messages=} or {sender=} must be provided."
            logger.error(error_msg)  # noqa: F821
            raise AssertionError(error_msg)
        if messages is None:
            messages = self._oai_messages[sender]

        user_question = messages[-1]["content"]

        ### Define the agents
        commander = autogen.AssistantAgent(
            name="Commander",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=4,
            system_message=f"Help me run the code, and tell other agents it is in the <img {self.file_name}> file location.",
            is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
            code_execution_config={"last_n_messages": 3, "work_dir": working_dir, "use_docker": False},
            llm_config=self.llm_config,
        )

        critics = MultimodalConversableAgent(
            name="Critics",
            system_message="""Criticize the input figure. How to replot the figure so it will be better? Find bugs and issues for the figure.
            Pay attention to the color, format, and presentation. Keep in mind of the reader-friendliness.
            If you think the figures is good enough, then simply say NO_ISSUES.""",
            llm_config=self.llm_config,
            human_input_mode="NEVER",
            max_consecutive_auto_reply=1,
            #     use_docker=False,
        )

        coder = autogen.AssistantAgent(
            name="Coder",
            llm_config=self.llm_config,
            human_input_mode="NEVER",
        )

        coder.update_system_message(
            coder.system_message
            + f"ALWAYS save the figure in `{self.file_name}` file. "
              f"Tell other agents it is in the <img {self.file_name}> file location."
              f"Set plt.show(block=False) plt.pause(0.1)."
        )

        # Data flow begins
        commander.initiate_chat(coder, message=user_question)
        #img = Image.open(os.path.join(working_dir, self.file_name))
        #plt.imshow(img)
        #plt.axis("off")  # Hide the axes
        #plt.show()

        for i in range(self._n_iters):
            commander.send(
                message=f"Improve <img {os.path.join(working_dir, f'{self.file_name}')}>",
                recipient=critics,
                request_reply=True,
            )

            feedback = commander._oai_messages[critics][-1]["content"]
            if feedback.find("NO_ISSUES") >= 0:
                break
            commander.send(
                message=f"Here is the feedback to your figure. Please improve! Save the result to `{self.file_name}`\n"
                + feedback,
                recipient=coder,
                request_reply=True,
            )
            #img = Image.open(os.path.join(working_dir, f"{self.file_name}"))
            #plt.imshow(img)
            #plt.axis("off")  # Hide the axes
            #plt.show()

        return True, os.path.join(working_dir, f"{self.file_name}")


class ConversationFlow:
    # This pattern is for local SQL use only. For other types of SQL connectors,
    # please check the SQL manipulation agent.

    @staticmethod
    async def get_conversation_response(
            message: str,
            topics: list = [],
            thread_memory: str = '',
            memory_record_switch=True,
            thread_chat_history: str = '',
            user_name: str = 'demo_result',
    ) -> ChatResponse:
        # Retrieve the application configuration
        _config = config.get_config()
        llm_config = _config.models[0].__dict__
        memory_path = _config.chat_history.memory_path

        # Initialize the knowledge base agent pattern.
        # Add predefined topics here to guide the conversation flow.
        agent_pattern = ConversationPattern(
            default_llm_config=llm_config,
            topics=topics,
            memory_record_switch=memory_record_switch,
            memory_path=memory_path,
            thread_memory=thread_memory
        )

        agent_pattern.creator = FigureCreator(name="Figure Creator~", llm_config=llm_config, user_name = user_name)

        res, memory_summary = await agent_pattern.get_conversation_response(message)

        return res, memory_summary
