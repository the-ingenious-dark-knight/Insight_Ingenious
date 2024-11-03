import chainlit as cl
from ingenious.models.chat import ChatRequest
import ingenious.dependencies as deps


@cl.on_message
async def main(message: cl.Message):
    chat_request: ChatRequest = ChatRequest(
        thread_id="123",
        user_id="123",
        user_prompt=message.content,
        user_name="test",
        conversation_flow="test_flow"
    )

    cs = deps.get_chat_service(
            deps.get_chat_history_repository(),
            conversation_flow=chat_request.conversation_flow
    )            
    
    ret = await cs.get_chat_response(chat_request)

    await cl.Message(
        content=ret.agent_response,
    ).send()
