# 🚀 Ingenious API Workflow Documentation

This document provides detailed API usage examples for all available workflows in the Insight Ingenious framework.

## 📡 Base API Information

- **Base URL**: `http://localhost:80` (or your configured port)
- **Endpoint**: `POST /api/v1/chat`
- **Content-Type**: `application/json`

## 🔥 Available Workflows

### 1. 🚴 bike_insights - Bike Sales Analysis

**Purpose**: Multi-agent workflow for comprehensive bike sales data analysis

**Required Input Format**:
```json
{
  "user_prompt": "{\"stores\": [...], \"revision_id\": \"unique-id\", \"identifier\": \"identifier\"}",
  "conversation_flow": "bike_insights"
}
```

**Example Request**:
```bash
curl -X POST http://localhost:80/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_prompt": "{\"stores\": [{\"name\": \"Bike World Sydney\", \"location\": \"NSW\", \"bike_sales\": [{\"product_code\": \"EB-SPECIALIZED-2023-TV\", \"quantity_sold\": 3, \"sale_date\": \"2023-04-15\", \"year\": 2023, \"month\": \"April\", \"customer_review\": {\"rating\": 4.2, \"comment\": \"Great bike for commuting!\"}}], \"bike_stock\": []}], \"revision_id\": \"test-001\", \"identifier\": \"april-sales\"}",
    "conversation_flow": "bike_insights"
  }'
```

**Data Structure**:
```json
{
  "stores": [
    {
      "name": "Store Name",
      "location": "Location",
      "bike_sales": [
        {
          "product_code": "PRODUCT-CODE",
          "quantity_sold": 1,
          "sale_date": "YYYY-MM-DD",
          "year": 2023,
          "month": "Month Name",
          "customer_review": {
            "rating": 4.5,
            "comment": "Customer feedback"
          }
        }
      ],
      "bike_stock": []
    }
  ],
  "revision_id": "unique-revision-id",
  "identifier": "unique-identifier"
}
```

**Agents Involved**:
- 📊 **fiscal_analysis_agent**: Analyzes sales data and trends
- 💭 **customer_sentiment_agent**: Processes customer reviews and ratings  
- 🔍 **bike_lookup_agent**: Retrieves bike prices and specifications
- 📝 **summary**: Aggregates insights from all agents

**Response Format**:
```json
{
  "thread_id": "uuid",
  "message_id": "identifier",
  "agent_response": "[{agent1_response}, {agent2_response}, ...]",
  "token_count": 1234,
  "followup_questions": {},
  "topic": null,
  "memory_summary": "",
  "event_type": null
}
```

---

### 2. 🎯 classification_agent - Input Classification

**Purpose**: Routes user input to appropriate specialized agents based on content

**Required Input Format**:
```json
{
  "user_prompt": "Your question or input text here",
  "conversation_flow": "classification_agent"
}
```

**Example Request**:
```bash
curl -X POST http://localhost:80/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_prompt": "Analyze this customer feedback: The bike was excellent!",
    "conversation_flow": "classification_agent"
  }'
```

**Use Cases**:
- General text classification
- Routing complex queries to specialized agents
- Sentiment analysis of user input
- Topic categorization

---

### 3. 🔍 knowledge_base_agent - Knowledge Search

**Purpose**: Search and retrieve information from configured knowledge bases

**Requirements**: 
- Azure Search Service configured
- Knowledge base indexed

**Example Request**:
```bash
curl -X POST http://localhost:80/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_prompt": "Find information about bike maintenance",
    "conversation_flow": "knowledge_base_agent"
  }'
```

---

### 4. 📊 sql_manipulation_agent - Database Queries

**Purpose**: Execute SQL queries based on natural language input

**Requirements**:
- Database connection configured
- SQL database accessible

**Example Request**:
```bash
curl -X POST http://localhost:80/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_prompt": "Show me the top selling bikes in the last month",
    "conversation_flow": "sql_manipulation_agent"
  }'
```

---

## 🛠️ Testing Your Workflows

### Quick Test Script

Save this as `test_workflows.sh`:

```bash
#!/bin/bash

echo "🧪 Testing Ingenious Workflows..."

# Test 1: bike_insights
echo "📊 Testing bike_insights workflow..."
curl -s -X POST http://localhost:80/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_prompt": "{\"stores\": [{\"name\": \"Test Store\", \"location\": \"NSW\", \"bike_sales\": [{\"product_code\": \"TEST-001\", \"quantity_sold\": 2, \"sale_date\": \"2023-04-01\", \"year\": 2023, \"month\": \"April\", \"customer_review\": {\"rating\": 4.5, \"comment\": \"Great bike!\"}}], \"bike_stock\": []}], \"revision_id\": \"test-1\", \"identifier\": \"test\"}",
    "conversation_flow": "bike_insights"
  }' | jq '.message_id, .token_count'

# Test 2: classification_agent  
echo "🎯 Testing classification_agent workflow..."
curl -s -X POST http://localhost:80/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_prompt": "This is a test message for classification",
    "conversation_flow": "classification_agent"
  }' | jq '.message_id, .token_count'

echo "✅ Tests completed!"
```

Make it executable: `chmod +x test_workflows.sh`

---

## 🚨 Common Issues & Solutions

### 1. "Expecting value: line 1 column 1 (char 0)"
**Problem**: bike_insights workflow expects JSON data in user_prompt  
**Solution**: Ensure user_prompt contains properly escaped JSON string

### 2. "Class ConversationFlow not found"
**Problem**: Workflow name incorrect or workflow not available  
**Solution**: Use correct workflow names (underscores, not hyphens)

### 3. "Validation error in field"
**Problem**: Missing or invalid configuration  
**Solution**: Check profiles.yml and .env files for required values

### 4. Server runs on wrong port
**Problem**: Port parameter not working  
**Solution**: Check WEB_PORT environment variable or config.yml

---

## 🔧 Configuration Requirements

### Minimal Setup (bike_insights + classification_agent)
```env
AZURE_OPENAI_API_KEY=your-key
AZURE_OPENAI_BASE_URL=your-endpoint
INGENIOUS_PROJECT_PATH=./config.yml
INGENIOUS_PROFILE_PATH=./profiles.yml
```

### Advanced Setup (all workflows)
- Azure Search Service (knowledge_base_agent)
- Database connection (sql_manipulation_agent)
- Additional authentication settings

---

## 📚 Additional Resources

- 📖 **Configuration Guide**: `/docs/configuration/README.md`
- 🏗️ **Custom Workflows**: `/docs/extensions/README.md`  
- 🐛 **Troubleshooting**: `/docs/troubleshooting/README.md`
- 🧪 **Testing Guide**: `/docs/testing/README.md`

For more help: `ingen workflows <workflow-name>` or `ingen --help`
