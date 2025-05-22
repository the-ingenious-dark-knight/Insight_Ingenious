# Configuration Guide

This document explains how to configure Insight Ingenious for your needs.

## Configuration Files

Insight Ingenious uses two main configuration files:

1. **config.yml** - Main application configuration
2. **profiles.yml** - Sensitive information like API keys

### Configuration Locations

- **config.yml**: By default, this file should be in your project's root directory
- **profiles.yml**: By default, this file is located at `~/.ingenious/profiles.yml`

### Environment Variables

You can override the config paths using environment variables:

- `INGENIOUS_PROJECT_PATH`: Path to your project's configuration file
- `INGENIOUS_PROFILE_PATH`: Path to your profiles configuration file
- `INGENIOUS_WORKING_DIR`: Working directory for the application

## Main Configuration (config.yml)

The `config.yml` file contains the main application settings:

```yaml
api_key: ""                    # Optional application API key
profile: "default"             # Profile to use from profiles.yml
log_level: "INFO"              # Logging level (DEBUG, INFO, WARNING, ERROR)

# Database configuration
database:
  type: "sqlite"               # Database type (sqlite, duckdb, cosmos)
  connection_string: "ingenious.db"

# File storage configuration
file_storage:
  type: "local"                # Storage type (local, azure_blob)
  base_path: "./storage"       # For local storage only

# ChainLit configuration
chainlit_configuration:
  enable: true                 # Enable/disable ChainLit UI
  theme: "light"               # UI theme (light, dark)

# Agent configurations
agents:
  - name: "general_assistant"  # Agent name
    model_config:
      model: "gpt-4o"          # Model to use
      temperature: 0.7         # Temperature for generation
      max_tokens: 2000         # Maximum tokens to generate
    system_prompt: "You are a helpful assistant."
  
  - name: "code_expert"        # Another agent
    model_config:
      model: "gpt-4o"
      temperature: 0.1
      max_tokens: 4000
    system_prompt: "You are an expert programmer."

# Conversation flows
conversation_flows:
  - name: "default"
    type: "basic"              # Flow type (basic, multi_agent, router)
    primary_agent: "general_assistant"

  - name: "programming_help"
    type: "basic"
    primary_agent: "code_expert"
```

## Profile Configuration (profiles.yml)

The `profiles.yml` file contains sensitive information like API keys:

```yaml
profiles:
  - name: "default"
    openai:
      api_key: "your_openai_api_key"
      organization: "your_organization_id"
    
    azure_openai:
      api_key: "your_azure_openai_key"
      api_base: "your_azure_openai_endpoint"
      api_version: "2023-12-01-preview"
    
    azure_storage:
      connection_string: "your_azure_storage_connection_string"
    
    azure_cosmos:
      endpoint: "your_cosmos_endpoint"
      key: "your_cosmos_key"
      database_name: "your_database_name"
```

## Configuration Options

### Database Configuration

Insight Ingenious supports multiple database backends:

#### SQLite
```yaml
database:
  type: "sqlite"
  connection_string: "ingenious.db"
```

#### DuckDB
```yaml
database:
  type: "duckdb"
  connection_string: "ingenious.duckdb"
```

#### Azure Cosmos DB
```yaml
database:
  type: "cosmos"
  database_name: "ingenious"
  container_name: "chat_history"
```

### File Storage Configuration

#### Local Storage
```yaml
file_storage:
  type: "local"
  base_path: "./storage"
```

#### Azure Blob Storage
```yaml
file_storage:
  type: "azure_blob"
  container_name: "ingenious-storage"
```

### Agent Configuration

Each agent can be configured with:

```yaml
agents:
  - name: "agent_name"
    model_config:
      model: "model_name"      # Model ID to use
      temperature: 0.7         # 0-1, higher means more random
      max_tokens: 2000         # Maximum tokens in response
      top_p: 1                 # Alternative to temperature
      frequency_penalty: 0     # -2.0 to 2.0, positive discourages repetition
      presence_penalty: 0      # -2.0 to 2.0, positive encourages new topics
    system_prompt: "Your system prompt here."
    tools: []                  # List of tools available to this agent
```

### Conversation Flow Types

#### Basic Flow
```yaml
conversation_flows:
  - name: "simple_conversation"
    type: "basic"
    primary_agent: "general_assistant"
```

#### Multi-Agent Flow
```yaml
conversation_flows:
  - name: "team_discussion"
    type: "multi_agent"
    agents: ["agent1", "agent2", "agent3"]
    coordinator: "agent1"      # Agent that coordinates the discussion
    max_turns: 10              # Maximum conversation turns
```

#### Router Flow
```yaml
conversation_flows:
  - name: "smart_router"
    type: "router"
    router_agent: "classifier" # Agent that decides routing
    target_flows: ["flow1", "flow2", "flow3"]
```

## Using Azure Key Vault

To use Azure Key Vault for secret management:

1. Set the `KEY_VAULT_NAME` environment variable:
   ```
   export KEY_VAULT_NAME=your-key-vault-name
   ```

2. Use the `get_kv_secret` function in your code:
   ```python
   from ingenious.config.config import get_kv_secret
   secret = get_kv_secret("secret-name")
   ```

## CLI Configuration

Several CLI commands help with configuration:

```bash
# Initialize a new project with default configuration
ingen_cli initialize-new-project

# Validate your configuration
ingen_cli validate-config --path ./config.yml

# Print the current configuration
ingen_cli show-config
```
