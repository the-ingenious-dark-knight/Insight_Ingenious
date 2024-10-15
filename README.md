# Introduction 
FastAgent is a multi-agent accelerator designed to get new use cases for LLMs up and running quickly.

# Getting Started
This section guides you through setting up the FastAgent, which is built with Python and FastAPI, on your system.

## Prerequisites
- Python 3.11 (3.10 minimum)
- pip (Python package installer)

## Recommended VS Code Extensions
The below VS Code extensions are recommended and listed in the workspace `.vscode/extensions.json` file:
- ms-python.flake8,
- ms-python.python,
- ms-python.debugpy,
- ms-python.vscode-pylance,
- ms-python.autopep8,
- ms-vscode.powershell,
- streetsidesoftware.code-spell-checker,
- streetsidesoftware.code-spell-checker-australian-english,
- pkief.material-icon-theme,
- samuelcolvin.jinjahtml

## Developer Tooling
The development specific Python packages are defined in the `requirements-dev.txt`, these are for linting, type checking & unit testing. Below are the developer tools used in the solution:

| Tool | Description | Config file |
|------|-------------|-------------|
| [autopep8](https://github.com/hhatto/autopep8)| Automatically formats Python code to conform to the [PEP 8](https://www.python.org/dev/peps/pep-0008) style guide | [.vscode/settings.json](.vscode/settings.json)
| [Flake8](https://flake8.pycqa.org/en/latest) | Linting tool for Python code | [.flake8](.flake8)<br>[.vscode/settings.json](.vscode/settings.json)
| [Pyright](https://microsoft.github.io/pyright) | Static type checker for Python code | [pyrightconfig.json](pyrightconfig.json)<br>[.vscode/settings.json](.vscode/settings.json)
| [pytest](https://docs.pytest.org/en/stable) | Unit testing framework for Python | [.vscode/settings.json](.vscode/settings.json)
| [pytest-cov](https://github.com/pytest-dev/pytest-cov) | Code coverage plugin for pytest | [.coveragerc](.coveragerc)
| [pytest-azurepipelines](https://github.com/Azure/pytest-azurepipelines) | Publishes pytest results in the Azure Pipelines UI | N/A

## Installation
1. Clone the repository to your local machine:
    ```shell
    git clone 
    ```

2. Navigate to the cloned repository:
    ```shell
    cd FastAgent
    ```

3. Create a virtual environment:
    ```shell
    python -m venv .venv
    ```

4. Activate the virtual environment:
    - On Windows:
      ```shell
      .venv\Scripts\activate
      ```
    - On macOS and Linux:
      ```shell
      source .venv/bin/activate
      ```

5. Install the required Python packages:
    ```shell
    pip install -r requirements.txt
    ```

6. To generate the local `.env` file, you can run the `generate-local-dotenv-file.ps1` script:
    ```shell
    ./generate-local-dotenv-file.ps1 -env "dev"
    ```
    After running the script, you should see the `.env` file generated with the required environment variables.
    > **Note:** Ensure you have PowerShell installed and configured on your system to run `.ps1` scripts. On macOS or Linux you might need to mark the script as executable with the command `chmod +x ./generate-local-dotenv-file.ps1`.
    

## Running the Application
Once all dependencies are installed, you can run the FastAPI server with the following command:
```shell
fastapi dev app/main.py
```

## Accessing the API Documentation
FastAPI automatically generates and serves interactive API documentation. Once the application is running, you can access the Swagger UI documentation at `http://127.0.0.1:8000/docs` and the ReDoc documentation at `http://127.0.0.1:8000/redoc`.

This should help you get the FastAgent backend solution up and running on your system. For further assistance, please refer to the FastAPI documentation.