---
title: "Quick Start Guide"
layout: single
permalink: /getting-started/
sidebar:
  nav: "docs"
toc: true
toc_label: "Quick Start Steps"
toc_icon: "rocket"
---

## Quick Start

Get Insight Ingenious running in 5 minutes!

### Prerequisites
- Python 3.13+
- Azure OpenAI API credentials
- [uv package manager](https://docs.astral.sh/uv/)

### 1. Install and Initialize
```bash
uv add ingenious
uv run ingen init
```

### 2. Configure Azure OpenAI
```bash
cp .env.example .env
# Edit .env to add your Azure OpenAI credentials:
# AZURE_OPENAI_API_KEY=your-key-here
# AZURE_OPENAI_BASE_URL=https://your-resource.openai.azure.com/
```

### 3. Start the Server
```bash
uv run ingen validate  # Optional: verify configuration
uv run ingen serve
```

### 4. Test the API
```bash
curl http://localhost:8000/api/v1/health
```

That's it! The server is now running. The `ingen init` command creates a sample `bike-insights` workflow to get you started.

## Available Workflows

- **bike-insights** - Sample workflow created by `ingen init` for testing
- **classification-agent** - Routes input to specialized agents
- **knowledge-base-agent** - Searches knowledge bases (ChromaDB)
- **sql-manipulation-agent** - Executes SQL queries (SQLite)

> **Note**: Azure Search and Azure SQL integrations are experimental.

## Next Steps

- **[Installation Guide](./installation.md)** - Detailed installation options
- **[Configuration Guide](./configuration.md)** - Complete configuration reference
- **[Azure SQL Setup](../guides/sql-agent-setup.md)** - Production database setup
- **[API Integration](../guides/api-integration.md)** - Using the REST API

## Sample API Request

```bash
# Test the bike-insights workflow
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_prompt": "{\"stores\": [{\"name\": \"Test Store\", \"location\": \"NSW\", \"bike_sales\": [{\"product_code\": \"B-001\", \"quantity_sold\": 1, \"sale_date\": \"2024-01-15\", \"year\": 2024, \"month\": \"January\", \"customer_review\": {\"rating\": 5.0, \"comment\": \"Great bike!\"}}]}]}",
    "conversation_flow": "bike-insights"
  }'
```

For more examples and detailed API documentation, see the [API Integration Guide](../guides/api-integration.md).
