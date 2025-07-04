# Insight Ingenious

A powerful framework for building, managing, and deploying multi-agent AI conversations.

## Overview
Insight Ingenious lets you orchestrate multiple AI agents and deploy them as an API for seamless integration into your applications.

## ⚡ Quick Start

Get up and running in 5 minutes with Azure OpenAI!

### Prerequisites
- ✅ Python 3.13+
- ✅ Azure OpenAI API credentials
- ✅ [uv package manager](https://docs.astral.sh/uv/) 

### 5-Minute Setup

1. **Install and Initialize**:
    ```bash
    # From your project directory
    uv pip install -e ./Insight_Ingenious
    uv run ingen init
    ```

2. **Configure Credentials**:
    ```bash
    # Edit .env with your Azure OpenAI credentials
    cp .env.example .env
    nano .env  # Add AZURE_OPENAI_API_KEY and AZURE_OPENAI_BASE_URL
    ```

3. **Set Environment and Start**:
    ```bash
    export INGENIOUS_PROJECT_PATH=$(pwd)/config.yml
    export INGENIOUS_PROFILE_PATH=$(pwd)/profiles.yml
    uv run ingen serve
    ```

4. **Test the API**:
    ```bash
    # Test bike insights workflow
    curl -X POST http://localhost:80/api/v1/chat \
      -H "Content-Type: application/json" \
      -d '{"user_prompt": "Hello", "conversation_flow": "classification_agent"}'
    ```

🎉 **That's it!** You should see a JSON response from the AI agent.

### 📚 Detailed Setup
- **📖 Complete guide**: [docs/QUICKSTART.md](docs/QUICKSTART.md) - Full walkthrough with examples
- **🔧 Troubleshooting**: [docs/troubleshooting/README.md](docs/troubleshooting/README.md) - Common issues & fixes
- **📡 API Reference**: [docs/api/WORKFLOWS.md](docs/api/WORKFLOWS.md) - All endpoints & workflows

## 🎯 Workflow Categories

Insight Ingenious provides multiple conversation workflows with different configuration requirements:

### ✅ **Minimal Configuration** (Azure OpenAI only)
- `classification_agent` - Route input to specialized agents
- `bike_insights` - Sample domain-specific analysis

### 🔍 **Azure Search Required**
- `knowledge_base_agent` - Search knowledge bases

### 📊 **Database Required**
- `sql_manipulation_agent` - Execute SQL queries

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

- **[⚡ Quick Start Guide](docs/QUICKSTART.md)** - **Complete 5-minute setup with examples**
- **[🛠️ Troubleshooting](docs/troubleshooting/README.md)** - **Common issues and solutions**
- **[📡 API Reference](docs/api/WORKFLOWS.md)** - **All endpoints and workflows**
- [Getting Started](docs/getting-started/README.md) - Installation and setup details
- [Workflow Configuration Requirements](docs/workflows/README.md) - Service setup for different workflows
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
