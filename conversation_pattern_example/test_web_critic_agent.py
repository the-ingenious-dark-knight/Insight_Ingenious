import os
import sys
import uuid

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), './../'))
sys.path.append(parent_dir)

import ingenious.dependencies as deps
from ingenious.models.chat import ChatRequest, ChatResponse
import asyncio
import ingenious.config.config as config

#Classification agent with improved memory using RAG user proxy.
async def process_message(chat_request: ChatRequest) -> ChatResponse:

    user = await deps.get_chat_history_repository().get_user(chat_request.user_name)
    print("user_id:", chat_request.user_id)
    print("user:",user)

    cs = deps.get_chat_service(
            deps.get_chat_history_repository(),
            conversation_flow=chat_request.conversation_flow
    )

    res = await cs.get_chat_response(chat_request)
    return res

new_guid = uuid.uuid4()
chat_request: ChatRequest = ChatRequest(
        thread_id=str(new_guid),
        user_id="elliot",
        user_prompt="",
        user_name="elliot",
        topic= "",
        memory_record = True,
        conversation_flow="web_critic_agent"
    )

chat_request.user_prompt = ("Write me a short story in 100 words based on the following: "
                            "The Australia men's national cricket team represents "
                            "Australia in men's international cricket. "
                            "It is the joint oldest team in Test cricket history,"
                            " playing in the first ever Test match in 1999;"
                            " the team current coach is Elliot Zhu.")
res = ChatResponse = asyncio.run(process_message(chat_request=chat_request))


print(res)
