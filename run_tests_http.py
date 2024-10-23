import ingenious.cli as cli
import ingenious.config.config as config
from ingenious.models.chat import ChatRequest, ChatResponse
import threading
import time
import requests
from requests.auth import HTTPBasicAuth
import uuid
import asyncio
import json
from dataclasses import asdict
import subprocess

from ingenious.utils.namespace_utils import print_namespace_modules

# Make sure you have set the environment variables 
_config: config.Config = config.get_config()


# Assuming _config is already defined and imported
username = _config.web_configuration.authentication.username
password = _config.web_configuration.authentication.password


new_guid = uuid.uuid4()
chat_request: ChatRequest = ChatRequest(
        thread_id=str(new_guid),
        user_id="elliot123",
        user_prompt="",
        user_name="elliot",
        memory_record = True,
        topic = "tennis, basketball",
        conversation_flow="classification_agent"
    )

print(new_guid)

t = "tennis"
chat_request.user_prompt = f"Explain the game of {t} to me?"
print(chat_request.user_prompt)

j = chat_request.model_dump()
print(j)

response = requests.post(
    f"http://localhost:{_config.web_configuration.port}/api/v1/chat",
    #f"http://localhost:9000/api/v1/chat",
    json=j,
    auth=HTTPBasicAuth(username, password)
)


print(response.status_code)
print(response.json())
