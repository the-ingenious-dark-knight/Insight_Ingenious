# Clean Architecture in Insight Ingenious

This document describes the clean architecture implementation in Insight Ingenious after the refactoring.

## Overview

The refactoring has transformed the project to follow clean architecture principles, with clear separation of concerns and dependency rules. The key principle is that dependencies point inward, with domain at the core.

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

## Design Patterns

The project uses several design patterns to promote code quality and maintainability:

### 1. Repository Pattern

The repository pattern abstracts the data layer and provides a consistent interface for data access:

```python
# Domain interface
class IChatHistoryRepository(ABC):
    @abstractmethod
    async def add_message(self, message: Message) -> str:
        pass

    @abstractmethod
    async def get_conversation(self, conversation_id: str) -> List[Message]:
        pass

# Infrastructure implementation
class ChatHistoryRepository(IChatHistoryRepository):
    def __init__(self, db_client):
        self.db_client = db_client

    async def add_message(self, message: Message) -> str:
        # Implementation
        pass

    async def get_conversation(self, conversation_id: str) -> List[Message]:
        # Implementation
        pass
```

### 2. Factory Pattern

The factory pattern centralizes object creation and manages dependencies:

```python
class Factory:
    def __init__(self, config):
        self.config = config
        self._instances = {}

    def get_chat_history_repository(self):
        if "chat_history_repository" not in self._instances:
            db_client = self._create_db_client()
            self._instances["chat_history_repository"] = ChatHistoryRepository(db_client)
        return self._instances["chat_history_repository"]

    def get_chat_service(self):
        if "chat_service" not in self._instances:
            self._instances["chat_service"] = ChatService(
                chat_history_repository=self.get_chat_history_repository(),
                config=self.config
            )
        return self._instances["chat_service"]
```

### 3. Dependency Injection

Dependencies are injected rather than created within components, promoting loose coupling and testability:

```python
class ChatService:
    def __init__(self, chat_history_repository, config):
        self.chat_history_repository = chat_history_repository
        self.config = config

    async def process_chat(self, user_input: str) -> ChatResponse:
        # Implementation using injected dependencies
        pass
```

## New Directory Structure

The project follows a clean architecture directory structure:

```
ingenious/
│
├── common/            # Common utilities and cross-cutting concerns
│   ├── config/        # Configuration management
│   ├── errors/        # Custom exceptions
│   ├── logging.py     # Logging configuration
│   └── utils/         # Utility functions
│
├── domain/            # Core business models and logic
│   ├── interfaces/    # Abstract interfaces
│   │   ├── repository/# Repository interfaces
│   │   └── service/   # Service interfaces
│   └── model/         # Domain entities and value objects
│
├── infrastructure/    # External systems implementation
│   ├── database/      # Database implementations
│   ├── external/      # External services
│   └── storage/       # File storage implementations
│
├── application/       # Business logic coordination
│   ├── factory.py     # Dependency injection factory
│   ├── repository/    # Repository implementations
│   └── service/       # Service implementations
│
├── presentation/      # User interfaces
│   ├── api/           # FastAPI endpoints
│   ├── chainlit/      # ChainLit UI
│   └── templates/     # Templates for various outputs
│
└── extensions/        # Extension system
    ├── loader.py      # Extension loading mechanism
    └── template/      # Template for new extensions
```

## Benefits of the Clean Architecture

1. **Separation of Concerns**: Each layer has a specific responsibility and clear boundaries
2. **Testability**: Interfaces and dependency injection make unit testing easier
3. **Flexibility**: Components can be replaced without affecting other parts of the system
4. **Maintainability**: Clear structure makes the codebase easier to understand and modify
5. **Extensibility**: New features can be added through the extension system without modifying core code

## Dependency Management with UV

The project uses the UV package manager for dependency management. UV offers several advantages:

1. **Speed**: 10-100x faster than pip for installing packages
2. **Lockfiles**: Reproducible environments with uv.lock
3. **Caching**: Efficient disk usage with global package caching
4. **Project Management**: Support for managing project dependencies

To set up the development environment with UV:

```bash
# Install dependencies
./install_deps.py

# Activate the virtual environment
source .venv/bin/activate
```

## Migration Status

The refactoring has been completed with the following achievements:

- ✅ Created new directory structure following clean architecture principles
- ✅ Moved files to their new locations
- ✅ Created interface definitions in the domain layer
- ✅ Updated import paths in key files
- ✅ Implemented Factory pattern for dependency injection
- ✅ Properly implemented IFileRepository interface
- ✅ Cleaned up old directories and files
- ✅ Verified no old import patterns remain
- ✅ Removed backup files

Additional improvements planned:

- Integration tests for the refactored architecture
- Continuous integration setup
- Expanded documentation on customizing and extending the system
