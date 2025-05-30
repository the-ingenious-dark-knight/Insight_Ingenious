# Getting Started

This guide will help you set up and run the ingenious-slim project.

## Prerequisites

- Python 3.9 or higher
- [uv](https://github.com/astral-sh/uv) installed (for package management)
- Azure OpenAI account with API access

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd ingenious-slim
```

2. Copy the environment template:

```bash
cp .env.example .env
```

3. Edit the `.env` file to add your Azure OpenAI credentials:

```
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_API_VERSION=2023-05-15
```

4. Install dependencies using uv:

```bash
uv pip install -e .
```

## Configuration

Edit `config.yaml` to customize your setup:

```yaml
app:
  name: "My Agent API"
  debug: false

auth:
  enabled: true
  # Username and password loaded from environment variables:
  # AUTH_USERNAME and AUTH_PASSWORD

models:
  default_llm:
    model: "gpt-4.1-mini"
    temperature: 0.7
    max_tokens: 1000
    # API credentials loaded from environment variables

agents:
  enabled:
    - "chat"
    - "research"
    - "sql"
```

## Running the Server

Always use `uv` to run the application:

```bash
# Using the built-in command
uv run python main.py

# Or using uvicorn through uv
uv run uvicorn main:app --reload

# With custom config
uv run python main.py --config my-config.yaml
```

## Testing the API

Visit `http://localhost:8000/docs` for interactive API documentation, or:

```bash
curl -u admin:your_password http://localhost:8000/api/v1/health
```

## Next Steps

- Check out the [examples](./examples/index.md) to see how to use the agents
- Learn how to [create custom agents](./guides/custom_agents.md)
- Explore the [API documentation](./api/index.md) for details on available endpoints
