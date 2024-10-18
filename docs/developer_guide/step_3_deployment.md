---

    weight: 4

---

# Step 3 - Deploying a New Prefab


In this step, you will learn how to set up the **Ingenious** package locally and deploy a new pattern.

## How to Write Your Test Workflow

You will need to write and test your custom workflow. The test files should be stored in the `conversation_pattern_example` directory for better organization.

### 1. Workflow Template

Below demonstrates the template to interact with the **Ingenious** package to process chat requests using a multi-agent system.

**Importing Modules**: 

Essential modules like `ToolFunctions`, `ChatRequest`, `ChatResponse`, and configuration settings are imported from the **Ingenious** package. These will be used to handle the chat logic.


```python
import os
import sys
import uuid

# Adding the parent directory to the system path to access necessary modules
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), './../'))
sys.path.append(parent_dir)

from ingenious.services.chat_services.multi_agent.tool_factory import ToolFunctions
import ingenious.dependencies as deps
import asyncio
from ingenious.models.chat import ChatRequest, ChatResponse
import ingenious.config.config as config
```

**Process Message Function**:

```python
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
```

- The `process_message` function is asynchronous, allowing it to handle multiple requests without blocking the main thread.
- It retrieves the user’s chat history using `get_user()`.
- A chat service (`cs`) is initialized with the user’s conversation flow, and a response is generated using `get_chat_response()`.


**Generate a Chat Request**:

```python
new_guid = uuid.uuid4()
chat_request: ChatRequest = ChatRequest(
    thread_id=str(new_guid),
    user_id="elliot",  # Assuming the user_id is "elliot"
    user_prompt="",
    user_name="elliot",
    conversation_flow="knowledge_base_agent"  # Using the classification agent flow
)
```


- A new GUID (Globally Unique Identifier) is generated for each chat session.
- A `ChatRequest` object is created, specifying the `thread_id`, `user_id`, `user_name`, and the conversation flow. In this case, we are using the **knowledge_base_agent** flow for handling knowledge-based queries.


**Reset Memory**

We store the summarized conversation memory locally in a markdown file.

```python
_config = config.get_config()
memory_path = _config.chat_history.memory_path
with open(f"{memory_path}/context.md", "w") as memory_file:
    memory_file.write("new conversation, please derive context from question")
```

- This block resets the memory by writing a default context into the memory file, which helps simulate a fresh conversation.


### 2. Write Examples
Please provide an example of a conversation that can be addressed using this specific pattern, such as the one shown in `conversation_pattern_example/test_multitool.py`.


=== "Example 1: Ambiguous Topic with Memory"

    ```python
    chat_request.user_prompt = f"Tell me about contact number?"
    res: ChatResponse = asyncio.run(process_message(chat_request=chat_request))
    
    chat_request.user_prompt = f"for safety?"
    res = asyncio.run(process_message(chat_request=chat_request))
    ```
    
    In this example, the conversation agent processes an ambiguous user query about a "contact number" and then follows up with an additional prompt, "for safety?", where memory helps to maintain context and derive the right response.



=== "Example 2: Known Topics Search"

    ```python
    # chat_request.user_prompt = f"Who is our first aider in health and emergency coordinator in safety?"
    # res: ChatResponse = asyncio.run(process_message(chat_request=chat_request))
    ```
    
    This example shows how a more direct query about known topics (e.g., first aider) can be processed using the same chat service.


### 3. Output Final Response

After processing, the final response from the agent is printed to the console for review. 

```python
print(res)
```

This is the message which the end user will observe.



## Release a Build

Once your workflow is tested, you can release a new build of the **Ingenious** package by running the following command:

```bash
python setup.py sdist bdist_wheel
```

This will generate a source distribution and a built distribution, which can be shared or deployed as needed.

