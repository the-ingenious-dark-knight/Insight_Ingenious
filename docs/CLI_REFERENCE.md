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
- `config.yml` - Project configuration (non-sensitive)
- `profiles.yml` - Environment profiles (API keys, secrets)
- `.env.example` - Example environment variables
- `ingenious_extensions/` - Custom agents and workflows
- `Dockerfile and .dockerignore` - Docker deployment templates
- `tmp/` - Temporary files and memory

**Next Steps:**
1. Copy `.env.example` to `.env` and add credentials
2. Set environment variables
3. Run `ingen serve`

### `ingen serve`
Start the API server with web interfaces.

**Options:**
- `--config, -c` - Path to config.yml (default: ./config.yml)
- `--profile, -p` - Path to profiles.yml (default: ./profiles.yml)
- `--host, -h` - Host to bind (default: 0.0.0.0)
- `--port` - Port to bind (default: 80)
- `--no-prompt-tuner` - Disable prompt tuner interface

**Interfaces:**
- API: `http://localhost:80/api/v1/`
- Health Check: `http://localhost:80/api/v1/health`
- Chat: `http://localhost:80/chainlit`
- Prompt Tuner: `http://localhost:80/prompt-tuner`

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

### `ingen document-processing <path>`
Extract text from documents (PDF, DOCX, images).

**Arguments:**
- `path` - File path, directory, or HTTP/S URL

**Options:**
- `--engine, -e` - Extractor backend (pymupdf, pdfminer, unstructured) (default: pymupdf)
- `--out, -o` - Output file for NDJSON results (default: stdout)

**Example:**
```bash
ingen document-processing document.pdf --engine pymupdf --out extracted.jsonl
ingen document-processing https://example.com/doc.pdf --out results.jsonl
```

## Environment Setup

### Required Environment Variables
```bash
export INGENIOUS_PROJECT_PATH=$(pwd)/config.yml
export INGENIOUS_PROFILE_PATH=$(pwd)/profiles.yml
```

### Optional Environment Variables
```bash
export SCRAPFLY_API_KEY=your_key_here  # For dataprep commands
```

## Configuration Files

### `config.yml`
Non-sensitive project configuration:
- Model settings
- Service configurations
- Logging settings
- Workflow definitions

### `profiles.yml`
Sensitive environment-specific settings:
- API keys
- Connection strings
- Secrets

### `.env`
Environment variables for local development.

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
