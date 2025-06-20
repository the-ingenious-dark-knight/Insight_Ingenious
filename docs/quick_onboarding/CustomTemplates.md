## Using Custom Templates

### Creating Custom Prompts

1. Create a new template in `templates/prompts/your_prompt_name.jinja`
2. Use Jinja2 syntax for dynamic content

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
