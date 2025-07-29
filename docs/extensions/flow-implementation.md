---
title: "Flow Implementation"
layout: single
permalink: /extensions/flow-implementation/
sidebar:
  nav: "docs"
toc: true
toc_label: "Flow Guide"
toc_icon: "stream"
---

This guide covers implementing custom conversation flows for AI agent orchestration in Insight Ingenious.

## Flow Implementation Patterns

Conversation flows enable you to set up how data is passed and responded to with your chatbots. There are two main patterns:

### Pattern 1: Static Method (Legacy)
Used for simpler flows that don't need access to the parent service.

```python
# conversation_flows/your_pattern_name/your_pattern_name.py
from ingenious.models.chat import ChatRequest

class ConversationFlow:
    @staticmethod
    async def get_conversation_response(
        message: str,
        topics=None,
        thread_memory: str = "",
        memory_record_switch: bool = True,
        thread_chat_history=None,
        chatrequest: ChatRequest = None,
    ) -> tuple[str, str]:
        # Implementation logic
        result = "Your response"
        memory_summary = "Summary of the conversation"
        return result, memory_summary
```

### Pattern 2: IConversationFlow Interface (Recommended)
Used for complex flows that need access to parent services and utilities.

```python
# conversation_flows/your_pattern_name/your_pattern_name.py
from ingenious.models.chat import ChatRequest, ChatResponse
from ingenious.services.chat_services.multi_agent.service import IConversationFlow

class ConversationFlow(IConversationFlow):
    async def get_conversation_response(
        self,
        chat_request: ChatRequest,
    ) -> ChatResponse:
        # Access parent service utilities
        agents = self.Get_Agents()  # Get agent configurations
        template = await self.Get_Template(file_name="template.jinja")
        models = self.Get_Models()  # Get LLM configurations
        
        # Your conversation logic here
        
        return ChatResponse(
            thread_id=chat_request.thread_id,
            message_id="unique_id",
            agent_response="Your response",
            token_count=0,
            max_token_count=0,
            memory_summary="",
        )
```
