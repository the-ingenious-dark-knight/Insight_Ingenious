---
title: "CLI Reference"
layout: single
permalink: /CLI_REFERENCE/
sidebar:
  nav: "docs"
toc: true
toc_label: "CLI Commands"
toc_icon: "terminal"
---

# Insight Ingenious CLI Reference

The `ingen` command-line interface provides intuitive commands for managing your AI agent workflows.

## Quick Start

```bash
# Initialize a new project
uv run ingen init

# Validate configuration
uv run ingen validate

# Start the server
uv run ingen serve

# List available workflows
uv run ingen workflows

# Run tests
uv run ingen test
```

## Core Commands

### `ingen init`
Initialize a new Insight Ingenious project in the current directory.

**What it creates:**
- `.env.example` - Example environment variables for configuration
- `ingenious_extensions/` - Custom agents and workflows
- `Dockerfile and .dockerignore` - Docker deployment templates
- `tmp/` - Temporary files and memory
- Migration templates for legacy YAML configurations (if needed)

**Next Steps:**
1. Copy `.env.example` to `.env` and add your credentials
2. Configure environment variables (see Configuration Guide)
3. Run `ingen validate` to verify setup
4. Run `ingen serve` to start the server

> **Note**: Ingenious now uses pydantic-settings with environment variables instead of YAML files. Legacy `config.yml` and `profiles.yml` can be migrated using the migration script.

### `ingen serve`
Start the API server with web interfaces.

**Options:**
- `--host, -h` - Host to bind (default: 0.0.0.0)
- `--port` - Port to bind (default: 80 or $WEB_PORT)
- `--config, -c` - Path to config.yml file (for legacy compatibility)
- `--profile, -p` - Path to profiles.yml file (for legacy compatibility)
- `--no-prompt-tuner` - Disable prompt tuner interface

**Interfaces:**
- API: `http://localhost:<port>/api/v1/` (e.g., `http://localhost:8000/api/v1/` when using `--port 8000`)
- Health Check: `http://localhost:<port>/api/v1/health`
- API Documentation: `http://localhost:<port>/docs`
- Prompt Management: `/api/v1/prompts/*` endpoints

**Example:**
```bash
# Start server on default port 80 (requires sudo on most systems)
sudo uv run ingen serve

# Start server on port 8000 (recommended for development)
uv run ingen serve --port 8000
```

> **Configuration**: The server uses environment variables for configuration. Ensure your `.env` file is properly configured before starting the server.

### `ingen workflows [workflow-name]`
Show available workflows and their requirements.

**Examples:**
```bash
uv run ingen workflows                          # List all workflows
uv run ingen workflows classification-agent     # Show specific workflow details
uv run ingen workflows bike-insights            # Show bike insights workflow (recommended start)
```

**Available Workflows:**
- `classification-agent` - Simple text classification and routing to categories (core library, minimal config)
- `bike-insights` - Sample domain-specific multi-agent analysis (template workflow, minimal config) **RECOMMENDED FOR NEW USERS**
- `knowledge-base-agent` - Search and retrieve information from knowledge bases (core library, supports ChromaDB or Azure Search)
- `sql-manipulation-agent` - Execute SQL queries based on natural language (core library, supports SQLite or Azure SQL)

**Note:**
- Core library workflows are always available
- Template workflows like `bike-insights` are created with `uv run ingen init`
- Both local (ChromaDB, SQLite) and Azure (Azure Search, Azure SQL) implementations are production-ready
- Legacy underscore names (`classification_agent`, `bike_insights`, etc.) are still supported for backward compatibility

### `ingen test`
Run agent workflow tests.

**Options:**
- `--log-level, -l` - Set logging verbosity (DEBUG, INFO, WARNING, ERROR)
- `--args` - Additional test arguments

**Example:**
```bash
uv run ingen test --log-level DEBUG --args="--test-name=MyTest"
```

### `ingen validate`
Validate system configuration and requirements.

**Purpose:**
Comprehensive validation of your Insight Ingenious setup including:
- Configuration file syntax
- Required dependencies
- Environment variables
- Service connectivity

**Example:**
```bash
uv run ingen validate
```

## Utility Commands

### `ingen prompt-tuner` (Removed)

> **Note**: The standalone prompt tuner has been removed. This command now shows an error message directing users to use `uv run ingen serve` instead. Use the main API server's prompt management endpoints (`/api/v1/prompts/*`).

### `ingen help [topic]`
Show detailed help and getting started guide.

**Topics:**
- `setup` - Initial project setup steps
- `workflows` - Understanding and configuring workflows
- `config` - Configuration file details
- `deployment` - Deployment options and best practices

**Example:**
```bash
uv run ingen help workflows    # Get workflow-specific help
```

### `ingen status`
Check system status and configuration.

**Example:**
```bash
uv run ingen status
```

### `ingen version`
Show version information.

**Example:**
```bash
uv run ingen version
```

### `ingen --help`
Show comprehensive help for all commands.

### `ingen <command> --help`
Get detailed help for specific commands.

**Examples:**
```bash
uv run ingen serve --help     # Get help for serve command
uv run ingen test --help      # Get help for test command
uv run ingen workflows --help # Get help for workflows command
```

## Data Processing Commands

### `ingen dataprep`
Web scraping utilities using Scrapfly.

**Subcommands:**
- `crawl <url>` - Scrape single page
- `batch <url1> <url2> ...` - Scrape multiple pages, outputs NDJSON

**Example:**
```bash
uv run ingen dataprep crawl https://example.com
uv run ingen dataprep batch https://example.com/page1 https://example.com/page2
```

> **Note**: Requires `scrapfly-sdk` optional dependency. Install with `uv add ingenious[dataprep]` or `uv add ingenious[full]`.

### `ingen document-processing extract <path>`
Extract text from documents (PDF, DOCX, images).

**Arguments:**
- `path` - File path, directory, or HTTP/S URL

**Options:**
- `--engine, -e` - Extractor backend (pymupdf, pdfminer, unstructured, azdocint) (default: pymupdf)
- `--out, -o` - Output file for NDJSON results (default: stdout)

**Example:**
```bash
uv run ingen document-processing extract document.pdf --engine pymupdf --out extracted.jsonl
uv run ingen document-processing extract https://example.com/doc.pdf --out results.jsonl
```

> **Note**: Requires document processing dependencies. Install with `uv add ingenious[document-processing]`.
> **For OCR needs**: Use the `azdocint` engine.

## Environment Setup

### Required Environment Variables

Ingenious uses environment variables with `INGENIOUS_` prefixes for all configuration:

```bash
# Core AI Model Configuration (required)
export INGENIOUS_MODELS__0__MODEL=gpt-4o-mini
export INGENIOUS_MODELS__0__API_KEY=your-api-key-here
export INGENIOUS_MODELS__0__BASE_URL=https://your-resource.openai.azure.com/...

# Optional: Web server settings
export INGENIOUS_WEB_CONFIGURATION__PORT=8000
export INGENIOUS_WEB_CONFIGURATION__AUTHENTICATION__ENABLE=false
```

### Optional Environment Variables
```bash
# For dataprep commands
export SCRAPFLY_API_KEY=your_key_here

# For database workflows
export INGENIOUS_LOCAL_SQL_DB__DATABASE_PATH=/tmp/sample_sql_db

# For Azure services (experimental)
export INGENIOUS_AZURE_SEARCH_SERVICES__0__KEY=your-search-key
export INGENIOUS_AZURE_SQL_SERVICES__CONNECTION_STRING="Driver=..."
```

## Configuration Methods

### `.env` File (Recommended)
Create a `.env` file in your project directory with your configuration:
```bash
# All INGENIOUS_ prefixed environment variables
# See Configuration Guide for complete examples
```

### Direct Environment Variables
Export variables directly in your shell or deployment environment.

### Migration from YAML
If you have legacy `config.yml` and `profiles.yml` files:
```bash
uv run python scripts/migrate_config.py --yaml-file config.yml --output .env
```

## Backward Compatibility

Legacy command names are still supported but hidden:
- `run_rest_api_server` → Use `serve`
- `run_test_batch` → Use `test`
- `initialize_new_project` → Use `init`
- `workflow_requirements` → Use `workflows`

## Error Handling

The CLI provides helpful error messages and suggestions:
- Missing configuration files
- Invalid workflow names
- Missing dependencies
- Environment variable issues

Use `uv run ingen workflows` to check workflow availability and requirements.

## Getting Help

- `ingen --help` - General help and list of all commands
- `ingen <command> --help` - Command-specific help and options
- `ingen workflows` - Show all available workflows and their requirements
- Documentation available in `docs/` directory
