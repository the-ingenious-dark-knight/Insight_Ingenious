# Infrastructure Layer

This directory contains the infrastructure layer of the application, following the principles of Clean Architecture and SOLID design.

## SOLID Principles Applied

### Single Responsibility Principle (SRP)
Each class has a single responsibility:
- Database clients handle database connections and operations
- Storage clients handle file and blob storage operations
- Repository implementations handle data access logic

### Open/Closed Principle (OCP)
The code is open for extension but closed for modification:
- Interfaces define contracts that can be extended with new implementations
- Factory classes allow for creating different implementations without changing client code

### Liskov Substitution Principle (LSP)
Derived classes can be substituted for their base classes:
- All implementations fully implement their interfaces
- Clients depend on interfaces, not concrete implementations

### Interface Segregation Principle (ISP)
Interfaces are focused and specific:
- Database interface defines only database operations
- Storage interface defines only storage operations
- Service interfaces define only service-specific operations

### Dependency Inversion Principle (DIP)
High-level modules depend on abstractions, not details:
- Domain interfaces are defined in the domain layer
- Infrastructure implementations depend on these interfaces
- Dependency injection is used to provide implementations

## Directory Structure

- `database/`: Database clients and repository implementations
  - `client/`: Specific database clients
  - `repo/`: Repository implementations using database clients
  - `sqlite/`: SQLite-specific implementations
  - `duckdb/`: DuckDB-specific implementations
  - `cosmos/`: Cosmos DB-specific implementations

- `external/`: External service integrations
  - `openai_service.py`: OpenAI API integration

- `storage/`: Storage clients and repository implementations
  - `azure/`: Azure Blob Storage implementations
  - `local/`: Local file storage implementations
  - `repo/`: Repository implementations using storage clients

## Factories

The infrastructure layer uses factory classes to create implementations:

- `database/factory.py`: Factory for database clients
- `database/repo/factory.py`: Factory for database repositories
- `external/factory.py`: Factory for external services
- `storage/factory.py`: Factory for storage clients
- `storage/repo/factory.py`: Factory for storage repositories

This allows for easy substitution of implementations and testing with mocks.

## Extending the Infrastructure Layer

To add a new implementation:

1. Implement the appropriate interface from the domain layer
2. Add a factory method to create the new implementation
3. Update any necessary configuration to use the new implementation

This approach ensures that the infrastructure layer can be extended without modifying existing code.
