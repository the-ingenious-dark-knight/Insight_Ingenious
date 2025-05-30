# Configuration Guide

This guide explains how to configure the Insight Ingenious application using YAML files and environment variables.

## Overview

The application uses a combination of:
- A YAML configuration file (`config.yaml` by default)
- Environment variables (typically in a `.env` file)

This approach provides flexibility while keeping configuration simple and readable.

## Configuration File Structure

The main configuration file (`config.yaml`) has the following structure:

```yaml
app:
  name: "AutoGen FastAPI Template"
  version: "1.0.0"
  debug: false

server:
  host: "0.0.0.0"
  port: 8000

auth:
  enabled: true
  # Username and password are loaded from environment variables:
  # AUTH_USERNAME and AUTH_PASSWORD

models:
  default_llm:
    model: "gpt-4.1-mini"
    temperature: 0.7
    max_tokens: 1000
    # API key, base_url, and api_version are loaded from environment variables

agents:
  # List of agent types to create by default
  enabled:
    - "chat"
    - "research"
    - "sql"
  
  # Optional configurations for specific agent types
  configs:
    chat:
      system_message: "You are a helpful AI assistant. Provide clear, concise, and accurate responses."
    
    research:
      system_message: "You are a research assistant. Help users find and analyze information from reliable sources."
    
    sql:
      database_path: "sample.db"  # Will create a sample SQLite database
      system_message: "You are a SQL expert. Help users write queries and analyze data safely."

logging:
  level: "INFO"
  format: "json"  # or "simple" for human-readable logs
```

## Environment Variables

Some configuration values should be stored as environment variables for security reasons:

### Required Environment Variables

For Azure OpenAI:
```
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_API_VERSION=2023-05-15
```

For authentication (if enabled):
```
AUTH_USERNAME=admin
AUTH_PASSWORD=your-secure-password
```

### Optional Environment Variables

```
APP_DEBUG=true       # Override debug mode
SERVER_PORT=9000     # Override server port
LOG_LEVEL=DEBUG      # Override logging level
```

## Using a Custom Configuration File

You can specify a custom configuration file when starting the application:

```bash
uv run python main.py --config custom.yaml
```

## Overriding Configuration at Runtime

The application loads configuration in this order, with later sources overriding earlier ones:

1. Default values in code
2. YAML configuration file
3. Environment variables

This means you can override any configuration value using environment variables.

## Configuration Sections

### App Configuration

Controls basic application settings:

```yaml
app:
  name: "My Application"    # Application name
  version: "1.0.0"          # Version number
  debug: false              # Debug mode
```

### Server Configuration

Controls the HTTP server:

```yaml
server:
  host: "0.0.0.0"    # Bind address
  port: 8000         # Port number
```

### Authentication Configuration

Controls API authentication:

```yaml
auth:
  enabled: true      # Enable/disable authentication
  # Credentials are loaded from environment variables
```

### Models Configuration

Configures the AI models:

```yaml
models:
  default_llm:
    model: "gpt-4.1-mini"     # Model name (must match your Azure OpenAI deployment)
    temperature: 0.7          # Response randomness (0.0-1.0)
    max_tokens: 1000          # Maximum tokens in response
```

### Agents Configuration

Configures which agents are available and their behavior:

```yaml
agents:
  enabled:
    - "chat"           # Enable the chat agent
    - "research"       # Enable the research agent
  
  configs:
    chat:
      system_message: "Custom system message for the chat agent"
```

### Logging Configuration

Controls logging behavior:

```yaml
logging:
  level: "INFO"        # Log level (DEBUG, INFO, WARNING, ERROR)
  format: "json"       # Log format (json or simple)
```

## Advanced Configuration

### Creating Environment-Specific Configurations

You can create multiple configuration files for different environments:

- `config.yaml` - Default configuration
- `config.dev.yaml` - Development configuration
- `config.prod.yaml` - Production configuration

### Configuration in Code

You can access the configuration in code using the `get_config` function:

```python
from core.config import get_config

config = get_config()
app_name = config.app.name
debug_mode = config.app.debug
```

## Troubleshooting

If you encounter configuration issues:

1. Check that your YAML syntax is valid
2. Verify that environment variables are set correctly
3. Check the application logs for configuration-related errors
4. Try running with the `--debug` flag for more verbose output
