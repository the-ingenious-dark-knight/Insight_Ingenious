---
title: "⚙️ Configuration Guide"
layout: single
permalink: /getting-started/configuration/
sidebar:
  nav: "docs"
toc: true
toc_label: "Configuration Options"
toc_icon: "cogs"
---

# Configuration Guide

This guide explains how to configure Insight Ingenious - an enterprise-grade Python library for AI agent APIs - for your specific deployment and Microsoft Azure service integrations. The library provides comprehensive configuration options for enterprise environments, debugging tools, and customization requirements.

## Configuration Overview

Insight Ingenious uses **pydantic-settings** for configuration via environment variables:

- **Environment Variables**: All configuration is done through environment variables with `INGENIOUS_` prefixes
- **`.env` Files**: Local configuration via `.env` files (recommended for development)
- **Environment Variable Hierarchies**: Support for nested configuration using double underscores (`__`)

## Migration from YAML Configuration

> **Important**: The legacy YAML configuration system (`config.yml`, `profiles.yml`) has been replaced with environment variables. If you have existing YAML files, use the migration script:

```bash
# Migrate existing YAML configuration to environment variables
uv run python scripts/migrate_config.py --yaml-file config.yml --output .env
uv run python scripts/migrate_config.py --yaml-file profiles.yml --output .env.profiles
```

## Setting Up Configuration

### Environment Variables

Configuration is now managed through environment variables with the `INGENIOUS_` prefix:

- Direct environment variables (e.g., `export INGENIOUS_MODELS__0__API_KEY=your-key`)
- `.env` files (recommended for local development)
- System environment variables (recommended for production)

### Configuration Loading Order

Ingenious loads configuration in this order (later sources override earlier ones):
1. Default values from pydantic models
2. Environment variables (system-wide)
3. `.env` file in current directory
4. `.env.local` file (for local overrides)

## Environment Variable Configuration

### Basic Configuration (.env file)

Create a `.env` file in your project directory with your configuration:

```bash
# Profile and Basic Settings
INGENIOUS_PROFILE=dev

# AI Model Configuration
INGENIOUS_MODELS__0__MODEL=gpt-4o-mini
INGENIOUS_MODELS__0__API_TYPE=rest
INGENIOUS_MODELS__0__API_VERSION=2024-08-01-preview
INGENIOUS_MODELS__0__API_KEY=your-api-key-here
INGENIOUS_MODELS__0__BASE_URL=https://your-resource.openai.azure.com/openai/deployments/gpt-4o-mini/chat/completions?api-version=2024-08-01-preview

# Chat History Storage
INGENIOUS_CHAT_HISTORY__DATABASE_TYPE=sqlite
INGENIOUS_CHAT_HISTORY__DATABASE_PATH=./tmp/high_level_logs.db
INGENIOUS_CHAT_HISTORY__MEMORY_PATH=./tmp

# Logging Configuration
INGENIOUS_LOGGING__ROOT_LOG_LEVEL=info
INGENIOUS_LOGGING__LOG_LEVEL=info

# Chat Service
INGENIOUS_CHAT_SERVICE__TYPE=multi_agent

# Web Server Configuration
INGENIOUS_WEB_CONFIGURATION__IP_ADDRESS=0.0.0.0
INGENIOUS_WEB_CONFIGURATION__PORT=8000
INGENIOUS_WEB_CONFIGURATION__AUTHENTICATION__ENABLE=false

# Tool and UI Services
INGENIOUS_TOOL_SERVICE__ENABLE=false
INGENIOUS_CHAINLIT_CONFIGURATION__ENABLE=false
INGENIOUS_PROMPT_TUNER__ENABLE=true

# File Storage (Local)
INGENIOUS_FILE_STORAGE__REVISIONS__ENABLE=true
INGENIOUS_FILE_STORAGE__REVISIONS__STORAGE_TYPE=local
INGENIOUS_FILE_STORAGE__REVISIONS__PATH=.files
INGENIOUS_FILE_STORAGE__DATA__ENABLE=true
INGENIOUS_FILE_STORAGE__DATA__STORAGE_TYPE=local
INGENIOUS_FILE_STORAGE__DATA__PATH=.files

# Local SQL Database (for sql-manipulation-agent)
INGENIOUS_LOCAL_SQL_DB__DATABASE_PATH=/tmp/sample_sql_db
INGENIOUS_LOCAL_SQL_DB__SAMPLE_CSV_PATH=
INGENIOUS_LOCAL_SQL_DB__SAMPLE_DATABASE_NAME=sample_sql_db
```

### Advanced Configuration with Azure Services

For production deployments with Azure services:

```bash
# Basic AI Model Configuration (same as above)
INGENIOUS_MODELS__0__MODEL=gpt-4o-mini
INGENIOUS_MODELS__0__API_KEY=your-api-key
INGENIOUS_MODELS__0__BASE_URL=https://your-resource.openai.azure.com/...

# Azure SQL Configuration (experimental)
INGENIOUS_AZURE_SQL_SERVICES__DATABASE_NAME=your-database
INGENIOUS_AZURE_SQL_SERVICES__CONNECTION_STRING="Driver={ODBC Driver 18 for SQL Server};Server=..."

# Azure Search Configuration (experimental)
INGENIOUS_AZURE_SEARCH_SERVICES__0__SERVICE=default
INGENIOUS_AZURE_SEARCH_SERVICES__0__ENDPOINT=https://your-search-service.search.windows.net
INGENIOUS_AZURE_SEARCH_SERVICES__0__KEY=your-search-api-key

# Azure Blob Storage
INGENIOUS_FILE_STORAGE__REVISIONS__STORAGE_TYPE=azure
INGENIOUS_FILE_STORAGE__REVISIONS__URL=https://your-storage.blob.core.windows.net/
INGENIOUS_FILE_STORAGE__REVISIONS__AUTHENTICATION_METHOD=default_credential

# Web Authentication
INGENIOUS_WEB_CONFIGURATION__AUTHENTICATION__ENABLE=true
INGENIOUS_WEB_CONFIGURATION__AUTHENTICATION__USERNAME=admin
INGENIOUS_WEB_CONFIGURATION__AUTHENTICATION__PASSWORD=your-secure-password
```

## Configuration Options Explained

### Chat History

Controls how conversation history is stored. Ingenious supports both SQLite (development) and Azure SQL (production) for chat history storage.

#### SQLite Setup (Development - Recommended)

For development environments, use SQLite (default):

```bash
# SQLite configuration (recommended for development)
INGENIOUS_CHAT_HISTORY__DATABASE_TYPE=sqlite
INGENIOUS_CHAT_HISTORY__DATABASE_PATH=./tmp/high_level_logs.db
INGENIOUS_CHAT_HISTORY__MEMORY_PATH=./tmp
```

No additional configuration required for SQLite.

#### Azure SQL Setup (Production)

For production environments, use Azure SQL Database:

**Step 1: Install Prerequisites**

On macOS:
```bash
# Install Microsoft ODBC Driver 18 for SQL Server
brew tap microsoft/mssql-release
brew install msodbcsql18 mssql-tools18

# Verify installation
odbcinst -q -d
```

On Ubuntu/Debian:
```bash
# Install Microsoft ODBC Driver 18 for SQL Server
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list > /etc/apt/sources.list.d/mssql-release.list
apt-get update
ACCEPT_EULA=Y apt-get install msodbcsql18
```

On Windows:
Download and install the ODBC Driver 18 for SQL Server from the Microsoft website.

**Step 2: Configure Environment Variables**

Add the Azure SQL configuration to your `.env` file:

```bash
# Azure SQL Configuration (experimental)
INGENIOUS_CHAT_HISTORY__DATABASE_TYPE=azuresql
INGENIOUS_CHAT_HISTORY__DATABASE_NAME=your_database_name
INGENIOUS_CHAT_HISTORY__DATABASE_CONNECTION_STRING="Driver={ODBC Driver 18 for SQL Server};Server=tcp:your-server.database.windows.net,1433;Database=your-database;Uid=your-username;Pwd=your-password;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"

# Azure SQL Services Configuration
INGENIOUS_AZURE_SQL_SERVICES__DATABASE_NAME=your_database_name
INGENIOUS_AZURE_SQL_SERVICES__CONNECTION_STRING="Driver={ODBC Driver 18 for SQL Server};Server=tcp:your-server.database.windows.net,1433;Database=your-database;Uid=your-username;Pwd=your-password;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
```

**Important Notes:**
- Use double quotes around the connection string to handle special characters
- Azure SQL integration is experimental and may contain bugs
- The connection string format is critical - ensure all parameters are correct
- Local SQLite implementation is recommended for stable operation

**Step 4: Validate Configuration**

```bash
uv run ingen validate
```

The Azure SQL database tables will be automatically created by Ingenious when first accessed. The following tables are created:
- `chat_history` - Main conversation messages
- `chat_history_summary` - Memory/summary storage
- `users` - User management
- `threads` - Thread/conversation management
- `steps`, `elements`, `feedbacks` - Chainlit UI integration

**Security Note**: Always use environment variables for sensitive connection strings. Never commit database credentials to version control.

### Models

Configures LLM models:

```yaml
models:
  - model: "gpt-4.1-nano"  # Model identifier
    api_type: "azure"  # API type (azure, openai)
    api_version: "2024-12-01-preview"  # API version
```

In `profiles.yml`:

```yaml
models:
  - model: "gpt-4.1-nano"
    api_key: "your-api-key"  # OpenAI or Azure OpenAI API key
    base_url: "https://your-endpoint.openai.azure.com/openai/deployments/gpt-4.1-nano/chat/completions?api-version=2024-12-01-preview"  # API endpoint
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
  port: 8000  # Default port (CLI overrides to 80 when using `ingen serve`)
  authentication:
    type: "basic"  # Authentication type
    enable: true  # Whether authentication is required
```

> **Note**: The default port in configuration is 8000, but the CLI command `ingen serve` defaults to port 80 unless specified otherwise. To use a different port, use `ingen serve --port 8000` or set the `WEB_PORT` environment variable.

In `profiles.yml`:

```yaml
web_configuration:
  authentication:
    enable: false  # Whether to enable authentication
    username: "admin"  # Basic auth username
    password: "your-secure-password"  # Basic auth password
```

### File Storage

Configures file storage with support for both local and Azure Blob Storage backends. This affects prompt template storage, memory management, and data persistence.

#### Local Storage Configuration

```yaml
file_storage:
  revisions:
    enable: true
    storage_type: "local"
    container_name: "revisions"  # Not used for local storage
    path: ".files"  # Local directory path
    add_sub_folders: true
  data:
    enable: true
    storage_type: "local"
    container_name: "data"  # Not used for local storage
    path: ".files"  # Local directory path
    add_sub_folders: true
```

#### Azure Blob Storage Configuration

```yaml
file_storage:
  revisions:
    enable: true
    storage_type: "azure"  # Use Azure Blob Storage
    container_name: "revisions"  # Azure container name
    path: "ingenious-files"  # Base path within container
    add_sub_folders: true
  data:
    enable: true
    storage_type: "azure"  # Use Azure Blob Storage
    container_name: "data"  # Azure container name
    path: "ingenious-files"  # Base path within container
    add_sub_folders: true
```

#### Azure Blob Storage profiles.yml Configuration

Configure authentication and connection details in `profiles.yml`:

```yaml
file_storage:
  revisions:
    url: "https://your-storage.blob.core.windows.net/"
    token: "${AZURE_STORAGE_CONNECTION_STRING:}"  # Connection string
    authentication_method: "token"  # Use connection string auth
  data:
    url: "https://your-storage.blob.core.windows.net/"
    token: "${AZURE_STORAGE_CONNECTION_STRING:}"  # Connection string
    authentication_method: "token"  # Use connection string auth
```

#### Authentication Methods

Azure Blob Storage supports multiple authentication methods:

1. **Connection String (Development)**:
   ```yaml
   authentication_method: "token"
   token: "DefaultEndpointsProtocol=https;AccountName=..."
   ```

2. **Managed Identity (Production)**:
   ```yaml
   authentication_method: "msi"
   client_id: "your-managed-identity-client-id"
   ```

3. **Service Principal**:
   ```yaml
   authentication_method: "client_id_and_secret"
   client_id: "your-app-registration-client-id"
   token: "your-client-secret"
   ```

4. **Default Azure Credential**:
   ```yaml
   authentication_method: "default_credential"
   ```

#### Environment Variables for Azure Blob Storage

Set these in your `.env` file:

```bash
AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=ingendev;AccountKey=YOUR_KEY;EndpointSuffix=core.windows.net"
AZURE_STORAGE_ACCOUNT_NAME="ingendev"
AZURE_STORAGE_ACCOUNT_KEY="YOUR_ACCOUNT_KEY"
AZURE_STORAGE_REVISIONS_URL="https://ingendev.blob.core.windows.net"
AZURE_STORAGE_DATA_URL="https://ingendev.blob.core.windows.net"
```

#### Features Enabled by File Storage

- **Prompt Template Management**: Store and version prompt templates
- **Memory Management**: Persist conversation context across sessions
- **Data Persistence**: Store functional test outputs and analysis results
- **API Integration**: `/api/v1/prompts` routes for prompt management
- **Multi-Environment Support**: Same codebase works with local or cloud storage

For detailed setup instructions, see the [Azure Blob Storage Setup Guide](../guides/azure-blob-storage-setup.md).

### Local SQL Database

Configures local SQL database for testing and development:

```yaml
local_sql_db:
  database_path: "/tmp/sample_sql_db"  # Path to SQLite database
  sample_csv_path: ""  # Path to sample CSV files for data loading
  sample_database_name: "sample_sql_db"
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

| Workflow | Description | External Services Required | Configuration Complexity | Availability |
|----------|-------------|----------------------------|--------------------------|--------------|
| `classification-agent` | Routes input to specialized agents | Azure OpenAI only | ✅ Minimal | Core library |
| `knowledge-base-agent` | Search knowledge bases | Azure OpenAI only (uses local ChromaDB) | ✅ Minimal | Core library (stable local implementation) |
| `sql-manipulation-agent` | Execute SQL queries | Azure OpenAI only (uses local SQLite) | ✅ Minimal | Core library (stable local implementation) |
| `bike-insights` | Sample domain-specific analysis | Azure OpenAI only | ✅ Minimal | Extension template* |

*Created when you run `ingen init` - part of project template, not core library.

> **Note**: Only local implementations (ChromaDB for knowledge-base-agent, SQLite for sql-manipulation-agent) are currently stable. Azure Search and Azure SQL integrations are experimental and may contain bugs.

### Workflow-Specific Configuration

#### 🚀 Quick Start: Minimal Configuration Workflows

For `classification-agent` and `bike-insights` (if created via `ingen init`), you only need basic Azure OpenAI setup:

```yaml
# config.yml
profile: dev
models:
  - model: ${AZURE_OPENAI_MODEL_NAME:gpt-4.1-nano}  # Environment variable substitution
    api_type: azure
    api_version: ${AZURE_OPENAI_API_VERSION:2024-12-01-preview}
    deployment: ${AZURE_OPENAI_DEPLOYMENT:gpt-4.1-nano}
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

For `knowledge-base-agent`, the local ChromaDB implementation is used by default and is stable:

**Local ChromaDB Implementation (Recommended - Stable)**
```yaml
# No additional configuration needed!
# The knowledge-base-agent uses local ChromaDB storage automatically
# Simply add documents to: ./.tmp/knowledge_base/
```

**Experimental Azure Search (May contain bugs)**
```yaml
# config.yml (additional)
azure_search_services:
  - service: "default"
    endpoint: "https://your-search-service.search.windows.net"

# profiles.yml (additional)
azure_search_services:
  - service: "default"
    key: "your-search-key"
```

> **Recommendation**: Use the local ChromaDB implementation, which requires no additional configuration and is stable.

#### 📊 Database Workflows (SQL Manipulation Agent)

For `sql-manipulation-agent` workflow, you have two database options:

**Local SQLite (Recommended - Stable)**
```yaml
# config.yml
local_sql_db:
  database_path: "/tmp/sample_sql_db"
  sample_csv_path: "./data/your_data.csv"

# profiles.yml
azure_sql_services:
  database_name: "skip"  # This enables SQLite mode
```

**Experimental Azure SQL (May contain bugs)**
```yaml
# config.yml
azure_sql_services:
  database_name: "your_database"
  server_name: "your-server.database.windows.net"
  driver: "ODBC Driver 18 for SQL Server"

# profiles.yml
azure_sql_services:
  connection_string: "Driver={ODBC Driver 18 for SQL Server};Server=tcp:yourserver.database.windows.net,1433;Database=your_database;Uid=your_username;Pwd=your_password;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
```

**Quick SQLite Setup:**
```bash
# Create sample database
uv run python -c "
from ingenious.utils.load_sample_data import sqlite_sample_db
sqlite_sample_db()
print('✅ Sample SQLite database created')
"

# Test SQL agent
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_prompt": "Show me all tables",
    "conversation_flow": "sql-manipulation-agent"
  }'
```

> **Recommendation**: Use the local SQLite implementation, which is simpler to set up and stable.

> 📖 **For complete SQL agent setup instructions**, see the [SQL Agent Setup Guide](../guides/sql-agent-setup.md)

### Testing Workflows

Use the CLI to check requirements and test workflows:

```bash
# Check what configuration is needed
uv run ingen workflows knowledge-base-agent

# Test a workflow
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"user_prompt": "Hello", "conversation_flow": "classification-agent"}'
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
