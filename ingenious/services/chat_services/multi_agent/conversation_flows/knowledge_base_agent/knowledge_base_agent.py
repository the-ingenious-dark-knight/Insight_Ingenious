import autogen
import autogen.retrieve_utils
import autogen.runtime_logging

import ingenious.config.config as config
from ingenious.models.chat import ChatResponse
from ingenious.services.chat_services.multi_agent.tool_factory import ToolFunctions
from ingenious.services.chat_services.multi_agent.conversation_patterns.knowledge_base_agent.knowledge_base_agent import \
    ConversationPattern


class ConversationFlow:
    @staticmethod
    async def get_conversation_response(message: str, thread_chat_history: list = [], topics: list = [],  memory_record = True) -> ChatResponse:
        # Get configuration for the LLM
        _config = config.get_config()
        llm_config = _config.models[0].__dict__

        # Initialize the knowledge base agent pattern, you only need to add defined topics here
        agent_pattern = ConversationPattern(default_llm_config=llm_config, topics=topics, memory_record = memory_record)

        search_agent = autogen.AssistantAgent(
            name="search_agent",
            system_message="I am a search agent responsible for retrieve result from search and pass to the researcher."
                           "my responses must be based strictly on the information found in the search results or guidelines, "
                           "without introducing any additional or external details. "
                           "When the research says AMBIGUOUS, please pass the query keywords without alternation."
                           "Tool Usage Rules:\n"
                           "if search health related information, please use argument: search_query str, index_name: 'vector-health'; "
                           "if search safety/emergency related information, please use argument: search_query str, index_name: 'vector-safety' "
                           "if the query quiet is ambiguous, try search in all index;"
                           "DO NOT do repeated search"
                           "DO NOT add extra information to search results."
                           "DO NOT ask follow up question."
                           "Only ask which index to search, or all index.",
            #add defined index here.
            description="I am a search agent focused on providing accurate information for search results.",
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
        res = await agent_pattern.get_conversation_response(message, thread_chat_history)

        return res
