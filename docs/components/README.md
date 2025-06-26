# Components Reference

This document provides detailed information about the key components of the Insight Ingenious framework.

## Multi-Agent Framework

### ConversationPattern

The `ConversationPattern` class is the foundation for defining how agents interact with each other.

#### Core Patterns

| Pattern | Description | Use Case |
|---------|-------------|----------|
| `classification_agent` | Classifies input and routes to topic-specific agents | Content classification, intent detection |
| `knowledge_base_agent` | Searches and retrieves information from knowledge bases | Question answering, information retrieval |
| `pandas_agent` | Processes and analyzes data using pandas | Data analysis, visualization |
| `sql_manipulation_agent` | Generates and executes SQL queries | Database interactions, data querying |
| `web_critic_agent` | Searches the web and fact-checks information | Research, fact verification |
| `education_expert` | Generates educational content and lesson plans | Educational material creation |

#### Key Methods

- `__init__(default_llm_config: dict, topics: list, memory_record_switch: bool, memory_path: str, thread_memory: str)`: Initializes the pattern
- `get_conversation_response(input_message: str) -> [str, str]`: Core method that processes input and returns agent response

### ConversationFlow

The `ConversationFlow` class implements specific use cases using conversation patterns.

#### Core Flows

| Flow | Description | Pattern Used |
|------|-------------|--------------|
| `classification_agent` | Routes inputs to specialized agents | `classification_agent` |
| `knowledge_base_agent` | Answers questions using knowledge bases | `knowledge_base_agent` |
| `pandas_agent` | Analyzes data and creates visualizations | `pandas_agent` |
| `sql_manipulation_agent` | Executes SQL queries based on natural language | `sql_manipulation_agent` |
| `web_critic_agent` | Searches the web and fact-checks information | `web_critic_agent` |

#### Key Methods

- `get_conversation_response(message: str, topics: list, thread_memory: str, memory_record_switch: bool, thread_chat_history: list) -> ChatResponse`: Processes input and returns response

### Agents

Agents are specialized AI entities that perform specific tasks in the conversation.

#### Core Agent Types

| Agent Type | Description | Used In |
|------------|-------------|---------|
| `AssistantAgent` | Standard agent for task completion | All patterns |
| `UserProxyAgent` | Represents the user in agent conversations | All patterns |
| `RetrieveUserProxyAgent` | User proxy with document retrieval capabilities | Knowledge-based patterns |
| `MultimodalConversableAgent` | Agent that can process images and text | `pandas_agent` |

#### Agent Definition

Agents are defined in markdown files with the following sections:

- **Name and Persona**: Agent identity
- **System Message**: Core instructions
- **Backstory**: Context and background
- **Instructions**: Detailed behavior guidelines
- **Examples**: Sample interactions

## Data Models

### Chat Models

These models define the structure of chat interactions:

- `ChatRequest`: Represents a user request
  - `thread_id`: Conversation thread identifier
  - `user_prompt`: User's input message
  - `event_type`: Type of event
  - `conversation_flow`: Which conversation flow to use

- `ChatResponse`: Represents an agent response
  - `response`: The content returned to the user
  - `metadata`: Additional information about the response

### Configuration Models

These models define the structure of configuration:

- `Config`: Top-level configuration model
  - `chat_history`: Chat history configuration
  - `models`: LLM model configurations
  - `logging`: Logging configuration
  - `tool_service`: Tool service configuration
  - `chat_service`: Chat service configuration
  - `chainlit_configuration`: Web UI configuration
  - `azure_search_services`: Search service configurations
  - `azure_sql_services`: SQL service configuration
  - `file_storage`: File storage configuration

- `Profile`: Contains sensitive configuration
  - `name`: Profile identifier
  - `models`: Model-specific API keys and endpoints
  - `azure_search_services`: Search service API keys
  - `web_configuration`: Authentication credentials

## Services

### ChatService

The `ChatService` interface defines the chat interaction API:

- `get_chat_response(chat_request: IChatRequest) -> IChatResponse`: Processes a chat request and returns a response

#### MultiAgentChatService

Implementation of `ChatService` that uses the multi-agent framework:

- `__init__(config: Config, chat_history_repository: ChatHistoryRepository, conversation_flow: str)`: Initializes the service
- `get_chat_response(chat_request: IChatRequest) -> IChatResponse`: Processes a chat request using the specified conversation flow

### ToolFunctions

The `ToolFunctions` class provides utility functions for agents:

- `execute_sql_local`: Executes SQL queries against local databases
- `execute_sql_azure`: Executes SQL queries against Azure SQL databases
- `search_azure`: Searches Azure Cognitive Search indices

## Storage

### ChatHistoryRepository

The `ChatHistoryRepository` interface defines chat history storage:

- `add_message(message: Message) -> str`: Adds a message to the history
- `get_thread_messages(thread_id: str) -> List[Message]`: Retrieves messages for a thread

#### Implementations

- `SQLiteChatHistoryRepository`: Stores chat history in SQLite
- `CosmosChatHistoryRepository`: Stores chat history in Azure Cosmos DB

### FileStorage

The `FileStorage` class manages file operations:

- `read_file(file_name: str, file_path: str) -> str`: Reads a file
- `write_file(content: str, file_name: str, file_path: str) -> bool`: Writes content to a file
- `get_prompt_template_path(revision_id: str) -> str`: Gets the path to a prompt template

#### Implementations

- `LocalFileStorage`: Stores files on the local filesystem
- `AzureFileStorage`: Stores files in Azure Blob Storage

## Web Interface

### Chainlit Integration

The Chainlit integration provides a web UI for chat interactions:

- `app.py`: Chainlit application definition
- `datalayer.py`: Data layer for Chainlit
- `index.html`: Landing page

### Prompt Tuner

The prompt tuner provides tools for developing and testing prompts:

- `run_flask_app.py`: Flask app for the prompt tuner
- `event_processor.py`: Processes prompt testing events
- `payload.py`: Handles test payloads

## Command Line Interface

The CLI provides commands for managing the framework:

- `initialize-new-project`: Creates a new project structure
- `run-rest-api-server`: Starts the FastAPI server with REST endpoints
- `run-test-batch`: Runs tests on agent prompts
- `run-prompt-tuner`: Starts the prompt tuning web application
- `dataprep`: Data preparation utilities including Scrapfly crawler

## API Layer

### FastAPI Integration

The API layer is built with FastAPI:

- `main.py`: Main FastAPI application
- `api/routes/`: API route definitions
  - `chat.py`: Chat endpoint
  - `message_feedback.py`: Feedback endpoint
  - `diagnostic.py`: Diagnostic endpoints
  - `prompts.py`: Prompt management endpoints

## Extension Points

### Custom Agents

Create custom agents by adding:

- `agent.md`: Agent definition
- `tasks/task.md`: Task description

### Custom Conversation Patterns

Create custom patterns by implementing:

- `ConversationPattern` class with required methods
- `ConversationFlow` class that uses the pattern

### Custom API Routes

Create custom routes by implementing:

- `Api_Routes` class with `add_custom_routes` method

### Custom Templates

Create custom prompt templates:

- Jinja2 templates in `templates/prompts/`
