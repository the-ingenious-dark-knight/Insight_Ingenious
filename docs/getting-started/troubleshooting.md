---
title: "Quick Troubleshooting"
layout: single
permalink: /getting-started/troubleshooting/
sidebar:
  nav: "docs"
toc: true
toc_label: "Quick Fixes"
toc_icon: "tools"
---

# Troubleshooting Guide

Common issues and solutions when working with Insight Ingenious.

## Configuration Issues

### Azure OpenAI Problems

**Error: "Azure OpenAI API key not found"**

**Solution:**
1. Check your environment variables:
   ```bash
   # Make sure these are set in your .env file or environment
   echo $AZURE_OPENAI_API_KEY
   echo $AZURE_OPENAI_BASE_URL
   echo $AZURE_OPENAI_DEPLOYMENT
   ```

2. Verify configuration is loaded:
   ```bash
   uv run python -c "from ingenious.config.config import get_config; print(get_config())"
   ```

3. Test configuration loading:
   ```bash
   uv run python -c "import ingenious.config.config as config; print(config.get_config().models[0].api_key)"
   ```

**Error: "Invalid Azure OpenAI deployment"**

**Solution:**
- Ensure `AZURE_OPENAI_DEPLOYMENT` environment variable matches your Azure deployment name
- Verify API version is supported (use `2024-08-01-preview` or newer)
- Check your Azure OpenAI resource has the model deployed

### Environment Variables

**Error: "Config file not found"**

**Solution:**
```bash
# Make sure .env file exists and is loaded
ls -la .env

# Source the .env file if needed
source .env

# Verify key environment variables are set
env | grep INGENIOUS_
```

## Workflow Issues

### Workflow Not Available

**Error: "conversation_flow not set" or "Unknown workflow"**

**Solution:**
1. Check available workflows:
   ```bash
   uv run ingen workflows
   ```

2. Use exact workflow names in API calls:
   ```bash
   # Correct
   curl -X POST http://localhost:8000/api/v1/chat \
     -d '{"user_prompt": "Hello", "conversation_flow": "classification-agent"}'

   # Wrong
   curl -X POST http://localhost:8000/api/v1/chat \
     -d '{"user_prompt": "Hello", "conversation_flow": "classify"}'
   ```

### Workflow Configuration Missing

**Error: "Search service not configured"**

**Solution for `knowledge-base-agent` (Recommended - Local ChromaDB):**
No configuration needed! The knowledge-base-agent uses local ChromaDB by default.

1. Simply add documents to: `./.tmp/knowledge_base/`
2. Documents are automatically indexed in ChromaDB
3. Works immediately without external services

**Alternative: Azure Search (Experimental - May contain bugs):**
1. Add Azure Search environment variables:
   ```bash
   # .env
   INGENIOUS_AZURE_SEARCH_SERVICES__0__SERVICE=default
   INGENIOUS_AZURE_SEARCH_SERVICES__0__ENDPOINT=https://your-search-service.search.windows.net
   INGENIOUS_AZURE_SEARCH_SERVICES__0__KEY=your-search-api-key
   ```

**Error: "Database connection failed"**

**Solution for `sql-manipulation-agent` (Recommended - Local SQLite):**
```bash
# .env
INGENIOUS_AZURE_SQL_SERVICES__DATABASE_NAME=skip  # This enables local mode
INGENIOUS_LOCAL_SQL_DB__DATABASE_PATH=/tmp/sample_sql.db
INGENIOUS_LOCAL_SQL_DB__SAMPLE_CSV_PATH=./data/your_data.csv
```

**Alternative: Azure SQL (Experimental - May contain bugs):**
```bash
# .env
INGENIOUS_AZURE_SQL_SERVICES__DATABASE_CONNECTION_STRING="Server=tcp:yourserver.database.windows.net,1433;Database=yourdatabase;..."
```

## Server Issues

### Port Conflicts

**Error: "Port already in use"**

**Solution:**
1. Find what's using the port:
   ```bash
   lsof -i :8081
   ```

2. Kill the process or use a different port:
   ```bash
   # Use different port
   uv run ingen serve --port 8082
   ```

3. Or change the port with environment variable:
   ```bash
   # .env
   INGENIOUS_WEB_CONFIGURATION__PORT=8082
   ```

### Server Won't Start

**Error: "FastAPI startup failed"**

**Solution:**
1. Check configuration syntax:
   ```bash
   # Test environment configuration
   uv run python -c "from ingenious.config.config import get_config; print(get_config())"
   ```

2. Check logs for specific errors
3. Start with minimal configuration first

## API Issues

### Authentication Problems

**Error: "401 Unauthorized"**

**Solution:**
1. Check if authentication is enabled:
   ```bash
   # Check environment variable
   echo $INGENIOUS_WEB_CONFIGURATION__AUTHENTICATION__ENABLE
   ```

2. Use basic auth in requests:
   ```bash
   curl -X POST http://localhost:8000/api/v1/chat \
     -H "Authorization: Basic $(echo -n username:password | base64)" \
     -d '{"user_prompt": "Hello", "conversation_flow": "classification-agent"}'
   ```

3. Or disable authentication for testing:
   ```bash
   # .env
   INGENIOUS_WEB_CONFIGURATION__AUTHENTICATION__ENABLE=false
   ```

### Request Format Issues

**Error: "422 Validation Error"**

**Solution:**
Ensure correct JSON format:
```bash
# Correct format
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_prompt": "Your message here",
    "conversation_flow": "classification-agent",
    "thread_id": "optional-thread-id"
  }'
```

Required fields:
- `user_prompt`: Your message (string)
- `conversation_flow`: Workflow name (string)

Optional fields:
- `thread_id`: For conversation continuity
- `topic`: Additional context

## Testing & Debugging

### Check System Status

```bash
# 1. Check all workflow configurations
curl http://localhost:8000/api/v1/workflows

# 2. Check specific workflow
curl http://localhost:8000/api/v1/workflow-status/classification-agent

# 3. Check system diagnostics
curl http://localhost:8000/api/v1/diagnostic
```

### Enable Debug Logging

```bash
# .env
INGENIOUS_LOGGING__ROOT_LOG_LEVEL=debug
INGENIOUS_LOGGING__LOG_LEVEL=debug
```

### Test Individual Components

```bash
# Test configuration loading
uv run python -c "import ingenious.config.config as config; print(config.get_config())"

# Test Azure OpenAI connection
uv run python -c "
from ingenious.dependencies import get_openai_service
service = get_openai_service()
print('OpenAI service created successfully')
"
```

## Performance Issues

### Slow Response Times

**Solutions:**
1. Check Azure OpenAI quota and rate limits
2. Use smaller models for testing
3. Reduce conversation complexity
4. Check network connectivity to Azure

### Memory Issues

**Solutions:**
1. Clear temporary files:
   ```bash
   rm -rf .tmp/*
   ```

2. Restart the server periodically
3. Monitor memory usage

## Common Workflow Fixes

### Start Fresh

If things are broken, reset to a clean state:

```bash
# 1. Stop the server (Ctrl+C)

# 2. Clear temporary files
rm -rf .tmp/

# 3. Verify configuration
uv run ingen workflows

# 4. Test minimal workflow first
uv run ingen serve
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"user_prompt": "Hello", "conversation_flow": "classification-agent"}'
```

### Progressive Setup

1. **Start simple**: Get `classification-agent` working first
2. **Add complexity**: Then try `knowledge-base-agent`
3. **Debug incrementally**: Don't configure everything at once

## Getting Help

### Before Opening an Issue:

1. Check this troubleshooting guide
2. Review [Configuration Guide](/getting-started/configuration)
3. Test with minimal configuration
4. Check GitHub issues for similar problems

### When Opening an Issue:

Include:
- Your environment variables (redact sensitive data)
- Error messages and logs
- Steps to reproduce
- Operating system and Python version
- Output of `uv run ingen workflows`

### Quick Diagnostic Info:

```bash
# Gather diagnostic info
echo "=== System Info ==="
uv --version
python --version

echo "=== Configuration Status ==="
uv run ingen workflows

echo "=== Workflow Status ==="
curl -s http://localhost:8000/api/v1/workflows || echo "Server not running"
```

---

**Still stuck?** Join our community or open an issue on GitHub with the diagnostic information above.
