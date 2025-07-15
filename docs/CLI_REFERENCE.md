---
title: "📝 CLI Reference"
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
ingen init

# Validate configuration
ingen validate

# Start the server
ingen serve

# List available workflows
ingen workflows

# Run tests
ingen test
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
- `--port` - Port to bind (default: 80)
- `--no-prompt-tuner` - Disable prompt tuner interface

**Interfaces:**
- API: `http://localhost:80/api/v1/`
- Health Check: `http://localhost:80/api/v1/health`
- Chat: `http://localhost:80/chainlit`
- Prompt Tuner: `http://localhost:80/prompt-tuner`

> **Configuration**: The server uses environment variables for configuration. Ensure your `.env` file is properly configured before starting the server.

### `ingen workflows [workflow-name]`
Show available workflows and their requirements.

**Examples:**
```bash
ingen workflows                          # List all workflows
ingen workflows classification-agent     # Show specific workflow details
ingen workflows bike-insights            # Show bike insights workflow (recommended start)
```

**Available Workflows:**
- `classification-agent` - Route input to specialized agents (core library, minimal config)
- `bike-insights` - Sample domain-specific analysis (project template, minimal config) ⭐ **RECOMMENDED**
- `knowledge-base-agent` - Search knowledge bases using local ChromaDB (core library, stable local implementation)
- `sql-manipulation-agent` - Execute SQL queries using local SQLite (core library, stable local implementation)

**Note:**
- Core library workflows are always available
- Template workflows like `bike-insights` are created with `ingen init`
- Only local implementations (ChromaDB, SQLite) are stable; Azure integrations are experimental
- Legacy underscore names (`classification_agent`, `bike_insights`, etc.) are still supported for backward compatibility

### `ingen test`
Run agent workflow tests.

**Options:**
- `--log-level, -l` - Set logging verbosity (DEBUG, INFO, WARNING, ERROR)
- `--args` - Additional test arguments

**Example:**
```bash
ingen test --log-level DEBUG --args="--test-name=MyTest"
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
ingen validate
```

## Utility Commands

### `ingen prompt-tuner`
Start standalone prompt tuning interface.

**Options:**
- `--port, -p` - Port (default: 5000)
- `--host, -h` - Host (default: 127.0.0.1)

**Example:**
```bash
ingen prompt-tuner --port 5000 --host 127.0.0.1
```

### `ingen --help`
Show comprehensive help for all commands.

### `ingen <command> --help`
Get detailed help for specific commands.

**Examples:**
```bash
ingen serve --help     # Get help for serve command
ingen test --help      # Get help for test command
ingen workflows --help # Get help for workflows command
```

## Data Processing Commands

### `ingen dataprep`
Web scraping utilities using Scrapfly.

**Subcommands:**
- `crawl <url>` - Scrape single page
- `batch <urls...>` - Scrape multiple pages

**Example:**
```bash
ingen dataprep crawl https://example.com --pretty
ingen dataprep batch https://a.com https://b.com --out results.ndjson
```

### `ingen document-processing extract <path>`
Extract text from documents (PDF, DOCX, images).

**Arguments:**
- `path` - File path, directory, or HTTP/S URL

**Options:**
- `--engine, -e` - Extractor backend (pymupdf, pdfminer, unstructured) (default: pymupdf)
- `--out, -o` - Output file for NDJSON results (default: stdout)

**Example:**
```bash
ingen document-processing extract document.pdf --engine pymupdf --out extracted.jsonl
ingen document-processing extract https://example.com/doc.pdf --out results.jsonl
```

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

Use `ingen workflows` to check workflow availability and requirements.

## Getting Help

- `ingen --help` - General help and list of all commands
- `ingen <command> --help` - Command-specific help and options
- `ingen workflows` - Show all available workflows and their requirements
- Documentation available in `docs/` directory
