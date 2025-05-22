import autogen
import autogen.retrieve_utils
import autogen.runtime_logging

import ingenious.config.config as config
from ingenious.models.chat import ChatResponse
from ingenious.services.chat_services.multi_agent.tool_factory import ToolFunctions
from ingenious.services.chat_services.multi_agent.conversation_patterns.knowledge_base_agent.knowledge_base_agent import ConversationPattern


class ConversationFlow:
    @staticmethod
    async def get_conversation_response(message: str, topics: list = [], thread_memory: str='', memory_record_switch = True, thread_chat_history: list[str, str] = []) -> ChatResponse:
        # Get configuration for the LLM
        _config = config.get_config()
        llm_config = _config.models[0].__dict__
        memory_path = _config.chat_history.memory_path

        # Initialize the knowledge base agent pattern, you only need to add defined topics here
        agent_pattern = ConversationPattern(default_llm_config=llm_config,
                                            topics= topics,
                                            memory_record_switch = memory_record_switch,
                                            memory_path = memory_path,
                                            thread_memory = thread_memory)


        agent_pattern.search_agent = autogen.AssistantAgent(
            name="search_agent",
            system_message=("Tasks: "
                            " - I write search_query from the information given by `researcher`. "
                            " - I **Always** suggest call function `search_tool`."
                            " - I make my own decision on conducting the search."
                            " - I can use the below arguments for the `search_tool`: "
                            " - if the query is about health, please use argument: search_query str, index_name: 'index-document-set-1'; "
                            " - if the query is about safety, please use argument: search_query str, index_name: 'index-document-set-2' "


                            "Rules for compose the query: "
                            f"- if the context is in predefined topics: {', '.join(agent_pattern.topics)}, "
                            f"  I will compose query using the relevant index. "
                            f"- if the question is not in predefined topics: {', '.join(agent_pattern.topics)} or lacks specific context,  "
                            f"  I will use keywords derived from the user question and search in all indexes: 'index-document-set-1', 'index-document-set-2'."


                            "Other Rules: "
                            " - My response MUST be based on the information found in the search results, without introducing any additional or external details. "
                            " - If there is no result from search, say 'no information can be found'. "
                            " - DO NOT give empty response. "
                            " - DO NOT do repeated search."
                            " - DO NOT terminate conversation."
                            " - DO NOT ask questions."),
            description= ("""I am **ONLY** allowed to speak **immediately** after `researcher`."""),
            llm_config=llm_config,
        )

        autogen.register_function(
            ToolFunctions.aisearch,
            caller=agent_pattern.search_agent,
            executor=agent_pattern.planner,
            name="search_tool",
            description="Use this tool to perform ai search."
        )


        # Get the conversation response using the pattern
        res, memory_summary = await agent_pattern.get_conversation_response(message)

        return res, memory_summary
