---
title: "Workflow Requirements"
layout: single
permalink: /workflows/
sidebar:
  nav: "docs"
toc: true
toc_label: "Workflow Types"
toc_icon: "project-diagram"
---

# Workflow Configuration Requirements

This guide outlines the configuration requirements for each conversation workflow in Insight Ingenious. Understanding these requirements will help you determine what external services and configurations are needed for each workflow.

## Workflow Architecture Overview

```mermaid
graph TB
    subgraph "Workflow Types"
        CLASSIFICATION[Classification Agent<br/>Route to specialists]
        BIKE[Bike Insights<br/>Sales analysis]
        KNOWLEDGE[Knowledge Base<br/>Information retrieval]
        SQL[SQL Manipulation<br/>Database queries]
        DOCUMENT[Document Processing<br/>Text extraction]
    end

    subgraph "Configuration Levels"
        MINIMAL[Minimal Config<br/>Azure OpenAI only]
        SEARCH[+ Azure Search]
        DATABASE[+ Database]
        SERVICES[+ Document Services]
    end

    subgraph "External Dependencies"
        AZURE_OPENAI[Azure OpenAI]
        AZURE_SEARCH[Azure Cognitive Search]
        AZURE_SQL[Azure SQL Database]
        AZURE_DOC[Azure Document Intelligence]
    end

    CLASSIFICATION --> MINIMAL
    BIKE --> MINIMAL

    KNOWLEDGE --> SEARCH

    SQL --> DATABASE

    DOCUMENT --> SERVICES

    MINIMAL --> AZURE_OPENAI
    SEARCH --> AZURE_OPENAI
    SEARCH --> AZURE_SEARCH
    DATABASE --> AZURE_OPENAI
    DATABASE --> AZURE_SQL
    SERVICES --> AZURE_OPENAI
    SERVICES --> AZURE_DOC

    classDef workflow fill:#e3f2fd
    classDef config fill:#f1f8e9
    classDef external fill:#fff3e0

    class CLASSIFICATION,BIKE,KNOWLEDGE,SQL,DOCUMENT workflow
    class MINIMAL,SEARCH,DATABASE,SERVICES config
    class AZURE_OPENAI,AZURE_SEARCH,AZURE_SQL,AZURE_DOC external
```

## Detailed Workflow Flows

### 🚴 Bike Insights Workflow

```mermaid
sequenceDiagram
    participant User
    participant API
    participant Coordinator
    participant BikeAgent as 🚴 Bike Agent
    participant SentimentAgent as 😊 Sentiment Agent
    participant FiscalAgent as 💰 Fiscal Agent
    participant SummaryAgent as 📝 Summary Agent
    participant AzureOpenAI as 🧠 Azure OpenAI

    User->>API: "Analyze bike sales for Q2"
    API->>Coordinator: Initialize bike-insights workflow

    Note over Coordinator: Load bike sales data
    Coordinator->>BikeAgent: Analyze sales performance
    BikeAgent->>AzureOpenAI: Request sales analysis
    AzureOpenAI-->>BikeAgent: Sales metrics & trends

    par Parallel Analysis
        Coordinator->>SentimentAgent: Analyze customer feedback
        SentimentAgent->>AzureOpenAI: Sentiment analysis
        AzureOpenAI-->>SentimentAgent: Customer satisfaction scores
    and
        Coordinator->>FiscalAgent: Calculate financial impact
        FiscalAgent->>AzureOpenAI: Financial calculations
        AzureOpenAI-->>FiscalAgent: Revenue & profit analysis
    end

    Coordinator->>SummaryAgent: Compile comprehensive report
    SummaryAgent->>AzureOpenAI: Summarize findings
    AzureOpenAI-->>SummaryAgent: Executive summary

    SummaryAgent-->>Coordinator: Final report
    Coordinator-->>API: Complete analysis
    API-->>User: Comprehensive bike sales report
```

### 🔍 Classification Agent Workflow

```mermaid
flowchart TD
    START([👤 User Input]) --> CLASSIFY{🔍 Classify Intent}

    CLASSIFY -->|Sales Query| BIKE_FLOW[🚴 Bike Insights Flow]
    CLASSIFY -->|Technical Question| KNOWLEDGE_FLOW[📚 Knowledge Base Flow]
    CLASSIFY -->|Data Query| SQL_FLOW[🗄️ SQL Query Flow]
    CLASSIFY -->|Document Task| DOC_FLOW[📄 Document Processing Flow]
    CLASSIFY -->|General Chat| CHAT_FLOW[💬 General Chat Flow]

    BIKE_FLOW --> BIKE_AGENT[🚴 Bike Analysis Agent]
    KNOWLEDGE_FLOW --> KNOWLEDGE_AGENT[📚 Knowledge Agent]
    SQL_FLOW --> SQL_AGENT[🗄️ SQL Agent]
    DOC_FLOW --> DOC_AGENT[📄 Document Agent]
    CHAT_FLOW --> CHAT_AGENT[💬 Chat Agent]

    BIKE_AGENT --> RESPONSE[📤 Formatted Response]
    KNOWLEDGE_AGENT --> RESPONSE
    SQL_AGENT --> RESPONSE
    DOC_AGENT --> RESPONSE
    CHAT_AGENT --> RESPONSE

    RESPONSE --> FINISH([🏁 End])

    classDef start fill:#c8e6c9
    classDef decision fill:#fff9c4
    classDef workflow fill:#e1f5fe
    classDef agent fill:#f3e5f5
    classDef finish fill:#ffcdd2

    class START start
    class CLASSIFY decision
    class BIKE_FLOW,KNOWLEDGE_FLOW,SQL_FLOW,DOC_FLOW,CHAT_FLOW workflow
    class BIKE_AGENT,KNOWLEDGE_AGENT,SQL_AGENT,DOC_AGENT,CHAT_AGENT agent
    class RESPONSE,FINISH finish
```

### � Knowledge Base Workflow

```mermaid
graph TB
    subgraph "📝 Input Processing"
        USER_QUERY[👤 User Query]
        INTENT_ANALYSIS[🔍 Intent Analysis]
        QUERY_ENHANCEMENT[✨ Query Enhancement]
    end

    subgraph "🔍 Search & Retrieval"
        AZURE_SEARCH[🔍 Azure Cognitive Search]
        VECTOR_SEARCH[🎯 Vector Search]
        KEYWORD_SEARCH[🔤 Keyword Search]
        HYBRID_SEARCH[🔀 Hybrid Search]
    end

    subgraph "📊 Content Processing"
        RELEVANCE_SCORING[📊 Relevance Scoring]
        CONTENT_RANKING[📈 Content Ranking]
        CONTEXT_EXTRACTION[📋 Context Extraction]
    end

    subgraph "🧠 AI Processing"
        AZURE_OPENAI[🧠 Azure OpenAI]
        CONTEXT_SYNTHESIS[🔗 Context Synthesis]
        RESPONSE_GENERATION[📝 Response Generation]
    end

    USER_QUERY --> INTENT_ANALYSIS
    INTENT_ANALYSIS --> QUERY_ENHANCEMENT
    QUERY_ENHANCEMENT --> AZURE_SEARCH

    AZURE_SEARCH --> VECTOR_SEARCH
    AZURE_SEARCH --> KEYWORD_SEARCH
    AZURE_SEARCH --> HYBRID_SEARCH

    VECTOR_SEARCH --> RELEVANCE_SCORING
    KEYWORD_SEARCH --> RELEVANCE_SCORING
    HYBRID_SEARCH --> RELEVANCE_SCORING

    RELEVANCE_SCORING --> CONTENT_RANKING
    CONTENT_RANKING --> CONTEXT_EXTRACTION
    CONTEXT_EXTRACTION --> AZURE_OPENAI

    AZURE_OPENAI --> CONTEXT_SYNTHESIS
    CONTEXT_SYNTHESIS --> RESPONSE_GENERATION

    classDef input fill:#e8f5e8
    classDef search fill:#fff3e0
    classDef processing fill:#e3f2fd
    classDef ai fill:#fce4ec

    class USER_QUERY,INTENT_ANALYSIS,QUERY_ENHANCEMENT input
    class AZURE_SEARCH,VECTOR_SEARCH,KEYWORD_SEARCH,HYBRID_SEARCH search
    class RELEVANCE_SCORING,CONTENT_RANKING,CONTEXT_EXTRACTION processing
    class AZURE_OPENAI,CONTEXT_SYNTHESIS,RESPONSE_GENERATION ai
```

### �️ SQL Manipulation Workflow

```mermaid
sequenceDiagram
    participant User
    participant SQLAgent
    participant AzureOpenAI
    participant Database

    User->>SQLAgent: "Show me sales by region"
    SQLAgent->>AzureOpenAI: Convert natural language to SQL
    AzureOpenAI-->>SQLAgent: Generated SQL query

    SQLAgent->>Database: Execute SQL query
    Note over Database: Supports both:<br/>- Azure SQL Database<br/>- Local SQLite
    Database-->>SQLAgent: Query results

    SQLAgent->>AzureOpenAI: Format results for user
    AzureOpenAI-->>SQLAgent: Natural language response

    SQLAgent-->>User: "Sales by region analysis"

    Note over SQLAgent,Database: Configuration determines:<br/>- Azure SQL vs SQLite<br/>- Database connection details<br/>- Query timeout settings
```

### 📄 Document Processing Workflow

```mermaid
graph TB
    subgraph "📁 Document Input"
        UPLOAD[📤 File Upload]
        VALIDATION[✅ File Validation]
        FORMAT_CHECK[📋 Format Check]
    end

    subgraph "🔍 Document Analysis"
        AZURE_DOC_INTEL[📄 Azure Document Intelligence]
        OCR[👁️ OCR Processing]
        LAYOUT_ANALYSIS[📐 Layout Analysis]
        TEXT_EXTRACTION[📝 Text Extraction]
    end

    subgraph "🧠 Content Processing"
        AZURE_OPENAI[🧠 Azure OpenAI]
        CONTENT_ANALYSIS[📊 Content Analysis]
        ENTITY_EXTRACTION[🏷️ Entity Extraction]
        SUMMARIZATION[📋 Summarization]
    end

    subgraph "💾 Output Generation"
        STRUCTURED_DATA[📊 Structured Data]
        INSIGHTS[💡 Key Insights]
        FORMATTED_RESPONSE[📝 Formatted Response]
    end

    UPLOAD --> VALIDATION
    VALIDATION --> FORMAT_CHECK
    FORMAT_CHECK --> AZURE_DOC_INTEL

    AZURE_DOC_INTEL --> OCR
    AZURE_DOC_INTEL --> LAYOUT_ANALYSIS
    AZURE_DOC_INTEL --> TEXT_EXTRACTION

    TEXT_EXTRACTION --> AZURE_OPENAI
    AZURE_OPENAI --> CONTENT_ANALYSIS
    AZURE_OPENAI --> ENTITY_EXTRACTION
    AZURE_OPENAI --> SUMMARIZATION

    CONTENT_ANALYSIS --> STRUCTURED_DATA
    ENTITY_EXTRACTION --> INSIGHTS
    SUMMARIZATION --> FORMATTED_RESPONSE

    classDef input fill:#e8f5e8
    classDef analysis fill:#fff3e0
    classDef processing fill:#e3f2fd
    classDef output fill:#fce4ec

    class UPLOAD,VALIDATION,FORMAT_CHECK input
    class AZURE_DOC_INTEL,OCR,LAYOUT_ANALYSIS,TEXT_EXTRACTION analysis
    class AZURE_OPENAI,CONTENT_ANALYSIS,ENTITY_EXTRACTION,SUMMARIZATION processing
    class STRUCTURED_DATA,INSIGHTS,FORMATTED_RESPONSE output
```

## Configuration Requirements by Workflow

### ✅ Minimal Configuration Workflows

These workflows only require basic Azure OpenAI configuration:

## Configuration Requirements by Workflow

### ✅ Minimal Configuration Workflows

These workflows only require basic Azure OpenAI configuration:

#### 🔍 Classification Agent
Routes input to specialized agents based on content analysis.

```mermaid
graph LR
    subgraph "Required Services"
        AZURE_OPENAI[🧠 Azure OpenAI<br/>Intent Classification]
    end

    subgraph "Configuration Files"
        CONFIG[📄 config.yml<br/>Model Settings]
        PROFILES[🔐 profiles.yml<br/>API Keys]
    end

    CONFIG --> AZURE_OPENAI
    PROFILES --> AZURE_OPENAI

    classDef service fill:#e3f2fd
    classDef config fill:#f1f8e9

    class AZURE_OPENAI service
    class CONFIG,PROFILES config
```

**Required Configuration:**
```yaml
# config.yml
profile: dev
models:
  - model: "gpt-4.1-nano"
    api_type: azure
    api_version: "2024-12-01-preview"

# profiles.yml
dev:
  azure_openai:
    endpoint: "https://your-resource.cognitiveservices.azure.com/"
    api_key: "your-api-key"
```

#### 🚴 Bike Insights
Sample domain-specific workflow for bike sales analysis.

```mermaid
graph TB
    subgraph "Required Services"
        AZURE_OPENAI[🧠 Azure OpenAI<br/>Multi-Agent Processing]
    end

    subgraph "Sample Data"
        BIKE_DATA[🚴 Bike Sales Data<br/>JSON Sample Files]
    end

    subgraph "Agent Coordination"
        BIKE_AGENT[🚴 Bike Analysis Agent]
        SENTIMENT_AGENT[😊 Sentiment Agent]
        FISCAL_AGENT[💰 Fiscal Agent]
        SUMMARY_AGENT[📝 Summary Agent]
    end

    AZURE_OPENAI --> BIKE_AGENT
    AZURE_OPENAI --> SENTIMENT_AGENT
    AZURE_OPENAI --> FISCAL_AGENT
    AZURE_OPENAI --> SUMMARY_AGENT

    BIKE_DATA --> BIKE_AGENT

    classDef service fill:#e3f2fd
    classDef data fill:#f1f8e9
    classDef agent fill:#fff3e0

    class AZURE_OPENAI service
    class BIKE_DATA data
    class BIKE_AGENT,SENTIMENT_AGENT,FISCAL_AGENT,SUMMARY_AGENT agent
```

### 🔍 Azure Search Required Workflows

#### 📚 Knowledge Base Agent
Search and retrieve information from knowledge bases.

```mermaid
graph TB
    subgraph "Required Services"
        AZURE_OPENAI[🧠 Azure OpenAI<br/>Response Generation]
        AZURE_SEARCH[🔍 Azure Cognitive Search<br/>Document Retrieval]
    end

    subgraph "Knowledge Sources"
        DOCUMENTS[📄 Documents<br/>PDFs, Word, Text]
        WEBSITES[🌐 Web Content<br/>Scraped Pages]
        DATABASES[🗄️ Structured Data<br/>FAQ, Knowledge Base]
    end

    subgraph "Search Capabilities"
        VECTOR_SEARCH[🎯 Vector Search<br/>Semantic Similarity]
        KEYWORD_SEARCH[🔤 Keyword Search<br/>Full-Text Search]
        HYBRID_SEARCH[🔀 Hybrid Search<br/>Combined Approach]
    end

    DOCUMENTS --> AZURE_SEARCH
    WEBSITES --> AZURE_SEARCH
    DATABASES --> AZURE_SEARCH

    AZURE_SEARCH --> VECTOR_SEARCH
    AZURE_SEARCH --> KEYWORD_SEARCH
    AZURE_SEARCH --> HYBRID_SEARCH

    VECTOR_SEARCH --> AZURE_OPENAI
    KEYWORD_SEARCH --> AZURE_OPENAI
    HYBRID_SEARCH --> AZURE_OPENAI

    classDef service fill:#e3f2fd
    classDef source fill:#f1f8e9
    classDef search fill:#fff3e0

    class AZURE_OPENAI,AZURE_SEARCH service
    class DOCUMENTS,WEBSITES,DATABASES source
    class VECTOR_SEARCH,KEYWORD_SEARCH,HYBRID_SEARCH search
```

**Additional Configuration Required:**
```yaml
# config.yml (additional)
azure_search:
  service_name: "your-search-service"
  index_name: "your-knowledge-index"
  api_version: "2023-11-01"

# profiles.yml (additional)
dev:
  azure_search:
    api_key: "your-search-api-key"
```

### 📊 Database Required Workflows

#### 🗄️ SQL Manipulation Agent
Execute SQL queries on Azure SQL or local databases.

```mermaid
graph TB
    subgraph "Required Services"
        AZURE_OPENAI[🧠 Azure OpenAI<br/>Query Generation & Formatting]
        DATABASE[🗄️ Database<br/>SQL Server, PostgreSQL, MySQL]
    end

    subgraph "Security Layer"
        QUERY_VALIDATOR[✅ Query Validator<br/>SQL Injection Prevention]
        PERMISSION_CHECK[🔐 Permission Check<br/>Table Access Control]
        OPERATION_FILTER[🛡️ Operation Filter<br/>Read-Only Enforcement]
    end

    subgraph "Query Processing"
        NL_TO_SQL[🔄 Natural Language to SQL]
        RESULT_FORMATTER[📊 Result Formatter]
        ERROR_HANDLER[⚠️ Error Handler]
    end

    AZURE_OPENAI --> NL_TO_SQL
    NL_TO_SQL --> QUERY_VALIDATOR
    QUERY_VALIDATOR --> PERMISSION_CHECK
    PERMISSION_CHECK --> OPERATION_FILTER
    OPERATION_FILTER --> DATABASE
    DATABASE --> RESULT_FORMATTER
    RESULT_FORMATTER --> AZURE_OPENAI

    classDef service fill:#e3f2fd
    classDef security fill:#ffcdd2
    classDef processing fill:#f1f8e9

    class AZURE_OPENAI,DATABASE service
    class QUERY_VALIDATOR,PERMISSION_CHECK,OPERATION_FILTER security
    class NL_TO_SQL,RESULT_FORMATTER,ERROR_HANDLER processing
```

**Additional Configuration Required:**
```yaml
# config.yml (additional)
database:
  type: "azure_sql"  # or "postgresql", "mysql", "sqlite"
  server: "your-server.database.windows.net"
  database: "your-database-name"
  driver: "ODBC Driver 18 for SQL Server"

# profiles.yml (additional)
dev:
  database:
    username: "your-username"
    password: "your-password"
    # Or use connection string:
    # connection_string: "your-full-connection-string"
```

### 📄 Document Processing Workflows

#### 📄 Document Processing Agent
Extract text from PDFs, DOCX, images using OCR.

```mermaid
graph TB
    subgraph "Required Services"
        AZURE_OPENAI[🧠 Azure OpenAI<br/>Content Analysis]
        AZURE_DOC_INTEL[📄 Azure Document Intelligence<br/>OCR & Text Extraction]
    end

    subgraph "Supported Formats"
        PDF[📕 PDF Files<br/>Text & Scanned]
        DOCX[📄 Word Documents<br/>DOCX Format]
        IMAGES[🖼️ Images<br/>PNG, JPG, TIFF]
        FORMS[📋 Forms<br/>Structured Documents]
    end

    subgraph "Processing Pipeline"
        UPLOAD[📤 File Upload]
        FORMAT_DETECTION[🔍 Format Detection]
        OCR_PROCESSING[👁️ OCR Processing]
        LAYOUT_ANALYSIS[📐 Layout Analysis]
        TEXT_EXTRACTION[📝 Text Extraction]
        CONTENT_ANALYSIS[📊 Content Analysis]
    end

    PDF --> UPLOAD
    DOCX --> UPLOAD
    IMAGES --> UPLOAD
    FORMS --> UPLOAD

    UPLOAD --> FORMAT_DETECTION
    FORMAT_DETECTION --> AZURE_DOC_INTEL
    AZURE_DOC_INTEL --> OCR_PROCESSING
    AZURE_DOC_INTEL --> LAYOUT_ANALYSIS
    AZURE_DOC_INTEL --> TEXT_EXTRACTION
    TEXT_EXTRACTION --> AZURE_OPENAI
    AZURE_OPENAI --> CONTENT_ANALYSIS

    classDef service fill:#e3f2fd
    classDef format fill:#f1f8e9
    classDef processing fill:#fff3e0

    class AZURE_OPENAI,AZURE_DOC_INTEL service
    class PDF,DOCX,IMAGES,FORMS format
    class UPLOAD,FORMAT_DETECTION,OCR_PROCESSING,LAYOUT_ANALYSIS,TEXT_EXTRACTION,CONTENT_ANALYSIS processing
```

**Additional Configuration Required:**
```yaml
# config.yml (additional)
document_intelligence:
  endpoint: "https://your-doc-intel.cognitiveservices.azure.com/"
  api_version: "2023-07-31"

# profiles.yml (additional)
dev:
  document_intelligence:
    api_key: "your-document-intelligence-api-key"
```

## Workflow Selection Guide

### 🎯 Choosing the Right Workflow

```mermaid
flowchart TD
    START([🤔 What do you want to do?]) --> DECISION{Choose your use case}

    DECISION -->|Route user queries<br/>to different specialists| CLASSIFICATION[🔍 Classification Agent]
    DECISION -->|Analyze business data<br/>with multiple perspectives| BIKE_INSIGHTS[🚴 Bike Insights]
    DECISION -->|Search through<br/>documents and knowledge| KNOWLEDGE[📚 Knowledge Base Agent]
    DECISION -->|Query databases<br/>with natural language| SQL[🗄️ SQL Manipulation]
    DECISION -->|Extract text from<br/>documents and images| DOCUMENT[📄 Document Processing]

    CLASSIFICATION --> SETUP_MINIMAL[⚙️ Minimal Setup<br/>Azure OpenAI only]
    BIKE_INSIGHTS --> SETUP_MINIMAL

    KNOWLEDGE --> SETUP_SEARCH[🔍 Search Setup<br/>+ Azure Cognitive Search]

    SQL --> SETUP_DATABASE[🗄️ Database Setup<br/>+ Database Connection]

    DOCUMENT --> SETUP_SERVICES[📄 Full Services Setup<br/>+ Document Intelligence]

    SETUP_MINIMAL --> READY[✅ Ready to Use]
    SETUP_SEARCH --> READY
    SETUP_DATABASE --> READY
    SETUP_SERVICES --> READY

    classDef start fill:#c8e6c9
    classDef decision fill:#fff9c4
    classDef workflow fill:#e1f5fe
    classDef setup fill:#f3e5f5
    classDef ready fill:#dcedc8

    class START start
    class DECISION decision
    class CLASSIFICATION,BIKE_INSIGHTS,KNOWLEDGE,SQL,DOCUMENT workflow
    class SETUP_MINIMAL,SETUP_SEARCH,SETUP_DATABASE,SETUP_SERVICES setup
    class READY ready
```

## Next Steps

1. **📖 Choose Your Workflow**: Select the workflow that best fits your use case
2. **⚙️ Configure Services**: Set up the required Azure services and configuration
3. **🧪 Test Setup**: Validate your configuration with sample queries
4. **🚀 Deploy**: Launch your workflow in your preferred environment
5. **📊 Monitor**: Track performance and optimize as needed

For detailed setup instructions, see:
- [Configuration Guide](/configuration/) - Complete setup instructions
- [Getting Started](/getting-started/) - Quick start tutorial
- [Development Guide](/development/) - Advanced customization
- [API Documentation](/api/) - Integration details
  database_path: "./.tmp/high_level_logs.db"
  memory_path: "./.tmp"
```

#### profiles.yml
```yaml
- name: "dev"
  models:
    - model: "gpt-4.1-nano"  # Must match config.yml
      api_key: "your-azure-openai-api-key"
      base_url: "https://your-endpoint.openai.azure.com/openai/deployments/gpt-4.1-nano/chat/completions?api-version=2024-08-01-preview"
      deployment: "gpt-4.1-nano"  # Your deployment name
```

---

### knowledge-base-agent (Azure Search Required)

**Purpose**: Search and retrieve information from Azure Cognitive Search indexes

**Additional Configuration Required**:

#### config.yml
```yaml
azure_search_services:
  - service: "default"
    endpoint: "https://your-search-service.search.windows.net"
```

#### profiles.yml
```yaml
azure_search_services:
  - service: "default"
    key: "your-azure-search-api-key"
```

**What you need to provide**:
- Azure Cognitive Search service endpoint
- Azure Cognitive Search API key
- Pre-configured search indexes (referenced in the workflow as 'index-document-set-1', 'index-document-set-2')

**Without this configuration**: The workflow will fail when trying to search knowledge bases.

---

### sql-manipulation-agent (Database Required)

**Purpose**: Execute SQL queries based on natural language input

**Configuration Options**:

#### Option 1: Local SQLite Database
```yaml
# config.yml
local_sql_db:
  database_path: "/tmp/sample_sql.db"
  sample_csv_path: "./ingenious/sample_dataset/cleaned_students_performance.csv"
  sample_database_name: "sample_data"

azure_sql_services:
  database_name: "skip"  # Use "skip" to enable local mode
```

#### Option 2: Azure SQL Database
```yaml
# config.yml
azure_sql_services:
  database_name: "your_database"
  table_name: "your_table"
```

```yaml
# profiles.yml
azure_sql_services:
  database_connection_string: "Server=tcp:yourserver.database.windows.net,1433;Database=yourdatabase;User ID=yourusername;Password=yourpassword;Encrypt=true;TrustServerCertificate=false;Connection Timeout=30;"
```

**What you need to provide**:
- For local: CSV file or SQLite database
- For Azure: Azure SQL connection string with proper credentials

**Without this configuration**: The workflow will fail when trying to execute SQL queries.

---

### classification-agent (Minimal Configuration)

**Purpose**: Classify user input and route to appropriate topic agents

**Configuration Required**: Only basic Azure OpenAI configuration (see "All Workflows" section above)

**What you need to provide**: Just Azure OpenAI credentials

**Without this configuration**: Will not work - requires Azure OpenAI for classification logic.

---

### bike-insights (Minimal Configuration)

**Purpose**: Sample domain-specific workflow for bike sales analysis

**Configuration Required**: Only basic Azure OpenAI configuration (see "All Workflows" section above)

**What you need to provide**: Just Azure OpenAI credentials

**Without this configuration**: Will not work - requires Azure OpenAI for analysis.

---

### document-processing (Optional Azure Services)

**Purpose**: Extract text from PDFs, DOCX, images using various engines

**Configuration Options**:

#### Basic (No external services)
Works with local engines: pymupdf, pdfminer, unstructured

#### Advanced OCR (Azure Document Intelligence)
For better OCR and semantic extraction:

**Environment Variables Required**:
```bash
export AZURE_DOC_INTEL_ENDPOINT="https://your-resource.cognitiveservices.azure.com"
export AZURE_DOC_INTEL_KEY="your-api-key"
```

**What you need to provide**:
- Azure Document Intelligence service endpoint
- Azure Document Intelligence API key

**Without this configuration**: Falls back to local extraction engines (limited OCR capabilities).

## Quick Start Guide

### 1. Minimal Setup (classification-agent, bike-insights)
1. Configure Azure OpenAI in `config.yml` and `profiles.yml`
2. Run: `uv run ingen run-rest-api-server`
3. Test with classification-agent or bike-insights workflows

### 2. Knowledge Base Setup (knowledge-base-agent)
1. Complete minimal setup above
2. Set up Azure Cognitive Search service
3. Create and populate search indexes
4. Add Azure Search configuration to config files
5. Test with knowledge-base-agent workflow

### 3. Database Setup (sql-manipulation-agent)
1. Complete minimal setup above
2. Choose local SQLite or Azure SQL
3. Configure database connection
4. Prepare data (CSV for local, tables for Azure SQL)
5. Test with sql-manipulation-agent workflow

### 4. Full Setup (All workflows)
1. Complete all setup steps above
2. Optionally configure Azure Document Intelligence
3. Test all workflows

## Testing Configuration

Use these commands to test specific workflows:

```bash
# Test basic configuration
curl -X POST http://localhost:8081/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"user_prompt": "Hello", "conversation_flow": "classification_agent"}'

# Test knowledge base (requires Azure Search)
curl -X POST http://localhost:8081/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"user_prompt": "Search for health information", "conversation_flow": "knowledge_base_agent"}'

# Test SQL queries (requires database)
curl -X POST http://localhost:8081/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"user_prompt": "Show me student performance data", "conversation_flow": "sql_manipulation_agent"}'
```

## Troubleshooting

### Common Issues

1. **"Azure OpenAI API key not found"**
   - Check profiles.yml has correct API key
   - Verify INGENIOUS_PROFILE_PATH environment variable

2. **"Search service not configured"**
   - Add Azure Search configuration to config.yml and profiles.yml
   - Verify search service endpoint and API key

3. **"Database connection failed"**
   - Check connection string in profiles.yml
   - Verify database exists and is accessible
   - For local SQLite, check file path and permissions

4. **"Document processing failed"**
   - For Azure: Check AZURE_DOC_INTEL_ENDPOINT and AZURE_DOC_INTEL_KEY
   - For local: Install required optional dependencies

### Getting Help

1. Check logs for specific error messages
2. Verify configuration files against templates
3. Test connection to external services independently
4. Review the [Configuration Guide](../configuration/README.md) for detailed setup instructions
