# Contributing to Insight Ingenious

Thank you for your interest in contributing to Insight Ingenious! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

By participating in this project, you agree to abide by our code of conduct, which expects all contributors to be respectful, open-minded, and collaborative.

## Getting Started

### Prerequisites

- Python 3.13 or higher
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
   uv init
   uv run ingen init
   ```

## Development Workflow

### Branch Strategy

- `main`: Stable production code
- Feature branches: Use format `feature/your-feature-name`
- Bug fix branches: Use format `fix/issue-description`

### Testing

Before submitting a PR, please ensure your code passes all tests:

```bash
uv run pytest
```

### Linting and Formatting

This project uses:
- [Pre-commit](https://pre-commit.com/) hooks to enforce standards

Install pre-commit hooks:
```bash
uv run pre-commit install
```

Occassionally run and run before submitting PR:
```bash
uv run pre-commit run --all-files
```

### Type Safety

This project uses:
- [mypy](https://mypy.readthedocs.io/) for static type checking

Occassionally run and run before submitting PR:
```bash
uv run mypy .
```

Refer to the mypy prompt in .github/prompts for a better understanding of expected type safety in a PR.

### Built-in Prompts
Please refer to the folder .github/prompts for pre-written prompts that will be helpful in developing Ingenious.

## Getting Help

If you need help, you can reach out to the maintainers

Thank you for contributing to Insight Ingenious!
