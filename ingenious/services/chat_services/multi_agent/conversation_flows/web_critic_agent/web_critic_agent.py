import autogen
import autogen.retrieve_utils
import autogen.runtime_logging

import ingenious.config.config as config
from ingenious.models.chat import ChatResponse
from ingenious.services.chat_services.multi_agent.conversation_patterns.web_critic_agent.web_critic_agent import ConversationPattern


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
        critic_agent = autogen.AssistantAgent(
            name="web_critic_agent",
            system_message=("""
            I **ALWAYS** use internet to check all information mentioned by `researcher` is a fact or not.
            I **ONLY** suggest complete removal or replacement for non-factual information to `researcher`.
            Rules:
            - If there is no feedback, just pass to `researcher` to compose the final response.
            - Do not talk things other than the suggestion from web search. 
            """),
            description = ("""I am **ONLY** allowed to speak **immediately** after `researcher`."""),
            llm_config=llm_config,
        )

        agent_pattern.add_assistant_agent(critic_agent)


        # Get the conversation response using the pattern
        res, memory_summary = await agent_pattern.get_conversation_response(message)

        return res, memory_summary
