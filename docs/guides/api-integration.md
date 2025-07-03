# 🌐 API Integration Guide

Complete guide to using the Insight Ingenious REST API for integrating conversation workflows into your applications.

## 🚀 Quick Start

### Basic API Call

```bash
curl -X POST http://localhost:8081/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_prompt": "Hello, how are you?",
    "conversation_flow": "classification_agent"
  }'
```

### Response Format

```json
{
  "thread_id": "thread_123",
  "message_id": "msg_456",
  "agent_response": "...",
  "token_count": 150,
  "memory_summary": "User greeted the system"
}
```

## 📋 Workflow Categories

### ✅ Minimal Configuration Workflows

These work with just Azure OpenAI setup:

#### Classification Agent
Route input to specialized agents based on content:

```bash
curl -X POST http://localhost:8081/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_prompt": "Analyze this customer feedback: Great product, fast delivery!",
    "conversation_flow": "classification_agent"
  }'
```

#### Bike Insights
Sample domain-specific workflow for business analysis:

```bash
curl -X POST http://localhost:8081/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_prompt": "Show me bike sales trends for April 2023",
    "conversation_flow": "bike_insights"
  }'
```

### 🔍 Azure Search Required Workflows

#### Knowledge Base Agent
Search and retrieve information from Azure Cognitive Search indexes:

```bash
curl -X POST http://localhost:8081/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_prompt": "Find health and safety information about workplace hazards",
    "conversation_flow": "knowledge_base_agent"
  }'
```

**Requirements:**
- Azure Cognitive Search service
- Pre-configured search indexes
- Search API key in profiles.yml

### 📊 Database Required Workflows

#### SQL Manipulation Agent
Execute SQL queries based on natural language:

```bash
curl -X POST http://localhost:8081/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_prompt": "Show me the average student performance by subject",
    "conversation_flow": "sql_manipulation_agent"
  }'
```

**Requirements:**
- Azure SQL Database OR local SQLite database
- Database connection string in profiles.yml

#### Pandas Agent
Data analysis and visualization using pandas:

```bash
curl -X POST http://localhost:8081/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_prompt": "Analyze the dataset and create visualizations showing performance trends",
    "conversation_flow": "pandas_agent"
  }'
```

**Requirements:**
- Local CSV data files
- SQLite database configuration

### 🌐 Web Search Workflows

#### Web Critic Agent
Perform web search and fact-checking (currently uses mock data):

```bash
curl -X POST http://localhost:8081/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_prompt": "Fact-check this claim: Solar energy is now cheaper than fossil fuels",
    "conversation_flow": "web_critic_agent"
  }'
```

## 🔧 Configuration Management

### Check Workflow Status

Before using a workflow, check if it's properly configured:

```bash
# Check all workflows
curl http://localhost:8081/api/v1/workflows

# Check specific workflow
curl http://localhost:8081/api/v1/workflow-status/knowledge_base_agent
```

Example response:
```json
{
  "workflow": "knowledge_base_agent",
  "configured": false,
  "missing_config": [
    "azure_search_services.key: Missing in profiles.yml"
  ],
  "required_config": ["models", "chat_service", "azure_search_services"],
  "external_services": ["Azure OpenAI", "Azure Cognitive Search"],
  "ready": false,
  "test_command": "curl -X POST http://localhost:8081/api/v1/chat...",
  "documentation": "See docs/workflows/README.md for setup instructions"
}
```

## 🔐 Authentication

### Basic Authentication

When authentication is enabled:

```bash
# Using basic auth
curl -X POST http://localhost:8081/api/v1/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic $(echo -n username:password | base64)" \
  -d '{
    "user_prompt": "Hello",
    "conversation_flow": "classification_agent"
  }'
```

### Disable Authentication

For development, disable in `profiles.yml`:

```yaml
web_configuration:
  authentication:
    enable: false
```

## 💬 Conversation Management

### Thread Continuity

Maintain conversation context using thread IDs:

```bash
# First message
curl -X POST http://localhost:8081/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_prompt": "Hello, my name is John",
    "conversation_flow": "classification_agent",
    "thread_id": "user-john-session-1"
  }'

# Follow-up message (same thread_id)
curl -X POST http://localhost:8081/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_prompt": "What did I just tell you my name was?",
    "conversation_flow": "classification_agent",
    "thread_id": "user-john-session-1"
  }'
```

### Get Conversation History

```bash
curl http://localhost:8081/api/v1/conversations/user-john-session-1
```

## 📝 Request & Response Reference

### Chat Request

```typescript
{
  "user_prompt": string,          // Required: User's message
  "conversation_flow": string,    // Required: Workflow to use
  "thread_id"?: string,          // Optional: For conversation continuity
  "topic"?: string | string[],   // Optional: Additional context
  "memory_record"?: boolean,     // Optional: Whether to save to memory
  "thread_memory"?: string,      // Optional: Previous context
  "event_type"?: string         // Optional: Event classification
}
```

### Chat Response

```typescript
{
  "thread_id": string,           // Conversation thread identifier
  "message_id": string,          // Unique message identifier
  "agent_response": string,      // AI agent's response
  "token_count": number,         // Tokens used in generation
  "max_token_count": number,     // Maximum tokens allowed
  "memory_summary": string,      // Summary for memory storage
  "content_filter_results"?: any, // Content filtering results
  "tool_calls"?: any,           // Any tool calls made
  "tool_call_id"?: string,      // Tool call identifier
  "tool_call_function"?: any    // Tool function details
}
```

## 🚨 Error Handling

### Common Error Responses

#### 400 Bad Request
```json
{
  "detail": "conversation_flow not set",
  "workflow": null,
  "available_workflows": ["classification_agent", "bike_insights", "..."]
}
```

#### 404 Workflow Not Found
```json
{
  "detail": "Unknown workflow: invalid_workflow",
  "available_workflows": ["classification_agent", "bike_insights", "..."]
}
```

#### 406 Not Acceptable
```json
{
  "detail": "Content filtered by Azure OpenAI safety systems"
}
```

#### 413 Payload Too Large
```json
{
  "detail": "Token limit exceeded. Reduce message size or conversation history."
}
```

#### 500 Internal Server Error
```json
{
  "detail": "Azure Search service not configured",
  "workflow": "knowledge_base_agent",
  "required_config": ["azure_search_services.endpoint", "azure_search_services.key"],
  "documentation": "See docs/workflows/README.md for setup instructions"
}
```

### Error Handling Best Practices

```python
import requests
import json

def call_ingenious_api(prompt, workflow, thread_id=None):
    """Example error handling for API calls"""

    payload = {
        "user_prompt": prompt,
        "conversation_flow": workflow
    }

    if thread_id:
        payload["thread_id"] = thread_id

    try:
        response = requests.post(
            "http://localhost:8081/api/v1/chat",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 400:
            error = response.json()
            print(f"Bad request: {error['detail']}")
            if 'available_workflows' in error:
                print(f"Available workflows: {error['available_workflows']}")
        elif response.status_code == 406:
            print("Content was filtered by safety systems")
        elif response.status_code == 413:
            print("Message too long, try reducing the size")
        elif response.status_code == 500:
            error = response.json()
            print(f"Configuration error: {error['detail']}")
            if 'required_config' in error:
                print(f"Missing configuration: {error['required_config']}")
        else:
            print(f"Unexpected error: {response.status_code}")

    except requests.exceptions.Timeout:
        print("Request timed out")
    except requests.exceptions.ConnectionError:
        print("Could not connect to server")
    except Exception as e:
        print(f"Unexpected error: {e}")

# Usage examples
call_ingenious_api("Hello", "classification_agent")
call_ingenious_api("Search for safety info", "knowledge_base_agent")
```

## 🔄 Integration Patterns

### Webhook Integration

For real-time processing:

```python
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    """Process incoming webhooks with Insight Ingenious"""

    data = request.json
    user_message = data.get('message', '')

    # Route to appropriate workflow based on content
    if 'search' in user_message.lower():
        workflow = 'knowledge_base_agent'
    elif 'data' in user_message.lower() or 'analysis' in user_message.lower():
        workflow = 'pandas_agent'
    else:
        workflow = 'classification_agent'

    # Call Insight Ingenious API
    response = requests.post(
        "http://localhost:8081/api/v1/chat",
        json={
            "user_prompt": user_message,
            "conversation_flow": workflow,
            "thread_id": data.get('user_id', 'anonymous')
        }
    )

    if response.status_code == 200:
        result = response.json()
        return jsonify({
            "status": "success",
            "response": result["agent_response"],
            "workflow_used": workflow
        })
    else:
        return jsonify({
            "status": "error",
            "message": "Processing failed"
        }), 500
```

### Batch Processing

For processing multiple requests:

```python
import asyncio
import aiohttp

async def process_batch(messages, workflow="classification_agent"):
    """Process multiple messages in parallel"""

    async def process_single(session, message, index):
        payload = {
            "user_prompt": message,
            "conversation_flow": workflow,
            "thread_id": f"batch_{index}"
        }

        async with session.post(
            "http://localhost:8081/api/v1/chat",
            json=payload
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                return {"error": f"Status {response.status}"}

    async with aiohttp.ClientSession() as session:
        tasks = [
            process_single(session, msg, i)
            for i, msg in enumerate(messages)
        ]
        return await asyncio.gather(*tasks)

# Usage
messages = [
    "Analyze customer satisfaction",
    "Search for product information",
    "Generate sales report"
]

results = asyncio.run(process_batch(messages))
```

## 🎯 Best Practices

### 1. Choose the Right Workflow

- **Simple classification/routing**: `classification_agent`
- **Domain-specific analysis**: `bike_insights` (or create custom)
- **Knowledge retrieval**: `knowledge_base_agent`
- **Data analysis**: `pandas_agent` or `sql_manipulation_agent`
- **Fact-checking**: `web_critic_agent`

### 2. Handle Configuration Gracefully

Always check workflow status before using:

```python
def ensure_workflow_ready(workflow_name):
    """Check if workflow is properly configured"""

    response = requests.get(
        f"http://localhost:8081/api/v1/workflow-status/{workflow_name}"
    )

    if response.status_code == 200:
        status = response.json()
        if not status["ready"]:
            print(f"Workflow {workflow_name} not ready:")
            for missing in status["missing_config"]:
                print(f"  - {missing}")
            return False
        return True
    else:
        print(f"Could not check status for {workflow_name}")
        return False
```

### 3. Implement Retry Logic

```python
import time
from functools import wraps

def retry_on_failure(max_retries=3, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    print(f"Attempt {attempt + 1} failed: {e}")
                    time.sleep(delay * (2 ** attempt))  # Exponential backoff
            return None
        return wrapper
    return decorator

@retry_on_failure(max_retries=3)
def call_api_with_retry(prompt, workflow):
    # Your API call logic here
    pass
```

### 4. Monitor Performance

```python
import time
import logging

def monitor_api_call(prompt, workflow):
    """Monitor API performance"""

    start_time = time.time()

    try:
        response = requests.post(
            "http://localhost:8081/api/v1/chat",
            json={"user_prompt": prompt, "conversation_flow": workflow},
            timeout=30
        )

        duration = time.time() - start_time

        if response.status_code == 200:
            result = response.json()
            logging.info(f"API call successful - Duration: {duration:.2f}s, Tokens: {result.get('token_count', 0)}")
            return result
        else:
            logging.error(f"API call failed - Status: {response.status_code}, Duration: {duration:.2f}s")

    except Exception as e:
        duration = time.time() - start_time
        logging.error(f"API call exception - Duration: {duration:.2f}s, Error: {e}")
```

## 📚 Additional Resources

- [Workflow Requirements](../workflows/README.md) - Understand configuration needs
- [Configuration Guide](../configuration/README.md) - Detailed setup instructions
- [Custom Agents](../development/custom-agents.md) - Create your own workflows
- [Troubleshooting](../getting-started/troubleshooting.md) - Common issues and solutions

---

**🚀 Ready to integrate?** Start with the minimal configuration workflows and gradually add more advanced features as your needs grow.
