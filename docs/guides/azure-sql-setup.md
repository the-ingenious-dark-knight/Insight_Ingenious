---
title: "Azure SQL Database Setup Guide"
layout: single
permalink: /guides/azure-sql-setup/
sidebar:
  nav: "docs"
toc: true
toc_label: "Setup Steps"
toc_icon: "database"
---

# Azure SQL Database Setup Guide

This guide walks you through setting up Azure SQL Database as the chat history storage backend for Insight Ingenious. Azure SQL provides enterprise-grade conversation persistence with high availability and scalability.

## Overview

Insight Ingenious supports two database backends for chat history:
- **SQLite**: For development and testing (default)
- **Azure SQL**: For production deployments (recommended)

This guide covers the Azure SQL setup process.

## Prerequisites

- Azure subscription with SQL Database access
- Azure SQL Database instance (or willingness to create one)
- Basic familiarity with Azure portal or Azure CLI
- Insight Ingenious project already initialized (`uv run ingen init`)

## Step 1: Azure SQL Database Setup

### Option A: Using Azure Portal

1. **Create Azure SQL Database**:
   - Go to [Azure Portal](https://portal.azure.com)
   - Navigate to "SQL Databases" → "Create"
   - Configure your database settings:
     - **Resource Group**: Create or select existing
     - **Database Name**: e.g., `ingenious-chat-history`
     - **Server**: Create new or select existing
     - **Pricing Tier**: Choose based on your needs (Basic for development)

2. **Configure Server Settings**:
   - **Server Name**: e.g., `your-company-ingenious`
   - **Location**: Choose closest to your deployment
   - **Authentication**: SQL Server authentication
   - **Admin Login**: Create username/password (save these!)

3. **Configure Firewall**:
   - Go to your SQL Server → "Networking"
   - Add your IP address to firewall rules
   - For Azure services: Enable "Allow Azure services and resources to access this server"

### Option B: Using Azure CLI

```bash
# Set variables
RESOURCE_GROUP="ingenious-rg"
SERVER_NAME="your-company-ingenious"
DATABASE_NAME="ingenious-chat-history"
LOCATION="eastus"
ADMIN_USER="ingenious-admin"
ADMIN_PASSWORD="YourSecurePassword123!"

# Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create SQL Server
az sql server create \
  --name $SERVER_NAME \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --admin-user $ADMIN_USER \
  --admin-password $ADMIN_PASSWORD

# Create database
az sql db create \
  --resource-group $RESOURCE_GROUP \
  --server $SERVER_NAME \
  --name $DATABASE_NAME \
  --service-objective Basic

# Configure firewall (add your IP)
az sql server firewall-rule create \
  --resource-group $RESOURCE_GROUP \
  --server $SERVER_NAME \
  --name "AllowMyIP" \
  --start-ip-address "YOUR_IP_ADDRESS" \
  --end-ip-address "YOUR_IP_ADDRESS"
```

## Step 2: Install ODBC Driver

Azure SQL requires the Microsoft ODBC Driver for SQL Server.

### macOS Installation

```bash
# Install Microsoft ODBC Driver 18 for SQL Server
brew tap microsoft/mssql-release
brew install msodbcsql18 mssql-tools18

# Verify installation
odbcinst -q -d
# Should show: [ODBC Driver 18 for SQL Server]
```

### Ubuntu/Debian Installation

```bash
# Install Microsoft ODBC Driver 18 for SQL Server
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list > /etc/apt/sources.list.d/mssql-release.list
apt-get update
ACCEPT_EULA=Y apt-get install msodbcsql18
```

### Windows Installation

Download and install the ODBC Driver 18 for SQL Server from the [Microsoft website](https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server).

### Verify ODBC Installation

```bash
odbcinst -q -d
```

Expected output:
```
[ODBC Driver 18 for SQL Server]
[ODBC Driver 17 for SQL Server]
```

## Step 3: Configure Connection String

### Get Connection String from Azure

1. **Azure Portal Method**:
   - Go to your SQL Database → "Connection strings"
   - Copy the "ODBC" connection string
   - It should look like:
     ```
     Driver={ODBC Driver 18 for SQL Server};Server=tcp:yourserver.database.windows.net,1433;Database=yourdatabase;Uid=yourusername;Pwd={your_password_here};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;
     ```

2. **Manual Construction**:
   ```
   Driver={ODBC Driver 18 for SQL Server};Server=tcp:YOUR_SERVER.database.windows.net,1433;Database=YOUR_DATABASE;Uid=YOUR_USERNAME;Pwd=YOUR_PASSWORD;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;
   ```

### Add to Environment Variables

Add the connection string to your `.env` file:

```bash
# .env
AZURE_SQL_CONNECTION_STRING=Driver={ODBC Driver 18 for SQL Server};Server=tcp:your-server.database.windows.net,1433;Database=your-database;Uid=your-username;Pwd=your-password;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;
```

## Step 4: Update Ingenious Configuration

### Update config.yml

```yaml
# config.yml
chat_history:
  database_type: "azuresql"
  database_name: "your_database_name"
```

### Update profiles.yml

```yaml
# profiles.yml
- name: dev
  chat_history:
    database_connection_string: ${AZURE_SQL_CONNECTION_STRING:REQUIRED_SET_IN_ENV}
```

## Step 5: Test Configuration

### Validate Configuration

```bash
uv run ingen validate
```

Expected output:
```
✅ Insight Ingenious Configuration Validation

1. Environment Variables:
  ✅ INGENIOUS_PROJECT_PATH: /path/to/config.yml
  ✅ INGENIOUS_PROFILE_PATH: /path/to/profiles.yml

2. Configuration File Validation:
  ✅ config.yml syntax and validation passed
  ✅ profiles.yml syntax and validation passed

3. Azure OpenAI Connectivity:
  ✅ AZURE_OPENAI_API_KEY found
  ✅ AZURE_OPENAI_BASE_URL found

✅ All validations passed! Your Ingenious setup is ready.
```

### Test Database Connection

```bash
uv run python -c "
import pyodbc
import os

conn_str = os.getenv('AZURE_SQL_CONNECTION_STRING')
if not conn_str:
    print('❌ AZURE_SQL_CONNECTION_STRING not set')
    exit(1)

try:
    conn = pyodbc.connect(conn_str)
    print('✅ Azure SQL connection successful!')
    cursor = conn.cursor()
    cursor.execute('SELECT @@VERSION')
    version = cursor.fetchone()[0]
    print(f'Connected to: {version[:50]}...')
    conn.close()
except Exception as e:
    print(f'❌ Connection failed: {e}')
"
```

### Test Ingenious Repository

```bash
uv run python -c "
import asyncio
from ingenious.ingenious.dependencies import get_config
from ingenious.ingenious.db.chat_history_repository import ChatHistoryRepository
from ingenious.models.database_client import DatabaseClientType

async def test_repo():
    config = get_config()
    db_type = DatabaseClientType(config.chat_history.database_type)
    repo = ChatHistoryRepository(db_type=db_type, config=config)

    try:
        messages = await repo.get_thread_messages('test-thread')
        print(f'✅ Azure SQL repository working! (Found {len(messages)} messages)')
    except Exception as e:
        print(f'❌ Repository error: {e}')

asyncio.run(test_repo())
"
```

## Step 6: Production Testing

### Start Ingenious Server

```bash
uv run ingen serve
```

### Test Chat History Storage

```bash
# Test with bike-insights workflow
curl -X POST "http://localhost:80/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_prompt": "{\"stores\": [{\"name\": \"Azure Test Store\", \"location\": \"NSW\", \"bike_sales\": [{\"product_code\": \"AZURE-001\", \"quantity_sold\": 1, \"sale_date\": \"2023-04-15\", \"year\": 2023, \"month\": \"April\", \"customer_review\": {\"rating\": 5.0, \"comment\": \"Testing Azure SQL integration!\"}}], \"bike_stock\": []}], \"revision_id\": \"azure-test-1\", \"identifier\": \"sql-test\"}",
    "conversation_flow": "bike-insights",
    "session_id": "azure-test-session"
  }'
```

### Verify Data Storage

Query the database directly to confirm messages are stored:

```bash
uv run python -c "
import pyodbc
import os

conn_str = os.getenv('AZURE_SQL_CONNECTION_STRING')
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

# Check if tables were created
cursor.execute('SELECT COUNT(*) FROM chat_history')
count = cursor.fetchone()[0]
print(f'Messages in chat_history table: {count}')

# Show recent messages
cursor.execute('SELECT TOP 5 thread_id, content FROM chat_history ORDER BY created_at DESC')
for row in cursor.fetchall():
    print(f'Thread: {row[0]}, Content: {row[1][:50]}...')

conn.close()
"
```

## Database Schema

Ingenious automatically creates the following tables in your Azure SQL database:

| Table | Purpose |
|-------|---------|
| `chat_history` | Main conversation messages |
| `chat_history_summary` | Memory/summary storage |
| `users` | User management |
| `threads` | Thread/conversation management |
| `steps` | Chainlit step tracking |
| `elements` | Chainlit UI elements |
| `feedbacks` | User feedback data |

No manual schema creation is required.

## Security Best Practices

### Connection String Security

1. **Never commit connection strings to version control**
2. **Use environment variables**: Store in `.env` files (not in Git)
3. **Rotate passwords regularly**: Especially for production
4. **Use least privilege**: Create dedicated database users with minimal permissions

### Network Security

1. **Configure firewall rules**: Only allow necessary IP addresses
2. **Use VNet integration**: For production deployments
3. **Enable threat detection**: Monitor for suspicious activities
4. **Regular security updates**: Keep ODBC drivers updated

### Monitoring

1. **Enable logging**: Monitor database connections and queries
2. **Set up alerts**: For connection failures or high usage
3. **Regular backups**: Ensure chat history is backed up
4. **Performance monitoring**: Track query performance and optimization

## Troubleshooting

### Common Issues

**Connection Timeout**:
- Increase `Connection Timeout` in connection string
- Check firewall rules
- Verify server name and port

**ODBC Driver Not Found**:
- Reinstall ODBC Driver 18 for SQL Server
- Verify with `odbcinst -q -d`

**Authentication Failed**:
- Verify username/password
- Check if user has database access
- Try connecting with SQL Server Management Studio first

**Table Not Found**:
- Tables are auto-created on first use
- Ensure user has CREATE TABLE permissions
- Check database name in connection string

For more troubleshooting help, see the [Troubleshooting Guide](/troubleshooting/#azure-sql-database-issues).

## Migration from SQLite

If you're migrating from SQLite to Azure SQL:

1. **Backup existing data**:
   ```bash
   cp ./.tmp/high_level_logs.db ./backup_$(date +%Y%m%d).db
   ```

2. **Update configuration** as described above

3. **Start fresh**: Azure SQL tables will be created automatically

4. **Optional data migration**: Write custom scripts if you need to preserve existing chat history

## Next Steps

- [Configure additional workflows](/workflows/)
- [Set up monitoring and alerts](/guides/monitoring/)
- [Learn about scaling considerations](/architecture/scaling/)
- [Explore security best practices](/guides/security/)

---

*This guide covers Azure SQL Database setup for Insight Ingenious. For other database options or advanced configurations, see the [Configuration Guide](/getting-started/configuration/).*
