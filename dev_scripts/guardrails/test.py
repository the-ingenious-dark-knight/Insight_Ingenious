import os
from openai import AzureOpenAI

#Current guardrail does not support azure in server mode.
#Quick alternative portkey.
#Limited function alternative, Azure Content Filter

# Set your API key and base URL
os.environ["OPENAI_API_KEY"] = "sk-your_openai_api_key"  # Set the API key here if not set in the environment
api_key = os.environ["OPENAI_API_KEY"]
base_url = "https://localhost:8000/guards/name-case/oai-syd-ing-dev-kfpqjli23em5m.openai.azure.com/openai/deployments/gpt-4o/completions?api-version=2024-08-01-preview"

# Initialize the AzureOpenAI client
client = AzureOpenAI(api_key=api_key, api_version='2024-08-01-preview', base_url=base_url)

# Make a completion request
response = client.Completion.create(
    engine="gpt-4",
    prompt="Explain environment variables in Python.",
    max_tokens=150
)

# Print the response from the API
print(response.choices[0].text)


from openai import AzureOpenAI

client = AzureOpenAI(
    api_key='#',
    api_version="2024-08-01-preview",
    azure_endpoint='https://oai-syd-ing-dev-kfpqjli23em5m.openai.azure.com'
)
completion = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": "Write a haiku about recursion in programming."
        }
    ]
)


from openai import AzureOpenAI

client = AzureOpenAI(
  azure_endpoint = 'http://127.0.0.1:8000/guards/name-case/openai/v1',
  api_key="1146698f66254e789bb81fa11517ebac",
  api_version="2024-08-01-preview"
)

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{
        "role": "user",
        "content": "Make up some gibberish for me please!"
    }]
)

print(completion.choices[0].message.content)














from openai import OpenAI
client = OpenAI(
    base_url='http://localhost:8000/guards/name-case/openai/v1',
)

completion = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": "Write a haiku about recursion in programming."
        }
    ]
)


#Non server version
from guardrails import Guard
import os
os.environ["AZURE_API_KEY"] = "#" # "my-azure-api-key"
os.environ["AZURE_API_BASE"] = "https://oai-syd-ing-dev-kfpqjli23em5m.openai.azure.com" # "https://example-endpoint.openai.azure.com"
os.environ["AZURE_API_VERSION"] = "2024-08-01-preview" # "2023-05-15"

guard = Guard()

result = guard(
    model="azure/gpt-4o",
    messages=[{"role":"user", "content":"How many moons does Jupiter have?"}],
)

print(f"{result.validated_output}")






