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
    #### For Linux-based Environments
    ```bash
    # Edit .env with your Azure OpenAI credentials
    cp .env.example .env
    nano .env  # Add AZURE_OPENAI_API_KEY and AZURE_OPENAI_BASE_URL
    ```
    #### For Windows-based Environments
    ```bash
    # Edit .env with your Azure OpenAI credentials
    cp .env.example .env
    # Assuming you have VSCode installation. If none, open .env file with your favorite editor
    # and add  AZURE_OPENAI_API_KEY and AZURE_OPENAI_BASE_URL to it.
    code .env  # Add AZURE_OPENAI_API_KEY and AZURE_OPENAI_BASE_URL
    ```

3. **Set Environment Variables**:
    ```bash
    export INGENIOUS_PROJECT_PATH=$(pwd)/config.yml
    export INGENIOUS_PROFILE_PATH=$(pwd)/profiles.yml
    ```

    #### For Windows-based Environments
    ```bash
    $env:INGENIOUS_PROJECT_PATH = "{your_project_folder}/config.yml"
    $env:INGENIOUS_PROFILE_PATH = "{profile_folder_location}/profiles.yml"                        
    uv run ingen validate  # Check configuration before starting
    ```

4. **Start the Server**:
    ```bash
    uv run ingen serve
    ```

5. **Verify Health**:
    ```bash
    # Check server health (default port is 80, but configurable)
    curl http://localhost:80/api/v1/health
    ```

6. **Test with Core Workflow**:
    ```bash
    # Test classification agent (available in core library)
    curl -X POST http://localhost:80/api/v1/chat \
      -H "Content-Type: application/json" \
      -d '{
        "user_prompt": "Analyze this customer feedback: Great product!",
        "conversation_flow": "classification-agent"
      }'
    ```

That's it! You should see a JSON response with AI analysis of the input.

**Note**: Core workflows like `classification-agent`, `knowledge-base-agent`, and `sql-manipulation-agent` are included in the library. The `bike-insights` workflow is only available when you run `ingen init` as part of the project template - it demonstrates how to build custom workflows on top of the core framework.

## CLI Commands

**Core commands:**
- `ingen init` - Initialize a new project with templates and configuration
- `ingen serve` - Start the API server with web interface
- `ingen workflows [workflow_name]` - List available workflows and their requirements
- `ingen test` - Run agent workflow tests
- `ingen prompt-tuner` - Start standalone prompt tuning interface

**Data processing commands:**
- `ingen document-processing extract <path>` - Extract text from documents (PDF, DOCX, images) 
- `ingen dataprep crawl <url>` - Web scraping utilities using Scrapfly

**Help and information:**
- `ingen --help` - Show comprehensive help
- `ingen <command> --help` - Get help for specific commands

For complete CLI reference, see [docs/CLI_REFERENCE.md](docs/CLI_REFERENCE.md).

## API Endpoints

When the server is running, the following endpoints are available:

**Core API:**
- `POST /api/v1/chat` - Chat with AI workflows
- `GET /api/v1/health` - Health check endpoint

**Diagnostics:**
- `GET /api/v1/workflows` - List all workflows and their status
- `GET /api/v1/workflow-status/{workflow_name}` - Check specific workflow configuration
- `GET /api/v1/diagnostic` - System diagnostic information

**API Management:**
- `GET /api/v1/prompts/list/{revision_id}` - List prompt templates
- `GET /api/v1/prompts/view/{revision_id}/{filename}` - View prompt content
- `POST /api/v1/prompts/update/{revision_id}/{filename}` - Update prompt
- `PUT /api/v1/messages/{message_id}/feedback` - Submit message feedback

**Authentication (if enabled):**
- `POST /api/v1/auth/login` - JWT login
- `POST /api/v1/auth/refresh` - Refresh JWT token
- `GET /api/v1/auth/verify` - Verify JWT token

**Web Interfaces:**
- `/chainlit` - Interactive chat interface
- `/prompt-tuner` - Prompt tuning interface (if enabled)

## Workflow Categories

Insight Ingenious provides multiple conversation workflows with different configuration requirements:

### Core Workflows (Available in library)
- `classification-agent` - Route input to specialized agents based on content (Azure OpenAI only)
- `knowledge-base-agent` - Search knowledge bases (requires Azure Cognitive Search or local ChromaDB)
- `sql-manipulation-agent` - Execute SQL queries (requires Azure SQL or local SQLite)

### Extension Template Workflows (Available via project template)
- `bike-insights` - Comprehensive bike sales analysis showcasing multi-agent coordination (**Note**: Created only when you run `ingen init` - demonstrates custom workflow development)

### Configuration Requirements by Workflow
- **Minimal setup** (Azure OpenAI only): `classification-agent`
- **Requires Azure Search**: `knowledge-base-agent` 
- **Requires database**: `sql-manipulation-agent` (supports both Azure SQL and SQLite)

> **Note**: Azure integrations (Search, SQL) are supported but may require additional configuration. Local implementations (SQLite) are recommended for development and testing.


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
