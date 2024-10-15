import autogen.retrieve_utils
import autogen.runtime_logging
import autogen
import ingenious.config.config as config
#import ingenious.dependencies as deps
#from ingenious.services.chat_services.multi_agent.agent_factory import AgentFactory #Agent factory is not used in the current pattern, group chat has been adopted
from ingenious.models.chat import Action, ChatRequest, ChatResponse, KnowledgeBaseLink, Product
from ingenious.services.chat_services.multi_agent.conversation_patterns.classification_agent.classification_agent import ConversationPattern


class ConversationFlow:
    @staticmethod
    async def get_conversation_response(message: str, thread_chat_history: list = []) -> ChatResponse:
        _config = config.get_config()      
        llm_config = _config.models[0].__dict__
        # Initialize the classification agent pattern
        _classification_agent_pattern = ConversationPattern(default_llm_config=llm_config)


        # Add the topic agents to the classification agent pattern
        tennis_agent = autogen.AssistantAgent(
            name="tennis",
            system_message="You are a topic agent responsible for answering queries about tennis. "
                           "Ensure that your answers are accurate, concise, "
                           "and formatted for easy readability. Do not provide memory or update context",
            description="You are a topic agent focused on providing information about tennis.",
            llm_config=llm_config,
        )

        _classification_agent_pattern.add_topic_agent(tennis_agent)

        soccer_agent = autogen.AssistantAgent(
            name="soccer",
            system_message="You are a topic agent responsible for answering queries about soccer. "
                           "Ensure that your answers are accurate, concise, "
                           "and formatted for easy readability. Do not provide memory or update context",
            description="You are a topic agent focused on providing information about soccer.",
            llm_config=llm_config,
        )

        _classification_agent_pattern.add_topic_agent(soccer_agent)

        basketball_agent = autogen.AssistantAgent(
            name="basketball",
            system_message="You are a topic agent responsible for answering queries about basketball. "
                           "Ensure that your answers are accurate, concise, "
                           "and formatted for easy readability. Do not provide memory",
            description="You are a topic agent focused on providing information about basketball.",
            llm_config=llm_config,
        )

        _classification_agent_pattern.add_topic_agent(basketball_agent)



        res = await _classification_agent_pattern.get_conversation_response(message, thread_chat_history)

        # Send a response back to the user
        return res

