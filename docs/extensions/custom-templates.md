---
title: "Custom Templates"
layout: single
permalink: /extensions/custom-templates/
sidebar:
  nav: "docs"
toc: true
toc_label: "Template Guide"
toc_icon: "file-code"
---

This guide covers creating and using custom templates in Insight Ingenious.

## Creating Custom Prompts

### Local Development
1. Create a new template in `templates/prompts/your_prompt_name.jinja`
2. Use Jinja2 syntax for dynamic content

### Production with Azure Blob Storage
1. Upload templates to the `prompts` container in Azure Blob Storage
2. Templates will be automatically discovered by the system
3. Local templates serve as fallbacks if Azure templates are unavailable

Example:
```jinja
I am an agent tasked with providing insights about {{ topic }} based on the input payload.

User input: {{ user_input }}

Please provide a detailed analysis focusing on:
1. Key facts
2. Relevant context
3. Potential implications

Response format:
{
  "analysis": {
    "key_facts": [],
    "context": "",
    "implications": []
  },
  "recommendation": ""
}
```
> Note: If you are familiar with Jinja, you can pass on custom values on the prompt using the **{{variable}}** syntax.

### Using Templates in Agents

1. Once the templates are properly defined, you can invoke its usage by using the function `Get_Template`.
2. Render the prompt.

Code implementation:
```python
async def get_conversation_response(self, chat_request: ChatRequest) -> ChatResponse:
    # Load the template
    template_content = await self.Get_Template(file_name="your_prompt_name.jinja")

    # Render the template with dynamic values
    env = Environment()
    template = env.from_string(template_content)
    rendered_prompt = template.render(
        topic="example topic",
        user_input=chat_request.user_prompt
    )

    # Use the rendered prompt
    your_agent.system_prompt = rendered_prompt
```

## Error Handling Best Practices

Always implement fallback templates when using the `Get_Template` method:

```python
async def get_conversation_response(self, chat_request: ChatRequest) -> ChatResponse:
    try:
        # Try to load custom template
        template_content = await self.Get_Template(file_name="your_prompt_name.jinja")
    except Exception as e:
        # Log the error for debugging
        self._logger.warning(f"Failed to load template: {str(e)}")
        
        # Provide fallback template
        template_content = """You are a helpful assistant.
        
User Request: {{ user_input }}

Please provide a helpful response."""

    # Continue with template rendering...
    env = Environment()
    template = env.from_string(template_content)
    rendered_prompt = template.render(user_input=chat_request.user_prompt)
```

## Template Upload to Azure Blob Storage

To upload templates to Azure Blob Storage for production use:

1. **Using Azure CLI:**
```bash
az storage blob upload \
    --account-name your-storage-account \
    --container-name prompts \
    --name your_template.jinja \
    --file ./templates/prompts/your_template.jinja
```

2. **Using the Prompts API:**
```bash
curl -X POST http://your-server/api/v1/prompts/update/your-revision/your_template.jinja \
    -H "Content-Type: application/json" \
    -d '{"content": "Your template content here..."}'
```
