# Azure OpenAI Integration

Insight Ingenious **exclusively** uses Azure OpenAI for all AI capabilities. This guide explains how to set up and use Azure OpenAI with this project.

## Important Note

This project **does not support** standard OpenAI API integration. All code and configurations are specifically designed for Azure OpenAI.

## Prerequisites

- An Azure account with access to Azure OpenAI services
- Azure OpenAI resource with deployed models
- API credentials for your Azure OpenAI resource

## Configuration

### Environment Variables

Set up the following environment variables in your `.env` file:

```
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_API_VERSION=2023-05-15
```

### Model Deployments

Ensure that you have deployed the necessary models in your Azure OpenAI resource. The application uses the following models by default:

- `gpt-4.1-mini` - The default model for most agents

You can change the model names in the `config.yaml` file to match your deployed models.

## Using Azure OpenAI in Custom Agents

When creating custom agents, you should use the AzureOpenAI client as shown in the example agents:

```python
from openai import AzureOpenAI

# Get client
def _get_client(self):
    """Get the Azure OpenAI client."""
    if self._client is None:
        # Create client with Azure OpenAI configuration
        config = self._get_model_config()
        self._client = AzureOpenAI(
            api_key=config.api_key,
            azure_endpoint=config.endpoint,
            api_version=config.api_version
        )
    return self._client
```

## Handling Responses

Azure OpenAI responses are structured slightly differently from standard OpenAI. Here's how to handle them:

```python
async def run(self, message: str, **kwargs) -> str:
    """Run the agent with a message."""
    try:
        client = self._get_client()
        model_config = self._get_model_config()
        
        response = client.chat.completions.create(
            model=self.config.model,
            messages=[
                {"role": "system", "content": self.config.system_message},
                {"role": "user", "content": message}
            ],
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens or 1000
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error in Azure OpenAI agent: {str(e)}")
        return f"Error: {str(e)}"
```

## Rate Limits and Quotas

Azure OpenAI has different rate limits and quotas than standard OpenAI. Be aware of these limitations when designing your application:

- Token per minute (TPM) limits based on your subscription
- Deployment-specific rate limits
- Maximum concurrent requests

You can check your usage and limits in the Azure Portal.

## Troubleshooting

Common issues with Azure OpenAI integration:

1. **Authentication errors**: Ensure your API key and endpoint are correct
2. **Model not found**: Check that the model name in your config matches a deployed model in your Azure resource
3. **Rate limit exceeded**: Implement retry logic or reduce the frequency of requests

If you're getting errors about models not being available, check the Azure OpenAI Studio to ensure the models are properly deployed.
