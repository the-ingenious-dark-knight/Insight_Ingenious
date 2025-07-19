# Azure Blob Storage Setup Guide

This guide walks you through setting up Azure Blob Storage integration for Ingenious Framework, enabling cloud-based file storage for prompts, memory, and data persistence.

## Overview

Azure Blob Storage integration provides:
- **Cloud-based file storage** for prompt templates and revisions
- **Distributed memory management** for conversation context across sessions
- **Scalable data storage** for functional test outputs and artifacts
- **Multi-environment support** with secure authentication methods

## Prerequisites

1. **Azure Account**: Access to Azure portal and ability to create storage accounts
2. **Storage Account**: An Azure Storage Account with Blob service enabled
3. **Access Keys**: Storage account name and access key for authentication

## Azure Storage Account Setup

### 1. Create Storage Account

```bash
# Using Azure CLI
az storage account create \
    --name ingendev \
    --resource-group your-resource-group \
    --location eastus \
    --sku Standard_LRS \
    --kind StorageV2
```

### 2. Get Connection String

```bash
# Get connection string
az storage account show-connection-string \
    --name ingendev \
    --resource-group your-resource-group \
    --query connectionString \
    --output tsv
```

### 3. Create Containers

```bash
# Create containers for different purposes
az storage container create --name revisions --connection-string "YOUR_CONNECTION_STRING"
az storage container create --name data --connection-string "YOUR_CONNECTION_STRING"
```

## Configuration

Ingenious now uses environment variables for configuration instead of YAML files. Add the following to your `.env` file:

### File Storage Configuration for Prompts/Revisions

```bash
# Azure Blob Storage Configuration for Prompts/Revisions
INGENIOUS_FILE_STORAGE__REVISIONS__ENABLE=true
INGENIOUS_FILE_STORAGE__REVISIONS__STORAGE_TYPE=azure
INGENIOUS_FILE_STORAGE__REVISIONS__CONTAINER_NAME=prompts
INGENIOUS_FILE_STORAGE__REVISIONS__PATH=./
INGENIOUS_FILE_STORAGE__REVISIONS__ADD_SUB_FOLDERS=true
INGENIOUS_FILE_STORAGE__REVISIONS__URL=https://YOUR_STORAGE_ACCOUNT.blob.core.windows.net
# Use connection string as token for authentication
INGENIOUS_FILE_STORAGE__REVISIONS__TOKEN=DefaultEndpointsProtocol=https;AccountName=YOUR_STORAGE_ACCOUNT;AccountKey=YOUR_ACCOUNT_KEY;EndpointSuffix=core.windows.net
```

### File Storage Configuration for Data

```bash
# Azure Blob Storage Configuration for Data Files
INGENIOUS_FILE_STORAGE__DATA__ENABLE=true
INGENIOUS_FILE_STORAGE__DATA__STORAGE_TYPE=azure
INGENIOUS_FILE_STORAGE__DATA__CONTAINER_NAME=data
INGENIOUS_FILE_STORAGE__DATA__PATH=./
INGENIOUS_FILE_STORAGE__DATA__ADD_SUB_FOLDERS=true
INGENIOUS_FILE_STORAGE__DATA__URL=https://YOUR_STORAGE_ACCOUNT.blob.core.windows.net
# Use connection string as token for authentication
INGENIOUS_FILE_STORAGE__DATA__TOKEN=DefaultEndpointsProtocol=https;AccountName=YOUR_STORAGE_ACCOUNT;AccountKey=YOUR_ACCOUNT_KEY;EndpointSuffix=core.windows.net
```

**Important Notes:**
- Replace `YOUR_STORAGE_ACCOUNT` with your actual Azure Storage account name
- Replace `YOUR_ACCOUNT_KEY` with your actual storage account key
- The `TOKEN` field accepts a connection string when it contains "DefaultEndpointsProtocol"
- Set `PATH` to `./` to avoid path duplication issues

## Authentication Methods

Ingenious supports multiple Azure authentication methods:

### 1. Connection String (Recommended for Development)
```bash
# The library automatically detects connection strings
INGENIOUS_FILE_STORAGE__REVISIONS__TOKEN=DefaultEndpointsProtocol=https;AccountName=...
```

### 2. Managed Identity (Recommended for Production)
```bash
INGENIOUS_FILE_STORAGE__REVISIONS__AUTHENTICATION_METHOD=msi
INGENIOUS_FILE_STORAGE__REVISIONS__CLIENT_ID=your-managed-identity-client-id
```

### 3. Service Principal
```bash
INGENIOUS_FILE_STORAGE__REVISIONS__AUTHENTICATION_METHOD=client_id_and_secret
INGENIOUS_FILE_STORAGE__REVISIONS__CLIENT_ID=your-app-registration-client-id
INGENIOUS_FILE_STORAGE__REVISIONS__TOKEN=your-client-secret
```

### 4. Default Azure Credential
```bash
INGENIOUS_FILE_STORAGE__REVISIONS__AUTHENTICATION_METHOD=default_credential
# No additional credentials needed - uses Azure SDK credential chain
```

## Memory Management Integration

With Azure Blob Storage configured, memory management automatically uses cloud storage:

### Memory Manager Features

```python
from ingenious.services.memory_manager import MemoryManager
from ingenious.dependencies import get_config

# Initialize memory manager
config = get_config()
memory_manager = MemoryManager(config)

# Write memory to Azure Blob Storage
await memory_manager.write_memory("Conversation context", thread_id="user-123")

# Read memory from Azure Blob Storage
context = await memory_manager.read_memory(thread_id="user-123")

# Maintain memory with word limits
await memory_manager.maintain_memory("New content", max_words=150, thread_id="user-123")
```

### Conversation Pattern Integration

All conversation patterns automatically use Azure Blob Storage for memory:

- **SQL Manipulation Agent**: Context stored in cloud
- **Knowledge Base Agent**: Search context persisted
- **Classification Agent**: Classification history maintained
- **Custom Patterns**: Memory operations seamlessly integrated

## Prompts API Integration

The `/api/v1/prompts` routes automatically work with Azure Blob Storage:

### API Endpoints

```bash
# List prompt files for a revision
GET /api/v1/prompts/list/{revision_id}

# View prompt content
GET /api/v1/prompts/view/{revision_id}/{filename}

# Update prompt content
POST /api/v1/prompts/update/{revision_id}/{filename}
```

### Example Usage

```bash
# List prompts
curl "http://localhost:8080/api/v1/prompts/list/v1.0"

# View prompt
curl "http://localhost:8080/api/v1/prompts/view/v1.0/user_prompt.md"

# Update prompt
curl -X POST "http://localhost:8080/api/v1/prompts/update/v1.0/user_prompt.md" \
     -H "Content-Type: application/json" \
     -d '{"content": "# Updated Prompt\nNew content here"}'
```

## Testing Your Setup

### 1. Basic Connectivity Test

```python
import asyncio
from ingenious.dependencies import get_config
from ingenious.files.files_repository import FileStorage

async def test_azure_connection():
    config = get_config()
    storage = FileStorage(config, "data")

    # Test write
    await storage.write_file("test content", "test.txt", "connectivity-test")

    # Test read
    content = await storage.read_file("test.txt", "connectivity-test")
    print(f"Success! Read: {content}")

    # Cleanup
    await storage.delete_file("test.txt", "connectivity-test")

asyncio.run(test_azure_connection())
```

### 2. Memory Manager Test

```python
import asyncio
from ingenious.services.memory_manager import MemoryManager
from ingenious.dependencies import get_config

async def test_memory_manager():
    config = get_config()
    memory_manager = MemoryManager(config)

    # Test memory operations
    await memory_manager.write_memory("Test memory content")
    content = await memory_manager.read_memory()
    print(f"Memory content: {content}")

    # Cleanup
    await memory_manager.delete_memory()

asyncio.run(test_memory_manager())
```

### 3. API Test

```bash
# Start the API server
uv run ingen serve --port 8000

# Test prompts endpoints (in another terminal)
# List all revisions
curl "http://localhost:8000/api/v1/revisions/list"

# Upload a prompt template
curl -X POST "http://localhost:8000/api/v1/prompts/update/my-workflow/template.jinja" \
  -H "Content-Type: application/json" \
  -d '{"content": "# My Template\nContent here..."}'

# View a prompt template
curl "http://localhost:8000/api/v1/prompts/view/my-workflow/template.jinja"

# List prompts in a revision
curl "http://localhost:8000/api/v1/prompts/list/my-workflow"
```

## Troubleshooting

### Common Issues

1. **Connection String Issues**
   - Ensure the connection string includes all required components
   - Verify account name and key are correct
   - Check that EndpointSuffix matches your Azure region

2. **AuthorizationPermissionMismatch Error**
   - This occurs when authentication method conflicts with credentials
   - If using a connection string, ensure it's properly detected
   - The library should auto-detect connection strings containing "DefaultEndpointsProtocol"

3. **Path Duplication Issues**
   - Set `INGENIOUS_FILE_STORAGE__REVISIONS__PATH=./` to avoid duplicate paths
   - The library automatically adds `templates/prompts/{revision_id}` for prompts

4. **Silent Failures**
   - Check server logs for error messages
   - The Azure file storage implementation now properly raises exceptions
   - Use the test scripts above to debug connectivity issues

2. **Authentication Failures**
   - For MSI: Ensure managed identity is assigned to the resource
   - For Service Principal: Verify client ID and secret are correct
   - For Default Credential: Check Azure CLI login status

3. **Container Access Issues**
   - Verify containers exist in the storage account
   - Check that the service principal has appropriate permissions
   - Ensure container names match configuration

4. **File Operation Errors**
   - Check network connectivity to Azure
   - Verify storage account is not behind firewall restrictions
   - Ensure sufficient storage quota

### Debug Mode

Enable debug logging to troubleshoot issues:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Connection Validation

```bash
# Test connection using Azure CLI
az storage blob list \
    --container-name revisions \
    --connection-string "YOUR_CONNECTION_STRING"
```

## Performance Considerations

### Optimization Tips

1. **Regional Proximity**: Choose Azure regions close to your deployment
2. **Connection Pooling**: Configure appropriate connection timeouts
3. **Blob Tier**: Use appropriate storage tiers (Hot/Cool/Archive)
4. **Caching**: Implement local caching for frequently accessed files

### Monitoring

Monitor your Azure Blob Storage usage:
- Storage account metrics in Azure portal
- Request counts and latency
- Data transfer costs
- Storage capacity utilization

## Security Best Practices

1. **Use Managed Identity** in production environments
2. **Rotate access keys** regularly
3. **Enable encryption** at rest and in transit
4. **Configure firewall rules** to restrict access
5. **Monitor access logs** for unusual activity
6. **Use least privilege** access principles

## Migration from Local Storage

To migrate from local to Azure Blob Storage:

1. **Backup existing data**:
   ```bash
   tar -czf local-storage-backup.tar.gz .files/
   ```

2. **Update configuration** as described above

3. **Upload existing files** to Azure:
   ```bash
   az storage blob upload-batch \
       --destination revisions \
       --source .files/ \
       --connection-string "YOUR_CONNECTION_STRING"
   ```

4. **Test the migration**:
   ```bash
   uv run python test_basic_integration.py
   ```

5. **Remove local files** after verification

## Next Steps

- Explore [API Integration Guide](api-integration.md) for advanced API usage
- Check [Architecture Overview](../architecture/README.md) for system design
- Review [Troubleshooting Guide](../troubleshooting/README.md) for common issues

## Support

For issues with Azure Blob Storage integration:
1. Check the troubleshooting section above
2. Review Azure Storage documentation
3. Open an issue in the Ingenious Framework repository
4. Consult Azure support for storage account issues
