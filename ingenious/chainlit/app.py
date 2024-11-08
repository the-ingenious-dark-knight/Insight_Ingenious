import chainlit as cl
from ingenious.models.chat import ChatRequest
import ingenious.dependencies as deps
import uuid

@cl.on_message
async def main(message: cl.Message):
    new_guid = uuid.uuid4()
    chat_request: ChatRequest = ChatRequest(
        thread_id= "demo_"+str(new_guid),
        user_id="Demo",
        user_prompt=message.content,
        user_name="Demo",
        topic="",
        conversation_flow="sql_manipulation_agent"
    )

    cs = deps.get_chat_service(
            deps.get_chat_history_repository(),
            conversation_flow=chat_request.conversation_flow
    )            
    
    ret = await cs.get_chat_response(chat_request)

    await cl.Message(
        content=ret.agent_response,
    ).send()
