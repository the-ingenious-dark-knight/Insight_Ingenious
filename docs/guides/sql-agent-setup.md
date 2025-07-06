---
title: "SQL Manipulation Agent Setup Guide"
layout: single
permalink: /guides/sql-agent-setup/
sidebar:
  nav: "docs"
toc: true
toc_label: "SQL Agent Setup"
toc_icon: "database"
---

# SQL Manipulation Agent Setup Guide

The SQL Manipulation Agent allows you to execute SQL queries using natural language input. This guide covers both SQLite (local development) and Azure SQL (production) setups.

## Overview

The SQL agent supports two database modes:
- **SQLite Mode**: Local development with SQLite database files
- **Azure SQL Mode**: Production deployments with Azure SQL Database

## Quick Start with SQLite (Recommended)

This is the fastest way to get started with the SQL agent for development and testing.

### Step 1: Install Ingenious

```bash
# From your project root
uv pip install -e ./ingenious
```

### Step 2: Initialize Project

```bash
# Initialize a new Ingenious project
ingen init

# This creates config.yml and profiles.yml files
```

### Step 3: Configure SQLite Mode

Edit your `profiles.yml` file to enable SQLite mode:

```yaml
# profiles.yml
azure_sql_services:
  database_name: "skip"  # This enables SQLite mode
local_sql_db:
  database_path: "/tmp/sample_sql.db"
```

### Step 4: Set Environment Variables

Create a `.env` file with your Azure OpenAI credentials:

```bash
# .env
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_BASE_URL=your-endpoint
AZURE_OPENAI_DEPLOYMENT=your-deployment-name
AZURE_OPENAI_API_VERSION=2024-12-01-preview
```

### Step 5: Create Sample Database

```bash
# Create a sample SQLite database with test data
uv run python -c "
from ingenious.utils.load_sample_data import sqlite_sample_db
sqlite_sample_db()
print('✅ Sample SQLite database created at /tmp/sample_sql.db')
"
```

### Step 6: Start the Server

```bash
# Start the Ingenious API server
ingen serve
```

### Step 7: Test SQL Queries

```bash
# Test basic table listing
curl -X POST http://localhost:80/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_prompt": "What tables are available in the database?",
    "conversation_flow": "sql-manipulation-agent"
  }'

# Test data queries
curl -X POST http://localhost:80/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_prompt": "Show me the first 5 rows from each table",
    "conversation_flow": "sql-manipulation-agent"
  }'
```

## Advanced Setup with Azure SQL

For production deployments, you can connect to Azure SQL Database.

### Prerequisites

- Azure SQL Database instance
- Database credentials (username/password)
- ODBC Driver 18 for SQL Server installed

### Configuration

1. **Configure profiles.yml** for Azure SQL:

```yaml
# profiles.yml
azure_sql_services:
  database_name: "your-database-name"
  server_name: "your-server.database.windows.net"
  driver: "ODBC Driver 18 for SQL Server"
  connection_string: "Driver={ODBC Driver 18 for SQL Server};Server=tcp:your-server.database.windows.net,1433;Database=your-database;Uid=your-username;Pwd=your-password;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
```

2. **Set environment variables**:

```bash
export AZURE_SQL_USERNAME="your-username"
export AZURE_SQL_PASSWORD="your-password"
```

3. **Test connection**:

```bash
# Validate configuration
uv run python -c "
from ingenious.config.config import load_app_config
config = load_app_config()
print('Azure SQL Config:', config.azure_sql_services)
if config.azure_sql_services and config.azure_sql_services.database_name != 'skip':
    print('✅ Azure SQL mode enabled')
else:
    print('✅ SQLite mode enabled')
"
```

## Example Queries

### Data Exploration

```bash
# Explore database schema
curl -X POST http://localhost:80/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_prompt": "Show me the structure of all tables",
    "conversation_flow": "sql-manipulation-agent"
  }'

# Check table sizes
curl -X POST http://localhost:80/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_prompt": "How many rows are in each table?",
    "conversation_flow": "sql-manipulation-agent"
  }'
```

### Business Analytics

```bash
# Sales analysis
curl -X POST http://localhost:80/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_prompt": "Show me the top 10 customers by total sales amount",
    "conversation_flow": "sql-manipulation-agent"
  }'

# Temporal analysis
curl -X POST http://localhost:80/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_prompt": "What were the monthly sales trends for the last 6 months?",
    "conversation_flow": "sql-manipulation-agent"
  }'
```

### Data Quality Checks

```bash
# Find missing data
curl -X POST http://localhost:80/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_prompt": "Check for any NULL values in the customer table",
    "conversation_flow": "sql-manipulation-agent"
  }'

# Data validation
curl -X POST http://localhost:80/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_prompt": "Find any duplicate entries in the orders table",
    "conversation_flow": "sql-manipulation-agent"
  }'
```

## Testing and Validation

### Automated Testing Script

Create a test script to validate your SQL agent setup:

```bash
#!/bin/bash
# test_sql_agent.sh

echo "🧪 Testing SQL Manipulation Agent..."

# Test 1: Basic connectivity
echo "📊 Test 1: Database connectivity"
curl -s -X POST http://localhost:80/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_prompt": "List all tables in the database",
    "conversation_flow": "sql-manipulation-agent"
  }' | jq -r '.response // .error'

echo ""

# Test 2: Schema exploration
echo "🔍 Test 2: Schema exploration"
curl -s -X POST http://localhost:80/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_prompt": "Describe the columns in the first table",
    "conversation_flow": "sql-manipulation-agent"
  }' | jq -r '.response // .error'

echo ""

# Test 3: Data query
echo "📈 Test 3: Data query"
curl -s -X POST http://localhost:80/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_prompt": "Show me 3 sample rows from any table",
    "conversation_flow": "sql-manipulation-agent"
  }' | jq -r '.response // .error'

echo ""
echo "✅ SQL Agent tests completed!"
```

Make it executable and run:

```bash
chmod +x test_sql_agent.sh
./test_sql_agent.sh
```

## Troubleshooting

### Common Issues

#### 1. "Database connection failed"

**For SQLite mode:**
- Ensure `database_name: "skip"` is set in profiles.yml
- Check that the database file path is writable
- Run the sample data creation script

**For Azure SQL mode:**
- Verify connection string format
- Check username/password credentials
- Ensure firewall allows connections
- Verify ODBC driver is installed

#### 2. "No tables found"

**Solution:**
```bash
# For SQLite, create sample data
uv run python -c "
from ingenious.utils.load_sample_data import sqlite_sample_db
sqlite_sample_db()
print('Sample data created')
"

# For Azure SQL, check if tables exist
# Connect to your database and verify table structure
```

#### 3. "Configuration validation failed"

**Solution:**
```bash
# Check configuration
uv run python -c "
from ingenious.config.config import load_app_config
config = load_app_config()
print('Config valid:', config is not None)
print('SQL config:', getattr(config, 'azure_sql_services', 'Not found'))
"
```

#### 4. "SQL query execution failed"

**Common causes:**
- AI generated invalid SQL syntax
- Referenced tables/columns don't exist
- Insufficient database permissions

**Debug steps:**
1. Check the actual SQL query in the response
2. Test the query manually in your database
3. Verify table and column names
4. Check database permissions

### Debug Mode

Enable detailed logging for troubleshooting:

```bash
# Set debug environment
export INGENIOUS_LOG_LEVEL=DEBUG

# Check SQL tool functions
uv run python -c "
from ingenious.services.chat_services.multi_agent.tool_functions_standard import SQL_ToolFunctions
sql_tools = SQL_ToolFunctions()
print('SQL Tools initialized:', sql_tools is not None)
"
```

### Configuration Validation

Validate your complete setup:

```bash
# Complete configuration check
uv run python -c "
from ingenious.config.config import load_app_config
from ingenious.config.profile import load_profile_config

config = load_app_config()
profile = load_profile_config()

print('=== Configuration Check ===')
print('Config loaded:', config is not None)
print('Profile loaded:', profile is not None)

if config:
    print('Azure SQL Services:', getattr(config, 'azure_sql_services', 'Not configured'))
    print('Local SQL DB:', getattr(config, 'local_sql_db', 'Not configured'))

if profile:
    print('Profile Azure SQL:', getattr(profile, 'azure_sql_services', 'Not configured'))

print('=== End Check ===')
"
```

## Integration with Other Workflows

The SQL agent can be combined with other Ingenious workflows:

### With Classification Agent

Route queries to SQL agent based on content:

```python
# Custom routing logic
if 'database' in user_prompt or 'sql' in user_prompt.lower():
    workflow = 'sql-manipulation-agent'
else:
    workflow = 'classification-agent'
```

### With Knowledge Base Agent

Use SQL results to enrich knowledge base searches:

1. Query database for specific data
2. Use results as context for knowledge base search
3. Combine structured data with unstructured knowledge

## Best Practices

### Security

1. **Never expose database credentials** in configuration files
2. **Use environment variables** for sensitive data
3. **Limit database permissions** to read-only when possible
4. **Validate SQL queries** before execution (built-in safety)

### Performance

1. **Use SQLite for development** - faster setup and testing
2. **Index frequently queried columns** in production databases
3. **Monitor query performance** and optimize slow queries
4. **Set appropriate connection timeouts**

### Data Management

1. **Regular backups** for production databases
2. **Version control** for database schema changes
3. **Test with sample data** before production deployment
4. **Monitor database size** and implement cleanup strategies

## Next Steps

Once your SQL agent is working:

1. **Explore other workflows** - bike-insights, knowledge-base-agent
2. **Create custom agents** - extend SQL functionality
3. **Build integrations** - combine with external systems
4. **Monitor usage** - track query patterns and performance

## Support

For additional help:

- Check the [Troubleshooting Guide](../troubleshooting/README.md)
- Review [API Documentation](../api/README.md)
- See [Configuration Guide](../getting-started/configuration.md)
- Run `ingen --help` for CLI assistance
