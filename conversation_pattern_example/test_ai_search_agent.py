import os
import sys
import uuid

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), './../'))
sys.path.append(parent_dir)

import ingenious.dependencies as deps
import asyncio
from ingenious.models.chat import ChatRequest, ChatResponse


async def process_message(chat_request: ChatRequest) -> ChatResponse:
    user = await deps.get_chat_history_repository().get_user(chat_request.user_name)
    print("user_id:", chat_request.user_id)
    print("user:", user)
    cs = deps.get_chat_service(
        chat_history_repository=deps.get_chat_history_repository(),
        conversation_flow=chat_request.conversation_flow
    )
    res = await cs.get_chat_response(chat_request)
    return res


# Generate a unique thread ID and create a chat request
new_guid = uuid.uuid4()
chat_request: ChatRequest = ChatRequest(
    thread_id=str(new_guid),
    user_id="elliot",  # Assuming the user_id is "elliot"
    user_prompt="",
    user_name="elliot",
    conversation_flow="knowledge_base_agent",  # Using the classification agent flow
    topic = "health, safety",
    memory_record = True,
)


# Example 1 search knowledge base under one ambiguous topic
chat_request.user_prompt = f"give me contact number?"
res: ChatResponse = asyncio.run(process_message(chat_request=chat_request))


# Print the final response
print(res)