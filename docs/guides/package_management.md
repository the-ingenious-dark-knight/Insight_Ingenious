# Package Management with uv

Insight Ingenious exclusively uses [uv](https://github.com/astral-sh/uv) for Python package management and environment operations. This guide explains how to use uv for common tasks in this project.

## What is uv?

uv is a modern, fast Python package installer and resolver. It serves as a replacement for pip, pip-tools, and virtualenv, offering significant performance improvements.

## Important Note

**Never use pip or pip-tools directly** in this project. Always use the uv commands listed below.

## Common Commands

### Running Python Scripts

Always run Python scripts through uv to ensure they use the correct environment:

```bash
# Run a Python script
uv run python main.py

# Run a specific module
uv run python -m module_name

# Run with command line arguments
uv run python main.py --config custom.yaml
```

### Installing Dependencies

```bash
# Install all dependencies
uv pip install -e .

# Install a specific package
uv add <package>

# Install a development dependency
uv add <package> --dev
```

### Removing Dependencies

```bash
# Remove a package
uv remove <package>

# Remove a development dependency
uv remove <package> --group dev
```

### Running Tests

```bash
# Run pytest
uv run pytest

# Run with specific options
uv run pytest tests/specific_test.py -v
```

### Viewing Installed Packages

```bash
# List packages in a tree structure
uv tree
```

## Working with Requirements Files

If you need to generate or update requirements files:

```bash
# Export dependencies to requirements.txt
uv pip freeze > requirements.txt
```

## Project Structure

The project's dependencies are defined in `pyproject.toml`. The uv lock file (`uv.lock`) ensures consistent installations across environments.

## Troubleshooting

If you encounter issues with dependencies:

1. Try removing the environment and reinstalling:
   ```bash
   uv pip uninstall -y -r <(uv pip freeze)
   uv pip install -e .
   ```

2. Check for conflicting dependencies:
   ```bash
   uv tree
   ```

3. Ensure your uv installation is up to date:
   ```bash
   pip install -U uv
   ```
