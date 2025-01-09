
# About

**Ingenious** is a multi-agent accelerator designed to streamline the development and deployment of use cases for Large Language Models (LLMs). 
It provides pre-built conversation patterns and agent services that can be customized and extended for various LLM-driven applications.

For detailed documentation: https://cuddly-fiesta-oz8nm4n.pages.github.io/.

- **[Our Open App](https://ingen-app.ambitiousriver-e696f55c.australiaeast.azurecontainerapps.io/)** - An open-source app for pattern demonstration.


## Setup Development Environment

To set up the development environment, follow these steps:

1. **Deactivate and Remove Existing Virtual Environment (if applicable)**:
   ```bash
   deactivate
   rm -rf .venv
   ```

2. **Create and Activate a New Virtual Environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install the Base Ingenious Package**:
   Run the following command to install the `ingenious` package without dependencies:
   ```bash
   pip install git+https://github.com/Insight-Services-APAC/Insight_Ingenious.git#egg=ingenious --force-reinstall
   ```

4. **Add the Ingenious Extensions Folder**:
   Place the `ingenious_extensions` folder into your project root directory. Ensure it contains the following structure:
   ```
   ingenious_extensions/
   ├── local_files/
   ├── models/
   ├── services/
   ├── templates/
   └── tests/
   ```

   This folder includes custom extensions such as models, services, and templates required for extending the base `ingenious` package.

5. **Create a `.gitignore` File**:
   Generate a `.gitignore` file to exclude unnecessary files and directories from version control:
   ```bash
      echo "
   .DS_Store
    /.venv
    /.chainlit
    /.idea
    /.cache
    /env_mkdocs/
    /ingenious_extensions/local_files/tmp/context.md
    /ingenious_extensions/local_files/tmp/*.db
    /functional_test_outputs/
   __pycache__" > .gitignore
   ```



### 6. **Create Profile and Configure Environment Variables**

Set up the environment variables following the provided insight documentation.


### 7. **Create Extension Templates (If not provided)**
```bash
ingen_cli generate-template-folders
```

### 8. **Run Tests**
Execute the test batch using the following command:
```bash
ingen_cli run-test-batch
```

