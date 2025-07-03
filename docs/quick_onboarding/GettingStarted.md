# Basic Onboarding

> This is a very simple guide just to get you started playing with the Ingenious playground.

Overall steps:
1. Clone the repo or get it via pip (and download dependencies of course, unless you don't wanna test)
2. Initialize the project
3. Run the test project.


## Clone the repo / Install via pip

```bash
# Clone the repository
git clone https://github.com/Insight-Services-APAC/Insight_Ingenious.git
cd Insight_Ingenious

# Install dependencies (make sure you have installed uv before doing this)
uv venv
uv pip install -e .

# Initialize project
ingen_cli initialize-new-project
```
## Initializing the project
Once you ran `ingen_cli` successfully, you need to deal with two configuration files--`config.yml` and `profiles.yml`.

### Configuration Files
1. Edit `config.yml` in your project directory (**_Note: you may need to coordinate with your team lead with this so that you may be provided the necessary credentials._**)
2. Create or edit `profiles.yml` in `~/.ingenious/`
3. Set environment variables. Replace `path/to/your/project` below with an actual file path, then run this in your terminal application:
   ```bash
   export INGENIOUS_PROJECT_PATH=/path/to/your/project/config.yml
   export INGENIOUS_PROFILE_PATH=~/.ingenious/profiles.yml
   ```

## Testing out the CLI

### Initialize a new project

```bash
ingen_cli initialize-new-project
```

This creates the necessary folder structure and configuration files.

### Check Workflow Requirements

Before starting, understand what each workflow needs:

```bash
# See all available workflows and their requirements
ingen_cli workflow-requirements all

# Check specific workflow requirements
ingen_cli workflow-requirements classification_agent
```

### Start with Minimal Configuration

For quick testing, start with workflows that only need Azure OpenAI:

1. Update `config.yml` with your Azure OpenAI model settings
2. Update `~/.ingenious/profiles.yml` with your API key and endpoint
3. Set environment variables:
   ```bash
   export INGENIOUS_PROJECT_PATH=/path/to/config.yml
   export INGENIOUS_PROFILE_PATH=$HOME/.ingenious/profiles.yml
   ```

### Start the Application

```bash
ingen_cli run-rest-api-server
```

Starts the FastAPI server with Chainlit UI.

### Testing the UI

Once the application is running, access the web UI at:
- http://localhost:8000 - Main application
- http://localhost:8000/chainlit - Chainlit chat interface
- http://localhost:8000/prompt-tuner - Prompt tuning interface

### Testing chat with the agents

#### Quick Test (Minimal Configuration)
Test with workflows that only need Azure OpenAI:

1. Navigate to http://localhost:8000/chainlit
2. Start a new conversation
3. Try these workflows:
   - "Hello" with `classification_agent`
   - "Analyze bike sales" with `bike_insights`

#### API Testing
```bash
# Test classification agent (minimal config needed)
curl -X POST http://localhost:8081/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"user_prompt": "Hello world", "conversation_flow": "classification_agent"}'
```

#### Advanced Workflows
For workflows requiring external services:

- **knowledge_base_agent**: Requires Azure Cognitive Search
- **sql_manipulation_agent**: Requires database connection

Check requirements with:
```bash
ingen_cli workflow-requirements <workflow_name>
```

See [Workflow Configuration Requirements](../workflows/README.md) for detailed setup.

> **Once you are able to run those commands successfully, access the UI, and test basic workflows, you're good to go! For advanced workflows requiring external services, check their specific configuration requirements.**

Next up: Building custom agents. Go to **CustomAgents.md**
