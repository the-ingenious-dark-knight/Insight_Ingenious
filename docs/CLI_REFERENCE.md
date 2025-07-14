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

# Check your configuration
ingen status

# Validate setup (recommended)
ingen validate

# Start the server
ingen serve

# List available workflows
ingen workflows
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

**Core Library Workflows (Always Available):**
- `classification-agent` - Route input to specialized agents (minimal config - Azure OpenAI only)
- `knowledge-base-agent` - Search knowledge bases (supports both local ChromaDB and Azure Search)
- `sql-manipulation-agent` - Execute SQL queries (supports both local SQLite and Azure SQL)

**Project Template Workflows (Created with `ingen init`):**
- `bike-insights` - Sample domain-specific multi-agent analysis ⭐ **RECOMMENDED START HERE**

**Implementation Notes:**
- **Local implementations are stable**: ChromaDB (knowledge-base-agent), SQLite (sql-manipulation-agent)
- **Azure integrations are experimental**: Azure Search, Azure SQL may contain bugs
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

### `ingen status`
Check system configuration and status.

Validates:
- Environment variables
- Configuration files
- Dependencies
- Available workflows

### `ingen validate`
Comprehensive validation of your Insight Ingenious setup.

**What it validates:**
- Configuration file syntax and required fields
- Profile file syntax and credentials
- Azure OpenAI connectivity
- Workflow requirements
- Dependencies

**Usage:**
```bash
ingen validate  # Recommended before starting server
```

This command helps identify issues before starting the server and provides specific fix recommendations.

### `ingen version`
Show version information.

### `ingen prompt-tuner`
Start standalone prompt tuning interface.

**Options:**
- `--port, -p` - Port (default: 5000)
- `--host, -h` - Host (default: 127.0.0.1)

### `ingen help [topic]`
Show detailed help and guides.

**Topics:**
- `setup` - Initial project setup
- `workflows` - Understanding workflows
- `config` - Configuration details
- `deployment` - Deployment options

## Data Processing Commands

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

### `ingen dataprep`
Web scraping utilities using Scrapfly.

**Subcommands:**
- `crawl <url>` - Scrape single page
- `batch <urls...>` - Scrape multiple pages

**Common Options:**
- `--api-key` - Override Scrapfly API key (or use SCRAPFLY_API_KEY env var)
- `--max-attempts` - Total tries per URL (default: 5)
- `--delay` - Initial back-off delay in seconds (default: 1)
- `--js / --no-js` - Enable/disable JavaScript rendering

**Example:**
```bash
ingen dataprep crawl https://example.com --pretty
ingen dataprep batch https://a.com https://b.com --max-attempts 3
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

Use `ingen status` to diagnose configuration problems.

## Getting Help

- `ingen --help` - General help
- `ingen <command> --help` - Command-specific help
- `ingen help` - Comprehensive getting started guide
- `ingen help <topic>` - Topic-specific guidance
