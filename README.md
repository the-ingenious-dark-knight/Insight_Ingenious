
# Ingenious

**Ingenious** is a multi-agent accelerator designed to streamline the development and deployment of use cases for Large Language Models (LLMs). It provides pre-built conversation patterns and agent services that can be customized and extended for various LLM-driven applications.

The core focus of this repository is the use of **conversation patterns** within the `multi_agent` architecture, allowing for rapid iteration and deployment of agents that support conversational tasks. **Detailed documentation** on how to configure, extend, and use the package will be provided through an online **MkDocs** site.

## Getting Started

This section will guide you through the process of setting up **Ingenious** on your system. The package is developed in Python and uses **FastAPI** for its API services.

### Prerequisites

Ensure you have the following prerequisites installed before proceeding:

- **Python 3.12** (Minimum required version: 3.12)
- **pip** (Python package installer)

### Recommended VS Code Extensions

To improve your development experience, the following VS Code extensions are recommended. These are included in the `.vscode/extensions.json` file for your convenience:

- ms-python.flake8
- ms-python.python
- ms-python.debugpy
- ms-python.vscode-pylance
- ms-python.autopep8
- ms-vscode.powershell
- streetsidesoftware.code-spell-checker
- streetsidesoftware.code-spell-checker-australian-english
- pkief.material-icon-theme
- samuelcolvin.jinjahtml

### Developer Tooling

The package includes development tools for linting, type checking, and testing. These are defined in the `requirements-dev.txt` file. Below is a table of the primary tools used:

| Tool                                                | Description                                                                                | Config File                           |
|-----------------------------------------------------|--------------------------------------------------------------------------------------------|---------------------------------------|
| [autopep8](https://github.com/hhatto/autopep8)       | Automatically formats Python code to follow the [PEP 8](https://www.python.org/dev/peps/pep-0008) style guide | `.vscode/settings.json`               |
| [Flake8](https://flake8.pycqa.org/en/latest)         | Python linting tool                                                                        | `.flake8`, `.vscode/settings.json`    |
| [Pyright](https://microsoft.github.io/pyright)       | Static type checker for Python                                                             | `pyrightconfig.json`, `.vscode/settings.json` |
| [pytest](https://docs.pytest.org/en/stable)          | Unit testing framework for Python                                                          | `.vscode/settings.json`               |
| [pytest-cov](https://github.com/pytest-dev/pytest-cov) | Code coverage plugin for pytest                                                           | `.coveragerc`                         |
| [pytest-azurepipelines](https://github.com/Azure/pytest-azurepipelines) | Publishes pytest results in Azure Pipelines UI                               | N/A                                   |

## Installation

Follow these steps to set up the **Ingenious** package locally:

1. **Clone the repository**:
    ```bash
    git clone <repository-url>
    ```

2. **Navigate to the repository**:
    ```bash
    cd ingenious
    ```

3. **Create a virtual environment**:
    ```bash
    python -m venv .venv
    ```

4. **Activate the virtual environment**:
    - On **Windows**:
      ```bash
      .venv\Scripts\activate
      ```
    - On **macOS/Linux**:
      ```bash
      source .venv/bin/activate
      ```

5. **Install the dependencies**:
    ```bash
    pip install -r requirements.txt
    ```


[//]: # ()
[//]: # (## Running the Application)

[//]: # ()
[//]: # (Once everything is installed, you can start the **FastAPI** server using the command:)

[//]: # ()
[//]: # (```bash)

[//]: # (uvicorn app.main:app --reload)

[//]: # (```)

[//]: # ()
[//]: # (This will start the development server, and the API will be accessible locally.)

[//]: # ()
[//]: # (### Accessing API Documentation)

[//]: # ()
[//]: # (After the server is running, you can view the interactive API documentation via:)

[//]: # ()
[//]: # (- **Swagger UI**: [http://127.0.0.1:8000/docs]&#40;http://127.0.0.1:8000/docs&#41;)

[//]: # (- **ReDoc**: [http://127.0.0.1:8000/redoc]&#40;http://127.0.0.1:8000/redoc&#41;)

[//]: # ()
[//]: # (## Conclusion)

[//]: # ()
[//]: # (**Ingenious** provides the scaffolding and pre-tested conversation patterns necessary to accelerate your LLM applications. For more in-depth documentation, including examples and best practices, please refer to the MkDocs-powered documentation site [here]&#40;#&#41;.)

[//]: # ()
