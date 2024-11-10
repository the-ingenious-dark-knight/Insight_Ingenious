import chainlit as cl
import chainlit.data as cl_data
from chainlit.input_widget import Select

from ingenious.models.chat import ChatRequest
import ingenious.dependencies as deps
import uuid

import ingenious.chainlit.datalayer as cl_data_custom

data_layer = cl_data_custom.DataLayer()
cl_data._data_layer = data_layer


@cl.on_message
async def main(message: cl.Message):
    settings = await cl.ChatSettings(
        [
            Select(
                id="Pattern",
                label="Ingenious Pattern",
                values=["classification_agent", "sql_manipulation_agent"],
                initial_index=0,
            ),
        ]
    ).send()

    new_guid = uuid.uuid4()
    chat_request: ChatRequest = ChatRequest(
        thread_id="demo_" + str(new_guid),
        user_id="Demo",
        user_prompt=message.content,
        user_name="Demo",
        topic="",
        memory_record=True,
        conversation_flow= settings["Pattern"]
    )

    cs = deps.get_chat_service(
        deps.get_chat_history_repository(),
        conversation_flow=chat_request.conversation_flow
    )

    ret = await cs.get_chat_response(chat_request)

    await cl.Message(
        content=ret.agent_response,
    ).send()


# Setting starters based on selected pattern
# @cl.set_starters
# async def set_starters():
#     if settings["Pattern"] == "classification_agent":
#         return [
#             cl.Starter(
#                 label="Let's do a test.",
#                 message="Can you tell me about basketball?",
#                 icon="/public/idea.png",
#             )
#         ]
#     elif settings["Pattern"] == "sql_manipulation_agent":
#         return [
#             cl.Starter(
#                 label="Let's do a test.",
#                 message="Can I have a count of all observations by gender?",
#                 icon="/public/idea.png",
#             )
#         ]

#cl.on_chat_resume
@cl.on_chat_start
async def on_chat_start():
    print("A new chat session has started!")
    print(f"Thread ID: {cl.user_session.get('id')}")
    user: cl.User = cl.user_session.get('user')
    await data_layer.set_user(user)
    if user:
        print(f"User ID: {user.identifier}")

    global settings
    settings = await cl.ChatSettings(
        [
            Select(
                id="Pattern",
                label="Ingenious Pattern",
                values=["classification_agent", "sql_manipulation_agent"],
                initial_index=0,
            ),
        ]
    ).send()
    print(f"Selected Pattern: {settings['Pattern']}")
    #value = settings["Pattern"]


@cl.on_stop
def on_stop():
    print("The user wants to stop the task!")


@cl.on_chat_end
def on_chat_end():
    print("The user disconnected!")