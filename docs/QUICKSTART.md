# ⚡ Quick Start Guide

Get Insight Ingenious up and running in 5 minutes!

## 🚀 Prerequisites

- ✅ Python 3.13+
- ✅ uv package manager  
- ✅ Azure OpenAI API credentials

## 📦 5-Minute Setup

### Step 1: Install & Initialize
```bash
# Navigate to your project directory
cd /path/to/your/project

# Install Ingenious library
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
# Test bike insights workflow
curl -X POST http://localhost:80/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_prompt": "{\"stores\": [{\"name\": \"Test Store\", \"location\": \"NSW\", \"bike_sales\": [{\"product_code\": \"TEST-001\", \"quantity_sold\": 2, \"sale_date\": \"2023-04-01\", \"year\": 2023, \"month\": \"April\", \"customer_review\": {\"rating\": 4.5, \"comment\": \"Great bike!\"}}], \"bike_stock\": []}], \"revision_id\": \"test-1\", \"identifier\": \"quickstart\"}",
    "conversation_flow": "bike_insights"
  }'
```

🎉 **That's it!** You should see a JSON response with analysis from multiple AI agents.

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
uv run ingen workflows bike_insights

# Quick server test
curl -s http://localhost:80/health || echo "Server not running"
```

---

## 📡 API Endpoints Quick Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/chat` | POST | Main chat/workflow endpoint |
| `/api/v1/workflow-status/{name}` | GET | Check workflow status |
| `/health` | GET | Server health check |
| `/docs` | GET | API documentation |

---

## 🎯 Available Workflows

### 🚴 bike_insights (Recommended for Testing)
**Purpose**: Comprehensive bike sales analysis  
**Requirements**: Azure OpenAI only  
**Input**: JSON with bike sales data  

### 🎯 classification_agent (Simple Test)
**Purpose**: Text classification and routing  
**Requirements**: Azure OpenAI only  
**Input**: Plain text  

### 🔍 knowledge_base_agent (Advanced)
**Purpose**: Knowledge base search  
**Requirements**: Azure OpenAI + Azure Search  

### 📊 sql_manipulation_agent (Advanced)  
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

# Use correct name (underscores, not hyphens)
"conversation_flow": "bike_insights"  # ✅
"conversation_flow": "bike-insights"  # ❌
```

### API returning errors?
```bash
# Check server logs in terminal
# Verify JSON format for bike_insights
# Test with classification_agent first (simpler)
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

- Start with `classification_agent` for simple testing
- Use `bike_insights` to see multi-agent coordination
- Check `uv run ingen status` when things break
- The minimal templates work better than full templates
- Environment variables override config file values
- Logs show detailed error messages

**Happy coding! 🎉**
