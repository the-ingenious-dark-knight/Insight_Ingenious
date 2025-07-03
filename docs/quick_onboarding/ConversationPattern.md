## Creating Custom Conversation Patterns

### Pattern Structure

1. Create a new pattern module in `ingenious/services/chat_services/multi_agent/conversation_patterns/your_pattern_name/`
2. Implement the `ConversationPattern` class following the interface
3. Create a corresponding flow in `ingenious/services/chat_services/multi_agent/conversation_flows/your_pattern_name/`

### Pattern Implementation Example

```python
# conversation_patterns/your_pattern_name/your_pattern_name.py
import autogen
import logging

class ConversationPattern:
    def __init__(self, default_llm_config: dict, topics: list, memory_record_switch: bool, memory_path: str, thread_memory: str):
        self.default_llm_config = default_llm_config
        self.topics = topics
        self.memory_record_switch = memory_record_switch
        self.memory_path = memory_path
        self.thread_memory = thread_memory

        # Initialize agents
        self.user_proxy = autogen.UserProxyAgent(
            name="user_proxy",
            human_input_mode="NEVER",
            system_message="I represent the user's request"
        )

        self.your_agent = autogen.AssistantAgent(
            name="your_agent",
            system_message="Your agent's system message",
            llm_config=self.default_llm_config
        )

    async def get_conversation_response(self, input_message: str) -> [str, str]:
        # Set up agent interactions
        result = await self.user_proxy.a_initiate_chat(
            self.your_agent,
            message=input_message
        )

        return result.summary, ""
```
