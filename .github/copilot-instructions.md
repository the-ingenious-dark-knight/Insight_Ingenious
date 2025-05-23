# Package Management: uv

This project uses uv for Python package and environment management.

## Common Commands

- **Add a dependency:**
  `uv add <package>`

- **Add a dev dependency:**
  `uv add <package> --dev`

- **Remove a dependency:**
  `uv remove <package>`

- **Run a command in the project environment:**
  `uv run <command>`

## Note

- Do **not** use `pip` or `pip-tools` directly; use `uv` commands above.
