import logging
from ingenious.db.chat_history_repository import ChatHistoryRepository
from ingenious.errors.content_filter_error import ContentFilterError
from ingenious.external_services.openai_service import OpenAIService
from ingenious.models.chat import Action, ChatRequest, ChatResponse, KnowledgeBaseLink, Product
from ingenious.models.message import Message
from ingenious.models.tool_call_result import ActionToolCallResult, KnowledgeBaseToolCallResult, ProductToolCallResult
from ingenious.services.tool_service import ToolService
from ingenious.utils.conversation_builder import (
    build_message, build_system_prompt,
    build_user_message, build_assistant_message, build_tool_message)
from ingenious.utils.token_counter import num_tokens_from_messages, get_max_tokens
from openai.types.chat import ChatCompletionMessageParam

logger = logging.getLogger(__name__)


class fast_agent_chat_service:
    def __init__(
            self,
            chat_history_repository: ChatHistoryRepository,
            openai_service: OpenAIService,
            tool_service: ToolService,
            conversation_pattern: str = ""):
        self.chat_history_repository = chat_history_repository
        self.openai_service = openai_service
        self.tool_service = tool_service

    async def get_chat_response(self, chat_request: ChatRequest) -> ChatResponse:
        # Initialize messages list
        messages: list[ChatCompletionMessageParam] = []

        # Initialize additional response fields - to be populated later
        follow_up_questions: dict[str, str] = {}
        actions: list[Action] = []
        knowledge_base_links: list[KnowledgeBaseLink] = []
        products: list[Product] = []

        # Check if thread exists
        if not chat_request.thread_id:
            # Create thread
            chat_request.thread_id = await self.chat_history_repository.create_thread()
        else:
            # Get thread messages & add to messages list
            thread_messages = await self.chat_history_repository.get_thread_messages(chat_request.thread_id)
            for thread_message in thread_messages:
                # Validate user_id
                if thread_message.user_id != chat_request.user_id:
                    raise ValueError("User ID does not match thread messages.")

                # Validate content_filter_results not present
                if thread_message.content_filter_results:
                    raise ContentFilterError(content_filter_results=thread_message.content_filter_results)

                # Add thread message to messages list
                message = build_message(
                    role=thread_message.role,
                    content=thread_message.content,
                    user_name=chat_request.user_name,
                    tool_calls=thread_message.tool_calls,
                    tool_call_id=thread_message.tool_call_id,
                    tool_call_function=thread_message.tool_call_function)
                messages.append(message)

        # If system prompt is not first message add it in the beginning
        if not messages or messages[0]["role"] != "system":

            # Add system prompt
            system_prompt_message = build_system_prompt(user_name=chat_request.user_name)
            messages.insert(0, system_prompt_message)

            # Save system prompt message
            await self.chat_history_repository.add_message(
                Message(
                    user_id=chat_request.user_id,
                    thread_id=chat_request.thread_id,
                    role=system_prompt_message["role"],
                    content=system_prompt_message["content"])
            )

        # Add latest user message
        user_message = build_user_message(chat_request.user_prompt, chat_request.user_name)
        messages.append(user_message)

        # Save user message
        user_message_id = await self.chat_history_repository.add_message(
            Message(
                user_id=chat_request.user_id,
                thread_id=chat_request.thread_id,
                role=user_message["role"],
                content=str(user_message["content"]))
        )

        # Get tool definitions
        tools = self.tool_service.get_tool_definitions()

        try:
            # Generate response from OpenAI with tool calls
            response_task = self.openai_service.generate_response(messages, tools)
            response = await response_task

        except ContentFilterError as cfe:
            # Update user message with content filter results
            await self.chat_history_repository.update_message_content_filter_results(
                user_message_id, chat_request.thread_id, cfe.content_filter_results)
            raise

        # Handle tool calls if any
        if response.tool_calls:
            # Convert to plain dict for DB storage
            tool_calls_list = [tool_call.to_dict() for tool_call in response.tool_calls]

            # Add assistants tool request
            assistant_message = build_assistant_message(response.content, tool_calls_list)
            messages.append(assistant_message)

            # Save assistant message
            await self.chat_history_repository.add_message(
                Message(
                    user_id=chat_request.user_id,
                    thread_id=chat_request.thread_id,
                    role=assistant_message["role"],
                    tool_calls=tool_calls_list)
            )

            # Process each tool call
            for tool_call in response.tool_calls:
                tool_response = await self.tool_service.execute_tool_call(tool_call)

                # Check return type from tool call
                if isinstance(tool_response, ProductToolCallResult):
                    products.extend(tool_response.products)

                if isinstance(tool_response, KnowledgeBaseToolCallResult):
                    knowledge_base_links.extend(tool_response.knowledge_base_links)

                if isinstance(tool_response, ActionToolCallResult):
                    actions.extend(tool_response.actions)

                # Add tool response
                tool_message = build_tool_message(
                    content=tool_response.results,
                    tool_call_id=tool_call.id,
                    function_name=tool_call.function.name)
                messages.append(tool_message)

                # Save tool message
                await self.chat_history_repository.add_message(
                    Message(
                        user_id=chat_request.user_id,
                        thread_id=chat_request.thread_id,
                        role=tool_message["role"],
                        content=tool_message["content"],
                        tool_call_id=tool_call.id,
                        tool_call_function=tool_call.function.to_dict())
                )

            # Get the final response from the model
            final_response = await self.openai_service.generate_response(messages)
            agent_response = final_response.content
        else:
            agent_response = response.content

        # Save agent response
        agent_message_id = await self.chat_history_repository.add_message(
            Message(
                user_id=chat_request.user_id,
                thread_id=chat_request.thread_id,
                role="assistant",
                content=agent_response)
        )

        # Get token counts
        max_token_count = get_max_tokens("gpt-3.5-turbo-0125")
        token_count = num_tokens_from_messages(messages)
        logger.debug(f"Token count: {token_count}/{max_token_count}")

        return ChatResponse(
            thread_id=chat_request.thread_id,
            message_id=agent_message_id,
            agent_response=agent_response or "Sorry we were unable to generate a response. Please try again.",
            followup_questions=follow_up_questions,
            actions=actions,
            knowledge_base_links=[],  # deleted for now
            products=products,
            token_count=token_count,
            max_token_count=max_token_count
        )
