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

## Directory Structure Requirements

**IMPORTANT**: Your flow directory name must match the conversation flow name exactly:

```
ingenious/services/chat_services/multi_agent/conversation_flows/
├── your_flow_name/
│   ├── __init__.py
│   └── your_flow_name.py        # Must match directory name
```

For a flow called `product_recommendation`, you must create:
- Directory: `product_recommendation/`
- File: `product_recommendation.py`
- Access via: `"conversation_flow": "product_recommendation"`

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
        models = self.Get_Models()  # Get LLM configurations
        template = await self.Get_Template(file_name="template.jinja")
        # Available helper methods:
        # - self.Get_Memory_Path() - Get memory storage path
        # - self.Get_Memory_File() - Get memory file path
        # - self.Maintain_Memory(content, max_words) - Update conversation memory

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

## Pattern Selection

The system automatically chooses between patterns based on your class implementation:

- **Static Pattern**: Used when your `ConversationFlow` class has no `__init__` method or takes no parameters
- **IConversationFlow Pattern**: Used when your class extends `IConversationFlow` and has an `__init__` method that expects a parent service

## Template Management

### Local Templates
Templates stored locally in `templates/prompts/` are accessible immediately:

```python
template = await self.Get_Template(file_name="your_template.jinja")
```

### Azure Blob Storage Templates
For production deployments with Azure Blob Storage enabled, templates should be uploaded to the `prompts` container. If a template is not found in Azure Blob Storage, the system will fall back gracefully with a default template.

### Template Best Practices
1. Always handle template loading errors gracefully
2. Provide fallback templates for critical flows
3. Use descriptive template names that match your flow purpose
4. Test templates both locally and with cloud storage

## Complete Working Example

Here's a complete example implementing both patterns:

### Static Method Pattern
```python
# conversation_flows/simple_helper/simple_helper.py
import logging
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
        # Simple response logic
        response = f"I can help you with: {message}"
        memory = f"User asked: {message[:50]}..."
        return response, memory
```

### IConversationFlow Pattern
```python
# conversation_flows/advanced_helper/advanced_helper.py
import uuid
from jinja2 import Environment
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient

from ingenious.models.chat import ChatRequest, ChatResponse
from ingenious.services.chat_services.multi_agent.service import IConversationFlow

class ConversationFlow(IConversationFlow):
    async def get_conversation_response(
        self, chat_request: ChatRequest
    ) -> ChatResponse:
        try:
            # Get model configuration
            models = self.Get_Models()
            model_config = models[0]

            # Load and render template
            try:
                template_content = await self.Get_Template(
                    file_name="advanced_helper_prompt.jinja"
                )
            except Exception:
                # Fallback template
                template_content = "You are a helpful assistant. User: {{ user_input }}"

            env = Environment()
            template = env.from_string(template_content)
            rendered_prompt = template.render(
                user_input=chat_request.user_prompt,
                thread_memory=getattr(chat_request, 'thread_memory', '')
            )

            # Create Azure OpenAI client
            model_client = AzureOpenAIChatCompletionClient(
                model=model_config.model,
                api_key=model_config.api_key,
                azure_endpoint=model_config.base_url,
                azure_deployment=model_config.deployment or model_config.model,
                api_version=model_config.api_version,
            )

            # Create agent and get response
            agent = AssistantAgent(
                name="advanced_helper",
                system_message=rendered_prompt,
                model_client=model_client,
            )

            response = await agent.on_messages(
                messages=[TextMessage(content=chat_request.user_prompt, source="user")],
                cancellation_token=None,  # Add proper cancellation token
            )

            await model_client.close()

            return ChatResponse(
                thread_id=chat_request.thread_id,
                message_id=str(uuid.uuid4()),
                agent_response=response.chat_message.content,
                token_count=0,
                max_token_count=0,
                memory_summary=f"Advanced help: {chat_request.user_prompt[:50]}...",
            )

        except Exception as e:
            self._logger.error(f"Error in advanced helper: {str(e)}")
            return ChatResponse(
                thread_id=chat_request.thread_id,
                message_id=str(uuid.uuid4()),
                agent_response="I apologize, but I encountered an error. Please try again.",
                token_count=0,
                max_token_count=0,
                memory_summary=f"Error in advanced helper: {str(e)[:50]}...",
            )
```
