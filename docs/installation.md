# Installation Guide

This guide provides detailed instructions for installing and setting up Insight Ingenious.

## Prerequisites

Before installing Insight Ingenious, ensure you have the following prerequisites:

- Python 3.13 or higher
- [uv](https://docs.astral.sh/uv/) package manager (recommended)
- Git (for cloning the repository)

## Installation Methods

### Method 1: Using uv (Recommended)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Insight-Services-APAC/Insight_Ingenious.git
   cd Insight_Ingenious
   ```

2. **Install uv** if you don't have it already:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **Create a virtual environment and install the package**:
   ```bash
   uv venv
   uv pip install -e .
   ```

4. **Initialize a new project**:
   ```bash
   ingen_cli initialize-new-project
   ```

5. **Verify installation**:
   ```bash
   ingen_cli run-test-batch
   ```

### Method 2: Using pip

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Insight-Services-APAC/Insight_Ingenious.git
   cd Insight_Ingenious
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install the package**:
   ```bash
   pip install -e .
   ```

4. **Initialize a new project**:
   ```bash
   ingen_cli initialize-new-project
   ```

## Configuration

After installing Insight Ingenious, you'll need to configure it:

### 1. Project Configuration

The framework uses a `config.yml` file for its main configuration. When you run `ingen_cli initialize-new-project`, a template configuration file is created in your current directory.

### 2. Profile Configuration

Profiles are used to store sensitive information such as API keys. By default, the profile configuration is stored at `~/.ingenious/profiles.yml`.

A typical profile configuration looks like:

```yaml
profiles:
  - name: default
    openai:
      api_key: your_openai_api_key
      organization: your_organization_id
    azure_openai:
      api_key: your_azure_openai_key
      api_base: your_azure_openai_endpoint
```

### 3. Environment Variables

You can also configure Insight Ingenious using environment variables:

- `INGENIOUS_PROJECT_PATH`: Path to your project's configuration file
- `INGENIOUS_PROFILE_PATH`: Path to your profiles configuration file
- `INGENIOUS_WORKING_DIR`: Working directory for the application
- `KEY_VAULT_NAME`: (Optional) Azure Key Vault name for secret management

## Docker Installation

Insight Ingenious provides Docker images for easy deployment:

1. **Build the Docker image**:
   ```bash
   docker build -f dev_utils/docker/development_images/linux_development_image_python.dockerfile -t ingenious:dev .
   ```

2. **Run the container**:
   ```bash
   docker run -p 8000:80 -v $(pwd):/app ingenious:dev
   ```

## Troubleshooting

### Common Issues

1. **Missing dependencies**:
   If you encounter errors about missing dependencies, ensure you've installed all required packages:
   ```bash
   uv pip install -e .
   ```

2. **Configuration not found**:
   Ensure the `config.yml` file is in your current directory or set the `INGENIOUS_PROJECT_PATH` environment variable.

3. **Profile not found**:
   Ensure the profiles.yml file exists at `~/.ingenious/profiles.yml` or set the `INGENIOUS_PROFILE_PATH` environment variable.

### Getting Help

If you continue to experience issues, please check the project's GitHub repository for additional support resources.
