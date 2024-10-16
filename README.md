
# Ingenious

**Ingenious** is a multi-agent accelerator designed to streamline the development and deployment of use cases for Large Language Models (LLMs). It provides pre-built conversation patterns and agent services that can be customized and extended for various LLM-driven applications.

The core focus of this repository is the use of **conversation patterns** within the `multi_agent` architecture, allowing for rapid iteration and deployment of agents that support conversational tasks. **Detailed documentation** on how to configure, extend, and use the package will be provided through an online **MkDocs** site.

## Getting Started

This section will guide you through the process of setting up **Ingenious** on your system. The package is developed in Python and uses **FastAPI** for its API services.

For detailed documentation: https://sturdy-fiesta-oz8q5k4.pages.github.io/



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
