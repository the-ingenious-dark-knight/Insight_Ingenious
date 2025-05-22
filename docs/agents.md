# Working with Agents

This document provides detailed information about working with agents in Insight Ingenious.

## What are Agents?

In Insight Ingenious, an agent is an AI entity designed to perform specific tasks and engage in conversations. Agents are configured with specific models, prompts, and behaviors to serve different purposes in your application.

## Agent Architecture

The agent system in Insight Ingenious is built around the following components:

1. **Agent Model**: The core definition of an agent, including its configuration and behavior
2. **Agent Chat**: Represents a conversation between agents or between an agent and a user
3. **Chat Service**: Manages the flow of messages between agents and users

## Built-in Agent Types

Insight Ingenious includes several built-in agent types:

### 1. Basic Assistant Agent

A simple agent that responds to user messages directly.

```yaml
agents:
  - name: "assistant"
    model_config:
      model: "gpt-4o"
      temperature: 0.7
    system_prompt: "You are a helpful assistant."
```

### 2. Function-enabled Agent

An agent that can call functions/tools to perform specific actions.

```yaml
agents:
  - name: "function_agent"
    model_config:
      model: "gpt-4o"
      temperature: 0.7
    system_prompt: "You are a helpful assistant with tool access."
    tools:
      - name: "search_web"
        description: "Search the web for information"
        parameters:
          query:
            type: "string"
            description: "The search query"
```

### 3. Router Agent

An agent that routes conversations to other agents based on the content.

```yaml
agents:
  - name: "router"
    model_config:
      model: "gpt-4o"
      temperature: 0.3
    system_prompt: "You are a router agent that directs requests to the appropriate specialized agent."
```

## Creating Custom Agents

You can create custom agents by extending the base Agent class in your extensions:

1. Create a new Python file in your extensions directory:

```python
# ingenious_extensions/agents/custom_agent.py
from ingenious.models.agent import Agent
from typing import Dict, Any, List
from ingenious.models.message import Message

class CustomAgent(Agent):
    """
    A custom agent implementation.
    """

    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        # Custom initialization

    async def process_message(self, message: Message) -> str:
        """
        Custom message processing logic.
        """
        # Your custom processing logic here
        return "Custom agent response"
```

2. Register your custom agent in the configuration:

```yaml
agents:
  - name: "my_custom_agent"
    type: "custom_agent"  # Points to your CustomAgent class
    model_config:
      model: "gpt-4o"
      temperature: 0.7
    system_prompt: "You are a custom agent."
```

## Agent Conversation Flows

Insight Ingenious supports different conversation flow types:

### 1. Basic Flow

A simple back-and-forth conversation between a user and a single agent.

```yaml
conversation_flows:
  - name: "simple_chat"
    type: "basic"
    primary_agent: "assistant"
```

### 2. Multi-Agent Flow

A conversation involving multiple agents, where agents can talk to each other.

```yaml
conversation_flows:
  - name: "team_discussion"
    type: "multi_agent"
    agents: ["researcher", "critic", "summarizer"]
    coordinator: "coordinator_agent"
    max_turns: 5
```

### 3. Sequential Flow

A conversation that follows a sequence of agent interactions.

```yaml
conversation_flows:
  - name: "sequential_process"
    type: "sequential"
    agent_sequence: ["input_processor", "analyzer", "generator"]
```

## Agent System Prompts

The system prompt is a crucial part of agent configuration. It defines the agent's personality, capabilities, and behavior. Some tips for effective system prompts:

1. **Be specific**: Clearly define the agent's role and capabilities
2. **Set boundaries**: Specify what the agent should not do
3. **Provide context**: Give background information relevant to the agent's role
4. **Include examples**: Demonstrate the desired behavior with examples

Example system prompt:

```
You are a customer service agent for Acme Corporation.
Your role is to help customers with product inquiries, order status, and technical support.

DO:
- Maintain a professional, friendly tone
- Ask clarifying questions when needed
- Provide accurate information about our products
- Escalate complex technical issues to our support team

DON'T:
- Make up information about products
- Promise delivery dates you can't verify
- Discuss our competitors' products
- Share internal company information

Our primary products include:
- AcmeWidget (smart home device)
- AcmeConnect (subscription service)
- AcmeCare (extended warranty)

When addressing technical issues, always first ask for the product model and firmware version.
```

## Agent Memory and State

Agents in Insight Ingenious maintain conversation state through the chat history repository. This provides agents with context from previous interactions in the same conversation.

To access and use this history:

```python
chat_history = self.chat_history_repository.get_messages(conversation_id)
```

## Using Agent Tools (Function Calling)

Agents can be equipped with tools that allow them to perform specific actions:

```yaml
agents:
  - name: "research_assistant"
    model_config:
      model: "gpt-4o"
      temperature: 0.7
    system_prompt: "You are a research assistant."
    tools:
      - name: "search_database"
        description: "Search the research database"
        parameters:
          query:
            type: "string"
            description: "The search query"
          filters:
            type: "object"
            properties:
              year:
                type: "number"
              author:
                type: "string"
```

In your custom code, you can implement the tool functionality:

```python
class ResearchAgent(Agent):
    def __init__(self, name, config):
        super().__init__(name, config)
        self.register_tool("search_database", self.search_database)

    async def search_database(self, query, filters=None):
        # Implementation of database search
        return {"results": [...]}
```

## Agent Events and Callbacks

Insight Ingenious provides an event system to track agent activities:

```python
@agent.on_message_received
async def handle_message(message):
    print(f"Received message: {message.content}")

@agent.on_response_sent
async def handle_response(message):
    print(f"Sent response: {message.content}")
```

## Testing Agents

To test your agents, you can use the CLI test commands:

```bash
# Test a specific agent
ingen_cli test-agent --agent-name my_agent --message "Hello, agent!"

# Run a batch of predefined tests
ingen_cli run-test-batch
```

## Debugging Agents

For debugging agents, you can:

1. **Enable Debug Logging**:
   ```yaml
   log_level: "DEBUG"
   ```

2. **Use the Diagnostic API**:
   ```
   GET /api/v1/diagnostic/agent/{agent_name}
   ```

3. **Trace Conversation Flows**:
   ```
   POST /api/v1/diagnostic/trace-conversation
   ```

4. **Review Agent Logs**:
   Agent activities are logged to the console and log files based on your logging configuration.
