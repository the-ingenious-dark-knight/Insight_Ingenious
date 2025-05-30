# ingenious-slim Documentation

Welcome to the ingenious-slim documentation. This guide will help you understand how to use, configure, and extend this slim fork of Insight Ingenious for building agent-based applications.

## About ingenious-slim

ingenious-slim is a lightweight fork of Insight Ingenious, providing a minimal, developer-friendly template for building AutoGen-based agent APIs with FastAPI. It provides a solid foundation for creating multi-agent applications with clean architecture and simple configuration.

## Key Features

- **Minimal Abstraction**: Thin wrapper over AutoGen and FastAPI
- **Simple Configuration**: YAML + .env files (no complex profiles)
- **Ready-to-Use Agents**: Chat, Research, and SQL agents included
- **RESTful API**: Clean endpoints for agent interaction
- **Basic Authentication**: HTTP Basic Auth built-in
- **Developer-Friendly**: Easy to understand, extend, and maintain

## Important Notes

- This project **exclusively uses** `uv` for Python package management and environment operations.
- This project **only supports** Azure OpenAI integrations, not standard OpenAI.

## Documentation Structure

- **[Getting Started](./getting_started.md)**: Quick start guide
- **[Guides](./guides/index.md)**: How-to guides for common tasks
- **[API Reference](./api/index.md)**: API endpoint documentation
- **[Architecture](./architecture/index.md)**: System architecture overview
- **[Examples](./examples/index.md)**: Example usage scenarios

## Contributing

Please see the [CONTRIBUTING.md](../CONTRIBUTING.md) file for guidelines on how to contribute to this project.
