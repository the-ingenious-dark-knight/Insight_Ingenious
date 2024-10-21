---

    weight: 4

---



This file contains the configuration settings for the application. The configuration file is written in YAML format. This file is designed to contain non-sensitive settings only. At run-time is is merged with the `profile.yml` information which contains the associated sensitive values. See the example below for a sample with detailed comments that explain the use of each configuration setting in the file.

```yaml
# Profile Configuration
profile: dev  # Defines the environment or profile for the deployment (e.g., dev, prod). NOTE this must match the profile in the profile.yml file

# Models Configuration
models: 
  - model: gpt-4-deployment  # Specifies the model being used (e.g., GPT-4 in Azure deployment)
    api_type: azure          # API type indicates that the deployment is through Azure
    api_version: 2024-02-01  # API version being used in the deployment

# Logging Configuration
logging: 
  root_log_level: debug  # Root logging level for overall logging output (can be debug, info, warning, error)
  log_level: debug       # Specific logging level for this application or service

# Chat History Configuration
chat_history:  
  database_type: sqlite  # Defines the type of database for storing chat history (e.g., sqlite or cosmos)
  database_path: tmp/high_level_logs.db  # Path to SQLite database file for storing chat logs (used only for SQLite)
  database_name: ToDoList  # Name of the database (used only for Cosmos DB, irrelevant for SQLite)
  memory_path: tmp         # Location for temporary memory or cache files (used by chroma db)

# Chat Service Configuration
chat_service:
  type: multi_agent  # Defines the type of chat service. Multi-agent implies multiple models or systems handling tasks

# Tool Service Configuration
tool_service:
  enable: false  # Tool service is disabled in this configuration (set to 'true' to enable)

# Azure Search Services Configuration
azure_search_services:
  - service: default    # Default Azure Search service configuration
    endpoint: https://search-demo-eli.search.windows.net  # Azure Search endpoint for queries

# Web Server Configuration
web_configuration:
  type: fastapi  # Framework being used for web services (currently only FastAPI is supported)
  ip_address: "0.0.0.0"  # IP address where the web service will be hosted (0.0.0.0 allows all incoming connections)
  port: 8000             # Port on which the service is exposed

# Authentication Configuration
authentication: 
  enable: true  # Authentication method for securing the service (set to 'false' to disable)
  type: basic    # Basic authentication type (can be expanded to other methods as needed)
```