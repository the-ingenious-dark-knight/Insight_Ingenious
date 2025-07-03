# Workflow Configuration Requirements

This guide outlines the configuration requirements for each conversation workflow in Insight Ingenious. Understanding these requirements will help you determine what external services and configurations are needed for each workflow.

## Overview

Insight Ingenious supports multiple conversation workflows, each with different external service dependencies. Some workflows work with minimal configuration, while others require specific Azure services, database connections, or API keys.

## Workflow Categories

### ✅ Works with Minimal Configuration
These workflows only require basic Azure OpenAI configuration:

- **classification_agent**: Routes input to specialized agents based on content
- **bike_insights**: Sample domain-specific workflow for bike sales analysis

### 🔍 Requires Azure Search Services
These workflows need Azure Cognitive Search configuration:

- **knowledge_base_agent**: Search and retrieve information from knowledge bases

### 📊 Requires Database Configuration
These workflows need database connections:

- **sql_manipulation_agent**: Execute SQL queries on Azure SQL or local databases
- **pandas_agent**: Data analysis using local CSV/database files

### 🌐 Requires Web Search Services
These workflows need web search capabilities:

- **web_critic_agent**: Perform web search and fact-checking

### 📄 Requires Document Processing Services
These workflows need Azure Document Intelligence (optional):

- **document-processing**: Extract text from PDFs, DOCX, images using OCR

## Detailed Configuration Requirements

### All Workflows (Required)

All workflows require basic Azure OpenAI configuration:

#### config.yml
```yaml
profile: dev
models:
  - model: "gpt-4.1-nano"  # Your model deployment name
    api_type: azure
    api_version: "2024-08-01-preview"

chat_service:
  type: multi_agent

chat_history:
  database_type: sqlite
  database_path: "./.tmp/high_level_logs.db"
  memory_path: "./.tmp"
```

#### profiles.yml
```yaml
- name: "dev"
  models:
    - model: "gpt-4.1-nano"  # Must match config.yml
      api_key: "your-azure-openai-api-key"
      base_url: "https://your-endpoint.openai.azure.com/openai/deployments/gpt-4.1-nano/chat/completions?api-version=2024-08-01-preview"
      deployment: "gpt-4.1-nano"  # Your deployment name
```

---

### knowledge_base_agent (Azure Search Required)

**Purpose**: Search and retrieve information from Azure Cognitive Search indexes

**Additional Configuration Required**:

#### config.yml
```yaml
azure_search_services:
  - service: "default"
    endpoint: "https://your-search-service.search.windows.net"
```

#### profiles.yml
```yaml
azure_search_services:
  - service: "default"
    key: "your-azure-search-api-key"
```

**What you need to provide**:
- Azure Cognitive Search service endpoint
- Azure Cognitive Search API key
- Pre-configured search indexes (referenced in the workflow as 'index-document-set-1', 'index-document-set-2')

**Without this configuration**: The workflow will fail when trying to search knowledge bases.

---

### sql_manipulation_agent (Database Required)

**Purpose**: Execute SQL queries based on natural language input

**Configuration Options**:

#### Option 1: Local SQLite Database
```yaml
# config.yml
local_sql_db:
  database_path: "/tmp/sample_sql.db"
  sample_csv_path: "./ingenious/sample_dataset/cleaned_students_performance.csv"
  sample_database_name: "sample_data"

azure_sql_services:
  database_name: "skip"  # Use "skip" to enable local mode
```

#### Option 2: Azure SQL Database
```yaml
# config.yml
azure_sql_services:
  database_name: "your_database"
  table_name: "your_table"
```

```yaml
# profiles.yml
azure_sql_services:
  database_connection_string: "Server=tcp:yourserver.database.windows.net,1433;Database=yourdatabase;User ID=yourusername;Password=yourpassword;Encrypt=true;TrustServerCertificate=false;Connection Timeout=30;"
```

**What you need to provide**:
- For local: CSV file or SQLite database
- For Azure: Azure SQL connection string with proper credentials

**Without this configuration**: The workflow will fail when trying to execute SQL queries.

---

### pandas_agent (Local Data Required)

**Purpose**: Data analysis and visualization using pandas

**Configuration Required**:
```yaml
# config.yml
local_sql_db:
  database_path: "/tmp/sample_sql.db"
  sample_csv_path: "./ingenious/sample_dataset/cleaned_students_performance.csv"
  sample_database_name: "sample_data"
```

**What you need to provide**:
- CSV data file for analysis
- Local SQLite database path

**Without this configuration**: The workflow will fall back to mock data or fail during data operations.

---

### web_critic_agent (Web Search Required)

**Purpose**: Perform web search and fact-checking

**Configuration Required**:
```yaml
# This workflow currently uses mock search results for testing
# Production deployment would require web search API configuration
```

**What you need to provide**:
- Currently uses mock data - no external configuration required for testing
- Production use would require web search API (Bing, Google, etc.)

**Without this configuration**: Works with mock data for testing purposes.

---

### classification_agent (Minimal Configuration)

**Purpose**: Classify user input and route to appropriate topic agents

**Configuration Required**: Only basic Azure OpenAI configuration (see "All Workflows" section above)

**What you need to provide**: Just Azure OpenAI credentials

**Without this configuration**: Will not work - requires Azure OpenAI for classification logic.

---

### bike_insights (Minimal Configuration)

**Purpose**: Sample domain-specific workflow for bike sales analysis

**Configuration Required**: Only basic Azure OpenAI configuration (see "All Workflows" section above)

**What you need to provide**: Just Azure OpenAI credentials

**Without this configuration**: Will not work - requires Azure OpenAI for analysis.

---

### document-processing (Optional Azure Services)

**Purpose**: Extract text from PDFs, DOCX, images using various engines

**Configuration Options**:

#### Basic (No external services)
Works with local engines: pymupdf, pdfminer, unstructured

#### Advanced OCR (Azure Document Intelligence)
For better OCR and semantic extraction:

**Environment Variables Required**:
```bash
export AZURE_DOC_INTEL_ENDPOINT="https://your-resource.cognitiveservices.azure.com"
export AZURE_DOC_INTEL_KEY="your-api-key"
```

**What you need to provide**:
- Azure Document Intelligence service endpoint
- Azure Document Intelligence API key

**Without this configuration**: Falls back to local extraction engines (limited OCR capabilities).

## Quick Start Guide

### 1. Minimal Setup (classification_agent, bike_insights)
1. Configure Azure OpenAI in `config.yml` and `profiles.yml`
2. Run: `uv run ingen run-rest-api-server`
3. Test with classification_agent or bike_insights workflows

### 2. Knowledge Base Setup (knowledge_base_agent)
1. Complete minimal setup above
2. Set up Azure Cognitive Search service
3. Create and populate search indexes
4. Add Azure Search configuration to config files
5. Test with knowledge_base_agent workflow

### 3. Database Setup (sql_manipulation_agent, pandas_agent)
1. Complete minimal setup above
2. Choose local SQLite or Azure SQL
3. Configure database connection
4. Prepare data (CSV for local, tables for Azure SQL)
5. Test with sql_manipulation_agent or pandas_agent workflows

### 4. Full Setup (All workflows)
1. Complete all setup steps above
2. Optionally configure Azure Document Intelligence
3. Test all workflows

## Testing Configuration

Use these commands to test specific workflows:

```bash
# Test basic configuration
curl -X POST http://localhost:8081/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"user_prompt": "Hello", "conversation_flow": "classification_agent"}'

# Test knowledge base (requires Azure Search)
curl -X POST http://localhost:8081/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"user_prompt": "Search for health information", "conversation_flow": "knowledge_base_agent"}'

# Test SQL queries (requires database)
curl -X POST http://localhost:8081/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"user_prompt": "Show me student performance data", "conversation_flow": "sql_manipulation_agent"}'
```

## Troubleshooting

### Common Issues

1. **"Azure OpenAI API key not found"**
   - Check profiles.yml has correct API key
   - Verify INGENIOUS_PROFILE_PATH environment variable

2. **"Search service not configured"**
   - Add Azure Search configuration to config.yml and profiles.yml
   - Verify search service endpoint and API key

3. **"Database connection failed"**
   - Check connection string in profiles.yml
   - Verify database exists and is accessible
   - For local SQLite, check file path and permissions

4. **"Document processing failed"**
   - For Azure: Check AZURE_DOC_INTEL_ENDPOINT and AZURE_DOC_INTEL_KEY
   - For local: Install required optional dependencies

### Getting Help

1. Check logs for specific error messages
2. Verify configuration files against templates
3. Test connection to external services independently
4. Review the [Configuration Guide](../configuration/README.md) for detailed setup instructions
