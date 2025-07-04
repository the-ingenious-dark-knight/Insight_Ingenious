---
title: "🏗️ Architecture Overview"
layout: mermaid
permalink: /architecture/
sidebar:
  nav: "docs"
toc: true
toc_label: "Architecture Components"
toc_icon: "sitemap"
---

# Architecture Overview

This document describes the high-level architecture of Insight Ingenious, explaining its key components and how they interact.

## System Architecture

Insight Ingenious is designed with a modular architecture that allows for extensibility and customization. The system consists of the following main components:

```mermaid
graph TB
    subgraph "🌐 Client Layer"
        UI[🎨 Web UI<br/>Chainlit Interface]
        API_CLIENT[📱 API Clients<br/>External Applications]
    end
    
    subgraph "🔗 API Gateway"
        API[🚀 FastAPI<br/>REST Endpoints]
        AUTH[🔐 Authentication<br/>& Authorization]
    end
    
    subgraph "🤖 Core Engine"
        AGENT_SERVICE[🎯 Agent Service<br/>Conversation Manager]
        FLOW_ENGINE[⚡ Flow Engine<br/>Pattern Orchestrator]
        LLM_SERVICE[🧠 LLM Service<br/>Azure OpenAI Integration]
    end
    
    subgraph "🔧 Extension Layer"
        CUSTOM_AGENTS[👥 Custom Agents<br/>Domain Specialists]
        PATTERNS[📋 Conversation Patterns<br/>Workflow Templates]
        TOOLS[🛠️ Custom Tools<br/>External Integrations]
    end
    
    subgraph "💾 Storage Layer"
        CONFIG[⚙️ Configuration<br/>YAML Files]
        HISTORY[📚 Chat History<br/>Session Management]
        FILES[📁 File Storage<br/>Documents & Assets]
    end
    
    subgraph "🌐 External Services"
        AZURE[☁️ Azure OpenAI<br/>GPT Models]
        EXTERNAL_API[🔌 External APIs<br/>Data Sources]
    end
    
    UI --> API
    API_CLIENT --> API
    API --> AUTH
    AUTH --> AGENT_SERVICE
    AGENT_SERVICE --> FLOW_ENGINE
    AGENT_SERVICE --> LLM_SERVICE
    FLOW_ENGINE --> PATTERNS
    AGENT_SERVICE --> CUSTOM_AGENTS
    CUSTOM_AGENTS --> TOOLS
    LLM_SERVICE --> AZURE
    TOOLS --> EXTERNAL_API
    AGENT_SERVICE --> HISTORY
    FLOW_ENGINE --> CONFIG
    AGENT_SERVICE --> FILES
    
    classDef clientLayer fill:#e1f5fe
    classDef apiLayer fill:#f3e5f5
    classDef coreLayer fill:#e8f5e8
    classDef extensionLayer fill:#fff3e0
    classDef storageLayer fill:#fce4ec
    classDef externalLayer fill:#f1f8e9
    
    class UI,API_CLIENT clientLayer
    class API,AUTH apiLayer
    class AGENT_SERVICE,FLOW_ENGINE,LLM_SERVICE coreLayer
    class CUSTOM_AGENTS,PATTERNS,TOOLS extensionLayer
    class CONFIG,HISTORY,FILES storageLayer
    class AZURE,EXTERNAL_API externalLayer
```

## Detailed Component Architecture

### 🤖 Multi-Agent Framework

The heart of Insight Ingenious is its multi-agent framework, which enables sophisticated AI conversations:

```mermaid
graph LR
    subgraph "🎯 Agent Service"
        MANAGER[👨‍💼 Conversation Manager]
        COORDINATOR[🎭 Agent Coordinator]
        STATE[📊 State Manager]
    end
    
    subgraph "👥 Agent Types"
        BIKE[🚴 Bike Analysis Agent]
        SENTIMENT[😊 Sentiment Agent]
        FISCAL[💰 Fiscal Agent]
        SUMMARY[📝 Summary Agent]
        CUSTOM[🔧 Custom Agents]
    end
    
    subgraph "📋 Conversation Patterns"
        SEQUENTIAL[➡️ Sequential Pattern]
        PARALLEL[⚡ Parallel Pattern]
        CONDITIONAL[🔀 Conditional Pattern]
        HIERARCHICAL[🌳 Hierarchical Pattern]
    end
    
    MANAGER --> COORDINATOR
    COORDINATOR --> STATE
    COORDINATOR --> BIKE
    COORDINATOR --> SENTIMENT
    COORDINATOR --> FISCAL
    COORDINATOR --> SUMMARY
    COORDINATOR --> CUSTOM
    
    MANAGER --> SEQUENTIAL
    MANAGER --> PARALLEL
    MANAGER --> CONDITIONAL
    MANAGER --> HIERARCHICAL
    
    classDef service fill:#e3f2fd
    classDef agents fill:#f1f8e9
    classDef patterns fill:#fff8e1
    
    class MANAGER,COORDINATOR,STATE service
    class BIKE,SENTIMENT,FISCAL,SUMMARY,CUSTOM agents
    class SEQUENTIAL,PARALLEL,CONDITIONAL,HIERARCHICAL patterns
```

### 🔗 API Layer Architecture

The API layer provides secure, scalable access to the system:

```mermaid
sequenceDiagram
    participant Client
    participant FastAPI
    participant Auth
    participant AgentService
    participant LLM
    participant Storage
    
    Client->>FastAPI: POST /api/chat
    FastAPI->>Auth: Validate API Key
    Auth-->>FastAPI: ✅ Authorized
    FastAPI->>AgentService: Process Request
    AgentService->>Storage: Load Chat History
    Storage-->>AgentService: Previous Context
    AgentService->>LLM: Generate Response
    LLM-->>AgentService: AI Response
    AgentService->>Storage: Save Response
    AgentService-->>FastAPI: Formatted Response
    FastAPI-->>Client: JSON Response
```

### 🎨 Web UI Integration

The Chainlit integration provides an intuitive user experience:

```mermaid
graph TD
    subgraph "🖥️ Frontend"
        CHAINLIT[🎨 Chainlit UI]
        COMPONENTS[🧩 UI Components]
        CHAT[💬 Chat Interface]
    end
    
    subgraph "🔄 WebSocket Layer"
        WS[🌐 WebSocket Handler]
        SESSION[📋 Session Manager]
    end
    
    subgraph "🤖 Backend Services"
        CHAT_SERVICE[💬 Chat Service]
        FILE_SERVICE[📁 File Service]
        AUTH_SERVICE[🔐 Auth Service]
    end
    
    CHAINLIT --> COMPONENTS
    COMPONENTS --> CHAT
    CHAT --> WS
    WS --> SESSION
    SESSION --> CHAT_SERVICE
    SESSION --> FILE_SERVICE
    SESSION --> AUTH_SERVICE
    
    classDef frontend fill:#e8eaf6
    classDef websocket fill:#f3e5f5
    classDef backend fill:#e8f5e8
    
    class CHAINLIT,COMPONENTS,CHAT frontend
    class WS,SESSION websocket
    class CHAT_SERVICE,FILE_SERVICE,AUTH_SERVICE backend
```

### 💾 Storage Architecture

The storage layer handles persistence and configuration:

```mermaid
graph TB
    subgraph "⚙️ Configuration"
        CONFIG_YML[📄 config.yml<br/>Project Settings]
        PROFILES_YML[🔐 profiles.yml<br/>API Keys & Secrets]
    end
    
    subgraph "📚 Chat Storage"
        HISTORY[💬 Chat History<br/>SQLite/Database]
        SESSIONS[👤 User Sessions<br/>Memory/Redis]
    end
    
    subgraph "📁 File Storage"
        UPLOADS[⬆️ File Uploads<br/>Local/Cloud Storage]
        TEMPLATES[📋 Templates<br/>YAML Files]
        LOGS[📊 System Logs<br/>Structured Logging]
    end
    
    subgraph "🔄 Data Flow"
        READ[📖 Read Operations]
        WRITE[✍️ Write Operations]
        CACHE[⚡ Caching Layer]
    end
    
    CONFIG_YML --> READ
    PROFILES_YML --> READ
    HISTORY --> READ
    HISTORY --> WRITE
    SESSIONS --> READ
    SESSIONS --> WRITE
    UPLOADS --> READ
    UPLOADS --> WRITE
    TEMPLATES --> READ
    LOGS --> WRITE
    
    READ --> CACHE
    WRITE --> CACHE
    
    classDef config fill:#fff3e0
    classDef chat fill:#e8f5e8
    classDef files fill:#f3e5f5
    classDef flow fill:#e1f5fe
    
    class CONFIG_YML,PROFILES_YML config
    class HISTORY,SESSIONS chat
    class UPLOADS,TEMPLATES,LOGS files
    class READ,WRITE,CACHE flow
```

## Data Flow Architecture

### 🔄 Request Processing Flow

```mermaid
flowchart TD
    START([🚀 User Request]) --> INPUT_VALIDATION{📋 Validate Input}
    INPUT_VALIDATION -->|✅ Valid| LOAD_CONTEXT[📚 Load Context]
    INPUT_VALIDATION -->|❌ Invalid| ERROR_RESPONSE[❌ Error Response]
    
    LOAD_CONTEXT --> SELECT_WORKFLOW{🎯 Select Workflow}
    SELECT_WORKFLOW --> BIKE_WORKFLOW[🚴 Bike Analysis]
    SELECT_WORKFLOW --> SENTIMENT_WORKFLOW[😊 Sentiment Analysis]
    SELECT_WORKFLOW --> FISCAL_WORKFLOW[💰 Fiscal Analysis]
    SELECT_WORKFLOW --> CUSTOM_WORKFLOW[🔧 Custom Workflow]
    
    BIKE_WORKFLOW --> AGENT_COORDINATION[👥 Agent Coordination]
    SENTIMENT_WORKFLOW --> AGENT_COORDINATION
    FISCAL_WORKFLOW --> AGENT_COORDINATION
    CUSTOM_WORKFLOW --> AGENT_COORDINATION
    
    AGENT_COORDINATION --> LLM_PROCESSING[🧠 LLM Processing]
    LLM_PROCESSING --> RESPONSE_FORMATTING[📝 Format Response]
    RESPONSE_FORMATTING --> SAVE_HISTORY[💾 Save to History]
    SAVE_HISTORY --> SEND_RESPONSE[📤 Send Response]
    
    ERROR_RESPONSE --> END([🏁 End])
    SEND_RESPONSE --> END
    
    classDef startEnd fill:#f8bbd9
    classDef process fill:#b3e5fc
    classDef decision fill:#fff9c4
    classDef workflow fill:#c8e6c9
    classDef error fill:#ffcdd2
    
    class START,END startEnd
    class LOAD_CONTEXT,AGENT_COORDINATION,LLM_PROCESSING,RESPONSE_FORMATTING,SAVE_HISTORY,SEND_RESPONSE process
    class INPUT_VALIDATION,SELECT_WORKFLOW decision
    class BIKE_WORKFLOW,SENTIMENT_WORKFLOW,FISCAL_WORKFLOW,CUSTOM_WORKFLOW workflow
    class ERROR_RESPONSE error
```

### 🤖 Multi-Agent Conversation Flow

```mermaid
sequenceDiagram
    participant User
    participant API
    participant Manager
    participant Agent1 as 🚴 Bike Agent
    participant Agent2 as 😊 Sentiment Agent
    participant Agent3 as 💰 Fiscal Agent
    participant Summary as 📝 Summary Agent
    participant LLM as 🧠 Azure OpenAI
    
    User->>API: "Analyze bike sales performance"
    API->>Manager: Route to bike_insights workflow
    
    Note over Manager: Initialize conversation pattern
    Manager->>Agent1: Analyze bike sales data
    Agent1->>LLM: Request data analysis
    LLM-->>Agent1: Sales metrics & trends
    Agent1-->>Manager: Sales analysis complete
    
    Manager->>Agent2: Analyze customer sentiment
    Agent2->>LLM: Sentiment analysis request
    LLM-->>Agent2: Customer satisfaction metrics
    Agent2-->>Manager: Sentiment analysis complete
    
    Manager->>Agent3: Analyze financial impact
    Agent3->>LLM: Financial calculation request
    LLM-->>Agent3: Revenue & profit analysis
    Agent3-->>Manager: Financial analysis complete
    
    Manager->>Summary: Compile comprehensive report
    Summary->>LLM: Summarization request
    LLM-->>Summary: Executive summary
    Summary-->>Manager: Final report ready
    
    Manager-->>API: Complete analysis
    API-->>User: Comprehensive bike sales report
```

## Extension Points & Customization

### 🔧 Extension Architecture

```mermaid
graph TB
    subgraph "🏭 Core Framework"
        CORE_API[🔧 Core API]
        CORE_AGENTS[👤 Base Agents]
        CORE_PATTERNS[📋 Base Patterns]
    end
    
    subgraph "🎯 Extension Interface"
        AGENT_INTERFACE[🤖 IAgent Interface]
        PATTERN_INTERFACE[🔄 IPattern Interface]
        TOOL_INTERFACE[🛠️ ITool Interface]
    end
    
    subgraph "🔌 Custom Extensions"
        CUSTOM_AGENT[👥 Custom Agent<br/>Domain Expert]
        CUSTOM_PATTERN[🎭 Custom Pattern<br/>Workflow Logic]
        CUSTOM_TOOL[⚙️ Custom Tool<br/>External Integration]
    end
    
    subgraph "📦 Extension Registry"
        REGISTRY[📋 Extension Registry]
        LOADER[⚡ Dynamic Loader]
        VALIDATOR[✅ Validation Engine]
    end
    
    CORE_API --> AGENT_INTERFACE
    CORE_AGENTS --> AGENT_INTERFACE
    CORE_PATTERNS --> PATTERN_INTERFACE
    
    AGENT_INTERFACE --> CUSTOM_AGENT
    PATTERN_INTERFACE --> CUSTOM_PATTERN
    TOOL_INTERFACE --> CUSTOM_TOOL
    
    CUSTOM_AGENT --> REGISTRY
    CUSTOM_PATTERN --> REGISTRY
    CUSTOM_TOOL --> REGISTRY
    
    REGISTRY --> LOADER
    REGISTRY --> VALIDATOR
    
    classDef core fill:#e3f2fd
    classDef interface fill:#f1f8e9
    classDef custom fill:#fff3e0
    classDef registry fill:#fce4ec
    
    class CORE_API,CORE_AGENTS,CORE_PATTERNS core
    class AGENT_INTERFACE,PATTERN_INTERFACE,TOOL_INTERFACE interface
    class CUSTOM_AGENT,CUSTOM_PATTERN,CUSTOM_TOOL custom
    class REGISTRY,LOADER,VALIDATOR registry
```

The API layer provides programmatic access to the system:

- REST API endpoints for chat interactions
- Authentication and security
- Integration points for custom extensions

### 3. Web UI

The Chainlit integration provides a user-friendly web interface:

- Interactive chat interface
- Visualization of agent responses
- User authentication

### 4. Storage Layer

The storage layer handles persistence:

- Chat history storage
- File management
- Configuration storage

### 5. Extensions Layer

The extensions layer allows for customization:

- Custom agents and conversation patterns
- Domain-specific prompts and templates
- Integration with external systems

## Data Flow

1. User input arrives through API or UI
2. The chat service processes the request
3. The appropriate conversation flow is selected
4. Agents collaborate based on conversation pattern
5. Results are returned to the user and stored

## Configuration System

Insight Ingenious uses a two-file configuration approach:

- `config.yml`: Project-specific, non-sensitive configuration
- `profiles.yml`: Environment-specific, sensitive configuration (API keys, credentials)

## Extension Points

The system is designed for extensibility at several points:

- **Custom Agents**: Create specialized agents for specific domains
- **Conversation Patterns**: Define new ways agents can interact
- **Conversation Flows**: Implement domain-specific conversation flows
- **Custom API Routes**: Add new API endpoints
- **Custom Models**: Define domain-specific data models
