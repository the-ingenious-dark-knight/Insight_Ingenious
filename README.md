# Setup Development Environment

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

4. **Add the Ingenious Extensions and tmp Folder**:
   Place the `ingenious_extensions` and `tmp` folder into your project root directory. Ensure it contains the following structure:
   ```
   tmp/
   ├── context.md
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
    /dist/
    /functional_test_outputs/
   __pycache__" > .gitignore
   ```



### 6. **Create Profile and Configure Environment Variables**

Set up the `APPSETTING_INGENIOUS_CONFIG` and `APPSETTING_INGENIOUS_PROFILE` environment variables with the following configuration:

#### **`APPSETTING_INGENIOUS_CONFIG`**
```json
{
    "profile": "dev",
    "models": [
        {
            "model": "model-name",
            "api_type": "azure",
            "api_version": "2024-08-01-preview"
        }
    ],
    "logging": {
        "root_log_level": "debug",
        "log_level": "debug"
    },
    "chat_history": {
        "database_type": "sqlite",
        "database_path": "./tmp/chat_history.db",
        "database_name": "ChatHistoryDB",
        "memory_path": "./tmp"
    },
    "chainlit_configuration": {
        "enable": false
    },
    "chat_service": {
        "type": "multi_agent"
    },
    "tool_service": {
        "enable": false
    },
    "local_sql_db": {
        "database_path": "./tmp/local_database.db",
        "sample_csv_path": "./data/sample_data.csv",
        "sample_database_name": "LocalSampleData"
    },
    "azure_sql_services": {
        "database_name": "skip",
        "table_name": "sample_table"
    },
    "azure_search_services": [
        {
            "service": "search-demo-service",
            "endpoint": "https://example.search.windows.net"
        }
    ],
    "web_configuration": {
        "type": "fastapi",
        "asynchronous": true,
        "ip_address": "0.0.0.0",
        "port": 80,
        "authentication": {
            "enable": false,
            "type": "basic"
        }
    },
    "file_storage": {
        "enable": true,
        "storage_type": "azure", #option: local or azure
        "container_name": "example-container",
        "path": "."
    }
}
```

#### **`APPSETTING_INGENIOUS_PROFILE`**
```json
[
    {
        "name": "dev",
        "models": [
            {
                "model": "model-name",
                "api_key": "your-api-key",
                "base_url": "https://example.azure.com/openai/deployments/model-name/chat/completions?api-version=2024-08-01-preview"
            }
        ],
        "chat_history": {
            "database_connection_string": "Your_Database_Connection_String_Here"
        },
        "azure_search_services": [
            {
                "service": "Your_Search_Service_Name",
                "key": "Your_Search_Service_Key"
            }
        ],
        "azure_sql_services": {
            "database_connection_string": "Your_SQL_Connection_String_Here"
        },
        "receiver_configuration": {
            "enable": true,
            "api_url": "https://example-web.azurewebsites.net/api/ai-response/publish",
            "api_key": "ReceiverApiKey"
        },
        "chainlit_configuration": {
            "enable": false,
            "authentication": {
                "enable": false,
                "github_secret": "",
                "github_client_id": ""
            }
        },
        "web_configuration": {
            "authentication": {
                "enable": false,
                "username": "example-user",
                "password": "hashed-password-here"
            }
        },
        "file_storage": {
            "url": "https://example.blob.core.windows.net/",
            "token": "your-access-token"
        }
    }
]
```

### 7. **Create Extension Templates (If not provided)**
```bash
ingen_cli generate-template-folders
```

### 8. **Run Tests**
Execute the test batch using the following command:
```bash
ingen_cli run-test-batch
```


You are now ready to begin development using the `ingenious` package and with CA extensions!
