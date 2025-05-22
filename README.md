# Insight Ingenious

A framework for building, managing, and deploying multi-agent AI conversations.

## Features
- Multi-agent orchestration
- Extensible with custom agents, templates, and APIs
- Database and file storage integration
- CLI and REST API

## Quickstart
1. Clone the repo:
   ```bash
   git clone https://github.com/Insight-Services-APAC/Insight_Ingenious.git
   cd Insight_Ingenious
   ```
2. Install [uv](https://docs.astral.sh/uv/):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
3. Set up the project and install dependencies:
   ```bash
   uv venv
   uv pip install -e .
   ```
4. Initialize and test:
   ```bash
   ingen_cli initialize-new-project
   ingen_cli run-test-batch
   ```

See [docs/](docs/) for full documentation.

## Contributing

Contributions to Insight Ingenious are welcome! Please refer to the [CONTRIBUTING.md](./CONTRIBUTING.md) file for detailed contribution guidelines including code standards, pull request process, and development setup.
