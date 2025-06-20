
### Flow Implementation Example

Conversation flow enables us to setup how data is passed and responded to with our chatbots. To create:

1. Setup a static method named get_conversation_response
2. Setup the agent pattern that will be followed through the conversation.

```python
# conversation_flows/your_pattern_name/your_pattern_name.py
from ingenious.models.chat import ChatResponse
from ingenious.services.chat_services.multi_agent.conversation_patterns.your_pattern_name.your_pattern_name import ConversationPattern

class ConversationFlow:
    @staticmethod
    async def get_conversation_response(message: str, topics: list = [], thread_memory: str='', memory_record_switch = True, thread_chat_history: list = []) -> ChatResponse:
        # Get configuration
        import ingenious.config.config as config
        _config = config.get_config()
        llm_config = _config.models[0].__dict__
        memory_path = _config.chat_history.memory_path

        # Initialize the conversation pattern
        agent_pattern = ConversationPattern(
            default_llm_config=llm_config,
            topics=topics,
            memory_record_switch=memory_record_switch,
            memory_path=memory_path,
            thread_memory=thread_memory
        )

        # Get the conversation response (probably this should be defined in the main function)
        res, memory_summary = await agent_pattern.get_conversation_response(message)

        return res, memory_summary
```

