---
title: "API Reference"
layout: single
permalink: /api/
sidebar:
  nav: "docs"
toc: true
toc_label: "API Sections"
toc_icon: "plug"
---

# API Reference

Complete API documentation for Insight Ingenious - an enterprise-grade Python library for building AI agent APIs with Microsoft Azure integrations. This reference covers REST endpoints, workflow examples, debugging utilities, and integration guides.

## 🚀 API Architecture Overview

```mermaid
graph TB
    subgraph "🌐 Client Applications"
        WEB_CLIENT[🖥️ Web Applications]
        MOBILE_CLIENT[📱 Mobile Apps]
        API_CLIENT[🔌 API Integrations]
        CLI_CLIENT[⌨️ CLI Tools]
    end

    subgraph "🎯 API Layer"
        FASTAPI[⚡ FastAPI Application]
        CHAT_API[💬 Chat API<br/>/api/v1/chat]
        DIAGNOSTIC_API[🔄 Diagnostic API<br/>/api/v1/workflow-status<br/>/api/v1/workflows<br/>/api/v1/diagnostic<br/>/api/v1/health]
        PROMPTS_API[📝 Prompts API<br/>/api/v1/prompts]
        FEEDBACK_API[💬 Feedback API<br/>/api/v1/message-feedback]
        CONVERSATION_API[🗣️ Conversation API<br/>/api/v1/conversations]
    end

    subgraph "🤖 Backend Services"
        CHAT_SERVICE[💬 Chat Service]
        MULTI_AGENT_SERVICE[🤖 Multi-Agent Service]
        CONFIG_SERVICE[⚙️ Config Service]
        FILE_STORAGE[💾 File Storage]
    end

    subgraph "🧠 External Services"
        AZURE_OPENAI[🧠 Azure OpenAI]
        AZURE_SEARCH[🔍 Azure Search]
        AZURE_SQL[🗄️ Azure SQL]
    end

    WEB_CLIENT --> FASTAPI
    MOBILE_CLIENT --> FASTAPI
    API_CLIENT --> FASTAPI
    CLI_CLIENT --> FASTAPI

    FASTAPI --> CHAT_API
    FASTAPI --> DIAGNOSTIC_API
    FASTAPI --> PROMPTS_API
    FASTAPI --> FEEDBACK_API
    FASTAPI --> CONVERSATION_API

    CHAT_API --> CHAT_SERVICE
    DIAGNOSTIC_API --> CONFIG_SERVICE
    PROMPTS_API --> FILE_STORAGE
    FEEDBACK_API --> CHAT_SERVICE
    CONVERSATION_API --> CHAT_SERVICE

    CHAT_SERVICE --> MULTI_AGENT_SERVICE
    MULTI_AGENT_SERVICE --> FILE_STORAGE
    MULTI_AGENT_SERVICE --> AZURE_OPENAI

    CONFIG_SERVICE --> AZURE_SEARCH
    CONFIG_SERVICE --> AZURE_SQL

    classDef client fill:#e8f5e8
    classDef api fill:#fff3e0
    classDef service fill:#e3f2fd
    classDef external fill:#fce4ec

    class WEB_CLIENT,MOBILE_CLIENT,API_CLIENT,CLI_CLIENT client
    class FASTAPI,CHAT_API,DIAGNOSTIC_API,PROMPTS_API,FEEDBACK_API,CONVERSATION_API api
    class CHAT_SERVICE,MULTI_AGENT_SERVICE,CONFIG_SERVICE,FILE_STORAGE service
    class AZURE_OPENAI,AZURE_SEARCH,AZURE_SQL external
```

## 🔄 API Request Flow

```mermaid
sequenceDiagram
    participant Client
    participant Gateway as 🔗 API Gateway
    participant Auth as 🔐 Auth Service
    participant API as 📡 API Endpoint
    participant Service as 🤖 Backend Service
    participant LLM as 🧠 Azure OpenAI
    participant Storage as 💾 Storage

    Client->>Gateway: HTTP Request
    Gateway->>Auth: Validate API Key
    Auth-->>Gateway: ✅ Authentication Success

    Gateway->>API: Route Request
    API->>Service: Process Request

    Service->>Storage: Load Context
    Storage-->>Service: Previous History

    Service->>LLM: Generate Response
    LLM-->>Service: AI Response

    Service->>Storage: Save Response
    Service-->>API: Formatted Response

    API-->>Gateway: HTTP Response
    Gateway-->>Client: JSON Response

    Note over Client,Storage: Error handling at each step<br/>with appropriate HTTP status codes
```

## 📡 Core API Endpoints

### 🔍 Endpoint Overview

```mermaid
graph LR
    subgraph "💬 Chat Endpoints"
        CHAT_POST[POST /api/v1/chat<br/>Send Message]
    end

    subgraph "🔄 Diagnostic Endpoints"
        WORKFLOW_STATUS[GET /api/v1/workflow-status/{name}<br/>Check Workflow Status]
        WORKFLOWS_LIST[GET /api/v1/workflows<br/>List All Workflows]
        DIAGNOSTIC[GET /api/v1/diagnostic<br/>System Diagnostic]
    end

    subgraph "❤️ System Endpoints"
        HEALTH[GET /api/v1/health<br/>Health Check]
    end

    subgraph "📝 Management Endpoints"
        PROMPTS_VIEW[GET /api/v1/prompts/view/{revision_id}/{filename}<br/>View Prompt]
        PROMPTS_LIST[GET /api/v1/prompts/list/{revision_id}<br/>List Prompts]
        PROMPTS_UPDATE[POST /api/v1/prompts/update/{revision_id}/{filename}<br/>Update Prompt]
        FEEDBACK[PUT /api/v1/message-feedback<br/>Message Feedback]
    end

    classDef chat fill:#e8f5e8
    classDef workflow fill:#fff3e0
    classDef system fill:#e3f2fd
    classDef management fill:#f3e5f5

    class CHAT_POST chat
    class WORKFLOW_STATUS,WORKFLOWS_LIST,DIAGNOSTIC workflow
    class HEALTH system
    class PROMPTS_VIEW,PROMPTS_LIST,PROMPTS_UPDATE,FEEDBACK management
```

### 💬 Chat API Flow

```mermaid
flowchart TD
    START([📱 Client Request]) --> VALIDATE{✅ Validate Input}
    VALIDATE -->|Valid| AUTH{🔐 Check Auth}
    VALIDATE -->|Invalid| ERROR_400[❌ 400 Bad Request]

    AUTH -->|Authorized| LOAD_CONTEXT[📚 Load Chat Context]
    AUTH -->|Unauthorized| ERROR_401[❌ 401 Unauthorized]

    LOAD_CONTEXT --> SELECT_WORKFLOW{🔄 Select Workflow}
    SELECT_WORKFLOW --> BIKE_INSIGHTS[🚴 bike-insights]
    SELECT_WORKFLOW --> CLASSIFICATION[🔍 classification-agent]
    SELECT_WORKFLOW --> KNOWLEDGE_BASE[🔍 knowledge-base-agent]
    SELECT_WORKFLOW --> SQL_AGENT[🗄️ sql-manipulation-agent]

    BIKE_INSIGHTS --> PROCESS_MESSAGE[⚡ Process Multi-Agent Workflow]
    CLASSIFICATION --> PROCESS_MESSAGE
    KNOWLEDGE_BASE --> PROCESS_MESSAGE
    SQL_AGENT --> PROCESS_MESSAGE

    PROCESS_MESSAGE --> LLM_CALL[🧠 Call Azure OpenAI]
    LLM_CALL --> SUCCESS{✅ Success?}

    SUCCESS -->|Yes| SAVE_RESPONSE[💾 Save Response]
    SUCCESS -->|No| ERROR_500[❌ 500 Server Error]

    SAVE_RESPONSE --> FORMAT_RESPONSE[📝 Format Response]
    FORMAT_RESPONSE --> RETURN_200[✅ 200 Success]

    ERROR_400 --> END([🏁 End])
    ERROR_401 --> END
    ERROR_500 --> END
    RETURN_200 --> END

    classDef start fill:#c8e6c9
    classDef process fill:#e1f5fe
    classDef decision fill:#fff9c4
    classDef workflow fill:#f3e5f5
    classDef success fill:#dcedc8
    classDef error fill:#ffcdd2

    class START start
    class LOAD_CONTEXT,PROCESS_MESSAGE,LLM_CALL,SAVE_RESPONSE,FORMAT_RESPONSE process
    class VALIDATE,AUTH,SELECT_WORKFLOW,SUCCESS decision
    class BIKE_INSIGHTS,CLASSIFICATION,KNOWLEDGE_BASE,SQL_AGENT workflow
    class RETURN_200 success
    class ERROR_400,ERROR_401,ERROR_500 error
```

### 🔄 Workflow API Flow

```mermaid
sequenceDiagram
    participant Client
    participant API as 📡 Chat API
    participant ChatService as 💬 Chat Service
    participant MultiAgentService as 🤖 Multi-Agent Service
    participant Agent1 as 🤖 Agent 1
    participant Agent2 as 🤖 Agent 2
    participant LLM as 🧠 Azure OpenAI

    Client->>API: POST /api/v1/chat
    Note over Client,API: {"user_prompt": "Help with SQL queries",<br/>"conversation_flow": "sql-manipulation-agent"}

    API->>ChatService: Process chat request
    ChatService->>MultiAgentService: Load conversation flow

    MultiAgentService->>Agent1: Start SQL agent processing
    MultiAgentService->>Agent2: Start classification if needed

    par Agent 1 Processing
        Agent1->>LLM: Parse natural language query
        LLM-->>Agent1: SQL generation
    and Agent 2 Processing (if needed)
        Agent2->>LLM: Classify query complexity
        LLM-->>Agent2: Query type classification
    end

    Agent1-->>MultiAgentService: Report SQL results
    Agent2-->>MultiAgentService: Report classification

    MultiAgentService->>MultiAgentService: Format results
    MultiAgentService-->>ChatService: Final response
    ChatService-->>API: Formatted response
    API-->>Client: 200 Success with SQL solution
```

## 🔐 Authentication & Security

### Authentication Flow

```mermaid
graph TB
    subgraph "🔑 Authentication Methods"
        BASIC_AUTH[� HTTP Basic Authentication<br/>Username/Password]
        NO_AUTH[🚪 Authentication Disabled<br/>Anonymous Access]
    end

    subgraph "🛡️ Security Features"
        HTTPS_TLS[🔐 HTTPS/TLS<br/>Transport Encryption]
        CONFIG_AUTH[⚙️ Configurable Authentication<br/>Enable/Disable via Config]
    end

    subgraph "✅ Validation Steps"
        HEADER_CHECK[📋 Authorization Header Check]
        CREDENTIALS_VERIFY[🔍 Credential Verification]
        CONFIG_CHECK[⚙️ Check Auth Config]
        ACCESS_GRANTED[✅ Access Granted]
    end

    BASIC_AUTH --> HEADER_CHECK
    NO_AUTH --> ACCESS_GRANTED
    CONFIG_CHECK --> BASIC_AUTH
    CONFIG_CHECK --> NO_AUTH

    HEADER_CHECK --> CREDENTIALS_VERIFY
    CREDENTIALS_VERIFY --> ACCESS_GRANTED

    HTTPS_TLS --> HEADER_CHECK
    CONFIG_AUTH --> CONFIG_CHECK

    classDef auth fill:#e8f5e8
    classDef security fill:#fff3e0
    classDef validation fill:#e3f2fd

    class BASIC_AUTH,NO_AUTH auth
    class HTTPS_TLS,CONFIG_AUTH security
    class HEADER_CHECK,CREDENTIALS_VERIFY,CONFIG_CHECK,ACCESS_GRANTED validation
```

### 🚀 Getting Started with the API

The Insight Ingenious API provides powerful endpoints for creating and managing AI-powered conversation workflows programmatically.

### Base API Information
- **Base URL**: `http://localhost:80` (default) or your configured port
- **Content-Type**: `application/json`
- **Authentication**: HTTP Basic Authentication (configurable)

### [🔄 Workflow API](/api/workflows/)
Complete documentation for all available workflow endpoints, including:
- Classification and routing workflows
- Educational content generation
- Knowledge base search and retrieval
- SQL query generation and execution

### 🛠️ Core API Endpoints

#### Health Check
```bash
GET /api/v1/health
```
Returns the health status of the API service.

#### List Available Workflows
```bash
GET /api/v1/workflows
```
Returns a list of all available workflow types and their configurations.

### 📋 Common API Patterns

#### Making API Requests
All API requests should include appropriate headers:

```bash
curl -X POST http://localhost:80/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"user_prompt": "Hello", "conversation_flow": "classification-agent"}'
```

With authentication enabled:
```bash
curl -X POST http://localhost:80/api/v1/chat \
  -H "Content-Type: application/json" \
  -u "username:password" \
  -d '{"user_prompt": "Hello", "conversation_flow": "classification-agent"}'
```

#### Response Format
All API responses follow a consistent format:

```json
{
  "status": "success|error",
  "data": {
    // Response data
  },
  "message": "Human-readable message",
  "timestamp": "2025-07-04T12:00:00Z"
}
```

## 🔧 Integration Examples

### Python Integration
```python
import requests

def call_chat_api(user_prompt, conversation_flow, username=None, password=None):
    auth = (username, password) if username and password else None

    response = requests.post(
        "http://localhost:80/api/v1/chat",
        json={
            "user_prompt": user_prompt,
            "conversation_flow": conversation_flow
        },
        headers={
            "Content-Type": "application/json"
        },
        auth=auth
    )
    return response.json()

# Example usage
result = call_chat_api("Hello", "classification-agent", "username", "password")
```

### JavaScript Integration
```javascript
async function callChatAPI(userPrompt, conversationFlow, username, password) {
    const auth = username && password ?
        'Basic ' + btoa(username + ':' + password) : undefined;

    const response = await fetch('http://localhost:80/api/v1/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            ...(auth && { 'Authorization': auth })
        },
        body: JSON.stringify({
            user_prompt: userPrompt,
            conversation_flow: conversationFlow
        })
    });

    return await response.json();
}

// Example usage
const result = await callChatAPI('Hello', 'classification-agent', 'username', 'password');
```

## 🔍 Error Handling

The API uses standard HTTP status codes and provides detailed error messages:

- `200 OK` - Successful request
- `400 Bad Request` - Invalid request parameters
- `401 Unauthorized` - Missing or invalid API key
- `404 Not Found` - Endpoint or resource not found
- `500 Internal Server Error` - Server-side error

Example error response:
```json
{
  "status": "error",
  "message": "Invalid workflow type specified",
  "error_code": "INVALID_WORKFLOW_TYPE",
  "timestamp": "2025-07-04T12:00:00Z"
}
```

## 📖 Additional Resources

- [🔄 Workflow API Documentation](/api/workflows/)
- [⚙️ Configuration Guide](/configuration/)
- [🛠️ Development Setup](/development/)
- [📝 CLI Reference](/CLI_REFERENCE/)

## 💡 Need Help?

- Check the [troubleshooting guide](/troubleshooting/)
- Review the [workflow examples](/api/workflows/)
- Open an issue on [GitHub](https://github.com/Insight-Services-APAC/Insight_Ingenious/issues)
