import os
import sys
from typing import Dict, Optional
import uuid

import chainlit as cl
import chainlit.data as cl_data

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), './../../'))
sys.path.append(parent_dir)
import ingenious.config.config as ig_config
from ingenious.models.chat import ChatRequest
import ingenious.dependencies as deps
import ingenious.chainlit.datalayer as cl_data_custom
from chainlit.types import ThreadDict

user = {}
config = ig_config.get_config()
data_layer = cl_data_custom.DataLayer()
cl_data._data_layer = data_layer


@cl.on_chat_resume
async def on_chat_resume(thread: ThreadDict):
    print(f"Resuming chat session!: {thread['id']}")
    root_messages = [m for m in thread["steps"] if m["parentId"] == None]
    for message in root_messages:
        if message["type"] == "user_message":
            pass
        else:
            pass

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

@cl.on_message
async def main(message: cl.Message):
    user: cl.User = cl.user_session.get('user')
    new_guid = uuid.uuid4()
    chat_request: ChatRequest = ChatRequest(
        thread_id=str(new_guid),
        user_id="test",
        user_prompt="",
        user_name="test",
        topic="",
        memory_record=True,
        conversation_flow="sql_manipulation_agent"
    )

    cs = deps.get_chat_service(
        deps.get_chat_history_repository(),
        conversation_flow=chat_request.conversation_flow
    )

    chat_request.user_prompt = (message.content)
    ret = await cs.get_chat_response(chat_request)

    await cl.Message(
        content=ret.agent_response,
    ).send()

@cl.set_starters
async def set_starters():
    return [
        cl.Starter(
            label="Let's do a test.",
            message=f"Can I have a count of all observations by gender?",
            icon="/public/idea.png",
        )
    ]

@cl.oauth_callback
def oauth_callback(
        provider_id: str,
        token: str,
        raw_user_data: Dict[str, str],
        default_user: cl.User,
) -> Optional[cl.User]:
    return default_user