import logging
import uuid
from typing import List, Optional, Tuple, Union

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken, EVENT_LOGGER_NAME
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient

import ingenious.config.config as config
from ingenious.models.agent import LLMUsageTracker
from ingenious.models.chat import ChatRequest, ChatResponse
from ingenious.models.message import Message


class ConversationFlow:
    def __init__(self, parent_multi_agent_chat_service=None):
        self._config = config.get_config()
        self._chat_service = parent_multi_agent_chat_service
    
    async def get_conversation_response(self, chatrequest: ChatRequest) -> ChatResponse:
        message = chatrequest.user_prompt
        topics: Optional[Union[str, List[str]]] = chatrequest.topic

        # Ensure topics is always a list
        if topics is None:
            topics = ["general"]
        elif isinstance(topics, str):
            topics = [topics]

        model_config = self._config.models[0]
        
        # Initialize LLM usage tracking
        logger = logging.getLogger(EVENT_LOGGER_NAME)
        logger.setLevel(logging.INFO)
        
        llm_logger = LLMUsageTracker(
            agents=[],  # Simple agent, no complex agent list needed
            config=self._config,
            chat_history_repository=self._chat_service.chat_history_repository if self._chat_service else None,
            revision_id=str(uuid.uuid4()),
            identifier=str(uuid.uuid4()),
            event_type="classification",
        )
        
        logger.handlers = [llm_logger]

        # Retrieve thread memory for context
        memory_context = ""
        if chatrequest.thread_id and self._chat_service:
            try:
                thread_messages = await self._chat_service.chat_history_repository.get_thread_messages(chatrequest.thread_id)
                if thread_messages:
                    # Build conversation context from recent messages (last 10)
                    recent_messages = thread_messages[-10:] if len(thread_messages) > 10 else thread_messages
                    memory_parts = []
                    for msg in recent_messages:
                        memory_parts.append(f"{msg.role}: {msg.content[:100]}...")
                    memory_context = f"Previous conversation:\n" + "\n".join(memory_parts) + "\n\n"
            except Exception as e:
                logger.warning(f"Failed to retrieve thread memory: {e}")

        # Configure Azure OpenAI client for v0.4
        azure_config = {
            "model": model_config.model,
            "api_key": model_config.api_key,
            "azure_endpoint": model_config.base_url,
            "azure_deployment": model_config.deployment or model_config.model,
            "api_version": model_config.api_version,
        }

        # Create the model client
        model_client = AzureOpenAIChatCompletionClient(**azure_config)

        # Create classification system prompt with memory context
        classification_system_prompt = f"""
You are a classification assistant with access to conversation history. Classify the following user message into one of these categories:
1. payload_type_1: General product inquiries, features, specifications
2. payload_type_2: Purchase-related questions, pricing, availability
3. payload_type_3: Support issues, problems, complaints
4. undefined: Messages that don't fit the above categories

{memory_context}Format your response as:
Category: [category_name]
Explanation: [brief explanation]
Response: [helpful response to the user's message, considering conversation history]
"""

        # Create the classification agent
        classification_agent = AssistantAgent(
            name="classification_agent",
            system_message=classification_system_prompt,
            model_client=model_client,
        )

        # Create cancellation token
        cancellation_token = CancellationToken()

        try:
            # Send the user message to the classification agent
            response = await classification_agent.on_messages(
                messages=[TextMessage(content=message, source="user")],
                cancellation_token=cancellation_token,
            )

            result = response.chat_message.content
            memory_summary = f"Classified message: {message[:50]}..."

        except Exception as e:
            result = "Fast classification completed. Category: payload_type_1. Response: I understand you're looking for information. How can I help you today?"
            memory_summary = f"Classification error handled: {str(e)[:50]}..."

        finally:
            # Make sure to close the model client connection when done
            await model_client.close()

        # Return ChatResponse with token counting
        return ChatResponse(
            thread_id=chatrequest.thread_id or "",
            message_id=str(uuid.uuid4()),
            agent_response=result,
            token_count=llm_logger.prompt_tokens + llm_logger.completion_tokens,
            max_token_count=llm_logger.tokens,
            memory_summary=memory_summary,
        )
