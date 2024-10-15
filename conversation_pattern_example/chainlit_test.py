import sys
import os
from typing import Dict, Optional
import chainlit as cl
import chainlit.data as cl_data
#from chainlit.data.sql_alchemy import SQLAlchemyDataLayer

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
    #memory = ConversationBufferMemory(return_messages=True)
    print(f"Resuming chat session!: {thread['id']}")
    root_messages = [m for m in thread["steps"] if m["parentId"] == None]
    for message in root_messages:
        if message["type"] == "user_message":
            pass
            #memory.chat_memory.add_user_message(message["output"])
        else:
            pass
            #memory.chat_memory.add_ai_message(message["output"])

    #cl.user_session.set("memory", memory)


@cl.on_chat_start
async def on_chat_start():
    print("A new chat session has started!")
    print(f"Thread ID: {cl.user_session.get('id')}")
    user: cl.User = cl.user_session.get('user')
    await data_layer.set_user(user)
    if user:
        print(f"User ID: {user.identifier}")    
    #m = cl.Message("Hello! I'm here to help you with your morning routine. Let's get started!")
    #await m.send()



@cl.on_stop
def on_stop():
    print("The user wants to stop the task!")

@cl.on_chat_end
def on_chat_end():
    print("The user disconnected!")

@cl.on_message
async def main(message: cl.Message):
    user: cl.User = cl.user_session.get('user')
    chat_request: ChatRequest = ChatRequest(
        thread_id=cl.user_session.get('id'),
        user_id=user.identifier,
        user_prompt=message.content,
        user_name="test",
        conversation_flow="classification_agent"
    )
    
    

    cs = deps.get_chat_service(
            deps.get_chat_history_repository(),
            deps.get_openai_service(),
            deps.get_tool_service(
                deps.get_product_search_manager(),
                deps.get_knowledge_base_search_manager()),
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
            label="Morning routine ideation",
            message="Can you help me create a personalized morning routine that would help increase my productivity throughout the day? Start by asking me about my current habits and what activities energize me in the morning.",
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
