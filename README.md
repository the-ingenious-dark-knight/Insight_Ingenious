# Insight Ingenious

A powerful framework for building, managing, and deploying multi-agent AI conversations.

## Overview
Insight Ingenious lets you orchestrate multiple AI agents and deploy them as an API for seamless integration into your applications.

## Quickstart

**Prerequisites:**

- **Python 3.13 or higher**

1. Clone the repository:
    ```bash
    git clone https://github.com/Insight-Services-APAC/Insight_Ingenious.git
    cd Insight_Ingenious
    ```

2. Install [uv](https://docs.astral.sh/uv/) for Python package and environment management (if not already installed):
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

3. Set up the project and install dependencies:
    ```bash
    uv sync
    uv run pre-commit install
    uv pip install -e .
    ```

4. Initialize a new project:
    ```bash
    uv run ingen initialize-new-project
    ```

5. **Check workflow requirements** (Important!):
    ```bash
    # See all available workflows and their configuration requirements
    uv run ingen workflow-requirements all

    # Check specific workflow requirements
    uv run ingen workflow-requirements classification_agent
    ```

6. **Configure your services**:
   - Update `config.yml` with your project settings
   - Update `~/.ingenious/profiles.yml` with API keys and credentials
   - Set environment variables:
     ```bash
     export INGENIOUS_PROJECT_PATH=/path/to/config.yml
     export INGENIOUS_PROFILE_PATH=$HOME/.ingenious/profiles.yml
     ```

7. **Start with minimal configuration** workflows:
   ```bash
   # Start the server
   uv run ingen run-rest-api-server

   # Test basic workflow (only needs Azure OpenAI)
   curl -X POST http://localhost:8081/api/v1/chat \
     -H "Content-Type: application/json" \
     -d '{"user_prompt": "Hello", "conversation_flow": "classification_agent"}'
   ```

8. Run pre-commit hooks on all files:
    ```bash
    uv run pre-commit run --all-files
    ```

## 🎯 Workflow Categories

Insight Ingenious provides multiple conversation workflows with different configuration requirements:

### ✅ **Minimal Configuration** (Azure OpenAI only)
- `classification_agent` - Route input to specialized agents
- `bike_insights` - Sample domain-specific analysis

### 🔍 **Azure Search Required**
- `knowledge_base_agent` - Search knowledge bases

### 📊 **Database Required**
- `sql_manipulation_agent` - Execute SQL queries
- `pandas_agent` - Data analysis with pandas

### 🌐 **Web Search** (currently mock)
- `web_critic_agent` - Web search and fact-checking

**📋 See [Workflow Configuration Requirements](docs/workflows/README.md) for detailed setup instructions.**

## Project Structure

- `ingenious/`: Core framework code
  - `api/`: API endpoints and routes
  - `chainlit/`: Web UI components
  - `config/`: Configuration management
  - `db/`: Database integration
  - `files/`: File storage utilities
  - `models/`: Data models and schemas
  - `services/`: Core services including chat and agent services
  - `templates/`: Prompt templates and HTML templates
  - `utils/`: Utility functions

- `ingenious_extensions_template/`: Template for custom extensions
  - `api/`: Custom API routes
  - `models/`: Custom data models
  - `sample_data/`: Sample data for testing
  - `services/`: Custom agent services
  - `templates/`: Custom prompt templates
  - `tests/`: Test harness for agent prompts

- `ingenious_prompt_tuner/`: Tool for tuning and testing prompts

## Documentation

For detailed documentation, see the [docs/](docs/) directory:

- **[Getting Started](docs/getting-started/README.md)** - **Quick start guide and installation**
- **[Workflow Configuration Requirements](docs/workflows/README.md)** - **Essential guide to configure workflows**
- [User Guides](docs/guides/README.md) - Feature-specific usage guides
- [Extensions & Customization](docs/extensions/README.md) - Creating custom components
- [Configuration Guide](docs/configuration/README.md) - Detailed configuration reference
- [Architecture Overview](docs/architecture/README.md) - System design and architecture
- [Development Guide](docs/development/README.md) - Contributing and development setup
- [Components Reference](docs/components/README.md) - Technical component documentation

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the terms specified in the [LICENSE](LICENSE) file.
