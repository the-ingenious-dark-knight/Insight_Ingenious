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

- Creation of specialized AI agents
- Orchestration of conversations between agents
- Definition of conversation patterns and flows
- Tool integration for agents

#### Key Classes

- `IConversationPattern`: Abstract base class for conversation patterns
- `IConversationFlow`: Interface for implementing conversation flows
- `multi_agent_chat_service`: Service managing agent conversations

### 2. API Layer

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
