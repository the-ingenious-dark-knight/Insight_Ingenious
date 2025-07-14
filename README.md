# Insight Ingenious

An enterprise-grade Python library for quickly setting up APIs to interact with AI Agents, featuring tight integrations with Microsoft Azure services and comprehensive utilities for debugging and customization.

## Quick Start

Get up and running in 5 minutes with Azure OpenAI!

### Prerequisites
- Python 3.13+
- Azure OpenAI API credentials
- [uv package manager](https://docs.astral.sh/uv/)

### 5-Minute Setup

1. **Install and Initialize**:
    ```bash
    # From your project directory
    uv add ingenious
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
    curl http://localhost:80/health
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

That's it! You should see a comprehensive JSON response with insights from multiple AI agents analyzing the bike sales data.

**Note**: The `bike-insights` workflow is created when you run `ingen init` - it's part of the project template setup, not included in the core library. You can now build on `bike-insights` as a template for your specific use case.

## CLI Commands

Core commands:
- `ingen init` - Initialize a new project
- `ingen serve` - Start the API server
- `ingen workflows` - List available workflows and requirements
- `ingen test` - Run workflow tests
- `ingen status` - Check system configuration
- `ingen validate` - Validate setup and configuration
- `ingen help` - Show comprehensive help

Data processing commands:
- `ingen document-processing <path>` - Extract text from documents (PDF, DOCX, images)
- `ingen dataprep crawl <url>` - Web scraping utilities using Scrapfly

For complete CLI reference, see [docs/CLI_REFERENCE.md](docs/CLI_REFERENCE.md).

## API Endpoints

When the server is running, the following endpoints are available:

**Core API:**
- `POST /api/v1/chat` - Chat with AI workflows
- `GET /health` - Health check endpoint

**Diagnostics:**
- `GET /workflows` - List all workflows and their status
- `GET /workflow-status/{workflow_name}` - Check specific workflow configuration
- `GET /diagnostic` - System diagnostic information

**Web Interfaces:**
- `/chainlit` - Interactive chat interface
- `/prompt-tuner` - Prompt tuning interface (if enabled)

## Workflow Categories

Insight Ingenious provides multiple conversation workflows with different configuration requirements:

### Core Workflows (Available in library)
- `classification-agent` - Route input to specialized agents based on content (Azure OpenAI only)
- `knowledge-base-agent` - Search knowledge bases using local ChromaDB (stable local implementation)
- `sql-manipulation-agent` - Execute SQL queries using local SQLite (stable local implementation)

### Extension Template Workflows (Available via project template)
- `bike-insights` - Comprehensive bike sales analysis showcasing multi-agent coordination (created when you run `ingen init`)

> **Note**: Only local implementations (ChromaDB for knowledge-base-agent, SQLite for sql-manipulation-agent) are currently stable. Azure Search and Azure SQL integrations are experimental and may contain bugs.


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

For detailed documentation, see the [docs](https://insight-services-apac.github.io/ingenious/) or view locally in the `docs/` directory.

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](https://github.com/Insight-Services-APAC/ingenious/blob/main/CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the terms specified in the [LICENSE](https://github.com/Insight-Services-APAC/ingenious/blob/main/LICENSE) file.
