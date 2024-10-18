This file contains the sensitive settings for the application. At run-time is is merged with the `config.yml` information which contains the associated non-sensitive values. See the example below for a sample with detailed comments that explain the use of each configuration setting in the file.

```yaml
# Environment/Deployment Configuration
- name: dev  # Specifies the environment or deployment profile (e.g., dev, prod). NOTE this must match the profile in the config.yml file
  models:
    - model: gpt-4-deployment  # Model being deployed (GPT-4)
      api_key: "12345abcd67890xyz"  # Example API key for accessing the GPT-4 model
      base_url: "https://api.openai.com/v1/gpt4"  # Example base URL for the model deployment API

# Chat History Configuration
  chat_history:        
    database_connection_string: "AccountEndpoint=https://yourcosmosdbaccount.documents.azure.com:443/;AccountKey=yourcosmosdbkey;"  
    # Example connection string for Cosmos DB to store chat history (used only for Cosmos)

# Azure Search Services Configuration
  azure_search_services:
    - service: default  # Defines the default Azure search service
      key: "AZURE_SEARCH_API_KEY"  # Example API key for the Azure search service

# Chainlit Configuration
  chainlit_configuration:
    enable: true  # Enables Chainlit integration
    authentication: 
      enable: true  # Enables authentication for Chainlit
      github_secret: "your_github_secret_key"  # Example GitHub secret key for OAuth authentication
      github_client_id: "your_github_client_id"  # Example GitHub client ID for OAuth authentication

# Web Configuration
  web_configuration:
    authentication: 
      username: "admin_user"  # Example username for basic authentication
      password: "super_secure_password"  # Example password for basic authentication

```