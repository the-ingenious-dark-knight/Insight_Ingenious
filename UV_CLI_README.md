# Running `ingen_cli` using `uv`

The Insight Ingenious CLI (`ingen_cli`) can now be run using the `uv run` command. This allows you to execute CLI commands within the project's virtual environment.

## Available Commands

```bash
# Show help and available commands
uv run ingen_cli --help

# Run tests
uv run ingen_cli run-test-batch

# Initialize a new project
uv run ingen_cli initialize-new-project

# Start the REST API server
uv run ingen_cli run-rest-api-server

# Run the prompt tuner
uv run ingen_cli run-prompt-tuner
```

## Command-Specific Options

Each command has its own set of options. Use `--help` to view them:

```bash
uv run ingen_cli run-test-batch --help
uv run ingen_cli run-rest-api-server --help
```

## Using Environment Variables

You can set environment variables to control the behavior of the CLI:

```bash
export INGENIOUS_PROJECT_PATH=/path/to/config.yml
export INGENIOUS_PROFILE_PATH=~/.ingenious/profiles.yml
export INGENIOUS_WORKING_DIR=/path/to/project

uv run ingen_cli run-rest-api-server
```
