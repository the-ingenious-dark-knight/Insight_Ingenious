---
title: "📡 API Reference"
layout: single
permalink: /api/
sidebar:
  nav: "docs"
toc: true
toc_label: "API Sections"
toc_icon: "plug"
---

# API Reference

Complete API documentation for Insight Ingenious, including REST endpoints, workflow examples, and integration guides.

## 🚀 Getting Started with the API

The Insight Ingenious API provides powerful endpoints for creating and managing AI-powered conversation workflows programmatically.

### Base API Information
- **Base URL**: `http://localhost:8000` (default local development)
- **Content-Type**: `application/json`
- **Authentication**: API key-based (see configuration guide)

## 📚 API Documentation Sections

### [🔄 Workflow API](/api/workflows/)
Complete documentation for all available workflow endpoints, including:
- Bike insights and analysis
- Customer sentiment analysis
- Financial data processing
- Document analysis workflows

### 🛠️ Core API Endpoints

#### Health Check
```bash
GET /health
```
Returns the health status of the API service.

#### List Available Workflows
```bash
GET /workflows
```
Returns a list of all available workflow types and their configurations.

### 📋 Common API Patterns

#### Making API Requests
All API requests should include appropriate headers:

```bash
curl -X POST http://localhost:8000/api/workflow \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{"workflow_type": "bike_insights", "query": "Show me sales data"}'
```

#### Response Format
All API responses follow a consistent format:

```json
{
  "status": "success|error",
  "data": {
    // Response data
  },
  "message": "Human-readable message",
  "timestamp": "2025-07-04T12:00:00Z"
}
```

## 🔧 Integration Examples

### Python Integration
```python
import requests

def call_workflow_api(workflow_type, query, api_key):
    response = requests.post(
        "http://localhost:8000/api/workflow",
        json={
            "workflow_type": workflow_type,
            "query": query
        },
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    )
    return response.json()

# Example usage
result = call_workflow_api("bike_insights", "Show sales trends", "your-api-key")
```

### JavaScript Integration
```javascript
async function callWorkflowAPI(workflowType, query, apiKey) {
    const response = await fetch('http://localhost:8000/api/workflow', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${apiKey}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            workflow_type: workflowType,
            query: query
        })
    });
    
    return await response.json();
}

// Example usage
const result = await callWorkflowAPI('bike_insights', 'Show sales trends', 'your-api-key');
```

## 🔍 Error Handling

The API uses standard HTTP status codes and provides detailed error messages:

- `200 OK` - Successful request
- `400 Bad Request` - Invalid request parameters
- `401 Unauthorized` - Missing or invalid API key
- `404 Not Found` - Endpoint or resource not found
- `500 Internal Server Error` - Server-side error

Example error response:
```json
{
  "status": "error",
  "message": "Invalid workflow type specified",
  "error_code": "INVALID_WORKFLOW_TYPE",
  "timestamp": "2025-07-04T12:00:00Z"
}
```

## 📖 Additional Resources

- [🔄 Workflow API Documentation](/api/workflows/)
- [⚙️ Configuration Guide](/configuration/)
- [🛠️ Development Setup](/development/)
- [📝 CLI Reference](/CLI_REFERENCE/)

## 💡 Need Help?

- Check the [troubleshooting guide](/troubleshooting/)
- Review the [workflow examples](/api/workflows/)
- Open an issue on [GitHub](https://github.com/Insight-Services-APAC/Insight_Ingenious/issues)
