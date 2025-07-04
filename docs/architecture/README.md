---
title: "Architecture Overview"
layout: single
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
    subgraph "Client Layer"
        UI[Web UI<br/>Chainlit Interface]
        API_CLIENT[API Clients<br/>External Applications]
    end

    subgraph "API Gateway"
        API[FastAPI<br/>REST Endpoints]
        AUTH[Authentication<br/>& Authorization]
    end

    subgraph "Core Engine"
        AGENT_SERVICE[Agent Service<br/>Conversation Manager]
        FLOW_ENGINE[Flow Engine<br/>Pattern Orchestrator]
        LLM_SERVICE[LLM Service<br/>Azure OpenAI Integration]
    end

    subgraph "Extension Layer"
        CUSTOM_AGENTS[Custom Agents<br/>Domain Specialists]
        PATTERNS[Conversation Patterns<br/>Workflow Templates]
        TOOLS[Custom Tools<br/>External Integrations]
    end

    subgraph "Storage Layer"
        CONFIG[Configuration<br/>YAML Files]
        HISTORY[Chat History<br/>Session Management]
        FILES[File Storage<br/>Documents & Assets]
    end

    subgraph "External Services"
        AZURE[Azure OpenAI<br/>GPT Models]
        EXTERNAL_API[External APIs<br/>Data Sources]
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

### Multi-Agent Framework

The heart of Insight Ingenious is its multi-agent framework, which enables sophisticated AI conversations:

```mermaid
graph LR
    subgraph "Agent Service"
        MANAGER[Conversation Manager]
        COORDINATOR[Agent Coordinator]
        STATE[State Manager]
    end

    subgraph "Agent Types"
        BIKE[Bike Analysis Agent]
        SENTIMENT[Sentiment Agent]
        FISCAL[Fiscal Agent]
        SUMMARY[Summary Agent]
        CUSTOM[Custom Agents]
    end

    subgraph "Conversation Patterns"
        SEQUENTIAL[Sequential Pattern]
        PARALLEL[Parallel Pattern]
        CONDITIONAL[Conditional Pattern]
        HIERARCHICAL[Hierarchical Pattern]
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

### API Layer Architecture

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

### Web UI Integration

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

### Storage Architecture

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

### Request Processing Flow

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

### Multi-Agent Conversation Flow

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

### Extension Architecture

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

## Key Classes and Interfaces

### Core Agent Framework

```mermaid
classDiagram
    class IConversationPattern {
        <<interface>>
        +execute(context: ConversationContext)
        +validate(input: Any)
        +get_pattern_type()
    }

    class IConversationFlow {
        <<interface>>
        +start_conversation(query: str)
        +process_step(step: ConversationStep)
        +finalize_conversation()
    }

    class BaseAgent {
        <<abstract>>
        +name: str
        +description: str
        +tools: List[Tool]
        +process_message(message: str)
        +get_system_prompt()
    }

    class BikeAnalysisAgent {
        +analyze_sales_data()
        +generate_insights()
        +create_visualizations()
    }

    class SentimentAgent {
        +analyze_sentiment()
        +extract_emotions()
        +score_satisfaction()
    }

    class FiscalAgent {
        +calculate_revenue()
        +analyze_profitability()
        +forecast_trends()
    }

    class MultiAgentChatService {
        +agents: Dict[str, BaseAgent]
        +patterns: Dict[str, IConversationPattern]
        +orchestrate_conversation()
        +manage_state()
    }

    IConversationPattern <|.. SequentialPattern
    IConversationPattern <|.. ParallelPattern
    IConversationFlow <|.. BikeInsightsFlow
    BaseAgent <|-- BikeAnalysisAgent
    BaseAgent <|-- SentimentAgent
    BaseAgent <|-- FiscalAgent
    MultiAgentChatService --> BaseAgent
    MultiAgentChatService --> IConversationPattern
```

## Configuration Architecture

### Configuration Management

```mermaid
graph TB
    subgraph "📁 Configuration Sources"
        CONFIG_FILE[📄 config.yml<br/>Project Configuration]
        PROFILES_FILE[🔐 profiles.yml<br/>Environment Secrets]
        ENV_VARS[🌍 Environment Variables]
        CLI_ARGS[⌨️ Command Line Args]
    end

    subgraph "🔄 Configuration Processing"
        LOADER[📖 Configuration Loader]
        VALIDATOR[✅ Schema Validator]
        MERGER[🔀 Configuration Merger]
    end

    subgraph "💾 Runtime Configuration"
        APP_CONFIG[⚙️ Application Config]
        AGENT_CONFIG[🤖 Agent Configurations]
        SERVICE_CONFIG[🔧 Service Settings]
    end

    CONFIG_FILE --> LOADER
    PROFILES_FILE --> LOADER
    ENV_VARS --> LOADER
    CLI_ARGS --> LOADER

    LOADER --> VALIDATOR
    VALIDATOR --> MERGER
    MERGER --> APP_CONFIG
    MERGER --> AGENT_CONFIG
    MERGER --> SERVICE_CONFIG

    classDef source fill:#e8f5e8
    classDef process fill:#fff3e0
    classDef runtime fill:#e3f2fd

    class CONFIG_FILE,PROFILES_FILE,ENV_VARS,CLI_ARGS source
    class LOADER,VALIDATOR,MERGER process
    class APP_CONFIG,AGENT_CONFIG,SERVICE_CONFIG runtime
```

## Deployment Architecture

### Deployment Options

```mermaid
graph TB
    subgraph "🖥️ Local Development"
        LOCAL_API[🔧 FastAPI Dev Server]
        LOCAL_UI[🎨 Chainlit Dev UI]
        LOCAL_DB[💾 SQLite Database]
    end

    subgraph "🐳 Docker Deployment"
        DOCKER_API[📦 API Container]
        DOCKER_UI[📦 UI Container]
        DOCKER_DB[📦 Database Container]
        DOCKER_COMPOSE[🔧 Docker Compose]
    end

    subgraph "☁️ Cloud Deployment"
        CLOUD_API[🌐 API Service]
        CLOUD_UI[🎨 Web App]
        CLOUD_DB[💾 Managed Database]
        CLOUD_STORAGE[📁 Object Storage]
    end

    subgraph "🔧 External Services"
        AZURE_OPENAI[🧠 Azure OpenAI]
        MONITORING[📊 Application Insights]
        LOGGING[📝 Centralized Logging]
    end

    LOCAL_API --> LOCAL_UI
    LOCAL_API --> LOCAL_DB

    DOCKER_COMPOSE --> DOCKER_API
    DOCKER_COMPOSE --> DOCKER_UI
    DOCKER_COMPOSE --> DOCKER_DB

    CLOUD_API --> CLOUD_UI
    CLOUD_API --> CLOUD_DB
    CLOUD_API --> CLOUD_STORAGE

    LOCAL_API --> AZURE_OPENAI
    DOCKER_API --> AZURE_OPENAI
    CLOUD_API --> AZURE_OPENAI

    CLOUD_API --> MONITORING
    CLOUD_API --> LOGGING

    classDef local fill:#e8f5e8
    classDef docker fill:#e3f2fd
    classDef cloud fill:#fff3e0
    classDef external fill:#fce4ec

    class LOCAL_API,LOCAL_UI,LOCAL_DB local
    class DOCKER_API,DOCKER_UI,DOCKER_DB,DOCKER_COMPOSE docker
    class CLOUD_API,CLOUD_UI,CLOUD_DB,CLOUD_STORAGE cloud
    class AZURE_OPENAI,MONITORING,LOGGING external
```

## Security Architecture

### Security Model

```mermaid
graph TB
    subgraph "🛡️ Authentication Layer"
        API_KEY[🔑 API Key Validation]
        JWT_TOKEN[🎫 JWT Tokens]
        SESSION_MGR[👤 Session Management]
    end

    subgraph "🔒 Authorization Layer"
        RBAC[👥 Role-Based Access]
        PERMISSIONS[📋 Permission System]
        RESOURCE_GUARD[🛡️ Resource Protection]
    end

    subgraph "🔐 Data Protection"
        ENCRYPTION[🔒 Data Encryption]
        SECRETS_MGR[🗝️ Secrets Management]
        AUDIT_LOG[📝 Audit Logging]
    end

    subgraph "🌐 Network Security"
        HTTPS[🔐 HTTPS/TLS]
        CORS[🌍 CORS Policy]
        RATE_LIMIT[⏱️ Rate Limiting]
    end

    API_KEY --> RBAC
    JWT_TOKEN --> RBAC
    SESSION_MGR --> RBAC

    RBAC --> PERMISSIONS
    PERMISSIONS --> RESOURCE_GUARD

    RESOURCE_GUARD --> ENCRYPTION
    ENCRYPTION --> SECRETS_MGR
    SECRETS_MGR --> AUDIT_LOG

    HTTPS --> CORS
    CORS --> RATE_LIMIT

    classDef auth fill:#e8f5e8
    classDef authz fill:#fff3e0
    classDef data fill:#e3f2fd
    classDef network fill:#fce4ec

    class API_KEY,JWT_TOKEN,SESSION_MGR auth
    class RBAC,PERMISSIONS,RESOURCE_GUARD authz
    class ENCRYPTION,SECRETS_MGR,AUDIT_LOG data
    class HTTPS,CORS,RATE_LIMIT network
```

## Performance & Scalability

### Performance Architecture

```mermaid
graph TB
    subgraph "⚡ Caching Strategy"
        REDIS[🔴 Redis Cache]
        MEMORY[💾 In-Memory Cache]
        CDN[🌐 CDN Cache]
    end

    subgraph "📊 Load Balancing"
        LOAD_BALANCER[⚖️ Load Balancer]
        API_INSTANCES[🔧 API Instances]
        HEALTH_CHECK[❤️ Health Checks]
    end

    subgraph "🔄 Async Processing"
        TASK_QUEUE[📋 Task Queue]
        WORKERS[👷 Background Workers]
        SCHEDULER[⏰ Job Scheduler]
    end

    subgraph "📈 Monitoring"
        METRICS[📊 Performance Metrics]
        ALERTS[🚨 Alert System]
        DASHBOARDS[📈 Monitoring Dashboard]
    end

    REDIS --> MEMORY
    MEMORY --> CDN

    LOAD_BALANCER --> API_INSTANCES
    LOAD_BALANCER --> HEALTH_CHECK

    TASK_QUEUE --> WORKERS
    WORKERS --> SCHEDULER

    METRICS --> ALERTS
    ALERTS --> DASHBOARDS

    API_INSTANCES --> REDIS
    API_INSTANCES --> TASK_QUEUE
    API_INSTANCES --> METRICS

    classDef cache fill:#e8f5e8
    classDef balance fill:#fff3e0
    classDef async fill:#e3f2fd
    classDef monitor fill:#fce4ec

    class REDIS,MEMORY,CDN cache
    class LOAD_BALANCER,API_INSTANCES,HEALTH_CHECK balance
    class TASK_QUEUE,WORKERS,SCHEDULER async
    class METRICS,ALERTS,DASHBOARDS monitor
```

## Extension Development

The system is designed for extensibility at several key points:

- **🤖 Custom Agents**: Create specialized agents for specific domains
- **📋 Conversation Patterns**: Define new ways agents can interact
- **🔄 Conversation Flows**: Implement domain-specific conversation flows
- **🔌 Custom API Routes**: Add new API endpoints
- **📊 Custom Models**: Define domain-specific data models
- **🛠️ Custom Tools**: Integrate with external systems and APIs

### Development Best Practices

1. **🏗️ Modular Design**: Keep components loosely coupled
2. **🧪 Test Coverage**: Maintain comprehensive test suites
3. **📝 Documentation**: Document all public APIs and interfaces
4. **🔐 Security**: Follow security best practices for all extensions
5. **⚡ Performance**: Consider performance implications of custom code
6. **🔄 Compatibility**: Ensure backward compatibility when possible

For detailed development instructions, see the [Development Guide](/development/).

## Next Steps

- 📖 Read the [Getting Started Guide](/getting-started/) to begin using the system
- 🛠️ Follow the [Development Guide](/development/) to start extending the framework
- 🔧 Check the [Configuration Guide](/configuration/) for setup details
- 📡 Explore the [API Documentation](/api/) for integration options
