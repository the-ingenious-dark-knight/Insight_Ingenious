---
title: "⚙️ Configuration Guide"
layout: single
permalink: /configuration/
sidebar:
  nav: "docs"
toc: true
toc_label: "Configuration Options"
toc_icon: "cogs"
---

# Configuration Guide

This guide explains how to configure Insight Ingenious for your project.

## Configuration Overview

Insight Ingenious uses a two-file configuration approach:

1. `config.yml`: Project-specific, non-sensitive configuration
2. `profiles.yml`: Environment-specific, sensitive configuration (API keys, credentials)

## Setting Up Configuration Files

### Initial Setup

When you run `ingen init`, template configuration files are generated:

- `config.yml` in your project directory
- `profiles.yml` in `~/.ingenious/` directory

### Environment Variables

Set these environment variables to specify configuration locations:

- `INGENIOUS_PROJECT_PATH`: Path to your project's `config.yml`
- `INGENIOUS_PROFILE_PATH`: Path to your `profiles.yml`

Alternatively, for Azure deployments:
- `APPSETTING_INGENIOUS_CONFIG`: JSON configuration string
- `APPSETTING_INGENIOUS_PROFILE`: JSON profile string

## Configuration File Structure

### config.yml

```yaml
chat_history:
  database_type: "sqlite"  # or "azuresql"
  database_path: "./.tmp/high_level_logs.db"  # Path to SQLite database file
  database_name: "chat_history"  # Name of the database (used for Azure SQL)
  memory_path: "./.tmp"  # Location for temporary memory/cache files (used by ChromaDB)

profile: "dev"  # Name of the profile to use from profiles.yml

models:
  - model: "gpt-4.1-nano"
    api_type: "azure"
    api_version: "2024-08-01-preview"

logging:
  root_log_level: "debug"
  log_level: "debug"

tool_service:
  enable: false

chat_service:
  type: "multi_agent"  # The type of chat service to use

chainlit_configuration:
  enable: false

azure_search_services:
  - service: "default"
    endpoint: "https://your-search-service.search.windows.net"

azure_sql_services:
  database_name: "dbo"
  table_name: "sample_table"

web_configuration:
  type: "fastapi"
  ip_address: "0.0.0.0"
  port: 80
  authentication:
    type: "basic"
    enable: true

local_sql_db:
  database_path: "/tmp/sample_sql.db"
  sample_csv_path: "./ingenious/sample_dataset/cleaned_students_performance.csv"
  sample_database_name: "sample_data"

prompt_tuner:
  mode: "fast_api"  # Mount in fast_api or standalone flask

file_storage:
  revisions:
    enable: true
    storage_type: "local"
    container_name: "jrsrevisions"
    path: ".files"
    add_sub_folders: true
  data:
    enable: true
    storage_type: "local"
    container_name: "jrsdata"
    path: ".files"
    add_sub_folders: true
```

### profiles.yml

```yaml
- name: "dev"
  models:
    - model: "gpt-4.1-nano"
      api_key: "your-api-key"
      base_url: "https://your-endpoint.openai.azure.com/openai/deployments/gpt-4.1-nano/chat/completions?api-version=2024-08-01-preview"

  chat_history:
    database_connection_string: "AccountEndpoint=..."

  azure_search_services:
    - service: "default"
      key: "your-search-key"

  azure_sql_services:
    database_connection_string: ""

  receiver_configuration:
    enable: false
    api_url: "https://your-api.azurewebsites.net/api/ai-response/publish"
    api_key: "DevApiKey"

  chainlit_configuration:
    enable: false
    authentication:
      enable: false
      github_client_id: ""
      github_secret: ""

  web_configuration:
    authentication:
      enable: false
      username: "admin"
      password: "your-secure-password"

  file_storage:
    revisions:
      url: "https://your-storage.blob.core.windows.net/"
      authentication_method: "default_credential"  # or "msi"
    data:
      url: "https://your-storage.blob.core.windows.net/"
      authentication_method: "default_credential"  # or "msi"
```

## Configuration Options Explained

### Chat History

Controls how conversation history is stored:

```yaml
chat_history:
  database_type: "sqlite"  # Options: "sqlite", "azuresql"
  database_path: "./.tmp/high_level_logs.db"  # SQLite database file path
  database_name: "chat_history"  # Database name (used for Azure SQL)
  memory_path: "./.tmp"  # Path for context memory files (used by ChromaDB)
```

### Models

Configures LLM models:

```yaml
models:
  - model: "gpt-4.1-nano"  # Model identifier
    api_type: "azure"  # API type (azure, openai)
    api_version: "2024-08-01-preview"  # API version
```

In `profiles.yml`:

```yaml
models:
  - model: "gpt-4.1-nano"
    api_key: "your-api-key"  # OpenAI or Azure OpenAI API key
    base_url: "https://your-endpoint.openai.azure.com/openai/deployments/gpt-4.1-nano/chat/completions?api-version=2024-08-01-preview"  # API endpoint
```

### Logging

Controls logging levels:

```yaml
logging:
  root_log_level: "debug"  # Global logging level (debug, info, warning, error)
  log_level: "debug"  # Application-specific logging level
```

### Chat Service

Specifies the chat service implementation:

```yaml
chat_service:
  type: "multi_agent"  # The conversation service to use
```

### Chainlit Configuration

Controls the web UI:

```yaml
chainlit_configuration:
  enable: true  # Whether to enable the Chainlit UI
```

In `profiles.yml`:

```yaml
chainlit_configuration:
  authentication:
    enable: false  # Whether to require authentication
    github_client_id: ""  # For GitHub OAuth
    github_secret: ""  # For GitHub OAuth
```

### Azure Search Services

Configures Azure Cognitive Search for knowledge bases:

```yaml
azure_search_services:
  - service: "default"  # Service identifier
    endpoint: "https://your-search-service.search.windows.net"
```

In `profiles.yml`:

```yaml
azure_search_services:
  - service: "default"
    key: "your-search-key"  # Azure Search API key
```

### Web Configuration

Controls API authentication and server settings:

```yaml
web_configuration:
  type: "fastapi"  # Web framework type
  ip_address: "0.0.0.0"  # IP address to bind to
  port: 80  # Port number
  authentication:
    type: "basic"  # Authentication type
    enable: true  # Whether authentication is required
```

In `profiles.yml`:

```yaml
web_configuration:
  authentication:
    enable: false  # Whether to enable authentication
    username: "admin"  # Basic auth username
    password: "your-secure-password"  # Basic auth password
```

### File Storage

Configures file storage with support for revisions and data storage:

```yaml
file_storage:
  revisions:
    enable: true
    storage_type: "local"  # Options: "local", "azure"
    container_name: "jrsrevisions"  # Azure container name
    path: ".files"  # Local storage path
    add_sub_folders: true  # Whether to create sub-folders
  data:
    enable: true
    storage_type: "local"  # Options: "local", "azure"
    container_name: "jrsdata"  # Azure container name
    path: ".files"  # Local storage path
    add_sub_folders: true  # Whether to create sub-folders
```

For Azure Blob Storage in `profiles.yml`:

```yaml
file_storage:
  revisions:
    url: "https://your-storage.blob.core.windows.net/"
    authentication_method: "default_credential"  # or "msi"
  data:
    url: "https://your-storage.blob.core.windows.net/"
    authentication_method: "default_credential"  # or "msi"
```

### Local SQL Database

Configures local SQL database for testing and development:

```yaml
local_sql_db:
  database_path: "/tmp/sample_sql.db"  # Path to SQLite database
  sample_csv_path: "./ingenious/sample_dataset/cleaned_students_performance.csv"
  sample_database_name: "sample_data"
```

### Azure SQL Services

Configures Azure SQL Database:

```yaml
azure_sql_services:
  database_name: "dbo"  # Database name
  table_name: "sample_table"  # Table name
```

In `profiles.yml`:

```yaml
azure_sql_services:
  database_connection_string: "Server=..."  # Azure SQL connection string
```

### Prompt Tuner

Configures the prompt tuning interface:

```yaml
prompt_tuner:
  mode: "fast_api"  # Options: "fast_api", "flask"
```

### Receiver Configuration

Configures external API integration in `profiles.yml`:

```yaml
receiver_configuration:
  enable: false
  api_url: "https://your-api.azurewebsites.net/api/ai-response/publish"
  api_key: "DevApiKey"
```

## Multi-Agent Conversation Flows

Insight Ingenious supports several built-in conversation flows for different use cases:

### Available Conversation Flows

| Workflow | Description | External Services Required | Configuration Complexity |
|----------|-------------|----------------------------|--------------------------|
| `classification_agent` | Routes input to specialized agents | Azure OpenAI only | ✅ Minimal |
| `bike_insights` | Sample domain-specific analysis | Azure OpenAI only | ✅ Minimal |
| `knowledge_base_agent` | Search knowledge bases | Azure OpenAI + Azure Search | 🔍 Moderate |
| `sql_manipulation_agent` | Execute SQL queries | Azure OpenAI + Database | 📊 Moderate |

### Workflow-Specific Configuration

#### 🚀 Quick Start: Minimal Configuration Workflows

For `classification_agent` and `bike_insights`, you only need basic Azure OpenAI setup:

```yaml
# config.yml
profile: dev
models:
  - model: "gpt-4.1-nano"
    api_type: azure
    api_version: "2024-08-01-preview"
chat_service:
  type: multi_agent
```

```yaml
# profiles.yml
- name: "dev"
  models:
    - model: "gpt-4.1-nano"
      api_key: "your-api-key"
      base_url: "https://your-endpoint.openai.azure.com/..."
```

#### 🔍 Knowledge Base Workflows

For `knowledge_base_agent`, add Azure Search configuration:

```yaml
# config.yml (additional)
azure_search_services:
  - service: "default"
    endpoint: "https://your-search-service.search.windows.net"
```

```yaml
# profiles.yml (additional)
azure_search_services:
  - service: "default"
    key: "your-search-key"
```

#### 📊 Database Workflows

For `sql_manipulation_agent`:

**Local SQLite option:**
```yaml
# config.yml
local_sql_db:
  database_path: "/tmp/sample_sql.db"
  sample_csv_path: "./data/your_data.csv"
azure_sql_services:
  database_name: "skip"  # Use "skip" for local mode
```

**Azure SQL option:**
```yaml
# config.yml
azure_sql_services:
  database_name: "your_database"
  table_name: "your_table"
```

```yaml
# profiles.yml
azure_sql_services:
  database_connection_string: "Server=tcp:yourserver.database.windows.net,..."
```

### Testing Workflows

Use the CLI to check requirements and test workflows:

```bash
# Check what configuration is needed
uv run ingen workflow-requirements knowledge_base_agent

# Test a workflow
curl -X POST http://localhost:8081/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"user_prompt": "Hello", "conversation_flow": "classification_agent"}'
```

### Configuring Conversation Flows

The conversation flow is specified in the chat service configuration:

```yaml
chat_service:
  type: "multi_agent"  # Enables multi-agent conversation flows
```

Each conversation flow has its own directory structure under:
- `ingenious/services/chat_services/multi_agent/conversation_flows/`
- `ingenious/services/chat_services/multi_agent/conversation_patterns/`

### Custom Conversation Flows

You can create custom conversation flows by:

1. Creating a new directory under `conversation_flows/`
2. Implementing the `ConversationFlow` class with a `get_conversation_response()` method
3. Creating corresponding conversation patterns that define agent interactions
4. Registering the flow in your configuration

## Environment Variables
