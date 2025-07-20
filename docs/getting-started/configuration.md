---
title: "Configuration Guide"
layout: single
permalink: /getting-started/configuration/
sidebar:
  nav: "docs"
toc: true
toc_label: "Configuration Options"
toc_icon: "cogs"
---

This guide explains how to configure Insight Ingenious - an enterprise-grade Python library for quickly setting up APIs to interact with AI Agents. The library provides comprehensive configuration options for enterprise environments, debugging tools, and customization requirements.

## Configuration Overview

Insight Ingenious uses **pydantic-settings** for configuration via environment variables:

- **Environment Variables**: All configuration is done through environment variables with `INGENIOUS_` prefixes
- **`.env` Files**: Local configuration via `.env` files (recommended for development)
- **Environment Variable Hierarchies**: Support for nested configuration using double underscores (`__`)

## Configuration Migration and Legacy Support

Ingenious has migrated from YAML-based configuration to environment variables:

- **Current System**: Environment variables with `INGENIOUS_` prefixes (via `.env` files)
- **Legacy System**: YAML configuration files (`config.yml`, `profiles.yml`) are no longer supported

### Migration from YAML Configuration

If you have existing YAML configuration files, use the migration script to convert them to environment variables:

```bash
# Migrate existing YAML configuration to environment variables
uv run python scripts/migrate_config.py --yaml-file config.yml --output .env
uv run python scripts/migrate_config.py --yaml-file profiles.yml --output .env.profiles
```

### Legacy YAML Configuration (No Longer Supported)

YAML configuration files are no longer supported. You must migrate to environment variables:
- `profiles.yml` - Previously contained sensitive data like API keys
- `config.yml` - Previously contained main configuration

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

# Tool Services
INGENIOUS_TOOL_SERVICE__ENABLE=false

# JWT Authentication (if authentication is enabled)
JWT_SECRET_KEY=your-secret-key-here
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

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

# Azure SQL Configuration
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
INGENIOUS_CHAT_HISTORY__CONNECTION_STRING="Driver={ODBC Driver 18 for SQL Server};Server=tcp:your-server.database.windows.net,1433;Database=your-database;Uid=your-username;Pwd=your-password;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"

# Azure SQL Services Configuration
INGENIOUS_AZURE_SQL_SERVICES__DATABASE_NAME=your_database_name
INGENIOUS_AZURE_SQL_SERVICES__CONNECTION_STRING="Driver={ODBC Driver 18 for SQL Server};Server=tcp:your-server.database.windows.net,1433;Database=your-database;Uid=your-username;Pwd=your-password;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
```

**Important Notes:**
- Use double quotes around the connection string to handle special characters
- The connection string format is critical - ensure all parameters are correct
- Both SQLite (local) and Azure SQL (cloud) implementations are production-ready

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

Configures LLM models using environment variables:

```bash
# Primary model configuration
INGENIOUS_MODELS__0__MODEL=gpt-4o-mini
INGENIOUS_MODELS__0__API_TYPE=rest
INGENIOUS_MODELS__0__API_VERSION=2024-08-01-preview
INGENIOUS_MODELS__0__API_KEY=your-api-key
INGENIOUS_MODELS__0__BASE_URL=https://your-resource.openai.azure.com/openai/deployments/gpt-4o-mini/chat/completions?api-version=2024-08-01-preview
INGENIOUS_MODELS__0__DEPLOYMENT=gpt-4o-mini

# Additional models (if needed)
INGENIOUS_MODELS__1__MODEL=gpt-4
INGENIOUS_MODELS__1__API_KEY=your-api-key-2
# ... etc
```

### Logging

Controls logging levels:

```bash
# Logging configuration
INGENIOUS_LOGGING__ROOT_LOG_LEVEL=info
INGENIOUS_LOGGING__LOG_LEVEL=info
```

Valid levels: `debug`, `info`, `warning`, `error`, `critical`

### Chat Service

Specifies the chat service implementation:

```bash
# Chat service configuration
INGENIOUS_CHAT_SERVICE__TYPE=multi_agent
```

### Chainlit Configuration (Removed)

> **Note**: Chainlit integration has been removed from this version. These configuration options are no longer used and will be ignored if set.

### Azure Search Services

Configures Azure Cognitive Search for knowledge bases:

```bash
# Azure Search configuration
INGENIOUS_AZURE_SEARCH_SERVICES__0__SERVICE=default
INGENIOUS_AZURE_SEARCH_SERVICES__0__ENDPOINT=https://your-search-service.search.windows.net
INGENIOUS_AZURE_SEARCH_SERVICES__0__KEY=your-search-api-key
```

### Web Configuration

Controls API authentication and server settings:

```bash
# Web server configuration
INGENIOUS_WEB_CONFIGURATION__TYPE=fastapi
INGENIOUS_WEB_CONFIGURATION__IP_ADDRESS=0.0.0.0
INGENIOUS_WEB_CONFIGURATION__PORT=8000
INGENIOUS_WEB_CONFIGURATION__ASYNCHRONOUS=false

# Authentication settings
INGENIOUS_WEB_CONFIGURATION__AUTHENTICATION__ENABLE=false
INGENIOUS_WEB_CONFIGURATION__AUTHENTICATION__TYPE=basic
INGENIOUS_WEB_CONFIGURATION__AUTHENTICATION__USERNAME=admin
INGENIOUS_WEB_CONFIGURATION__AUTHENTICATION__PASSWORD=your-secure-password
```

> **Note**: The default port in configuration is 80. The CLI command `uv run ingen serve` defaults to port 80, but can be overridden with `--port` flag. For local development, it's recommended to use port 8000 by running `uv run ingen serve --port 8000`.

### File Storage

Configures file storage with support for both local and Azure Blob Storage backends. This affects prompt template storage, memory management, and data persistence.

#### Local Storage Configuration

```bash
# Local file storage configuration
INGENIOUS_FILE_STORAGE__REVISIONS__ENABLE=true
INGENIOUS_FILE_STORAGE__REVISIONS__STORAGE_TYPE=local
INGENIOUS_FILE_STORAGE__REVISIONS__PATH=.files
INGENIOUS_FILE_STORAGE__REVISIONS__ADD_SUB_FOLDERS=true

INGENIOUS_FILE_STORAGE__DATA__ENABLE=true
INGENIOUS_FILE_STORAGE__DATA__STORAGE_TYPE=local
INGENIOUS_FILE_STORAGE__DATA__PATH=.files
INGENIOUS_FILE_STORAGE__DATA__ADD_SUB_FOLDERS=true
```

#### Azure Blob Storage Configuration

```bash
# Azure Blob Storage configuration
INGENIOUS_FILE_STORAGE__REVISIONS__ENABLE=true
INGENIOUS_FILE_STORAGE__REVISIONS__STORAGE_TYPE=azure
INGENIOUS_FILE_STORAGE__REVISIONS__CONTAINER_NAME=revisions
INGENIOUS_FILE_STORAGE__REVISIONS__PATH=ingenious-files
INGENIOUS_FILE_STORAGE__REVISIONS__ADD_SUB_FOLDERS=true
INGENIOUS_FILE_STORAGE__REVISIONS__URL=https://your-storage.blob.core.windows.net/
INGENIOUS_FILE_STORAGE__REVISIONS__AUTHENTICATION_METHOD=default_credential

INGENIOUS_FILE_STORAGE__DATA__ENABLE=true
INGENIOUS_FILE_STORAGE__DATA__STORAGE_TYPE=azure
INGENIOUS_FILE_STORAGE__DATA__CONTAINER_NAME=data
INGENIOUS_FILE_STORAGE__DATA__PATH=ingenious-files
INGENIOUS_FILE_STORAGE__DATA__ADD_SUB_FOLDERS=true
INGENIOUS_FILE_STORAGE__DATA__URL=https://your-storage.blob.core.windows.net/
INGENIOUS_FILE_STORAGE__DATA__AUTHENTICATION_METHOD=default_credential
```

#### Azure Blob Storage Authentication

Configure authentication using environment variables:

**Environment Variables:**
```bash
# Connection string authentication
INGENIOUS_FILE_STORAGE__REVISIONS__AUTHENTICATION_METHOD=token
AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=..."

# Or default credential authentication (recommended for production)
INGENIOUS_FILE_STORAGE__REVISIONS__AUTHENTICATION_METHOD=default_credential
```

#### Authentication Methods

Azure Blob Storage supports multiple authentication methods via environment variables:

1. **Default Azure Credential (Recommended for Production)**:
   ```bash
   INGENIOUS_FILE_STORAGE__REVISIONS__AUTHENTICATION_METHOD=default_credential
   ```

2. **Connection String (Development)**:
   ```bash
   INGENIOUS_FILE_STORAGE__REVISIONS__AUTHENTICATION_METHOD=token
   AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=..."
   ```

3. **Managed Identity**:
   ```bash
   INGENIOUS_FILE_STORAGE__REVISIONS__AUTHENTICATION_METHOD=msi
   INGENIOUS_FILE_STORAGE__REVISIONS__CLIENT_ID=your-managed-identity-client-id
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

For detailed setup instructions, see the File Storage configuration section above.

### Local SQL Database

Configures local SQL database for testing and development:

```bash
# Local SQLite database configuration
INGENIOUS_LOCAL_SQL_DB__DATABASE_PATH=/tmp/sample_sql_db
INGENIOUS_LOCAL_SQL_DB__SAMPLE_CSV_PATH=
INGENIOUS_LOCAL_SQL_DB__SAMPLE_DATABASE_NAME=sample_sql_db
```

### Azure SQL Services

Configures Azure SQL Database:

```bash
# Azure SQL configuration
INGENIOUS_AZURE_SQL_SERVICES__DATABASE_NAME=your_database
INGENIOUS_AZURE_SQL_SERVICES__TABLE_NAME=sample_table
INGENIOUS_AZURE_SQL_SERVICES__CONNECTION_STRING="Driver={ODBC Driver 18 for SQL Server};Server=tcp:your-server.database.windows.net,1433;Database=your-database;Uid=your-username;Pwd=your-password;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
```

### Prompt Tuner (Removed)

> **Note**: The standalone prompt tuner interface has been removed from this version. Use the main API server for prompt management via the `/api/v1/prompts/*` endpoints. The `ingen prompt-tuner` command will show an error directing users to use `ingen serve` instead.

### Receiver Configuration

Configures external API integration:

```bash
# External API integration
INGENIOUS_RECEIVER_CONFIGURATION__ENABLE=false
INGENIOUS_RECEIVER_CONFIGURATION__API_URL=https://your-api.azurewebsites.net/api/ai-response/publish
INGENIOUS_RECEIVER_CONFIGURATION__API_KEY=DevApiKey
```

## Multi-Agent Conversation Flows

Insight Ingenious supports several built-in conversation flows for different use cases:

### Available Conversation Flows

| Workflow | Description | External Services Required | Configuration Complexity | Availability |
|----------|-------------|----------------------------|--------------------------|--------------|
| `classification-agent` | Routes input to specialized agents | Azure OpenAI only |  Minimal | Core library |
| `knowledge-base-agent` | Search knowledge bases | Azure OpenAI only (uses local ChromaDB) |  Minimal | Core library (stable local implementation) |
| `sql-manipulation-agent` | Execute SQL queries | Azure OpenAI only (uses local SQLite) |  Minimal | Core library (stable local implementation) |
| `bike-insights` | Sample domain-specific analysis | Azure OpenAI only |  Minimal | Extension template* |

*Created when you run `uv run ingen init` - part of project template, not core library.

> **Note**: Both local implementations (ChromaDB, SQLite) and Azure implementations (Azure Search, Azure SQL) are production-ready. Choose based on your infrastructure requirements.

### Workflow-Specific Configuration

####  Quick Start: Minimal Configuration Workflows

For `classification-agent` and `bike-insights` (if created via `ingen init`), you only need basic Azure OpenAI setup:

```bash
# Basic configuration for minimal workflows
INGENIOUS_PROFILE=dev
INGENIOUS_MODELS__0__MODEL=gpt-4o-mini
INGENIOUS_MODELS__0__API_TYPE=rest
INGENIOUS_MODELS__0__API_VERSION=2024-08-01-preview
INGENIOUS_MODELS__0__DEPLOYMENT=gpt-4o-mini
INGENIOUS_MODELS__0__API_KEY=your-api-key
INGENIOUS_MODELS__0__BASE_URL=https://your-resource.openai.azure.com/openai/deployments/gpt-4o-mini/chat/completions?api-version=2024-08-01-preview
INGENIOUS_CHAT_SERVICE__TYPE=multi_agent
```

####  Knowledge Base Workflows

For `knowledge-base-agent`, the local ChromaDB implementation is used by default and is stable:

**Local ChromaDB Implementation (Recommended - Stable)**
```bash
# No additional configuration needed!
# The knowledge-base-agent uses local ChromaDB storage automatically
# Simply add documents to: ./.tmp/knowledge_base/
```

**Azure Search Implementation (Production-ready)**
```bash
# Additional Azure Search configuration
INGENIOUS_AZURE_SEARCH_SERVICES__0__SERVICE=default
INGENIOUS_AZURE_SEARCH_SERVICES__0__ENDPOINT=https://your-search-service.search.windows.net
INGENIOUS_AZURE_SEARCH_SERVICES__0__KEY=your-search-key
```

> **Note**: Both ChromaDB (local) and Azure Search (cloud) implementations are production-ready. ChromaDB requires no additional configuration.

####  Database Workflows (SQL Manipulation Agent)

For `sql-manipulation-agent` workflow, you have two database options:

**Local SQLite (Recommended - Stable)**
```bash
# Local SQLite configuration
INGENIOUS_LOCAL_SQL_DB__DATABASE_PATH=/tmp/sample_sql_db
INGENIOUS_LOCAL_SQL_DB__SAMPLE_CSV_PATH=./data/your_data.csv
INGENIOUS_LOCAL_SQL_DB__SAMPLE_DATABASE_NAME=sample_sql_db
```

**Azure SQL Implementation (Production-ready)**
```bash
# Azure SQL configuration
INGENIOUS_AZURE_SQL_SERVICES__DATABASE_NAME=your_database
INGENIOUS_AZURE_SQL_SERVICES__TABLE_NAME=your_table
INGENIOUS_AZURE_SQL_SERVICES__CONNECTION_STRING="Driver={ODBC Driver 18 for SQL Server};Server=tcp:yourserver.database.windows.net,1433;Database=your_database;Uid=your_username;Pwd=your_password;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
```

**Quick SQLite Setup:**
```bash
# Create sample database
uv run python -c "
from ingenious.utils.load_sample_data import sqlite_sample_db
sqlite_sample_db()
print(' Sample SQLite database created')
"

# Test SQL agent
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_prompt": "Show me all tables",
    "conversation_flow": "sql-manipulation-agent"
  }'
```

> **Note**: Both SQLite (local) and Azure SQL (cloud) implementations are production-ready. SQLite is simpler to set up for development.

>  **For complete SQL agent setup instructions**, see the [SQL Agent Setup Guide](../guides/sql-agent-setup.md)

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

```bash
# Enable multi-agent conversation flows
INGENIOUS_CHAT_SERVICE__TYPE=multi_agent
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

### Complete Environment Variable Reference

All Ingenious configuration uses environment variables with the `INGENIOUS_` prefix. Here's a comprehensive list:

#### Core Configuration

**Required for all deployments:**
```bash
# Model Configuration
INGENIOUS_MODELS__0__MODEL=gpt-4o-mini
INGENIOUS_MODELS__0__API_TYPE=rest  # or "azure" for Azure OpenAI
INGENIOUS_MODELS__0__API_VERSION=2024-12-01-preview
INGENIOUS_MODELS__0__DEPLOYMENT=gpt-4o-mini
INGENIOUS_MODELS__0__API_KEY=your-api-key
INGENIOUS_MODELS__0__BASE_URL=https://your-resource.openai.azure.com/

# Chat Service
INGENIOUS_CHAT_SERVICE__TYPE=multi_agent
```

#### Authentication Configuration

**For production deployments with authentication:**
```bash
# JWT Authentication
JWT_SECRET_KEY=your-secret-key-here  # Generate a secure random key
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Web Authentication
INGENIOUS_WEB_CONFIGURATION__AUTHENTICATION__ENABLE=true
INGENIOUS_WEB_CONFIGURATION__AUTHENTICATION__USERNAME=admin
INGENIOUS_WEB_CONFIGURATION__AUTHENTICATION__PASSWORD=secure-password
```

#### Document Processing Configuration

**For document extraction features:**
```bash
# Document Processing Limits
INGEN_MAX_DOWNLOAD_MB=20  # Maximum file size for downloads
INGEN_URL_TIMEOUT_SEC=30  # Timeout for URL fetching

# Scrapfly API (for web scraping)
SCRAPFLY_API_KEY=your-scrapfly-key  # Required for dataprep commands
```

#### Database Configuration

**For chat history storage:**
```bash
# SQLite (Default - Local Development)
INGENIOUS_CHAT_HISTORY__DATABASE_TYPE=sqlite
INGENIOUS_CHAT_HISTORY__DATABASE_PATH=./.tmp/chat_history.db
INGENIOUS_CHAT_HISTORY__MEMORY_PATH=./.tmp

# Azure SQL (Production)
INGENIOUS_CHAT_HISTORY__DATABASE_TYPE=azuresql
INGENIOUS_CHAT_HISTORY__DATABASE_NAME=your_database_name
INGENIOUS_CHAT_HISTORY__CONNECTION_STRING="Driver={ODBC Driver 18 for SQL Server};Server=tcp:your-server.database.windows.net,1433;Database=your-database;Uid=your-username;Pwd=your-password;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
```

#### File Storage Configuration

**For prompt and data storage:**
```bash
# Local Storage (Default)
INGENIOUS_FILE_STORAGE__REVISIONS__STORAGE_TYPE=local
INGENIOUS_FILE_STORAGE__DATA__STORAGE_TYPE=local

# Azure Blob Storage (Production)
INGENIOUS_FILE_STORAGE__REVISIONS__STORAGE_TYPE=azure
INGENIOUS_FILE_STORAGE__REVISIONS__URL=https://your-storage.blob.core.windows.net/
INGENIOUS_FILE_STORAGE__REVISIONS__AUTHENTICATION_METHOD=default_credential
INGENIOUS_FILE_STORAGE__DATA__STORAGE_TYPE=azure
INGENIOUS_FILE_STORAGE__DATA__URL=https://your-storage.blob.core.windows.net/
INGENIOUS_FILE_STORAGE__DATA__AUTHENTICATION_METHOD=default_credential

# Azure Storage Connection (if using connection string auth)
AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=youraccount;AccountKey=yourkey;EndpointSuffix=core.windows.net"
```

#### Workflow-Specific Configuration

**For SQL manipulation workflow:**
```bash
# Local SQL Database
INGENIOUS_LOCAL_SQL_DB__DATABASE_PATH=/tmp/sample_sql_db
INGENIOUS_LOCAL_SQL_DB__SAMPLE_CSV_PATH=./data/your_data.csv
INGENIOUS_LOCAL_SQL_DB__SAMPLE_DATABASE_NAME=sample_sql_db

# Azure SQL Services
INGENIOUS_AZURE_SQL_SERVICES__DATABASE_NAME=your-database-name
INGENIOUS_AZURE_SQL_SERVICES__TABLE_NAME=your-table-name
INGENIOUS_AZURE_SQL_SERVICES__CONNECTION_STRING="your-connection-string"
```

**For knowledge base workflow:**
```bash
# Azure Search (Optional - Experimental)
INGENIOUS_AZURE_SEARCH_SERVICES__0__SERVICE=default
INGENIOUS_AZURE_SEARCH_SERVICES__0__ENDPOINT=https://your-search-service.search.windows.net
INGENIOUS_AZURE_SEARCH_SERVICES__0__KEY=your-search-api-key
```

#### Web Server Configuration

```bash
# Server Settings
INGENIOUS_WEB_CONFIGURATION__PORT=8000  # Default is 80
WEB_PORT=8000  # Alternative port setting
```

#### Profile Configuration

```bash
# Profile Selection (optional)
INGENIOUS_PROFILE=dev  # or "prod", "staging"
```

### Environment Variable Best Practices

1. **Use `.env` files for local development** - Never commit these to version control
2. **Use proper quoting** - Complex values (connection strings) should be quoted
3. **Follow naming conventions** - Always use `INGENIOUS_` prefix for Ingenious-specific settings
4. **Secure sensitive values** - Use secret management tools in production

## Complete Environment Variables Reference

This section documents ALL environment variables used by Ingenious, including those not part of the main configuration models.

### Authentication & Security Variables

```bash
# JWT Authentication
JWT_SECRET_KEY=your-secret-key-here  # Required for JWT authentication
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15   # Access token expiry (default: 15)
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7      # Refresh token expiry (default: 7)

# Azure Key Vault (for secret management)
KEY_VAULT_NAME=your-key-vault-name   # Azure Key Vault name for retrieving secrets
```

### Document Processing Variables

```bash
# Document Processing Limits
INGEN_MAX_DOWNLOAD_MB=20            # Max file size for downloads (default: 20)
INGEN_URL_TIMEOUT_SEC=30            # Timeout for URL fetching (default: 30)

# Azure Document Intelligence
AZURE_DOC_INTEL_ENDPOINT=https://your-doc-intel.cognitiveservices.azure.com/
AZURE_DOC_INTEL_KEY=your-doc-intel-api-key
AZDOCINT_MAX_POLLS=300              # Max polling attempts (default: 300)
AZDOCINT_MAX_SECS=600               # Max processing time (default: 600)
```

### Data Preparation Variables

```bash
# Web Scraping (Scrapfly)
SCRAPFLY_API_KEY=your-scrapfly-api-key  # Required for web scraping features
```

### Azure OpenAI Variables

These are used by the Azure OpenAI SDK directly:

```bash
# Azure OpenAI SDK Variables
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_BASE_URL=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=your-deployment-name
AZURE_OPENAI_API_VERSION=2024-08-01-preview
AZURE_OPENAI_MODEL_NAME=gpt-4
```

### Profile and Path Variables

```bash
# Configuration File Paths
INGENIOUS_PROFILE_PATH=path/to/profiles  # Directory containing profile configs
APPSETTING_INGENIOUS_PROFILE=dev         # Active profile selection
INGENIOUS_PROJECT_PATH=/path/to/project  # Project root directory
INGENIOUS_WORKING_DIR=/path/to/workdir   # Working directory
LOADENV=true                            # Whether to load .env files
```

### Azure SQL Connection Variables

Note: The model uses `connection_string` field, not `database_connection_string`:

```bash
# Correct field name for Azure SQL
INGENIOUS_AZURE_SQL_SERVICES__CONNECTION_STRING="Driver={ODBC Driver 18 for SQL Server};..."
```

### Server Port Configuration

The server port can be configured in multiple ways (in order of precedence):

```bash
# Option 1: CLI flag (highest precedence)
uv run ingen serve --port 8000

# Option 2: Environment variable
WEB_PORT=8000

# Option 3: Ingenious configuration
INGENIOUS_WEB_CONFIGURATION__PORT=8000

# Default: 80
```

### Azure SDK Environment Variables

These variables are used by Azure SDK libraries, not directly by Ingenious:

```bash
# Azure Storage SDK
AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;..."
AZURE_STORAGE_ACCOUNT_NAME=yourstorageaccount
AZURE_STORAGE_ACCOUNT_KEY=yourstoragekey

# Azure Default Credential Chain
AZURE_CLIENT_ID=your-service-principal-id
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_SECRET=your-service-principal-secret
```

### Docker & Container Variables

```bash
# Container Environment
APPSETTING_WEBSITE_SITE_NAME=your-app-service-name  # Azure App Service name
```

### Legacy Variables (Deprecated)

These variables are no longer used but may appear in old configurations:

```bash
# YAML Configuration (No longer supported)
PROFILES_PATH=./profiles.yml  # Deprecated - use environment variables
CONFIG_PATH=./config.yml      # Deprecated - use environment variables
```

### Environment Variable Best Practices

1. **Use `.env` files for local development** - Never commit these to version control
2. **Use proper quoting** - Complex values (connection strings) should be quoted
3. **Follow naming conventions** - Always use `INGENIOUS_` prefix for Ingenious-specific settings
4. **Secure sensitive values** - Use secret management tools in production
5. **Document custom variables** - Add comments in your `.env.example` file
