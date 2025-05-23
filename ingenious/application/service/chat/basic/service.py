from ingenious.domain.interfaces.service.chat_service import IChatService
from ingenious.domain.model.chat import ChatRequest, ChatResponse

class basic_chat_service(IChatService):
    def __init__(self, config, chat_history_repository, conversation_flow):
        self.config = config
        self.chat_history_repository = chat_history_repository
        self.conversation_flow = conversation_flow

    async def get_chat_response(self, chat_request: ChatRequest) -> ChatResponse:
        # Return a minimal valid ChatResponse for test purposes
        return ChatResponse(
            thread_id=chat_request.thread_id or "test_thread",
            message_id="test_message",
            agent_response="Test agent response",
            token_count=1,
            max_token_count=10,
        )

    async def process_chat_request(self, chat_request: ChatRequest) -> ChatResponse:
        return await self.get_chat_response(chat_request)

__all__ = ["basic_chat_service"]
