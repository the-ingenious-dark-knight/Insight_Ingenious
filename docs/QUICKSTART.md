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

### Step 1: Install & Initialize
```bash
# Navigate to your project directory
cd /path/to/your/project

# Install Ingenious library for enterprise AI agent APIs
uv pip install -e ./Insight_Ingenious

# Initialize project structure
uv run ingen init
```

### Step 2: Configure Credentials
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your Azure OpenAI credentials
nano .env
```

Add these required values to `.env`:
```env
AZURE_OPENAI_API_KEY=your-azure-openai-api-key-here
AZURE_OPENAI_BASE_URL=https://your-endpoint.cognitiveservices.azure.com/
```

### Step 3: Set Environment Variables
```bash
export INGENIOUS_PROJECT_PATH=$(pwd)/config.yml
export INGENIOUS_PROFILE_PATH=$(pwd)/profiles.yml
```

### Step 4: Start the Server
```bash
uv run ingen serve
```

### Step 5: Test the API
```bash
# Test bike insights workflow (the "Hello World" of Ingenious!)
curl -X POST http://localhost:80/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_prompt": "{\"stores\": [{\"name\": \"QuickStart Store\", \"location\": \"NSW\", \"bike_sales\": [{\"product_code\": \"QS-001\", \"quantity_sold\": 1, \"sale_date\": \"2023-04-15\", \"year\": 2023, \"month\": \"April\", \"customer_review\": {\"rating\": 5.0, \"comment\": \"Perfect bike for getting started!\"}}], \"bike_stock\": []}], \"revision_id\": \"quickstart-1\", \"identifier\": \"hello-world\"}",
    "conversation_flow": "bike-insights"
  }'
```

🎉 **That's it!** You should see a comprehensive JSON response with analysis from multiple AI agents - this showcases the multi-agent coordination that makes Ingenious powerful!

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
curl -X POST http://localhost:80/api/v1/chat \
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
uv pip install -e ./Insight_Ingenious
uv run ingen init

# Set environment variables
export INGENIOUS_PROJECT_PATH=$(pwd)/config.yml
export INGENIOUS_PROFILE_PATH=$(pwd)/profiles.yml

echo "✅ Setup complete!"
echo "📝 Next: Edit .env with your Azure OpenAI credentials"
echo "🚀 Then run: uv run ingen serve"
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
curl -s http://localhost:80/api/v1/health || echo "Server not running"
```

---

## 📡 API Endpoints Quick Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/chat` | POST | Main chat/workflow endpoint |
| `/api/v1/workflow-status/{name}` | GET | Check workflow status |
| `/api/v1/health` | GET | Server health check |
| `/docs` | GET | API documentation |

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

# Try different port
uv run ingen serve --port 8081

# Check logs for errors
uv run ingen serve 2>&1 | grep -i error
```

### Profile validation errors?
```bash
# Use minimal template
cp Insight_Ingenious/ingenious/ingenious_extensions_template/profiles.minimal.yml ./profiles.yml

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
2. **🔧 Customize workflows**: Edit templates in `ingenious_extensions/`
3. **🧪 Create your own agents**: Follow patterns in existing workflows
4. **🚀 Deploy to production**: See deployment guides

---

## 💡 Pro Tips

- **Start with `bike-insights`** - it's the "Hello World" that shows off Ingenious's power
- Use `classification-agent` only if you want something simpler
- Check `uv run ingen status` when things break
- The minimal templates work better than full templates
- Environment variables override config file values
- Logs show detailed error messages

**Happy coding! 🎉**
