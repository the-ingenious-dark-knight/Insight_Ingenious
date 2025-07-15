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

## Quick Start

Get up and running in 5 minutes with Azure OpenAI!

### Prerequisites
- Python 3.13+
- Azure OpenAI API credentials
- [uv package manager](https://docs.astral.sh/uv/)

### 5-Minute Setup

1. **Install and Initialize**:
    ```bash
    # From your project directory - choose based on features needed
    uv add ingenious[standard]    # Recommended: includes SQL agent support
    # OR  
    uv add ingenious[azure-full]  # Full Azure integration
    # OR
    uv add ingenious             # Minimal installation
    
    # Initialize project  
    uv run ingen init
    ```

2. **Configure Credentials**:
    ```bash
    # Copy appropriate template and edit with your credentials
    cp .env.development .env      # For local development
    # OR
    cp .env.azure-full .env       # For full Azure integration
    
    # Edit with your actual Azure OpenAI credentials
    nano .env
    ```

3. **Validate Setup** (Recommended):
    ```bash
    # No need to set project/profile paths - pydantic-settings handles configuration
    uv run ingen validate  # Check configuration before starting
    ```
    
    > **Important**: YAML configuration files (`config.yml`, `profiles.yml`) are no longer supported. All configuration must be done via environment variables with `INGENIOUS_` prefixes.

4. **Start the Server**:
    ```bash
    uv run ingen serve
    ```

5. **Verify Health**:
    ```bash
    # Check server health (default development port is 8000)
    curl http://localhost:8000/api/v1/health
    ```

6. **Test the API**:
    ```bash
    # Test bike insights workflow (the "Hello World" of Ingenious)
    curl -X POST http://localhost:8000/api/v1/chat \
      -H "Content-Type: application/json" \
      -d '{
        "user_prompt": "{\"stores\": [{\"name\": \"QuickStart Store\", \"location\": \"NSW\", \"bike_sales\": [{\"product_code\": \"QS-001\", \"quantity_sold\": 1, \"sale_date\": \"2023-04-15\", \"year\": 2023, \"month\": \"April\", \"customer_review\": {\"rating\": 5.0, \"comment\": \"Perfect bike for getting started!\"}}], \"bike_stock\": []}], \"revision_id\": \"quickstart-1\", \"identifier\": \"hello-world\"}",
        "conversation_flow": "bike-insights"
      }'
    ```

🎉 **That's it!** You should see a comprehensive JSON response with insights from multiple AI agents analyzing the bike sales data.

**Note**: The `bike-insights` workflow is created when you run `ingen init` - it's part of the project template setup, not included in the core library. You can now build on `bike-insights` as a template for your specific use case.

## Workflow Categories

Insight Ingenious provides multiple conversation workflows with different configuration requirements:

### **"Hello World" Workflow** (Available via project template)
- `bike-insights` - **The recommended starting point** - Comprehensive bike sales analysis showcasing multi-agent coordination (created when you run `ingen init`)

### **Core Workflows (Azure OpenAI only)**
- `classification-agent` - Route input to specialized agents based on content

### **Local Stable Implementations** (RECENTLY FIXED)
- `knowledge-base-agent` - Search knowledge bases using local ChromaDB ✅ **STABLE & WORKING**
- `sql-manipulation-agent` - Execute SQL queries using local SQLite ✅ **STABLE & WORKING**

> **Note**: Local implementations (ChromaDB for knowledge-base-agent, SQLite for sql-manipulation-agent) are stable and have been recently fixed to work with the latest autogen and pydantic-settings. Azure Search and Azure SQL integrations are experimental and contain known bugs.

### Quick Local Agent Testing

**Test SQL Agent:**
```bash
# No setup required - creates SQLite database automatically
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_prompt": "What is the average math score for students?",
    "conversation_flow": "sql-manipulation-agent"
  }'
```

**Test Knowledge Base Agent:**
```bash
# Create a simple knowledge base document first
mkdir -p .tmp/knowledge_base
echo "# Health Guide\n\nDrink 8 glasses of water daily for proper hydration." > .tmp/knowledge_base/health.md

# Test the agent
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_prompt": "How much water should I drink daily?",
    "conversation_flow": "knowledge-base-agent"
  }'
```

## Azure SQL Database Setup (Optional)

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
    uv run ingen serve --port 8000
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
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_prompt": "{\"stores\": [{\"name\": \"Store A\", \"location\": \"NSW\", \"bike_sales\": [{\"product_code\": \"A-001\", \"quantity_sold\": 2, \"sale_date\": \"2024-01-10\", \"year\": 2024, \"month\": \"January\", \"customer_review\": {\"rating\": 4.5, \"comment\": \"Good value\"}}], \"bike_stock\": []}, {\"name\": \"Store B\", \"location\": \"VIC\", \"bike_sales\": [{\"product_code\": \"B-001\", \"quantity_sold\": 1, \"sale_date\": \"2024-01-12\", \"year\": 2024, \"month\": \"January\", \"customer_review\": {\"rating\": 5.0, \"comment\": \"Perfect!\"}}], \"bike_stock\": []}], \"revision_id\": \"multi-store-1\", \"identifier\": \"comparison\"}",
    "conversation_flow": "bike-insights"
  }'
```

### Dependencies for Local Agents

If you're using the local stable implementations, you may need to install additional dependencies:

```bash
# For knowledge-base-agent (ChromaDB support)
uv add chromadb

# For sql-manipulation-agent (async file operations)
uv add aiofiles

# For autogen compatibility (latest version)
uv add autogen-ext
```

These dependencies are automatically included in:
- `ingenious[standard]` (includes aiofiles)
- `ingenious[knowledge-base]` (includes chromadb)
- `ingenious[azure-full]` (includes all dependencies)

### SQL Agent Setup (STABLE LOCAL IMPLEMENTATION)

The SQL agent now works out-of-the-box with local SQLite:

```bash
# Test SQL queries - database is created automatically with sample data
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_prompt": "What is the average math score for students?",
    "conversation_flow": "sql-manipulation-agent"
  }'
```

The SQL agent automatically creates a SQLite database with sample student performance data for testing.
