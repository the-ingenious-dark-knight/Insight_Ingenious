import chainlit as cl
import chainlit.data as cl_data

from ingenious.models.chat import ChatRequest
import ingenious.dependencies as deps
import uuid

import ingenious.chainlit.datalayer as cl_data_custom
data_layer = cl_data_custom.DataLayer()
cl_data._data_layer = data_layer


@cl.on_message
async def main(message: cl.Message):
    new_guid = uuid.uuid4()
    chat_request: ChatRequest = ChatRequest(
        thread_id="demo_" + str(new_guid),
        user_id="Demo",
        user_prompt=message.content,
        user_name="Demo",
        topic="tennis, basketball",
        memory_record=True,
        conversation_flow="classification_agent"
    )

    cs = deps.get_chat_service(
            deps.get_chat_history_repository(),
            conversation_flow=chat_request.conversation_flow
    )            
    
    ret = await cs.get_chat_response(chat_request)

    await cl.Message(
        content=ret.agent_response,
    ).send()


@cl.set_starters
async def set_starters():
    return [
        cl.Starter(
            label="Let's do a test.",
            message=f"Can you tell me about basketball?",
            icon="/public/idea.png",
        )
    ]


@cl.on_chat_start
async def on_chat_start():
    print("A new chat session has started!")
    print(f"Thread ID: {cl.user_session.get('id')}")
    user: cl.User = cl.user_session.get('user')
    await data_layer.set_user(user)
    if user:
        print(f"User ID: {user.identifier}")

@cl.on_stop
def on_stop():
    print("The user wants to stop the task!")

@cl.on_chat_end
def on_chat_end():
    print("The user disconnected!")