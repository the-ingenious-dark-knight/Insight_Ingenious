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
    Create a `.env` file with your Azure OpenAI credentials:
    ```bash
    # Create .env file with your credentials
    cat > .env << 'EOF'
    # Azure OpenAI Configuration
    INGENIOUS_MODELS__0__MODEL=gpt-4o-mini
    INGENIOUS_MODELS__0__API_KEY=your-api-key-here
    INGENIOUS_MODELS__0__BASE_URL=https://your-resource.openai.azure.com/openai/deployments/gpt-4o-mini/chat/completions?api-version=2024-08-01-preview
    INGENIOUS_MODELS__0__API_TYPE=rest
    INGENIOUS_MODELS__0__API_VERSION=2024-08-01-preview

    # Optional: Enable authentication
    INGENIOUS_WEB_CONFIGURATION__AUTHENTICATION__ENABLE=false
    EOF
    ```

3. **Validate Configuration**:
    ```bash
    uv run ingen validate  # Check configuration before starting
    ```

    > **Note**: Ingenious now uses **pydantic-settings** for configuration via environment variables. The legacy YAML configuration files (`config.yml`, `profiles.yml`) have been migrated to environment variables with `INGENIOUS_` prefixes.

4. **Start the Server**:
    ```bash
    uv run ingen serve
    ```

5. **Verify Health**:
    ```bash
    # Check server health (default port is 80)
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
- `ingen validate` - Validate system configuration and requirements
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
- `knowledge-base-agent` - Search knowledge bases (stable local ChromaDB implementation, experimental Azure Search)
- `sql-manipulation-agent` - Execute SQL queries (stable local SQLite implementation, experimental Azure SQL)

### Extension Template Workflows (Available via project template)
- `bike-insights` - Comprehensive bike sales analysis showcasing multi-agent coordination (**Note**: Created only when you run `ingen init` - demonstrates custom workflow development)

### Configuration Requirements by Workflow
- **Minimal setup** (Azure OpenAI only): `classification-agent`, `bike-insights`
- **Local implementations** (stable): `knowledge-base-agent` (ChromaDB), `sql-manipulation-agent` (SQLite)
- **Azure integrations** (experimental): Azure Search for knowledge base, Azure SQL for database queries

> **Note**: Local implementations (ChromaDB, SQLite) are stable and recommended for production. Azure integrations are experimental and may contain bugs. Use `uv run ingen workflows` to check configuration requirements for each workflow.


## Project Structure

- `ingenious/`: Core framework code
  - `api/`: API endpoints and routes
  - `auth/`: Authentication and JWT handling
  - `chainlit/`: Web UI components
  - `cli/`: Command-line interface modules
  - `config/`: Configuration management (pydantic-settings based, environment variables)
  - `core/`: Core logging and error handling
  - `dataprep/`: Data preparation utilities
  - `db/`: Database integration (SQLite and Azure SQL)
  - `document_processing/`: Document analysis and processing
  - `errors/`: Error handling and custom exceptions
  - `external_services/`: External service integrations
  - `files/`: File storage utilities
  - `main/`: FastAPI application factory and routing
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
