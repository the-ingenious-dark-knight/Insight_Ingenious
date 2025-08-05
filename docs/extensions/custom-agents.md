---
title: "Creating Custom Agents"
layout: single
permalink: /extensions/custom-agents/
sidebar:
  nav: "docs"
toc: true
toc_label: "Custom Agents"
toc_icon: "robot"
---

The next step in working with the Ingenious library is working with the creation of agents for orchestration.
This is done by defining the agent's persona, existing/prior knowledge/experience, the explicit instruction and set of examples that the model can follow for the output.

## Creating External Agents (Recommended)

The preferred approach is to create agents **outside** the library code using the external extension pattern. This allows you to develop custom agents without modifying the core library.

### External Agent Setup

1. **Create Extension Directory Structure** (if not exists):
   ```
   your_project/
   └── ingenious_extensions/
       ├── __init__.py
       ├── services/
       │   └── chat_services/
       │       └── multi_agent/
       │           └── conversation_flows/
       │               └── your_agent_name/
       │                   ├── __init__.py
       │                   ├── your_agent_name.py
       │                   └── templates/
       │                       └── prompts/
       │                           └── agent_prompt.jinja
       └── models/
           └── agent.py
   ```

2. **Implement IConversationFlow Interface**:
   ```python
   # your_agent_name.py
   from ingenious.models.chat import ChatRequest, ChatResponse
   from ingenious.services.interfaces.IConversationFlow import IConversationFlow
   from autogen_agentchat import AssistantAgent, UserProxyAgent
   
   class ConversationFlow(IConversationFlow):
       async def get_conversation_response(
           self, chat_request: ChatRequest
       ) -> ChatResponse:
           # Your multi-agent workflow implementation
           pass
   ```

3. **Agent Discovery**: The system uses a 3-tier discovery mechanism:
   - First: `ingenious_extensions` (your local directory)
   - Then: `ingenious.ingenious_extensions_template` (library template)
   - Finally: `ingenious.services.chat_services.multi_agent.conversation_flows` (core library)

### Complete External Agent Implementation

Here's a complete example of an external multi-agent workflow:

**Directory Structure:**
```
your_project/
└── ingenious_extensions/
    └── services/
        └── chat_services/
            └── multi_agent/
                └── conversation_flows/
                    └── product_research/
                        ├── __init__.py
                        ├── product_research.py
                        └── templates/
                            └── prompts/
                                ├── market_research_agent_prompt.jinja
                                ├── technical_analysis_agent_prompt.jinja
                                └── recommendation_agent_prompt.jinja
```

**Implementation (`product_research.py`):**
```python
from typing import Any, Dict
import json
from autogen_agentchat import AssistantAgent, UserProxyAgent
from autogen_core import CancellationToken
from jinja2 import Template

from ingenious.models.chat import ChatRequest, ChatResponse
from ingenious.services.interfaces.IConversationFlow import IConversationFlow

class ConversationFlow(IConversationFlow):
    def __init__(self, parent_service):
        super().__init__(parent_service)
        self.template_service = parent_service.template_service
    
    async def get_conversation_response(
        self, chat_request: ChatRequest
    ) -> ChatResponse:
        try:
            # Load templates with fallback
            market_template = await self._load_template_with_fallback("market_research_agent_prompt.jinja")
            technical_template = await self._load_template_with_fallback("technical_analysis_agent_prompt.jinja")
            recommendation_template = await self._load_template_with_fallback("recommendation_agent_prompt.jinja")
            
            # Create specialized agents
            market_agent = AssistantAgent(
                name="market_research_agent",
                model_client=self.parent_service.model_client,
                system_message=market_template,
            )
            
            technical_agent = AssistantAgent(
                name="technical_analysis_agent", 
                model_client=self.parent_service.model_client,
                system_message=technical_template,
            )
            
            recommendation_agent = AssistantAgent(
                name="recommendation_agent",
                model_client=self.parent_service.model_client,
                system_message=recommendation_template,
            )
            
            user_proxy = UserProxyAgent(name="user_proxy")
            
            # Execute multi-agent workflow
            result = await user_proxy.a_send_message(
                message=chat_request.user_prompt,
                recipient=market_agent,
                request_reply=True,
            )
            
            return ChatResponse(
                response=result.chat_message.content,
                conversation_flow="product-research"
            )
            
        except Exception as e:
            return ChatResponse(
                response=f"Error in product research workflow: {str(e)}",
                conversation_flow="product-research"
            )
    
    async def _load_template_with_fallback(self, template_name: str) -> str:
        """Load template with fallback to default content if Azure storage fails"""
        try:
            return await self.template_service.load_template(f"templates/prompts/{template_name}")
        except Exception as e:
            print(f"Failed to load template {template_name}: {e}, using fallback")
            return self._get_fallback_template(template_name)
    
    def _get_fallback_template(self, template_name: str) -> str:
        """Provide fallback templates when Azure storage is unavailable"""
        fallbacks = {
            "market_research_agent_prompt.jinja": """You are a market research specialist...
            Your task is to analyze market trends and provide insights about {{user_prompt}}""",
            "technical_analysis_agent_prompt.jinja": """You are a technical analysis expert...
            Analyze the technical specifications and requirements for {{user_prompt}}""",
            "recommendation_agent_prompt.jinja": """You are a recommendation expert...
            Provide specific recommendations based on the analysis of {{user_prompt}}"""
        }
        return fallbacks.get(template_name, "You are a helpful AI assistant.")
```

**Template Example (`market_research_agent_prompt.jinja`):**
```jinja2
You are a market research specialist with expertise in technology products and market analysis.

Your task is to analyze market trends, pricing, and availability for the following request:
{{ user_prompt }}

Please provide:
1. Current market landscape
2. Price ranges and value propositions
3. Popular brands and models
4. Market trends and recommendations

Be thorough but concise in your analysis.
```

### Testing Your External Agent

1. **Copy to Template Directory**: For the agent to be discovered, copy your extension to the library's template directory:
   ```bash
   cp -r ingenious_extensions/services/chat_services/multi_agent/conversation_flows/your_agent \
       your_library_path/ingenious/ingenious_extensions_template/services/chat_services/multi_agent/conversation_flows/
   ```

2. **Test via API**: Use the conversation flow in API requests:
   ```json
   {
     "user_prompt": "Your test prompt",
     "conversation_flow": "your-agent-name",
     "thread_id": "test-thread-001"
   }
   ```

### Best Practices for External Agents

- **Template Fallbacks**: Always implement fallback templates for when Azure storage is unavailable
- **Error Handling**: Wrap workflows in try-catch blocks with meaningful error messages
- **Agent Naming**: Use descriptive names that reflect the agent's specialized role
- **Modular Design**: Keep agent logic focused on specific domains or tasks
- **Testing**: Test both with and without Azure storage configuration

## Creating Internal Agents (Library Modification)

If you need to modify the library directly (not recommended for most use cases):

### Setting up the agent

1. Create a new agent folder in `ingenious/services/chat_services/multi_agent/agents/your_agent_name/`
2. Create these files:
   - `agent.md`: Agent definition and persona (required)
   - `tasks/task.md`: Task description for the agent (optional, used for agents with specific task flows)

### Agent Definition Example


```md
# Your Agent Name

## Name and Persona

* Name: Your name is Ingenious and you are a [Specialty] Expert
* Description: You are a [specialty] expert assistant. Your role is to [description of responsibilities].

## System Message

### Backstory

[Background information about the agent's role and knowledge]

### [Additional sections as needed, e.g., Curriculum, Cohort Considerations, etc.]

[Content specific to your agent's domain]

## Role

[Detailed description of the agent's specific role and responsibilities]

Reply TERMINATE in the end when everything is done.
```

> **Note**: LLMs work best with a more precise syntax and information provided. It does not need to be always quite verbose, but always be mindful of the language that you use with the commands/prompt that you make.
