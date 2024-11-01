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

        #please revise index name in this section.
        search_agent = autogen.AssistantAgent(
            name="search_agent",
            system_message=("Tasks: "
                            " - I use search_query given by `researcher` to conduct an AI search. "
                            " - I can use the below arguments for the `search_tool`: "
                            " - if the query is about health, please use argument: search_query str, index_name: 'index-document-set-1'; "
                            " - if the query is about safety and emergency, please use argument: search_query str, index_name: 'index-document-set-2' "
                            " - if the query contains AMBIGUOUS, I will search all index for a keyword match using the keyword provided by the researcher."
                            "Rules: "
                            " - The response MUST be based on the information found in the search results, without introducing any additional or external details. "
                            " - I can delete the keyword AMBIGUOUS and conduct the search just based on meaningful keywords."
                            " - If there is no result from search, say 'no information can be found'. "
                            " - I **ALWAYS** call `search_tool` if being select for speak."
                            " - DO NOT do repeated search."
                            " - DO NOT participate conversation other than provide search result.."
                            " - DO NOT terminate conversation."
                            " - DO NOT ask follow up question."),
            description= ("""I am **ONLY** allowed to speak **immediately** after `researcher`."""),
            llm_config=llm_config,
        )

        agent_pattern.add_function_agent(
            topic_agent=search_agent,
            executor=agent_pattern.researcher,  # Use the same research proxy executor for safety searches
            tool=ToolFunctions.aisearch,
            tool_name="search_tool",
            tool_description="Use this tool to perform AI searches"
        )


        # Get the conversation response using the pattern
        res, memory_summary = await agent_pattern.get_conversation_response(message)

        return res, memory_summary
