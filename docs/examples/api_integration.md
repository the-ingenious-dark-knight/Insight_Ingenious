# API Integration Examples

This document provides examples of how to integrate with the Insight Ingenious API from external applications.

## Basic API Authentication

All API requests require HTTP Basic Authentication:

```python
import requests

# Base URL
base_url = "http://localhost:8000"

# Authentication credentials
username = "admin"
password = "your_password"

# Make an authenticated request
response = requests.get(
    f"{base_url}/health",
    auth=(username, password)
)

print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
```

## Health Check

Check if the API is healthy:

```python
import requests

response = requests.get(
    "http://localhost:8000/health",
    auth=("admin", "your_password")
)

if response.status_code == 200 and response.json()["status"] == "ok":
    print("API is healthy!")
else:
    print("API health check failed.")
```

## Chat with an Agent

Send a message to a chat agent:

```python
import requests

# Chat request
chat_data = {
    "message": "Hello! Can you tell me about Python programming?",
    "agent_type": "chat"
}

# Send the request
response = requests.post(
    "http://localhost:8000/api/v1/chat",
    json=chat_data,
    auth=("admin", "your_password")
)

# Process the response
if response.status_code == 200:
    result = response.json()
    print(f"Agent: {result['agent_type']}/{result['agent_name']}")
    print(f"Response: {result['response']}")
else:
    print(f"Error: {response.status_code}")
    print(response.text)
```

## Research with a Research Agent

Use the research agent for information gathering:

```python
import requests

# Research request
research_data = {
    "message": "Research the impact of artificial intelligence on healthcare",
    "agent_type": "research"
}

# Send the request
response = requests.post(
    "http://localhost:8000/api/v1/chat",
    json=research_data,
    auth=("admin", "your_password")
)

# Process the response
if response.status_code == 200:
    result = response.json()
    print(f"Research Results:\n{result['response']}")
else:
    print(f"Error: {response.status_code}")
    print(response.text)
```

## Generate SQL with a SQL Agent

Use the SQL agent to generate database queries:

```python
import requests

# SQL request
sql_data = {
    "message": "Create a query to find all users who registered in the last 30 days",
    "agent_type": "sql"
}

# Send the request
response = requests.post(
    "http://localhost:8000/api/v1/chat",
    json=sql_data,
    auth=("admin", "your_password")
)

# Process the response
if response.status_code == 200:
    result = response.json()
    print(f"Generated SQL:\n{result['response']}")
else:
    print(f"Error: {response.status_code}")
    print(response.text)
```

## List Available Agent Types

Get a list of available agent types:

```python
import requests

response = requests.get(
    "http://localhost:8000/api/v1/agents/types",
    auth=("admin", "your_password")
)

if response.status_code == 200:
    agent_types = response.json()
    print("Available agent types:")
    for agent_type in agent_types:
        print(f"- {agent_type}")
else:
    print(f"Error: {response.status_code}")
    print(response.text)
```

## Create a New Agent Instance

Create a custom agent instance:

```python
import requests

# Agent creation request
agent_data = {
    "agent_type": "chat",
    "name": "my_custom_chat",
    "config": {
        "system_message": "You are a friendly and helpful assistant specialized in technical support.",
        "temperature": 0.5
    }
}

# Send the request
response = requests.post(
    "http://localhost:8000/api/v1/agents",
    json=agent_data,
    auth=("admin", "your_password")
)

# Process the response
if response.status_code == 200:
    result = response.json()
    print(f"Agent created: {result['success']}")
else:
    print(f"Error: {response.status_code}")
    print(response.text)
```

## Complete Python Client Example

Here's a complete example of a Python client for the API:

```python
import requests
from typing import Dict, Any, Optional, List

class InsightIngeniousClient:
    """Client for the Insight Ingenious API."""
    
    def __init__(self, base_url: str, username: str, password: str):
        """Initialize the client."""
        self.base_url = base_url
        self.auth = (username, password)
    
    def check_health(self) -> Dict[str, Any]:
        """Check the API health."""
        response = requests.get(
            f"{self.base_url}/health",
            auth=self.auth
        )
        response.raise_for_status()
        return response.json()
    
    def list_agent_types(self) -> List[str]:
        """List available agent types."""
        response = requests.get(
            f"{self.base_url}/api/v1/agents/types",
            auth=self.auth
        )
        response.raise_for_status()
        return response.json()
    
    def list_agents(self) -> List[str]:
        """List available agent instances."""
        response = requests.get(
            f"{self.base_url}/api/v1/agents",
            auth=self.auth
        )
        response.raise_for_status()
        return response.json()
    
    def chat(self, message: str, agent_type: str = "chat", context: Optional[Dict[str, Any]] = None) -> str:
        """Chat with an agent."""
        data = {
            "message": message,
            "agent_type": agent_type,
            "context": context
        }
        
        response = requests.post(
            f"{self.base_url}/api/v1/chat",
            json=data,
            auth=self.auth
        )
        response.raise_for_status()
        return response.json()["response"]
    
    def create_agent(self, agent_type: str, name: str, config: Optional[Dict[str, Any]] = None) -> bool:
        """Create a new agent instance."""
        data = {
            "agent_type": agent_type,
            "name": name,
            "config": config
        }
        
        response = requests.post(
            f"{self.base_url}/api/v1/agents",
            json=data,
            auth=self.auth
        )
        response.raise_for_status()
        return response.json()["success"]
    
    def delete_agent(self, agent_name: str) -> bool:
        """Delete an agent instance."""
        response = requests.delete(
            f"{self.base_url}/api/v1/agents/{agent_name}",
            auth=self.auth
        )
        response.raise_for_status()
        return response.json()["success"]


# Usage example
if __name__ == "__main__":
    client = InsightIngeniousClient(
        base_url="http://localhost:8000",
        username="admin",
        password="your_password"
    )
    
    # Check health
    health = client.check_health()
    print(f"API Health: {health['status']}")
    
    # List agent types
    agent_types = client.list_agent_types()
    print(f"Available agent types: {agent_types}")
    
    # Chat with an agent
    response = client.chat(
        message="Hello! Can you tell me about Python programming?",
        agent_type="chat"
    )
    print(f"Chat response: {response}")
```

## JavaScript Client Example

Here's an example of a JavaScript client for the API:

```javascript
class InsightIngeniousClient {
  constructor(baseUrl, username, password) {
    this.baseUrl = baseUrl;
    this.credentials = btoa(`${username}:${password}`);
  }

  async request(endpoint, method = 'GET', data = null) {
    const headers = {
      'Authorization': `Basic ${this.credentials}`,
      'Content-Type': 'application/json'
    };

    const options = {
      method,
      headers
    };

    if (data) {
      options.body = JSON.stringify(data);
    }

    const response = await fetch(`${this.baseUrl}${endpoint}`, options);
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  async checkHealth() {
    return this.request('/health');
  }

  async listAgentTypes() {
    return this.request('/api/v1/agents/types');
  }

  async listAgents() {
    return this.request('/api/v1/agents');
  }

  async chat(message, agentType = 'chat', context = null) {
    const data = {
      message,
      agent_type: agentType,
      context
    };

    const response = await this.request('/api/v1/chat', 'POST', data);
    return response.response;
  }

  async createAgent(agentType, name, config = null) {
    const data = {
      agent_type: agentType,
      name,
      config
    };

    const response = await this.request('/api/v1/agents', 'POST', data);
    return response.success;
  }

  async deleteAgent(agentName) {
    const response = await this.request(`/api/v1/agents/${agentName}`, 'DELETE');
    return response.success;
  }
}

// Usage example
async function main() {
  const client = new InsightIngeniousClient(
    'http://localhost:8000',
    'admin',
    'your_password'
  );

  try {
    // Check health
    const health = await client.checkHealth();
    console.log(`API Health: ${health.status}`);

    // List agent types
    const agentTypes = await client.listAgentTypes();
    console.log(`Available agent types: ${agentTypes.join(', ')}`);

    // Chat with an agent
    const response = await client.chat(
      'Hello! Can you tell me about JavaScript programming?',
      'chat'
    );
    console.log(`Chat response: ${response}`);
  } catch (error) {
    console.error('Error:', error.message);
  }
}

main();
```
