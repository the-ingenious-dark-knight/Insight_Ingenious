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

3. **Validate Setup** (Recommended):
    ```bash
    export INGENIOUS_PROJECT_PATH=$(pwd)/config.yml
    export INGENIOUS_PROFILE_PATH=$(pwd)/profiles.yml
    uv run ingen validate  # Check configuration before starting
    ```

4. **Start the Server**:
    ```bash
    uv run ingen serve
    ```

5. **Verify Health**:
    ```bash
    # Check server health
    curl http://localhost:80/api/v1/health
    ```

6. **Test the API**:
    ```bash
    # Test bike insights workflow (the "Hello World" of Ingenious)
    curl -X POST http://localhost:80/api/v1/chat \
      -H "Content-Type: application/json" \
      -d '{
        "user_prompt": "{\"stores\": [{\"name\": \"QuickStart Store\", \"location\": \"NSW\", \"bike_sales\": [{\"product_code\": \"QS-001\", \"quantity_sold\": 1, \"sale_date\": \"2023-04-15\", \"year\": 2023, \"month\": \"April\", \"customer_review\": {\"rating\": 5.0, \"comment\": \"Perfect bike for getting started!\"}}], \"bike_stock\": []}], \"revision_id\": \"quickstart-1\", \"identifier\": \"hello-world\"}",
        "conversation_flow": "bike-insights"
      }'
    ```

🎉 **That's it!** You should see a comprehensive JSON response with insights from multiple AI agents analyzing the bike sales data.

### 📚 Detailed Setup
- **📖 Complete guide**: [docs/QUICKSTART.md](docs/QUICKSTART.md) - Full walkthrough with examples
- **🔧 Troubleshooting**: [docs/troubleshooting/README.md](docs/troubleshooting/README.md) - Common issues & fixes
- **📡 API Reference**: [docs/api/WORKFLOWS.md](docs/api/WORKFLOWS.md) - All endpoints & workflows

## 🎯 Workflow Categories

Insight Ingenious provides multiple conversation workflows with different configuration requirements:

### ⭐ **"Hello World" Workflow** (Azure OpenAI only)
- `bike-insights` - **The recommended starting point** - Comprehensive bike sales analysis showcasing multi-agent coordination

### ✅ **Simple Text Processing** (Azure OpenAI only)
- `classification-agent` - Route input to specialized agents based on content

### 🔍 **Azure Search Required**
- `knowledge-base-agent` - Search knowledge bases

### 📊 **Database Required**
- `sql-manipulation-agent` - Execute SQL queries

**📋 See [Workflow Configuration Requirements](docs/workflows/README.md) for detailed setup instructions.**

## Project Structure

- `ingenious/`: Core framework code
  - `api/`: API endpoints and routes
  - `chainlit/`: Web UI components
  - `config/`: Configuration management
  - `core/`: Core logging and utilities
  - `dataprep/`: Data preparation utilities
  - `db/`: Database integration
  - `document_processing/`: Document analysis and processing
  - `errors/`: Error handling and custom exceptions
  - `external_services/`: External service integrations
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
