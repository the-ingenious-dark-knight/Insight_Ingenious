# Insight Ingenious Architecture

This document outlines the architectural design of Insight Ingenious, explaining the key components, their interactions, and the design principles behind the system.

## System Overview

Insight Ingenious is a framework for building, managing, and deploying multi-agent AI conversations. The system follows clean architecture principles with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────────┐
│                     Presentation Layer                          │
│  ┌────────────┐    ┌────────────────┐    ┌────────────────┐    │
│  │ REST API   │    │   ChainLit UI  │    │      CLI       │    │
│  └─────┬──────┘    └────────┬───────┘    └────────┬───────┘    │
└────────┼─────────────────────┼────────────────────┼─────────────┘
          │                     │                    │
          │                     │                    │
          ▼                     ▼                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Application Layer                           │
│  ┌────────────┐    ┌────────────────┐    ┌────────────────┐    │
│  │  Services  │    │  Repositories  │    │    Factory     │    │
│  └─────┬──────┘    └────────┬───────┘    └────────────────┘    │
└────────┼─────────────────────┼────────────────────────────────────┘
          │                     │
          │                     │
          ▼                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Domain Layer                                │
│  ┌────────────┐    ┌────────────────┐    ┌────────────────┐    │
│  │   Models   │    │   Interfaces   │    │  Domain Logic  │    │
│  └────────────┘    └────────────────┘    └────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
          │                     │
          │                     │
          ▼                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Infrastructure Layer                         │
│  ┌────────────┐    ┌────────────────┐    ┌────────────────┐    │
│  │  Database  │    │ External APIs  │    │ File Storage   │    │
│  └────────────┘    └────────────────┘    └────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

## Architecture Layers

### 1. Presentation Layer

The presentation layer is responsible for handling user interactions and displaying information:

- **API**: REST API endpoints built with FastAPI
- **ChainLit**: Web-based user interface for chat interactions
- **CLI**: Command-line interface for administration and testing

### 2. Application Layer

The application layer orchestrates the flow of data and coordinates business operations:

- **Services**: Implement business logic and orchestrate domain objects
- **Repositories**: Implementations of domain interfaces for data access
- **Factory**: Creates and manages dependencies using dependency injection

### 3. Domain Layer

The domain layer contains the business rules, entities, and interfaces:

- **Models**: Business entities and value objects
- **Interfaces**: Abstract definitions for repositories and services
- **Domain Logic**: Core business rules that remain constant regardless of external systems

### 4. Infrastructure Layer

The infrastructure layer provides implementations for external systems:

- **Database**: Database access implementations (Cosmos, DuckDB, SQLite)
- **External APIs**: Integration with external services (OpenAI, etc.)
- **Storage**: File storage and retrieval mechanisms
  - **MessageFeedbackService**: Manages user feedback on messages
  - **External Services**: Integrations with external systems like OpenAI

### 3. Agents System

- **Agent Model**: Base models for defining agent behaviors
- **AgentChat**: Represents chat interactions between agents
- **Agent Orchestration**: Manages the flow of conversations between multiple agents

### 4. Data Storage

- **Chat History**: Stores conversation history
- **File Storage**: Manages file attachments and document storage
- **Database Backends**: Multiple database support
  - SQLite
  - DuckDB
  - Azure Cosmos DB

## Design Principles

Insight Ingenious follows several key design principles:

1. **Modularity**: The system is divided into loosely coupled components that can be developed and tested independently.

2. **Extensibility**: The framework is designed to be extended with custom agents, templates, and APIs.

3. **Configuration-Driven**: Much of the system behavior is driven by configuration files rather than code changes.

4. **Abstraction Layers**: Abstract interfaces are used to ensure components depend on abstractions rather than concrete implementations.

## Extension Points

Insight Ingenious provides several extension points:

1. **Custom Agent Types**: Create custom agents by extending the base Agent class.

2. **API Extensions**: Add custom API routes to extend the system's functionality.

3. **Storage Backends**: Implement custom storage backends for chat history and files.

4. **Templates**: Define custom prompt templates and conversation flows.

## Data Flow

1. User requests enter through the API or CLI interface.
2. Requests are routed to the appropriate service.
3. Services use agents to process the request.
4. Agents interact with external services (like LLMs) and data storage.
5. Responses flow back through the service and are returned to the user.

## Security Model

Insight Ingenious supports multiple security features:

1. **API Authentication**: Configure API keys or OAuth for API access.
2. **Azure Key Vault Integration**: Secret management with Azure Key Vault.
3. **Content Filtering**: Filter inappropriate content in conversations.

## Deployment Options

The system supports multiple deployment options:

1. **Local Development**: Run locally for development and testing.
2. **Docker Containers**: Containerized deployment for production.
3. **Cloud Deployment**: Deploy to cloud platforms like Azure.
