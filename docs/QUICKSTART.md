---
title: "⚡ Quick Start Guide"
layout: single
permalink: /quickstart/
sidebar:
  nav: "docs"
toc: true
toc_label: "Quick Start Steps"
toc_icon: "bolt"
---

# ⚡ Quick Start Guide

Get Insight Ingenious up and running in 5 minutes! This enterprise-grade Python library enables rapid deployment of AI agent APIs with seamless Microsoft Azure integrations.

## 🚀 Prerequisites

- ✅ Python 3.13+
- ✅ uv package manager
- ✅ Azure OpenAI API credentials

## 📦 5-Minute Setup

1. **Install and Initialize**:
    ```bash
    # For local development (if you have the ingenious source code)
    uv pip install -e ./ingenious

    # Or for production install from package
    uv add ingenious

    # Initialize project template
    uv run ingen init

    # Install additional dependencies for environment variable loading
    uv add python-dotenv
    ```

2. **Configure Credentials**:
    ```bash
    # Create .env file with your Azure OpenAI credentials
    cat > .env << 'EOF'
    AZURE_OPENAI_API_KEY=your_api_key_here
    AZURE_OPENAI_BASE_URL=https://your-endpoint.openai.azure.com/
    AZURE_OPENAI_MODEL_NAME=gpt-4.1-nano
    AZURE_OPENAI_DEPLOYMENT=gpt-4.1-nano
    AZURE_OPENAI_API_VERSION=2024-12-01-preview
    LOCAL_SQL_CSV_PATH=./sample_data.csv
    EOF

    # Edit with your actual credentials
    nano .env
    ```

3. **Validate Setup** (Recommended):
    ```bash
    export INGENIOUS_PROJECT_PATH=$(pwd)/config.yml
    export INGENIOUS_PROFILE_PATH=$(pwd)/profiles.yml
    uv run ingen validate  # Check configuration before starting
    ```

4. **Start the Server**:
    ```bash
    # Default port (may require admin privileges on some systems)
    uv run ingen serve

    # Alternative port if 80 is not available
    uv run ingen serve --port 8080
    ```

5. **Verify Health**:
    ```bash
    # Check server health (adjust port if using alternative)
    curl http://localhost:80/api/v1/health
    # or
    curl http://localhost:8080/api/v1/health
    ```

6. **Test the API**:
    ```bash
    # Test bike insights workflow (the "Hello World" of Ingenious)
    # Adjust port to match your server (80 or 8080)
    curl -X POST http://localhost:8080/api/v1/chat \
      -H "Content-Type: application/json" \
      -d '{
        "user_prompt": "{\"stores\": [{\"name\": \"QuickStart Store\", \"location\": \"NSW\", \"bike_sales\": [{\"product_code\": \"QS-001\", \"quantity_sold\": 1, \"sale_date\": \"2023-04-15\", \"year\": 2023, \"month\": \"April\", \"customer_review\": {\"rating\": 5.0, \"comment\": \"Perfect bike for getting started!\"}}], \"bike_stock\": []}], \"revision_id\": \"quickstart-1\", \"identifier\": \"hello-world\"}",
        "conversation_flow": "bike-insights"
      }'
    ```

🎉 **That's it!** You should see a comprehensive JSON response with insights from multiple AI agents analyzing the bike sales data.

**Note**: The `bike-insights` workflow is created when you run `ingen init` - it's part of the project template setup, not included in the core library.

## 🗄️ Azure SQL Database Setup (Optional)

For production deployments with persistent chat history storage in Azure SQL Database:

### Prerequisites
- ✅ Azure SQL Database instance with credentials
- ✅ ODBC Driver 18 for SQL Server installed

### Setup Steps

1. **Install ODBC Driver** (if not already installed):
    ```bash
    # macOS
    brew tap microsoft/mssql-release
    brew install msodbcsql18

    # Verify installation
    odbcinst -q -d | grep "ODBC Driver 18"
    ```

2. **Add Azure SQL credentials to .env**:
    ```bash
    # Add to your existing .env file
    echo 'AZURE_SQL_CONNECTION_STRING=Driver={ODBC Driver 18 for SQL Server};Server=tcp:your-server.database.windows.net,1433;Database=your-database;Uid=your-username;Pwd=your-password;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;' >> .env
    ```

3. **Update config.yml for Azure SQL**:
    ```bash
    # Update chat_history section in config.yml
    sed -i.bak 's/database_type: "sqlite"/database_type: "azuresql"/' config.yml
    ```

4. **Update profiles.yml for environment variable**:
    ```yaml
    # Edit profiles.yml - update the chat_history section
    chat_history:
      database_connection_string: ${AZURE_SQL_CONNECTION_STRING}
    ```

5. **Validate Azure SQL setup**:
    ```bash
    uv run ingen validate
    ```

6. **Test with Azure SQL**:
    ```bash
    # Start server and test - chat history will now be stored in Azure SQL
    uv run ingen serve --port 8080
    ```

**Benefits of Azure SQL:**
- ✅ Production-grade chat history persistence
- ✅ Multi-user conversation management
- ✅ Enterprise security and compliance
- ✅ Automatic table creation and management

## 📊 Data Format Examples

### Simple bike-insights Request (Basic)
```json
{
  "user_prompt": "{\"stores\": [{\"name\": \"Test Store\", \"location\": \"NSW\", \"bike_sales\": [{\"product_code\": \"B-001\", \"quantity_sold\": 1, \"sale_date\": \"2024-01-15\", \"year\": 2024, \"month\": \"January\", \"customer_review\": {\"rating\": 5.0, \"comment\": \"Great bike!\"}}], \"bike_stock\": []}], \"revision_id\": \"test-1\", \"identifier\": \"example\"}",
  "conversation_flow": "bike-insights"
}
```

### Advanced bike-insights Request (With Stock Data)
```json
{
  "user_prompt": "{\"stores\": [{\"name\": \"Premium Bikes\", \"location\": \"Sydney\", \"bike_sales\": [{\"product_code\": \"PB-2024-001\", \"quantity_sold\": 3, \"sale_date\": \"2024-01-15\", \"year\": 2024, \"month\": \"January\", \"customer_review\": {\"rating\": 4.8, \"comment\": \"Excellent quality!\"}}], \"bike_stock\": [{\"bike\": {\"brand\": \"Specialized\", \"model\": \"Turbo Vado\", \"year\": 2024, \"price\": 2899.99, \"battery_capacity\": 0.75, \"motor_power\": 500}, \"quantity\": 5}]}], \"revision_id\": \"advanced-1\", \"identifier\": \"example\"}",
  "conversation_flow": "bike-insights"
}
```

### bike_stock Object Format
The `bike_stock` array requires objects with this structure:
```json
{
  "bike": {
    "brand": "string",      // Required: Bike manufacturer
    "model": "string",      // Required: Bike model name
    "year": 2024,          // Required: Manufacturing year
    "price": 2899.99,      // Required: Price in dollars
    // Optional fields for electric bikes:
    "battery_capacity": 0.75,  // kWh
    "motor_power": 500,        // Watts
    // Optional fields for mountain bikes:
    "suspension": "full",      // Type of suspension
    // Optional fields for road bikes:
    "frame_material": "carbon" // Frame material
  },
  "quantity": 5             // Required: Stock quantity
}
```

### Multiple Stores Example
```bash
curl -X POST http://localhost:8080/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_prompt": "{\"stores\": [{\"name\": \"Store A\", \"location\": \"NSW\", \"bike_sales\": [{\"product_code\": \"A-001\", \"quantity_sold\": 2, \"sale_date\": \"2024-01-10\", \"year\": 2024, \"month\": \"January\", \"customer_review\": {\"rating\": 4.5, \"comment\": \"Good value\"}}], \"bike_stock\": []}, {\"name\": \"Store B\", \"location\": \"VIC\", \"bike_sales\": [{\"product_code\": \"B-001\", \"quantity_sold\": 1, \"sale_date\": \"2024-01-12\", \"year\": 2024, \"month\": \"January\", \"customer_review\": {\"rating\": 5.0, \"comment\": \"Perfect!\"}}], \"bike_stock\": []}], \"revision_id\": \"multi-store-1\", \"identifier\": \"comparison\"}",
    "conversation_flow": "bike-insights"
  }'
```

---

## 🛠️ One-Line Setup Script

Save this as `setup.sh`:

```bash
#!/bin/bash
set -e

echo "🚀 Setting up Insight Ingenious..."

# Install and initialize
uv add ingenious
uv run ingen init

# Set environment variables
export INGENIOUS_PROJECT_PATH=$(pwd)/config.yml
export INGENIOUS_PROFILE_PATH=$(pwd)/profiles.yml

echo "✅ Setup complete!"
echo "📝 Next: Edit .env with your Azure OpenAI credentials"
echo "🚀 Then run: uv run ingen serve --port 8080"
```

Run with: `chmod +x setup.sh && ./setup.sh`

---

## 🧪 Verification Commands

```bash
# Check system status
uv run ingen status

# List available workflows
uv run ingen workflows

# Test specific workflow requirements
uv run ingen workflows bike-insights

# Quick server test
curl -s http://localhost:8080/api/v1/health || echo "Server not running"
```

---

## 📡 API Endpoints Quick Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/chat` | POST | Main chat/workflow endpoint |
| `/api/v1/workflow-status/{name}` | GET | Check workflow status |
| `/api/v1/health` | GET | Server health check |
| `/docs` | GET | API documentation |

**Note:** Adjust `localhost:8080` to match your server port (default is 80, but 8080 is common for development).

---

## Available Workflows

### bike-insights (Hello World - **START HERE!**)
**Purpose**: The "Hello World" of Ingenious - comprehensive bike sales analysis showcasing multi-agent coordination
**Requirements**: Azure OpenAI only
**Availability**: Created when you run `ingen init` (part of project template)
**Input**: JSON with bike sales data
**Why start here?**: Demonstrates the full power of multi-agent workflows

### classification-agent (Simple Alternative)
**Purpose**: Text classification and routing (try this if bike-insights seems complex)
**Requirements**: Azure OpenAI only
**Availability**: Core library (always available)
**Input**: Plain text

### knowledge-base-agent (Advanced)
**Purpose**: Knowledge base search
**Requirements**: Azure OpenAI + Azure Search

### 📊 sql-manipulation-agent (Advanced)
**Purpose**: Natural language to SQL
**Requirements**: Azure OpenAI + Database connection

---

## 🚨 Quick Troubleshooting

### Server won't start?
```bash
# Check configuration
uv run ingen status

# Try different port (common solution for port 80 permission issues)
uv run ingen serve --port 8080

# Check logs for errors
uv run ingen serve 2>&1 | grep -i error
```

### Port 80 permission denied?
```bash
# Use alternative port (recommended for development)
uv run ingen serve --port 8080

# Update all curl commands to use :8080 instead of :80
```

### Environment variables not loading?
```bash
# Ensure python-dotenv is installed
uv add python-dotenv

# Check .env file format (no spaces around =)
cat .env

# Test environment variable loading
python -c "
from dotenv import load_dotenv
import os
load_dotenv()
print('AZURE_OPENAI_API_KEY:', os.getenv('AZURE_OPENAI_API_KEY', 'NOT_FOUND'))
"
```

### Profile validation errors?
```bash
# Use minimal template
cp ingenious/ingenious/ingenious_extensions_template/profiles.minimal.yml ./profiles.yml

# Check environment variables
env | grep AZURE_OPENAI
```

### Workflow not found?
```bash
# Check available workflows
uv run ingen workflows

# Use correct name (hyphens preferred, underscores legacy)
```
```json
{
  "user_prompt": "Your bike sales data here...",
  "conversation_flow": "bike-insights"  // ✅ Preferred (hyphenated)
}

// Legacy format (still supported):
{
  "user_prompt": "Your bike sales data here...",
  "conversation_flow": "bike_insights"  // ✅ Legacy (still works)
}
```
```

### API returning errors?
```bash
# Check server logs in terminal
# Verify JSON format for bike-insights
# Try with classification-agent first if bike-insights seems complex
```

---

## 🔄 Reset If Needed

```bash
# Clean slate
rm -rf ingenious_extensions/ tmp/ config.yml profiles.yml .env

# Start over
uv run ingen init
```

---

## 📚 Next Steps

Once you have the basic setup working:

1. **📖 Read the full documentation**: `/docs/`
2. **�️ Try the SQL Agent**: Follow the [SQL Agent Setup Guide](guides/sql-agent-setup.md) for database queries
3. **�🔧 Customize workflows**: Edit templates in `ingenious_extensions/`
4. **🧪 Create your own agents**: Follow patterns in existing workflows
5. **🚀 Deploy to production**: See deployment guides

### Quick SQL Agent Setup

If you want to try database queries with natural language:

```bash
# Set up SQLite database
uv run python -c "
from ingenious.utils.load_sample_data import sqlite_sample_db
sqlite_sample_db()
print('✅ Sample database created')
"

# Test SQL queries
curl -X POST http://localhost:8080/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_prompt": "Show me all tables in the database",
    "conversation_flow": "sql-manipulation-agent"
  }'
```

---

## 💡 Pro Tips

- **Start with `bike-insights`** - it's the "Hello World" that shows off Ingenious's power
- Use `classification-agent` only if you want something simpler
- Check `uv run ingen status` when things break
- The minimal templates work better than full templates
- Environment variables override config file values
- Logs show detailed error messages

**Happy coding! 🎉**
