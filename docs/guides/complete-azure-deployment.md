---
title: "Complete Azure Deployment Guide"
layout: single
permalink: /guides/complete-azure-deployment/
sidebar:
  nav: "docs"
toc: true
toc_label: "Setup Steps"
toc_icon: "database"
---

This guide provides step-by-step instructions for deploying the Ingenious bike-insights workflow with full Azure integration, including Azure SQL Database for chat history and Azure Blob Storage for prompt management.

##  Overview

This deployment includes:
- **Bike-Insights Workflow**: Multi-agent system with 4 specialized agents
- **Azure SQL Database**: Chat history storage
- **Azure Blob Storage**: Cloud-based prompt template management
- **API Integration**: Full REST API support for prompts management

##  Prerequisites

### Required Azure Resources
- Azure SQL Database instance
- Azure Storage Account with Blob service
- Azure OpenAI service with GPT-4.1-nano deployment

### Local Development Requirements
- Python 3.13+
- [uv package manager](https://docs.astral.sh/uv/)
- ODBC Driver 18 for SQL Server

##  Step-by-Step Deployment

### Step 1: Install Ingenious Library

```bash
# Set up uv project
uv init

# Install as package
uv add "ingenious[azure-full]"
```

### Step 2: Initialize Project

```bash
# Initialize with bike-insights template
uv run ingen init
```

This creates:
- `.env.example` - Environment variable template
- `ingenious_extensions/` - Bike-insights workflow

### Step 3: Configure Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Update `.env` with your Azure credentials:

```bash
# =============================================================================
# REQUIRED: Azure OpenAI Configuration
# =============================================================================
# Using nested environment variables format (recommended)
INGENIOUS_MODELS__0__MODEL=gpt-4.1-nano
INGENIOUS_MODELS__0__API_TYPE=rest
INGENIOUS_MODELS__0__API_VERSION=2024-12-01-preview
INGENIOUS_MODELS__0__DEPLOYMENT=your-gpt4-deployment-name
INGENIOUS_MODELS__0__API_KEY=your-azure-openai-api-key-here
INGENIOUS_MODELS__0__BASE_URL=https://your-resource.openai.azure.com/

# =============================================================================
# REQUIRED: Azure SQL Database Configuration
# =============================================================================
INGENIOUS_CHAT_HISTORY__DATABASE_TYPE=azuresql
INGENIOUS_CHAT_HISTORY__DATABASE_NAME=ChatHistory
INGENIOUS_CHAT_HISTORY__DATABASE_CONNECTION_STRING=${AZURE_SQL_CONNECTION_STRING}

# =============================================================================
# REQUIRED: Azure SQL Database Configuration
# =============================================================================
AZURE_SQL_CONNECTION_STRING=Driver={ODBC Driver 18 for SQL Server};Server=tcp:your-server.database.windows.net,1433;Database=your-database;Uid=your-username;Pwd=your-password;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;

# =============================================================================
# REQUIRED: Azure Blob Storage Configuration
# =============================================================================
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=your-account;AccountKey=your-key;EndpointSuffix=core.windows.net
AZURE_STORAGE_REVISIONS_URL=https://your-account.blob.core.windows.net/
AZURE_STORAGE_DATA_URL=https://your-account.blob.core.windows.net/

# =============================================================================
# OPTIONAL: Web Server Configuration
# =============================================================================
INGENIOUS_WEB_CONFIGURATION__IP_ADDRESS=0.0.0.0
INGENIOUS_WEB_CONFIGURATION__PORT=8080
```
> **Important:** When configuring Azure SQL, always use the connection string from the **ODBC** tab in the Azure Portal. Do **not** use ADO.NET or JDBC connection strings, as these formats are incompatible and will cause connection errors.

### Step 5: Configure Azure Blob Storage Integration

Add these environment variables to your `.env` file:

```bash
# Azure Blob Storage configuration
INGENIOUS_FILE_STORAGE__REVISIONS__ENABLE=true
INGENIOUS_FILE_STORAGE__REVISIONS__STORAGE_TYPE=azure
INGENIOUS_FILE_STORAGE__REVISIONS__CONTAINER_NAME=prompts
INGENIOUS_FILE_STORAGE__REVISIONS__PATH=ingenious-files
INGENIOUS_FILE_STORAGE__REVISIONS__ADD_SUB_FOLDERS=true
INGENIOUS_FILE_STORAGE__REVISIONS__URL=${AZURE_STORAGE_REVISIONS_URL}
INGENIOUS_FILE_STORAGE__REVISIONS__TOKEN=${AZURE_STORAGE_CONNECTION_STRING}
INGENIOUS_FILE_STORAGE__REVISIONS__AUTHENTICATION_METHOD=token

INGENIOUS_FILE_STORAGE__DATA__ENABLE=true
INGENIOUS_FILE_STORAGE__DATA__STORAGE_TYPE=azure
INGENIOUS_FILE_STORAGE__DATA__CONTAINER_NAME=data
INGENIOUS_FILE_STORAGE__DATA__PATH=ingenious-files
INGENIOUS_FILE_STORAGE__DATA__ADD_SUB_FOLDERS=true
INGENIOUS_FILE_STORAGE__DATA__URL=${AZURE_STORAGE_DATA_URL}
INGENIOUS_FILE_STORAGE__DATA__TOKEN=${AZURE_STORAGE_CONNECTION_STRING}
INGENIOUS_FILE_STORAGE__DATA__AUTHENTICATION_METHOD=token
```

> **⚠️ Important Configuration Gotcha**: The Azure files implementation checks for connection strings in the `TOKEN` field, not just the `AZURE_STORAGE_CONNECTION_STRING` environment variable. When using `AUTHENTICATION_METHOD=token`, you **must** set the `TOKEN` field to your Azure Storage connection string. Simply having `AZURE_STORAGE_CONNECTION_STRING` defined is not sufficient - the connection string must be explicitly passed through the `TOKEN` configuration field for each storage container.

### Step 6: Install ODBC Driver (if not already installed)

#### macOS
```bash
brew tap microsoft/mssql-release
brew install msodbcsql18

# Verify installation
odbcinst -q -d | grep "ODBC Driver 18"
```

#### Ubuntu/Debian
```bash
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list > /etc/apt/sources.list.d/mssql-release.list
apt-get update
ACCEPT_EULA=Y apt-get install msodbcsql18
```

### Step 7: Upload Prompt Templates to Azure Blob Storage

#### Use the Provided Upload Script (Recommended for bike-insights)

For bike-insights workflow, use the dedicated [upload script](https://github.com/Insight-Services-APAC/ingenious/blob/main/scripts/upload_bike_templates.py):
```bash
# Ensure server is running first
uv run ingen serve --port 8080 &

# Upload bike-insights templates
uv run python scripts/upload_bike_templates.py
```
        
### Step 8: Validate Configuration

```bash
# Environment variables are loaded from .env file
uv run ingen validate
```

Expected output:
```
 Insight Ingenious Configuration Validation
1. Environment Variables:
2. Configuration File Validation:
3. Azure OpenAI Connectivity:
4. Workflow Availability:
 All validations passed! Your Ingenious setup is ready.
```

### Step 9: Start the Server

```bash
# Environment variables are loaded from .env file
uv run ingen serve --port 8080
```

### Step 10: Test the Deployment

#### Test Server Health
```bash
curl http://localhost:8080/api/v1/health
```

#### Test Bike-Insights Workflow
```bash
curl -X POST http://localhost:8080/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_prompt": "{\"stores\": [{\"name\": \"Test Store\", \"location\": \"NSW\", \"bike_sales\": [{\"product_code\": \"TEST-001\", \"quantity_sold\": 2, \"sale_date\": \"2024-01-15\", \"year\": 2024, \"month\": \"January\", \"customer_review\": {\"rating\": 4.5, \"comment\": \"Great bike for testing!\"}}], \"bike_stock\": [{\"bike\": {\"brand\": \"TestBrand\", \"model\": \"TestModel\", \"year\": 2024, \"price\": 1299.99, \"battery_capacity\": 0.75, \"motor_power\": 500}, \"quantity\": 5}]}], \"revision_id\": \"test-1\", \"identifier\": \"basic-test\"}",
    "conversation_flow": "bike-insights"
  }'
```

#### Test Prompts API
```bash
# List prompt templates
curl "http://localhost:8080/api/v1/prompts/list/quickstart-1"

# View a prompt template
curl "http://localhost:8080/api/v1/prompts/view/quickstart-1/bike_lookup_agent_prompt.jinja"

# Update a prompt template
curl -X POST "http://localhost:8080/api/v1/prompts/update/quickstart-1/bike_lookup_agent_prompt.jinja" \
  -H "Content-Type: application/json" \
  -d '{"content": "### UPDATED ROLE\nYou are an updated bike lookup agent...\n"}'
```

#### That's it! You should now have an API served locally with integrations to Azure SQL, Blob, and OpenAI. You can branch out from this starting point and use the auto-generated Dockerfile to deploy to production.