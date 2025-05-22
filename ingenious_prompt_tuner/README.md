# Ingenious Prompt Tuner

This package provides a modular Flask-based UI for prompt tuning and agent testing in the Insight Ingenious framework.

## Structure (after refactor)
- `__init__.py`: App factory and blueprint registration
- `auth.py`: Authentication blueprint
- `utilities.py`: Utility functions and helpers
- `event_handler.py`: Event data loading and chat request preparation
- `routes/`: All Flask blueprints (home, prompts, responses)
- `templates/`: HTML and JS templates
- `static/`: Static assets

## Removed/legacy files
- `auth_manager.py`, `config_manager.py`, `error_handler.py`, `run_flask_app.py`, and all empty files in `services/` are removed for clarity and maintainability.

## Usage
Import and use `create_app()` from `ingenious_prompt_tuner`.
