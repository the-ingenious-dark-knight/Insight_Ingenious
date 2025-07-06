# Contributing to Insight Ingenious

Thank you for your interest in contributing to Insight Ingenious! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

By participating in this project, you agree to abide by our code of conduct, which expects all contributors to be respectful, open-minded, and collaborative.

## Getting Started

### Prerequisites

- Python 3.10 or higher
- [uv](https://docs.astral.sh/uv/) for Python package management
- Git

### Setting Up Your Development Environment

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/ingenious.git
   cd ingenious
   ```

3. Set up a development environment:
   ```bash
   uv sync --extra dev
   ```

4. Configure your project:
   ```bash
   uv run ingen initialize-new-project
   ```

## Development Workflow

### Branch Strategy

- `main`: Stable production code
- `develop`: Integration branch for features
- Feature branches: Use format `feature/your-feature-name`
- Bug fix branches: Use format `fix/issue-description`

### Making Changes

1. Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes, adhering to the coding standards

3. Add and commit your changes:
   ```bash
   git add .
   git commit -m "Description of your changes"
   ```

4. Push your branch to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

5. Create a Pull Request against the `develop` branch of the main repository

### Testing

Before submitting a PR, please ensure your code passes all tests:

```bash
uv run pytest
```

You can also use the test harness to verify agent behavior:

```bash
uv run ingen run-test-batch
```

### Code Style

This project uses:
- [Ruff](https://docs.astral.sh/ruff/) for linting and formatting
- [Pre-commit](https://pre-commit.com/) hooks to enforce standards

Install pre-commit hooks:
```bash
uv add pre-commit --dev
pre-commit install
```

## Project Structure

When adding new features, please follow the existing structure:

- Put core framework code in `ingenious/`
- Add extension templates to `ingenious_extensions_template/`
- Update relevant documentation in `docs/`

### Adding a New Conversation Pattern

1. Create a new module in `ingenious/services/chat_services/multi_agent/conversation_patterns/`
2. Implement a `ConversationPattern` class that follows the interface
3. Create a corresponding flow in `ingenious/services/chat_services/multi_agent/conversation_flows/`
4. Add appropriate tests

### Adding a New Agent

1. Create a new module in `ingenious/services/chat_services/multi_agent/agents/`
2. Define the agent's system prompt and behavior
3. Register the agent in the appropriate conversation pattern

## Documentation

Please update documentation when adding or modifying features:

- Code should be well commented
- Update relevant markdown files in `docs/`
- Add examples for new features

## Pull Request Process

1. Ensure all tests pass
2. Update documentation as needed
3. Get at least one code review
4. Once approved, a maintainer will merge your PR

## Release Process

Releases are managed by the core team using semantic versioning:

- Major version: Breaking API changes
- Minor version: New features, non-breaking changes
- Patch version: Bug fixes and minor improvements

## Getting Help

If you need help, you can:
- Open an issue for questions
- Reach out to the maintainers

Thank you for contributing to Insight Ingenious!
