import datetime
import json

# Ingenious imports
import ingenious.config.config as ingen_config
import ingenious.dependencies as ingen_deps
from ingenious.models.chat import ChatRequest
from ingenious.services.chat_service import ChatService

thread_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
user_prompt = "give me some test message"

chat_history_repository = ingen_deps.get_chat_history_repository()

chat_request = ChatRequest(
    thread_id=thread_id, user_prompt=user_prompt, conversation_flow="pet_insights"
)

chat_service = ChatService(
    chat_service_type="multi_agent",
    chat_history_repository=chat_history_repository,
    conversation_flow="pet_insights",
    config=ingen_config.get_config(),
)

response = chat_service.get_chat_response(chat_request)

response_content = json.loads(
    json.loads(response.agent_response)["response"]["content"]
)
